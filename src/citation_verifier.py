"""
Deterministic Citation Verifier & Character-Span Snapping Engine.
Verifies word-for-word string containment within single speaker turns.
Snaps slightly noisy quotes (dropped 'um'/'uh', punctuation differences) to exact transcript spans.
"""

import re
import sqlite3
import difflib
from typing import Dict, List, Tuple, Optional, Any


def normalize_tokens(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words, preserving internal underscores."""
    return re.findall(r"[A-Za-z0-9_]+", text.lower())


def normalize_string(text: str) -> str:
    """Normalize whitespace and lower-case text."""
    return re.sub(r"\s+", " ", text).strip().lower()


class CitationVerifier:
    def __init__(self, db_path: str = "meeting_memory.db"):
        self.db_path = db_path

    def _get_turns_for_meeting(self, meeting_id: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute("""
            SELECT id, meeting_id, team_id, phase, turn_index, timestamp, speaker, text, word_count, char_start, char_end
            FROM turns
            WHERE meeting_id = ?
            ORDER BY turn_index ASC
        """, (meeting_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def snap_to_verbatim_span(self, candidate_quote: str, raw_turn: str, min_words: int = 6) -> Optional[str]:
        """
        Locates the best matching contiguous character span in raw_turn corresponding to candidate_quote.
        Preserves natural speech tokens ('um', 'uh', 'L_C_D_', punctuation).
        """
        clean_cand = normalize_string(candidate_quote)
        clean_raw = normalize_string(raw_turn)

        # 1. Direct exact containment check
        if clean_cand in clean_raw:
            escaped_words = [re.escape(w) for w in candidate_quote.strip().split()]
            pattern_str = r"\s+".join(escaped_words)
            m = re.search(pattern_str, raw_turn, re.IGNORECASE)
            if m:
                matched_span = raw_turn[m.start():m.end()].strip()
                if len(matched_span.split()) >= min_words:
                    return matched_span

        cand_tokens = normalize_tokens(candidate_quote)
        if len(cand_tokens) < 3:
            return None

        raw_words = raw_turn.split()
        if len(raw_words) < min_words:
            return None

        # Build list of normalized tokens for each word in raw_words
        raw_word_tokens = [re.findall(r"[A-Za-z0-9_]+", w.lower()) for w in raw_words]
        flattened_raw = [t for sublist in raw_word_tokens for t in sublist]

        matcher = difflib.SequenceMatcher(None, cand_tokens, flattened_raw)
        best_match = matcher.find_longest_match(0, len(cand_tokens), 0, len(flattened_raw))
        
        # If match coverage is high enough (at least 4 tokens or 50% of quote)
        if best_match.size >= max(4, int(len(cand_tokens) * 0.5)):
            token_count = 0
            start_word_idx = 0
            end_word_idx = len(raw_words)

            for w_idx, w_tokens in enumerate(raw_word_tokens):
                prev_count = token_count
                token_count += len(w_tokens)
                if prev_count <= best_match.b < token_count:
                    start_word_idx = w_idx
                if prev_count < (best_match.b + best_match.size) <= token_count:
                    end_word_idx = w_idx + 1
                    break

            # Expand window to satisfy min_words constraint if needed
            while end_word_idx - start_word_idx < min_words and end_word_idx < len(raw_words):
                end_word_idx += 1
            while end_word_idx - start_word_idx < min_words and start_word_idx > 0:
                start_word_idx -= 1

            candidate_span = " ".join(raw_words[start_word_idx:end_word_idx]).strip()
            # Clean leading/trailing punctuation if dangling
            candidate_span = candidate_span.strip(" ,.-;:?")
            if len(candidate_span.split()) >= min_words:
                return candidate_span

        return None

    def verify_and_repair_citation(
        self, meeting_id: str, quote: str, candidate_turn_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Verifies citation against transcripts in meeting_id.
        Returns: (is_valid, final_quote, matched_turn_dict)
        """
        turns = self._get_turns_for_meeting(meeting_id)
        if not turns:
            return False, f"Meeting {meeting_id} not found in database", None

        # 1. Candidate turn check
        if candidate_turn_id:
            cand_turn = next((t for t in turns if t["id"] == candidate_turn_id), None)
            if cand_turn:
                snapped = self.snap_to_verbatim_span(quote, cand_turn["text"])
                if snapped:
                    return True, snapped, cand_turn

        clean_quote = normalize_string(quote)

        # 2. Exact match check
        for turn in turns:
            if clean_quote in normalize_string(turn["text"]):
                snapped = self.snap_to_verbatim_span(quote, turn["text"])
                if snapped and len(snapped.split()) >= 6:
                    return True, snapped, turn

        # 3. High token-overlap snap
        cand_tokens = set(normalize_tokens(quote))
        if not cand_tokens:
            return False, quote, None

        best_turn = None
        best_overlap = 0.0
        best_snapped = None

        for turn in turns:
            turn_tokens = set(normalize_tokens(turn["text"]))
            overlap = len(cand_tokens.intersection(turn_tokens)) / len(cand_tokens)
            if overlap >= 0.5 and overlap > best_overlap:
                snapped = self.snap_to_verbatim_span(quote, turn["text"])
                if snapped:
                    best_overlap = overlap
                    best_turn = turn
                    best_snapped = snapped

        if best_snapped and len(best_snapped.split()) >= 6:
            return True, best_snapped, best_turn

        return False, quote, None
