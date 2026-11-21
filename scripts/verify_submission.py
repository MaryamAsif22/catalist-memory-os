#!/usr/bin/env python3
"""
Verification Script for Catalist Media Agentic AI Assessment Submission.
Audits answers.json against questions.json and transcripts/ for schema compliance,
verbatim citation accuracy, single-turn containment, and constraint satisfaction.
"""

import os
import sys
import json
import re
import argparse
from typing import Dict, List, Tuple, Any


def normalize_text(text: str) -> str:
    """Normalize whitespace and lower-case text for robust exact matching."""
    return re.sub(r"\s+", " ", text).strip().lower()


def parse_turns(transcript_path: str) -> List[Dict[str, str]]:
    """Parse a transcript into individual speaker turns."""
    if not os.path.exists(transcript_path):
        return []
    
    with open(transcript_path, "r", encoding="utf-8") as f:
        content = f.read()

    turn_pattern = re.compile(r"^(\d{2}:\d{2}:\d{2})\s+(Speaker\s+[A-D])", re.MULTILINE)
    matches = list(turn_pattern.finditer(content))
    
    turns = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        turn_text = content[start:end].strip()
        turns.append({
            "timestamp": match.group(1),
            "speaker": match.group(2),
            "raw_text": turn_text,
            "normalized_text": normalize_text(turn_text)
        })
    return turns


def verify_citation_in_transcript(meeting_id: str, quote: str, transcripts_dir: str) -> Tuple[bool, str]:
    """
    Verifies that quote is:
    1. At least 6 words long
    2. Exists word-for-word inside a single speaker turn in transcripts/{meeting_id}.txt
    """
    clean_quote = normalize_text(quote)
    words = quote.strip().split()
    if len(words) < 6:
        return False, f"Quote is only {len(words)} words long (minimum is 6 words): '{quote[:30]}...'"
    
    file_path = os.path.join(transcripts_dir, f"{meeting_id}.txt")
    if not os.path.exists(file_path):
        return False, f"Transcript file not found: {file_path}"
    
    turns = parse_turns(file_path)
    if not turns:
        return False, f"Could not parse any speaker turns from {file_path}"
    
    for turn in turns:
        if clean_quote in turn["normalized_text"]:
            return True, f"Matched in {turn['speaker']} at {turn['timestamp']}"
            
    return False, f"Quote not found in any single speaker turn of {meeting_id}: '{clean_quote[:60]}...'"


def audit_submission(answers_path: str, questions_path: str, transcripts_dir: str) -> bool:
    print("=" * 80)
    print(f"AUDITING SUBMISSION: {answers_path}")
    print("=" * 80)

    if not os.path.exists(answers_path):
        print(f"[FAIL] Submission file '{answers_path}' does not exist.")
        return False

    try:
        with open(answers_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[FAIL] Invalid JSON in '{answers_path}': {e}")
        return False

    if "answers" not in data or "brief" not in data:
        print("[FAIL] Missing top-level 'answers' or 'brief' key in submission.")
        return False

    answers = data["answers"]
    brief = data["brief"]

    # Load questions
    expected_qids = []
    if os.path.exists(questions_path):
        with open(questions_path, "r", encoding="utf-8") as f:
            qdata = json.load(f)
            expected_qids = [q["question_id"] for q in qdata.get("questions", [])]

    print(f"Total answers provided: {len(answers)}")
    print(f"Expected questions count: {len(expected_qids)}")

    passed_answers = 0
    failed_answers = 0
    errors = []

    answer_map = {a.get("question_id"): a for a in answers if "question_id" in a}

    for qid in expected_qids:
        if qid not in answer_map:
            errors.append(f"[{qid}] Missing answer completely.")
            failed_answers += 1
            continue

        item = answer_map[qid]
        ans_text = item.get("answer", "").strip()
        citations = item.get("citations", [])

        # Check answer text
        if not ans_text:
            errors.append(f"[{qid}] Answer text is empty.")
            failed_answers += 1
            continue

        # Check sentence count: 1 to 3 plain sentences (Instruction 7)
        sentences = [s.strip() for s in re.split(r"[.!?]+", ans_text) if s.strip()]
        if not (1 <= len(sentences) <= 3):
            errors.append(f"[{qid}] Answer has {len(sentences)} sentences (must be 1-3).")
            failed_answers += 1
            continue

        # Check citations count: 1 to 3
        if not (1 <= len(citations) <= 3):
            errors.append(f"[{qid}] Answer has {len(citations)} citations (must be 1-3).")
            failed_answers += 1
            continue

        # Check distinct meetings: at least two meetings of the named team (Instruction 7)
        distinct_mids = set(c.get("meeting_id", "").strip() for c in citations if c.get("meeting_id"))
        if len(distinct_mids) < 2:
            errors.append(f"[{qid}] Citations cover only {len(distinct_mids)} meeting ({list(distinct_mids)}). Instruction 7 requires at least two meetings of the named team.")
            failed_answers += 1
            continue

        # Verify each citation
        citation_failed = False
        for c_idx, cit in enumerate(citations):
            mid = cit.get("meeting_id", "").strip()
            quote = cit.get("quote", "").strip()

            if not mid or not quote:
                errors.append(f"[{qid}] Citation #{c_idx+1} missing meeting_id or quote.")
                citation_failed = True
                continue

            ok, msg = verify_citation_in_transcript(mid, quote, transcripts_dir)
            if not ok:
                errors.append(f"[{qid}] Citation #{c_idx+1} verification failed in {mid}: {msg}")
                citation_failed = True

        if citation_failed:
            failed_answers += 1
        else:
            passed_answers += 1

    # Check brief
    brief_ok = True
    print("-" * 80)
    print("VERIFYING BRIEF FOR TEAM TS3012...")
    if not isinstance(brief, str) or len(brief.strip()) < 100:
        errors.append("[BRIEF] Brief is too short or not a string.")
        brief_ok = False
    else:
        # Check required sections
        required_concepts = ["decid", "change", "action", "disagree"]
        brief_lower = brief.lower()
        for concept in required_concepts:
            if concept not in brief_lower:
                errors.append(f"[BRIEF] Brief appears to be missing section/concept for: '{concept}'")
                brief_ok = False

    print("-" * 80)
    print(f"SUMMARY: {passed_answers}/{len(expected_qids)} questions passed citation audit.")
    if brief_ok:
        print("[BRIEF] TS3012 briefing check passed.")
    else:
        print("[BRIEF] TS3012 briefing had issues.")

    if errors:
        print(f"\nTotal Errors Found: {len(errors)}")
        for err in errors[:25]:
            print("  - " + err)
        if len(errors) > 25:
            print(f"  ... and {len(errors) - 25} more errors.")
        return False

    print("\n[SUCCESS] ALL CHECKS PASSED PERFECTLY!")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit submission against AMI corpus and questions")
    parser.add_argument("--answers", default="answers.json", help="Path to answers.json")
    parser.add_argument("--questions", default="questions.json", help="Path to questions.json")
    parser.add_argument("--transcripts", default="transcripts", help="Path to transcripts directory")
    args = parser.parse_args()

    success = audit_submission(args.answers, args.questions, args.transcripts)
    sys.exit(0 if success else 1)
