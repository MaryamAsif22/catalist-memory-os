# AGENTS.md: Architecture Governance & System Invariants

This document establishes the mandatory operational rules, architectural contracts, model-vs-code boundaries, and verification invariants for the **Catalist Media Meeting Memory System**.

---

## 1. Core System Invariants

### 1.1 Strict Model-vs-Code Boundary
To ensure sub-millisecond execution, zero hallucination on deterministic operations, and bounded compute costs, the following boundary is strictly enforced:

- **What Code Does (Never Call an LLM For These):**
  - **Transcript Ingestion & Turn Parsing:** Regular expressions must be used to segment transcripts by `timestamp`, `speaker`, and turn boundaries.
  - **Temporal Sequence Resolution:** Meeting phase ordering ($a < b < c < d$) is an immutable algebraic rule, not a subject for model inference.
  - **Lexical Indexing & Filtering:** Keyword indexing and token search are handled strictly by SQLite FTS5 with BM25 ranking.
  - **Citation Verification:** Checking whether a candidate quote is an exact, word-for-word substring of a single speaker turn is executed programmatically.
  - **Citation Snapping / Alignment:** If an LLM drops conversational noise (e.g. `"um"`, `"uh"`, or hyphenated acronyms like `L_C_D_`), a deterministic alignment algorithm snaps the quote to the exact character offset of the raw transcript.
- **What LLMs Do (And Why):**
  - **Query Decomposition:** Parsing complex multi-hop natural language questions into atomic entity and phase queries.
  - **Cross-Meeting Coreference Resolution:** Resolving conversational references (e.g., "that feature", "the other battery option", "the price cut").
  - **Temporal Dialectic Synthesis:** Reasoning about which statements represent provisional brainstorming vs final consensus, and tracking how decisions evolved across time.

---

## 2. Scalability Invariants (10,000+ Meetings)

1. **Zero Global Prompt Injection:** Under no circumstances may whole meetings or multi-meeting transcripts be concatenated into an LLM context window. All retrieval must be chunk- and turn-bounded.
2. **Partitioned Ingestion:** Ingestion operates on atomic `TurnRecord` units indexed by `(team_id, meeting_phase, turn_id)`.
3. **Sub-10ms Retrieval at Scale:**
   - Pre-filtering by `team_id` partitions the search space immediately.
   - SQLite FTS5 BM25 search executes in $< 5\text{ms}$ even on multi-gigabyte databases.
4. **Stateless Worker Parallelism:** Ingestion and question-answering workers are stateless and horizontally scaleable across worker pools.

---

## 3. Verbatim Citation Invariants

The evaluation harness evaluates citations automatically using strict substring matching. Any paraphrase or hallucination is an instant failure.

Every citation MUST satisfy the following rules:
1. **Meeting ID Valid:** Must match an existing meeting identifier in `transcripts/` (e.g., `TS3006d`).
2. **Minimum Word Count:** Every citation quote must be **at least 6 words long** (`len(quote.split()) >= 6`).
3. **Single Turn Containment:** The quote must exist entirely within **one single speaker turn**. A citation cannot cross dialogue boundaries or span multiple speakers.
4. **Exact Verbatim Accuracy:** All original speech artifacts—stutters, false starts, `"um"`, `"uh"`, and corpus-specific token representations (such as `L_C_D_`)—must be preserved verbatim.
5. **Quantity Constraint:** Each question answer must include **between 1 and 3 citations**.

---

## 4. Multi-Agent Role Contracts

```
[User / Evaluation Harness]
            |
            v
+------------------------+
| Query Planner Agent    | -> Parses question, extracts team_id, generates sub-queries
+------------------------+
            |
            v
+------------------------+
| Temporal Resolver Agent| -> Retrieves chronological turns, resolves conflicts & state
+------------------------+
            |
            v
+------------------------+
| Citation Verifier Loop | -> Programmatically verifies quote in raw turn; snaps / repairs
+------------------------+
            |
            v
+------------------------+
| Output Formatter       | -> Emits valid schema into answers.json (1-3 sentences + citations)
+------------------------+
```

### Agent Roles:
- **`IngestionEngine` (Code):** Parses raw files into structured SQLite FTS5 records.
- **`QueryPlanner` (LLM):** Deconstructs the query into `(phase_filter, entity_keywords, target_aspect)`.
- **`TemporalResolver` (LLM + Hybrid Search):** Retrieves evidence across phases $a, b, c, d$ chronologically and tracks decision evolution.
- **`CitationVerifier` (Code + Repair Loop):** Validates verbatim matching and enforces character span integrity.
- **`BriefingPipeline` (Map-Reduce):** Sequentially summarizes meetings $a \to b \to c$ for Team TS3012, producing decisions, changes, open actions with owners, and unresolved disputes.

---

## 5. Automated Verification Standard

Before declaring any output complete, the companion verification script must be executed:
```bash
python scripts/verify_submission.py --answers answers.json
```
The script validates:
- Schema conformance against `questions.json`.
- All 25 questions answered (Q01–Q25).
- Sentence count constraints (1–3 sentences per answer).
- Exact word-for-word substring citation validation against the source transcripts.
- TS3012 briefing section completeness and citation validity.
