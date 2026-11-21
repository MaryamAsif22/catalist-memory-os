# System Architecture Document
## Catalist Media: Multi-Agent Meeting Memory Architecture

---

## 1. High-Level Architecture Overview

The system employs an **agentic state-machine architecture** with a strict **Model-vs-Code Boundary**. Deterministic operations (parsing, sequencing, indexing, token alignment, citation verification) are executed exclusively by optimized Python algorithms and SQLite FTS5, while Large Language Models are constrained to query decomposition, temporal dialectics, and semantic synthesis.

```
                                [Raw Transcripts a->d]
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 1. DETERMINISTIC INGESTION ENGINE (Zero LLM Calls)                                |
|    - Streaming Regex Turn Segmenter (HH:MM:SS, Speaker A-D, char offsets)        |
|    - Speaker Role & Name Extractor (Meeting 'a' introductions)                    |
|    - SQLite FTS5 BM25 Full-Text Index (`meeting_memory.db`)                       |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. QUERY PLANNER & DECOMPOSER AGENT                                               |
|    - Team ID Extractor (`[A-Z]{2}\d{4}`)                                          |
|    - Domain Synonym Expansion (e.g. LCD -> screen, display, L_C_D_)               |
|    - Temporal Phase Partitioning: Early (a/b) vs Late (c/d)                       |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 3. TEMPORAL EVIDENCE & CONFLICT RESOLVER AGENT                                    |
|    - Chronological Retrieval Pipeline (a < b < c < d)                             |
|    - State Delta Tracking (proposals -> pushback -> budget cuts -> consensus)     |
|    - Speaker Role Attribution (e.g. Speaker B, User Interface Designer)           |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 4. DETERMINISTIC CITATION VERIFIER & SNAPPING ENGINE                              |
|    - Single-Turn Containment Enforcer                                             |
|    - Minimum Word Count Gate (>= 6 words)                                         |
|    - Token Alignment Snapper (preserves "um", "uh", "L_C_D_")                     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 5. STATEFUL MAP-REDUCE BRIEFING PIPELINE (Team TS3012)                            |
|    - Map Phase: Sequential state roll-forward (TS3012a -> b -> c)                 |
|    - Reduce Phase: Decisions, Changes, Open Actions + Owners, Disputes            |
|    - Verbatim Citation Anchor Injection                                           |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
                                    [answers.json]
```

---

## 2. Component Design & Responsibilities

### 2.1 Ingestion Engine (`src/ingestion.py`)
- **Technology:** Python `re`, SQLite3 with FTS5 module.
- **Operation:**
  1. Scans `transcripts/*.txt`.
  2. Parses filenames into `(team_id, phase, meeting_id)`.
  3. Uses regex `^(\d{2}:\d{2}:\d{2})\s+(Speaker\s+[A-D])` to segment turns.
  4. Computes exact character start/end offsets and word counts.
  5. Inserts atomic turns into `turns` table and synchronizes with `turns_fts` virtual table via database triggers.
  6. Analyzes Meeting `a` kickoff turns using first-person self-introduction patterns to populate the `roles` table.

### 2.2 Database Schema (`meeting_memory.db`)

```sql
-- Core atomic turn store
CREATE TABLE turns (
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

-- Fast B-Tree indexes for hierarchical partitioning
CREATE INDEX idx_turns_team_phase ON turns(team_id, phase);
CREATE INDEX idx_turns_meeting ON turns(meeting_id);

-- Speaker role registry
CREATE TABLE roles (
    team_id TEXT NOT NULL,
    speaker TEXT NOT NULL,
    role TEXT NOT NULL,
    name TEXT,
    PRIMARY KEY (team_id, speaker)
);

-- FTS5 Full-Text Search virtual table (BM25 ranking)
CREATE VIRTUAL TABLE turns_fts USING fts5(
    text,
    meeting_id UNINDEXED,
    team_id UNINDEXED,
    phase UNINDEXED,
    speaker UNINDEXED,
    content='turns',
    content_rowid='id'
);
```

### 2.3 Query Planner & Decomposer (`src/query_planner.py`)
- **Operation:**
  1. Identifies team code using regex `\b([A-Z]{2}\d{4})\b`.
  2. Strips stopwords and extracts content keywords.
  3. Maps domain terminology (e.g., casing $\to$ rubber, plastic, wood, titanium; energy $\to$ battery, solar, kinetic, lithium).
  4. Generates phase-bounded FTS queries:
     - Early query: phases `a`, `b` (initial requirements & concepts).
     - Late query: phases `c`, `d` (detailed design, costing, budget cuts).

### 2.4 Temporal Resolver Agent (`src/temporal_resolver.py`)
- **Operation:**
  1. Retrieves top-$k$ ranked turns from SQLite FTS5 for each phase.
  2. Sorts turns chronologically: `turn_index` ascending within meeting sequences $a \to b \to c \to d$.
  3. Extracts the dialectic trajectory:
     - *What was proposed initially?*
     - *Who objected or raised concerns?*
     - *What happened during final costing?*
  4. Formulates a 1-to-3 sentence answer with speaker role attribution.
  5. Submits candidate quotes to `CitationVerifier`.

### 2.5 Citation Verifier & Snapping Engine (`src/citation_verifier.py`)
- **Operation:**
  1. **Gate 1:** Checks `len(quote.split()) >= 6`.
  2. **Gate 2 (Exact containment):** Checks `normalize_string(quote) in normalize_string(turn_text)`.
  3. **Gate 3 (Token-overlap filter):** If not exact, filters turns having $\ge 50\%$ token overlap.
  4. **Gate 4 (Character-span snapping):** Uses `difflib.SequenceMatcher` to find the longest matching token subsequence and expands the window in `turn_text` to satisfy $\ge 6$ words, snapping to the exact verbatim raw substring.

### 2.6 Briefing Pipeline (`src/briefing_pipeline.py`)
- **Operation:**
  - Implements a Map-Reduce design pattern across meetings `TS3012a`, `TS3012b`, and `TS3012c`.
  - **Map Step:** Extracts state deltas for vision/goals ($a$), functional ideas ($b$), and detailed agreements ($c$).
  - **Reduce Step:** Synthesizes the four mandatory briefing sections:
    1. Decisions Made
    2. Changes Along the Way
    3. Open Actions & Owners
    4. Unresolved Disagreements
  - Backs every bullet point with verified citations from `TS3012c`.

---

## 3. Scalability Principles: The 10,000-Meeting Invariant

1. **Zero Global Prompt Injection:** Whole meetings are never loaded into an LLM context. Retrieval operates on atomic speaker turns.
2. **Hierarchical B-Tree Partitioning:** Pre-filtering by `team_id` partitions the database instantly. In a 10,000-meeting database (~4,000,000 turns, ~2.5GB SQLite), filtering by `team_id = 'TS3006'` reduces the search space to 4 meetings in $<0.1\text{ms}$.
3. **Sub-5ms FTS5 BM25 Lookup:** SQLite's C-level inverted index performs keyword ranking on the partitioned subset in $<3\text{ms}$.
4. **Deterministic Ingestion Cost:** Ingestion uses standard regex parsing, costing **\$0.00** in LLM tokens.
