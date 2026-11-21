---
name: verify-submission
description: Programmatically audit answers.json and TS3012 brief for schema compliance, verbatim citation accuracy, and constraint enforcement.
---

# Verify Submission Skill

Use this skill to audit the system's generated `answers.json` and briefing output against all Catalist Media requirements.

## What It Checks
1. **JSON Schema Conformance:** Validates that `answers.json` has the top-level keys `"answers"` and `"brief"`.
2. **Question Completeness:** Verifies that all 25 questions (Q01 through Q25) from `questions.json` are present.
3. **Answer Constraints:**
   - Answers are concise (1 to 3 plain sentences).
   - Speaker letters (`Speaker A`, `B`, `C`, `D`) and roles are attributed when required.
4. **Verbatim Citation Integrity:**
   - Each answer has between 1 and 3 citations.
   - Each citation references a valid `meeting_id`.
   - Each citation quote has $\ge 6$ words.
   - Each citation is verified as an exact, normalized substring contained within a **single speaker turn** in `transcripts/{meeting_id}.txt`.
5. **TS3012 Briefing Verification:**
   - Checks presence and length of the pre-meeting brief.
   - Verifies coverage of key required sections: Decisions Made, Evolutionary Changes, Open Action Items & Owners, and Unresolved Disagreements.
   - Verifies all embedded citations against `transcripts/TS3012*.txt`.

## How to Run

```bash
python scripts/verify_submission.py --answers answers.json --transcripts transcripts/ --questions questions.json
```
