# Project Memory & Decision Ledger
## Catalist Media Meeting Memory System

This document serves as the persistent memory store and architectural decision record (ADR) for the Catalist Media Meeting Memory System. It preserves critical context, domain insights, design trade-offs, and debug traces.

---

## 1. Key Architectural Decisions (ADRs)

### ADR-01: SQLite FTS5 (BM25) Over External Vector Databases
- **Decision:** Use SQLite FTS5 for primary indexing and retrieval instead of Pinecone, ChromaDB, or Weaviate.
- **Context:** The corpus requires finding specific numbers (`"12.50"`, `"7.60"`), technical terms (`"L_C_D_"`, `"titanium"`), and precise component names (`"stress ball"`, `"kinetic"`).
- **Trade-off:** Pure dense vector embeddings often blur specialized acronyms or exact numerical thresholds into broad semantic neighborhoods. FTS5 provides exact lexical BM25 matching in $< 2\text{ms}$ with zero network overhead, zero cloud subscription costs, and a portable single-file database.

### ADR-02: Atomic Speaker Turns as Ingestion Chunks
- **Decision:** Chunk transcripts strictly by individual speaker turns rather than arbitrary token counts or time windows.
- **Context:** The evaluation harness enforces that every citation must exist entirely within a **single speaker turn**.
- **Trade-off:** Chunking by fixed token lengths (e.g. 500 tokens) would inevitably split dialogue mid-turn or combine statements across different speakers, risking instant citation failure.

### ADR-03: Zero-LLM Deterministic Ingestion
- **Decision:** Use streaming regex (`^\d{2}:\d{2}:\d{2}\s+Speaker\s+[A-D]`) to parse all transcripts and extract speaker roles without calling any LLM.
- **Context:** At 10,000 meetings, calling an LLM for ingestion would cost thousands of dollars and take hours.
- **Result:** Ingested all 138 meetings (~676,000 words) in **1.8 seconds** at **\$0.00** cost.

### ADR-04: Automated Character-Span Alignment & Snapping
- **Decision:** Implement a deterministic token-alignment algorithm in `src/citation_verifier.py` to snap fuzzy LLM quotes back to exact character spans in raw transcripts.
- **Context:** LLMs frequently "clean up" speech disfluencies, dropping `"um"`, `"uh"`, or hyphenations like `"L_C_D_"`. The evaluation harness checks strings word-for-word, so any cleaned-up quote fails.
- **Result:** Quotes retain authentic speech tokens, guaranteeing 100% exact substring containment.

### ADR-05: Forward Chronological Dialectic Tracking ($a \to b \to c \to d$)
- **Decision:** Process candidate turns in strict chronological order.
- **Context:** Many questions ask: *"What did they plan first, what did they end with, and why did they switch?"*
- **Result:** Allows the reasoning agent to track decision evolution: from kickoff proposals in $a$, to functional brainstorming in $b$, detailed trade-offs in $c$, and final budget cuts in $d$.

---

## 2. Corpus Ground Truth & Domain Knowledge

- **Corpus Makeup:** 138 real meetings from the AMI Meeting Corpus (~676,000 words) across 35 teams.
- **Team Phase Distribution:** 33 teams have 4 meetings (`a`, `b`, `c`, `d`). Exactly 2 teams have only 3 meetings: `IS1002` and `IS1005`.
- **Team Roles in Kickoff ($a$):**
  - **Speaker A:** Project Manager (leads meetings, sets agenda, presents budget limits).
  - **Speaker B:** User Interface Designer (controls buttons, menus, usability).
  - **Speaker C:** Industrial Designer (specifies materials, battery, casing, hardware).
  - **Speaker D:** Marketing Expert (focuses on customer preferences, market trends, retail pricing).
- **TS3012 Briefing Horizon:** The brief is specifically for Team TS3012 **prior to their final meeting ($d$)**. It synthesizes meetings `TS3012a`, `b`, and `c`, capturing the state of the project right before meeting $d$ begins.

---

## 3. Real Bugs Caught, Diagnostic Traces & Permanent Fixes

### Bug 1: SequenceMatcher Global Ratio Dilution
- **Symptom:** Valid candidate quotes were rejected during snapping when matched against long speaker turns.
- **Root Cause:** In Python's `difflib.SequenceMatcher`, comparing a 7-word quote to a 100-word turn yields a global similarity ratio of $2 \times 7 / (7 + 100) = 0.13$, falling below standard threshold checks.
- **Fix:** Switched from global ratio checks to a token set intersection filter ($\ge 50\%$ token overlap) followed by a sliding window substring matcher.

### Bug 2: 4-to-5 Word Citation Length Violations
- **Symptom:** First automated audit reported 10 question failures where quotes had fewer than 6 words (e.g. `"Could drop the speech recognition"` = 5 words).
- **Root Cause:** LLMs prefer minimal, punchy quotes without trailing conversational context.
- **Fix:** Added a turn-expansion routine that expands candidate spans to full complete sentences within the same turn, guaranteeing $\ge 6$ words.

### Bug 3: Speaker A Role Misattribution
- **Symptom:** Speaker A was misclassified as "Marketing Expert" in TS3012.
- **Root Cause:** In Turn 0, Speaker A introduced himself as Project Manager, then turned to Speaker D and said: *"You're our Marketing Expert"*. A naive keyword check assigned Marketing to Speaker A.
- **Fix:** Constrained role pattern matching to first-person self-introductions (`"I'll be your..."`, `"My name is..."`) and excluded second-person phrases (`"you're"`).

### Bug 4: Formal Contraction Expansion in Brief Citations
- **Symptom:** Deep audit of the TS3012 brief caught 3 citations failing substring checks (`"Let us vote on it"` instead of `"Let's vote on it"`).
- **Root Cause:** The brief generator wrote clean English instead of preserving conversational contractions.
- **Fix:** Replaced the brief quotes with the exact verbatim raw transcript tokens, achieving 100% pass on all 9 brief citations.

---

## 4. Cost & Latency Scalability Ledger

| Metric | 138 Meetings (Test Set) | 1,000 Meetings | 10,000 Meetings |
| :--- | :--- | :--- | :--- |
| **Ingestion Latency** | 1.8 seconds | ~13 seconds | ~2.1 minutes |
| **Ingestion Token Cost** | **\$0.00** | **\$0.00** | **\$0.00** |
| **Database Size** | 10.4 MB | ~75 MB | ~750 MB |
| **Query Retrieval Time** | $< 2\text{ ms}$ | $< 3\text{ ms}$ | $< 5\text{ ms}$ (partitioned) |
| **LLM Query Cost (25 Qs)**| ~\$0.08 | ~\$0.08 | ~\$0.08 |

---

## 5. Current State of the System

- **Submission File:** `answers.json` (25 answers + TS3012 brief).
- **Verification Audit:** **25 / 25 questions passed (100% precision) | TS3012 Brief passed**.
- **CLI Commands Verified:**
  - `python main.py ingest`
  - `python main.py ask --qid Q01`
  - `python main.py brief --team TS3012`
  - `python main.py run --all --verify`
  - `python scripts/verify_submission.py --answers answers.json`
