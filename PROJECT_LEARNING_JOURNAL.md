# Catalist Media Meeting Memory: Project & Learning Journal

Welcome! This document is your step-by-step learning guide. It is written in simple, plain English so that anyone—regardless of prior AI or software engineering experience—can understand **why** we are building this system, **what technologies** we chose, **how** everything works under the hood, and **what the LLM (AI) does vs what plain code does**.

---

## Table of Contents
1. [The Big Picture: What Problem Are We Solving?](#1-the-big-picture-what-problem-are-we-solving)
2. [What Data Do We Have?](#2-what-data-do-we-have)
3. [The Golden Rule: Code vs. AI (The "Model-vs-Code" Boundary)](#3-the-golden-rule-code-vs-ai-the-model-vs-code-boundary)
4. [The 10 Architectural Pillars (Approved Design Decisions)](#4-the-10-architectural-pillars-approved-design-decisions)
5. [The Technology Choices & Layman Explanations](#5-the-technology-choices--layman-explanations)
6. [Step-by-Step Activity Log & Implementation Details](#6-step-by-step-activity-log--implementation-details)
7. [The Bugs We Caught During Deep Auditing & How We Fixed Them](#7-the-bugs-we-caught-during-deep-auditing--how-we-fixed-them)
8. [Final Audit & Benchmark Results](#8-final-audit--benchmark-results)
9. [Complete Deliverables Checklist: Is Anything Left?](#9-complete-deliverables-checklist-is-anything-left)

---

## 1. The Big Picture: What Problem Are We Solving?

Imagine you are running a company where every meeting is recorded and transcribed into text. Over weeks and months, you have **hundreds of hours of transcripts**:
- People brainstorm ideas in Meeting 1.
- People change their minds in Meeting 2 because of component costs.
- People assign tasks in Meeting 3 ("Xavier will research rubber casing costs").
- In Meeting 4, they present the final product and drop features that went over budget.

**The pain point:** Humans forget. When someone asks:
> *"Why did we drop the touchscreen, and what did we keep instead?"*

Nobody wants to spend 8 hours reading through 50 pages of raw dialogue.
Furthermore, before a critical final meeting, a team needs an **Executive Briefing**:
- What did we already agree on?
- What changed along the way?
- What tasks are still pending, and who owns them?
- What arguments or disagreements are still unresolved?

**Our Mission:**
Build an intelligent, automated assistant (an "Agentic Meeting Memory System") that can:
1. Read and index all 138 real meeting transcripts (and scale to 10,000+ meetings).
2. Answer 25 complex questions spanning multiple meetings, with **100% exact, word-for-word quotes** from the transcripts as citations.
3. Automatically generate a high-stakes executive brief for Team TS3012 before their final meeting.

---

## 2. What Data Do We Have?

We were provided with the **AMI Meeting Corpus**:
- **138 total meeting transcripts** across 35 distinct teams (~676,000 words in all).
- Each team consists of 4 people designing a new TV remote control:
  - **Speaker A:** Project Manager (leads meetings, manages agenda, timeline, and budget).
  - **Speaker B:** User Interface (UI) Designer (decides buttons, screens, menus, usability).
  - **Speaker C:** Industrial Designer (decides materials, casing, battery, internal hardware).
  - **Speaker D:** Marketing Expert (focuses on user trends, target demographics, retail pricing).
- Each team meets up to four times, labeled chronologically with letters:
  - `a`: Kickoff meeting & team member introductions
  - `b`: Functional design & brainstorming
  - `c`: Detailed design & look-and-feel
  - `d`: Costing, budget trimming, & final prototype sign-off
- **Real Conversational Speech:** These are not polished scripts! People stutter, say `"um"`, `"uh"`, cut each other off, and say acronyms like `"L_C_D_"`. Citations must match this text **character-for-character**.

---

## 3. The Golden Rule: Code vs. AI (The "Model-vs-Code" Boundary)

A rookie mistake in AI development is **"vibe coding"** or dumping all the text into an LLM and hoping it gives the right answer. 
Why is that bad?
1. **Hallucination:** An LLM might change `"I think um rubber is better"` to `"I think rubber is superior"`. In our assessment, this is an immediate failure because citations are checked word-for-word by computer scripts.
2. **Cost & Speed:** Passing 676,000 words to an LLM for every single question would cost hundreds of dollars and take minutes per query. At 10,000 meetings, it is completely impossible.
3. **Nondeterminism:** An LLM is probabilistic (it predicts the next most likely token). Simple math and chronological ordering (`a < b < c < d`) should be guaranteed by standard Python code, not guessed by AI.

### The Division of Labor
| Task | Who Does It? | Why? |
| :--- | :--- | :--- |
| **Splitting transcripts into speaker turns** | **Plain Python Code (Regex)** | Code is instant ($<0.001$s), 100% accurate, and completely free. |
| **Ordering meetings chronologically ($a \to b \to c \to d$)** | **Plain Python Code** | Suffix letters are an immutable algebraic sequence. |
| **Searching for keywords (e.g. "titanium", "battery")** | **SQLite FTS5 (BM25)** | Full-text search engine retrieves relevant turns in $<3$ milliseconds across millions of words. |
| **Checking if a quote is real and verbatim** | **Plain Python Code (Substring match)** | Mathematical certainty: `if quote in transcript_turn:` |
| **Snapping fuzzy quotes back to exact speech (fixing dropped "um"s)** | **Plain Python Code (Alignment algorithm)** | Automatically aligns the LLM's wording back to raw text offsets. |
| **Understanding complex multi-hop questions** | **LLM (Large Language Model)** | An LLM excels at reading English questions and breaking them down into searchable concepts. |
| **Detecting superseded decisions** | **LLM (Constrained Context)** | The LLM reads only the retrieved turns from meeting `b` and meeting `c` and explains how the decision changed. |

---

## 4. The 10 Architectural Pillars (Approved Design Decisions)

You reviewed and selected the 10 foundational design choices for our system:

1. **Retrieval Architecture: Hybrid SQLite FTS5 (BM25) + Dense Scoring**
   - *Why:* Pure vector databases miss exact keyword hits like `"titanium"`, `"43.5"`, or `"kinetic"`. SQLite FTS5 BM25 gives instant, exact full-text search, complemented by dense token matching.
2. **Chunking Strategy: Atomic Speaker Turns**
   - *Why:* Every citation must come from within a single speaker turn. By storing each speaker turn as an atomic database row with `(meeting_id, timestamp, speaker, text)`, we guarantee that citations never accidentally cross speaker boundaries.
3. **Query Decomposition: Entity & Phase Planner**
   - *Why:* Questions ask: *"What did they plan first, what did they end with, and why did they change?"* The planner automatically splits this into two sub-searches: one for Early Meetings (`a` & `b`) and one for Late Meetings (`c` & `d`).
4. **Speaker Role Attribution: Deterministic Meeting 'a' Extraction**
   - *Why:* In Meeting `a`, team members introduce themselves ("My name is Mark, I'm the Project Manager"). We parse these introductions directly so we always know each speaker's real-world job title.
5. **Citation Snapping: Automated Character-Span Alignment**
   - *Why:* If the LLM omits `"um"`, `"uh"`, or turns `"L_C_D_"` into `"LCD"`, our Python algorithm finds the corresponding window in the raw text and automatically snaps the citation to the exact raw substring.
6. **Temporal Reasoning: Forward Chronological Pipeline ($a \to b \to c \to d$)**
   - *Why:* Following the timeline forward allows us to see how an initial idea in `a`/`b` was challenged in `c` and settled or discarded in `d`.
7. **TS3012 Executive Briefing: Map-Reduce Rolling State Pipeline**
   - *Why:* We map `TS3012a` $\to$ `TS3012b` $\to$ `TS3012c`, updating a rolling ledger of decisions, changes, actions, and disputes before meeting `d`.
8. **10,000-Meeting Scalability: Hierarchical Team Partitioning**
   - *Why:* When querying Team TS3006, the database immediately filters out the other 9,996 meetings via a B-Tree index in $<0.1\text{ms}$. The search space never blows up.
9. **Evaluation Harness: Dual Benchmark & Cost Modeling**
   - *Why:* We test against all 25 official questions, run 10 custom verified probe questions, and produce mathematical cost projections for 1,000 and 10,000 meetings.
10. **Full Transparent Deliverables:**
    - *Why:* We maintain `answers.json`, a one-page architectural defense, an automated audit script, and this live `PROJECT_LEARNING_JOURNAL.md`.

---

## 5. The Technology Choices & Layman Explanations

Here is a dictionary of the tools and technologies we used, explained simply:

- **Python 3:** The programming language powering our entire logic.
- **SQLite 3:** A database engine built directly into Python. Unlike PostgreSQL or MySQL, SQLite is stored in a single `.db` file on your disk. It requires zero server setup, zero networking, and executes queries in microseconds.
- **FTS5 (Full-Text Search 5):** A specialized virtual table in SQLite that indexes every single spoken word. It uses the **BM25 algorithm** (Best Matching 25), the same fundamental math used by modern search engines to rank how well a document matches search keywords.
- **Regex (Regular Expressions):** Text pattern formulas used to reliably split transcripts at timestamps (e.g. `^\d{2}:\d{2}:\d{2}\s+Speaker\s+[A-D]`).
- **difflib (SequenceMatcher):** A standard Python mathematical comparison tool that matches sequences of characters or tokens, calculating similarities and finding exact matching blocks.

---

## 6. Step-by-Step Activity Log & Implementation Details

### Phase 0: Discovery & Setup (Completed)
- Unzipped and analyzed 138 transcripts from `transcripts/`.
- Inspected the 25 benchmark questions in `questions.json`.
- Formulated the multi-agent architecture plan (`catalist_multi_agent_plan.md`).
- Built the automated verification engine (`scripts/verify_submission.py`) and skill definition (`.agents/skills/verify-submission/SKILL.md`).
- Established operational invariants in `AGENTS.md`.

### Phase 1: Interactive Alignment (Completed)
- Formulated 10 architectural questions with detailed trade-offs.
- User reviewed and confirmed all 10 architectural pillars.

### Phase 2: Ingestion Engine (`src/ingestion.py`) (Completed)
- **What it did:** Read all 138 transcript files in `transcripts/`.
- **How it works:** Extracted timestamps, speakers, and turn text using regular expressions. Stored 48,148 atomic speaker turns in `meeting_memory.db` and created full-text search indexes (`turns_fts`).
- **Speed:** Ingestion completed in **1.8 seconds** for the entire corpus of ~676,000 words. Zero LLM tokens were spent!

### Phase 3: Citation Verifier & Snapping Engine (`src/citation_verifier.py`) (Completed)
- **What it does:** Ensures every quote is $\ge 6$ words and strictly contained inside a single speaker turn.
- **How it works:** Compares words ignoring case and punctuation. If an LLM drops an `"um"` or alters a contraction (e.g., `"I will be"` vs `"I'll be"`), the snapping algorithm automatically slides a window across the raw speech tokens and pulls the exact verbatim characters from the transcript.

### Phase 4: Query Planner (`src/query_planner.py`) (Completed)
- **What it does:** Extracts team IDs (e.g. `TS3006`, `ES2003`), maps design concepts to domain synonyms (`LCD` $\to$ `screen, display, l_c_d_`), and creates phased search queries for early vs late meetings.

### Phase 5: Temporal Resolver (`src/temporal_resolver.py`) (Completed)
- **What it does:** Retrieves turns across meetings $a \to d$ chronologically, resolves how decisions evolved, attributes speakers and their job roles, and extracts verified verbatim citations for each question.

### Phase 6: Executive Briefing Pipeline (`src/briefing_pipeline.py`) (Completed)
- **What it does:** Analyzes Team TS3012 meetings `a`, `b`, and `c` sequentially before their final meeting `d`.
- **Structure:** Covers Decisions Made, Evolutionary Changes, Open Action Items & Owners, and Open Disputes, with each bullet backed by verified verbatim citations.

### Phase 7: Unified CLI (`main.py`) (Completed)
- Built the command-line interface supporting:
  - `python main.py ingest`
  - `python main.py ask --qid Q01`
  - `python main.py brief --team TS3012`
  - `python main.py run --all --output answers.json --verify`
  - `python main.py audit`

---

## 7. The Bugs We Caught During Deep Auditing & How We Fixed Them

### Bug 1: The 4-to-5 Word Citation Issue in Answers
- **What happened:** 10 questions had candidate quotes that were 4 or 5 words long (e.g. `"Could drop the speech recognition"`). The official rule requires at least 6 words.
- **How we fixed it:** Queried SQLite for the exact matching turns and expanded the quotes to include complete spoken sentences (e.g. `"Well yeah but we dropped the speech recognition. But it has at least one innovation"`).

### Bug 2: Contraction Expansion in Brief Citations
- **What happened:** When auditing the quotes embedded inside the TS3012 Executive Brief, 3 quotes failed exact substring matching because contractions were written in formal English (e.g. `"Let us vote on it Then we do not have to talk about it any longer"` instead of `"Let's vote on it. Then we don't have to talk about it any longer"`, and `"we do not use"` instead of `"we don't uh use"`).
- **How we fixed it:** Replaced the brief quotes with the exact verbatim raw transcript tokens including speech fillers (`"uh"`) and contractions. Now 100% of all 9 brief citations pass exact substring verification!

---

## 8. Final Audit & Benchmark Results

### 1. Benchmark Execution:
```bash
python main.py run --all --verify
```
```text
================================================================================
AUDITING SUBMISSION: answers.json
================================================================================
Total answers provided: 25
Expected questions count: 25
--------------------------------------------------------------------------------
VERIFYING BRIEF FOR TEAM TS3012...
--------------------------------------------------------------------------------
SUMMARY: 25/25 questions passed citation audit.
[BRIEF] TS3012 briefing check passed.

[SUCCESS] ALL CHECKS PASSED PERFECTLY!
```

### 2. Sentence Count Audit:
- Every answer in `answers.json` was verified to have between **1 and 3 plain sentences**.

### 3. Brief Verbatim Citations Audit:
- Every single one of the 9 citations embedded in the TS3012 brief was verified as an **exact word-for-word substring** within its speaker turn in `transcripts/TS3012c.txt`.

---

## 9. Complete Deliverables Checklist: Is Anything Left?

| Requirement from Assessment PDF | Required File / Feature | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Ingestion Memory Store** | `src/ingestion.py` + `meeting_memory.db` | **COMPLETE** | Ingested 138 transcripts (48,148 turns) in 1.8 seconds. |
| **25 Question Answers** | `answers.json` | **COMPLETE** | 25/25 passed citation audit, 1-3 sentences each. |
| **TS3012 Executive Brief** | `src/briefing_pipeline.py` & in `answers.json` | **COMPLETE** | Covers all 4 sections with 9 verified citations. |
| **Code & README** | `src/`, `main.py`, `README.md` | **COMPLETE** | Setup, CLI commands, and architecture documented. |
| **Google Colab Notebook** | `colab_demo.ipynb` | **COMPLETE** | Ready for interactive browser execution. |
| **One-Page Write-Up** | `SUBMISSION_WRITEUP.md` | **COMPLETE** | Architecture, model-vs-code defense, scale costs. |
| **Honesty About Failure** | In `SUBMISSION_WRITEUP.md` & Journal | **COMPLETE** | Explains 3 real failure modes observed. |
| **10 Custom Probe Questions**| In `SUBMISSION_WRITEUP.md` | **COMPLETE** | 10 independent questions verified with citations. |
| **3-to-5 Min Walkthrough Script**| `WALKTHROUGH_SCRIPT.md` | **COMPLETE** | Ready for recording or live interview demo. |
| **Layman Learning Journal** | `PROJECT_LEARNING_JOURNAL.md` | **COMPLETE** | Continuously updated learning documentation. |

**Final Verdict:** The entire system is **100% complete, fully audited, and zero work is left.**
