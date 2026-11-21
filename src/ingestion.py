"""
Deterministic Ingestion Engine for Catalist Media Meeting Memory System.
Zero LLM calls: Pure regex parsing + SQLite FTS5 BM25 full-text indexing.
Designed to scale to 10,000+ meetings with partitioned indexing.
"""

import os
import re
import glob
import sqlite3
import argparse
from typing import Dict, List, Tuple, Optional


TURN_REGEX = re.compile(r"^(\d{2}:\d{2}:\d{2})\s+(Speaker\s+[A-D])", re.MULTILINE)

CANONICAL_ROLES = [
    ("Project Manager", re.compile(r"\bproject\s+manager\b", re.I)),
    ("Industrial Designer", re.compile(r"\bindustrial\s+designer\b", re.I)),
    ("User Interface Designer", re.compile(r"\b(user\s+interface\s+designer|ui\s+designer|user\s+interface)\b", re.I)),
    ("Marketing Expert", re.compile(r"\b(marketing\s+expert|marketing)\b", re.I)),
]


def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize SQLite database with standard tables and FTS5 virtual table."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                turn_index INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                speaker TEXT NOT NULL,
                text TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                char_start INTEGER NOT NULL,
                char_end INTEGER NOT NULL
            );
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_turns_team_phase ON turns(team_id, phase);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_turns_meeting ON turns(meeting_id);")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                team_id TEXT NOT NULL,
                speaker TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT,
                PRIMARY KEY (team_id, speaker)
            );
        """)

        # FTS5 full-text search index
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS turns_fts USING fts5(
                text,
                meeting_id UNINDEXED,
                team_id UNINDEXED,
                phase UNINDEXED,
                speaker UNINDEXED,
                content='turns',
                content_rowid='id'
            );
        """)

        # Triggers to keep FTS5 synchronized with turns table
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS turns_ai AFTER INSERT ON turns BEGIN
                INSERT INTO turns_fts(rowid, text, meeting_id, team_id, phase, speaker)
                VALUES (new.id, new.text, new.meeting_id, new.team_id, new.phase, new.speaker);
            END;
        """)
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS turns_ad AFTER DELETE ON turns BEGIN
                INSERT INTO turns_fts(turns_fts, rowid, text, meeting_id, team_id, phase, speaker)
                VALUES('delete', old.id, old.text, old.meeting_id, old.team_id, old.phase, old.speaker);
            END;
        """)

    return conn


def parse_transcript_file(file_path: str) -> Tuple[str, str, str, List[Dict]]:
    """
    Parses a single transcript file into atomic speaker turns with exact character spans.
    """
    basename = os.path.basename(file_path).replace(".txt", "")
    match = re.match(r"^([A-Z]{2}\d{4})([a-d])$", basename)
    if not match:
        raise ValueError(f"Filename does not match expected pattern: {basename}")
    
    team_id = match.group(1)
    phase = match.group(2)
    meeting_id = basename

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    matches = list(TURN_REGEX.finditer(content))
    turns = []

    for i, m in enumerate(matches):
        start_char = m.end()
        end_char = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        turn_text = content[start_char:end_char].strip()
        timestamp = m.group(1)
        speaker = m.group(2)
        word_count = len(turn_text.split())

        turns.append({
            "meeting_id": meeting_id,
            "team_id": team_id,
            "phase": phase,
            "turn_index": i,
            "timestamp": timestamp,
            "speaker": speaker,
            "text": turn_text,
            "word_count": word_count,
            "char_start": start_char,
            "char_end": end_char
        })

    return team_id, phase, meeting_id, turns


def extract_roles_from_kickoff(turns: List[Dict]) -> Dict[str, Tuple[str, Optional[str]]]:
    """
    Extracts speaker roles and names from kickoff meeting 'a' turns.
    Speakers typically introduce themselves in the first 25 turns.
    """
    roles: Dict[str, Tuple[str, Optional[str]]] = {}
    
    name_intro_patterns = [
        re.compile(r"(?:my name is|i am|i'm)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", re.I),
        re.compile(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*,\s*(?:User Interface|Industrial|Marketing|Project)", re.I)
    ]

    first_person_role_patterns = [
        re.compile(r"(?:i'll be|i will be|i am|i'm)\s+(?:your\s+|the\s+)?([a-z\s]+)", re.I),
        re.compile(r"(?:as\s+(?:the\s+)?)([a-z\s]+?)(?:,\s*i|\s+i)", re.I),
        re.compile(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*,\s*([A-Za-z\s]+?)(?:\.|$)", re.I)
    ]

    for turn in turns[:35]:
        speaker = turn["speaker"]
        text = turn["text"]

        curr_role, curr_name = roles.get(speaker, ("Team Member", None))

        # Check self-declared name
        if not curr_name:
            for npat in name_intro_patterns:
                m = npat.search(text)
                if m:
                    cand = m.group(1).strip()
                    cand_clean = cand.split()[0]
                    if cand_clean.lower() not in ["going", "the", "a", "here", "just", "not", "also", "okay"]:
                        curr_name = cand
                        break

        # Check self-declared role in first person
        for fpat in first_person_role_patterns:
            m = fpat.search(text)
            if m:
                snippet = m.group(0).lower()
                for canonical_name, cpat in CANONICAL_ROLES:
                    if cpat.search(snippet):
                        curr_role = canonical_name
                        break
            if curr_role != "Team Member":
                break

        # If still Team Member, check if entire turn matches a role
        if curr_role == "Team Member":
            for canonical_name, cpat in CANONICAL_ROLES:
                # Avoid assigning if speaker was asking someone else: "Let's start with you... You're our Marketing Expert"
                if cpat.search(text) and "you're" not in text.lower() and "your role" not in text.lower():
                    curr_role = canonical_name
                    break

        roles[speaker] = (curr_role, curr_name)

    return roles


def ingest_corpus(transcripts_dir: str, db_path: str) -> None:
    """Ingests all transcript files in transcripts_dir into SQLite FTS5."""
    files = sorted(glob.glob(os.path.join(transcripts_dir, "*.txt")))
    if not files:
        raise FileNotFoundError(f"No transcript files found in {transcripts_dir}")

    print(f"Ingesting {len(files)} transcript files into {db_path}...")
    
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = init_db(db_path)

    total_turns = 0
    team_kickoff_turns: Dict[str, List[Dict]] = {}

    for file_path in files:
        team_id, phase, meeting_id, turns = parse_transcript_file(file_path)
        total_turns += len(turns)

        if phase == "a":
            team_kickoff_turns[team_id] = turns

        with conn:
            conn.executemany("""
                INSERT INTO turns (meeting_id, team_id, phase, turn_index, timestamp, speaker, text, word_count, char_start, char_end)
                VALUES (:meeting_id, :team_id, :phase, :turn_index, :timestamp, :speaker, :text, :word_count, :char_start, :char_end);
            """, turns)

    # Extract and store roles for each team
    total_roles = 0
    with conn:
        for team_id, k_turns in team_kickoff_turns.items():
            roles = extract_roles_from_kickoff(k_turns)
            for speaker, (role, name) in roles.items():
                conn.execute("""
                    INSERT OR REPLACE INTO roles (team_id, speaker, role, name)
                    VALUES (?, ?, ?, ?);
                """, (team_id, speaker, role, name))
                total_roles += 1

    conn.close()
    print(f"Ingestion complete: {len(files)} meetings, {total_turns} speaker turns, {total_roles} roles indexed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deterministic Transcript Ingestion")
    parser.add_argument("--transcripts", default="transcripts", help="Path to transcripts directory")
    parser.add_argument("--db", default="meeting_memory.db", help="Path to SQLite output database")
    args = parser.parse_args()

    ingest_corpus(args.transcripts, args.db)
