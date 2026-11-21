# Product Requirements Document (PRD)
## Catalist Media: Agentic Meeting Memory & Executive Briefing System

---

## 1. Executive Summary & Problem Statement

### 1.1 The Problem
In modern organizations, founders, executives, and product teams spend dozens of hours every week in recorded meetings. Over a period of several months, this accumulates into hundreds of hours of raw audio and transcripts:
- **Meeting Amnesia:** Decisions made in Meeting 1 are often forgotten by Meeting 3.
- **Superseded Decisions:** A technical consensus formed in an early brainstorming session (e.g. using kinetic batteries or titanium casing) is overturned in a later meeting due to budget caps, but team members continue working with outdated assumptions.
- **Untracked Commitments:** Action items assigned casually in conversation ("Xavier will check rubber prices") fall through the cracks because nobody reads 50 pages of raw dialogue prior to the next sync.
- **Search Inefficiency:** Existing search tools perform keyword matching across flat documents, completely lacking temporal dialectics, speaker role awareness, and the ability to distinguish provisional brainstorming from final sign-offs.

### 1.2 The Solution
Build an autonomous, episodic meeting memory agent that turns raw, unstructured meeting transcripts (from the AMI Meeting Corpus: 138 meetings across 35 teams, ~676,000 words) into an authoritative, queryable memory store. The system answers multi-hop temporal questions with 100% exact, word-for-word citations and synthesizes pre-meeting executive briefs.

---

## 2. Goals & Success Metrics

### 2.1 Primary Goals
1. **Zero Hallucination on Citations:** Every answer must be backed by 1 to 3 verbatim citations ($\ge 6$ words) strictly contained within a single speaker turn in the raw transcript.
2. **Temporal Dialectic Synthesis:** Correctly track decision trajectories across chronological sequences ($a \to b \to c \to d$), recognizing when agreements were modified or abandoned.
3. **Executive Pre-Meeting Briefing:** Generate a structured, actionable brief for Team TS3012 prior to their final meeting ($d$), highlighting what was decided, what changed along the way, open action items with owners, and unresolved disputes.
4. **10,000-Meeting Scalability:** Architect an ingestion and retrieval engine that executes queries in sub-5ms latency and costs \$0.00 in ingestion tokens.

### 2.2 Quantitative Success Metrics
- **Verification Pass Rate:** 100% on automated schema, word count, and substring citation validation (`verify_submission.py`).
- **Benchmark Coverage:** 25 out of 25 benchmark questions answered accurately in 1–3 plain sentences.
- **Ingestion Latency:** $< 2.0\text{ seconds}$ for 138 meetings (~676,000 words) on local compute.
- **Query Response Latency:** $< 10\text{ ms}$ for candidate turn retrieval.

---

## 3. Target Users & Personas

### 3.1 The Busy Founder / Executive
- **Needs:** Fast, trustworthy answers to questions about past commitments, pricing agreements, and feature trade-offs.
- **Pain Point:** Has no time to read 40-page transcripts; needs grounded answers with exact quotes they can verify in one second.

### 3.2 Product Managers & Team Leads
- **Needs:** Pre-meeting briefs before critical milestone reviews.
- **Pain Point:** Keeping track of who was assigned which action item and what technical disagreements remain unresolved heading into final budget reviews.

### 3.3 Engineering & Technical Reviewers
- **Needs:** Auditable, deterministic systems that do not break at enterprise scale.
- **Pain Point:** Skeptical of probabilistic "vibe-coded" LLM wrappers that hallucinate quotes or choke when the transcript volume exceeds context windows.

---

## 4. Core Features & Functional Requirements

### Feature 1: Deterministic Ingestion & Partitioned Indexing
- **FR-1.1:** Automatically ingest transcripts formatted as `[team_id][phase].txt` using streaming regex to segment turns by timestamp (`HH:MM:SS`) and speaker (`Speaker A-D`).
- **FR-1.2:** Calculate exact character offsets (`char_start`, `char_end`) and word counts for every turn.
- **FR-1.3:** Build an SQLite FTS5 (BM25) full-text index with tokenizer rules that retain corpus-specific tokens (e.g. `L_C_D_`, numbers, hyphens).
- **FR-1.4:** Automatically extract speaker roles (Project Manager, UI Designer, Industrial Designer, Marketing Expert) and names from Meeting `a` kickoff turns.

### Feature 2: Query Decomposition & Semantic Planning
- **FR-2.1:** Parse incoming questions to extract target `team_id` and map domain terminology (e.g. casing $\to$ rubber, plastic, wood, titanium).
- **FR-2.2:** Automatically partition search queries into early phases ($a/b$) vs. late phases ($c/d$) to isolate decision evolution.

### Feature 3: Temporal Reasoning & Conflict Resolution
- **FR-3.1:** Order candidate evidence chronologically ($a < b < c < d$).
- **FR-3.2:** Detect superseded decisions (e.g. when a feature agreed upon in Meeting `b` is dropped in Meeting `d` due to budget overruns).
- **FR-3.3:** Attribute speakers by their letter label and real-world job title.
- **FR-3.4:** Format responses into 1 to 3 concise, plain English sentences.

### Feature 4: Verbatim Citation Verification & Snapping
- **FR-4.1:** Verify that candidate quotes are at least 6 words long (`len(quote.split()) >= 6`).
- **FR-4.2:** Enforce that quotes are 100% contained within a single speaker turn (no crossing dialogue turns).
- **FR-4.3:** Automatically snap fuzzy LLM citations (where conversational noise like `"um"` or `"uh"` was dropped) to the exact character span in the raw transcript.

### Feature 5: Stateful Map-Reduce Briefing Pipeline (Team TS3012)
- **FR-5.1:** Roll state forward sequentially: `TS3012a` $\to$ `TS3012b` $\to$ `TS3012c`.
- **FR-5.2:** Emit four structured sections:
  1. *What has been decided*
  2. *What changed along the way*
  3. *Open actions and who owns them*
  4. *Disagreements still open*
- **FR-5.3:** Back every bullet point with an exact verbatim citation verified against `transcripts/TS3012*.txt`.

### Feature 6: Programmatic Evaluation & Verification Harness
- **FR-6.1:** Standalone verification script (`scripts/verify_submission.py`) auditing `answers.json` for schema compliance, sentence counts, and verbatim substring matches.
- **FR-6.2:** Comprehensive CLI (`main.py`) supporting interactive live question answering, brief generation, and automated auditing.

---

## 5. Non-Functional Requirements (NFRs)

- **Reliability:** Zero unverified or hallucinated citations in submission output.
- **Performance:** Full benchmark execution and verification across 25 questions in under 5 seconds.
- **Portability:** Zero heavy external framework dependencies; runs cleanly on Python 3.10+ using standard library and SQLite3.
- **Maintainability:** Clear Model-vs-Code boundary documented in code and governance files.
