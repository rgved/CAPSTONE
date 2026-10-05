# Phase 5 — Efficient Fetch Service

Status: Complete

---

# Objective

Introduce the Efficient Fetch Service.

The purpose of this phase is to reduce context size before information reaches future reasoning agents.

The Efficient Fetch Service acts as an intelligent content reduction layer between application data and future AI analysis.

The goal is:

```text
Large Web Content
        ↓

Efficient Fetch
        ↓

Relevant Context Only
```

No vulnerability analysis should occur.

No findings should be generated.

No security reasoning should occur.

---

# Architecture Context

Current System:

```text
Recon Agent
        ↓

Feature Extraction Agent
        ↓

SQLite
        ↓

ChromaDB
```

After Phase 5:

```text
Recon Agent
        ↓

Feature Extraction Agent
        ↓

Semantic Memory
        ↓

Efficient Fetch
```

The Analysis Agent does not yet exist.

This phase only prepares data for future analysis.

---

# Required Reading

Before implementation:

1. AGENTS.md
2. docs/architecture.md
3. docs/contracts.md
4. docs/phases/phase1.md
5. docs/phases/phase2.md
6. docs/phases/phase3.md
7. docs/phases/phase4.md

---

# Problem Statement

Future Analysis Agents cannot efficiently process:

```text
Entire Pages
Entire DOM Trees
Entire HTML Documents
All Routes
All Scripts
```

Passing everything directly to an LLM causes:

* excessive token usage
* increased latency
* reduced reasoning quality
* higher operational cost

The Efficient Fetch Service solves this problem.

---

# Core Concept

Input:

```text
Large Document
```

Example:

```text
50,000 tokens
```

Output:

```text
Relevant Context
```

Example:

```text
2,000 tokens
```

The service should preserve information relevant to the requested query.

---

# New Components

Create:

```text
backend/

├── services/
│   └── efficient_fetch/
```

---

# Folder Structure

```text
backend/

├── services/
│   └── efficient_fetch/
│       ├── efficient_fetch_service.py
│       ├── chunking.py
│       ├── ranking.py
│       └── fetch_models.py
```

---

# Efficient Fetch Contract

Implement:

```python
efficient_fetch(
    source_text,
    query_hint
)
```

Returns:

```json
{
  "structured_content": "...",
  "token_count_naive": 50000,
  "token_count_efficient": 1800
}
```

This contract was previously defined in architecture revisions.

---

# Query Hint

The query hint represents what the future worker is interested in.

Examples:

```text
authentication forms
```

```text
admin functionality
```

```text
file upload features
```

```text
search functionality
```

The query hint guides relevance scoring.

---

# Content Chunking

Create:

```python
chunk_document()
```

Responsibilities:

* split large content
* preserve semantic boundaries
* avoid breaking forms and structures

Target chunk size:

```text
500–1000 tokens
```

Do not use LLMs.

Pure deterministic processing.

---

# Relevance Ranking

Create:

```python
rank_chunks()
```

Input:

```text
Chunks
+
Query Hint
```

Output:

```text
Top K Relevant Chunks
```

Initial implementation:

```text
Semantic Similarity
```

using Phase 4 embeddings.

No LLM ranking.

---

# Retrieval Flow

```text
User Query
      ↓

Query Hint
      ↓

Retrieve Candidates
      ↓

Rank Candidates
      ↓

Select Top K
      ↓

Return Reduced Context
```

---

# Efficient Fetch Result

Create model:

```python
EfficientFetchResult
```

Example:

```json
{
  "structured_content": "...",
  "token_count_naive": 42000,
  "token_count_efficient": 2200
}
```

---

# Metrics

Track:

```text
token_count_naive
```

and

```text
token_count_efficient
```

These metrics are required for research evaluation.

Future papers and presentations will use:

```text
Context Reduction %
```

Formula:

(token_count_naive - token_count_efficient)
/
token_count_naive
× 100

````

---

# Orchestrator Changes

Add new action:

```text
RUN_EFFICIENT_FETCH
````

Mission flow becomes:

```text
RUN_RECON
        ↓

EXTRACT_FEATURES
        ↓

RUN_EFFICIENT_FETCH
        ↓

STOP
```

No Analysis Agent yet.

---

# Database Changes

None.

SQLite schema remains unchanged.

ChromaDB remains unchanged.

---

# Testing Requirements

Create:

```text
tests/

├── test_chunking.py
├── test_ranking.py
├── test_efficient_fetch.py
```

---

## test_chunking.py

Verify:

* documents split correctly
* chunk sizes respected

---

## test_ranking.py

Verify:

* relevant chunks ranked above unrelated chunks

---

## test_efficient_fetch.py

Verify:

* context reduction occurs
* token metrics recorded
* contract compliance

---

# Out Of Scope

The following are prohibited.

---

## Analysis Agent

Reason:

Phase 6.

Do not implement.

---

## Security Findings

Reason:

Analysis Agent not implemented.

Do not generate:

* vulnerabilities
* attack paths
* severity levels
* recommendations

---

## Report Agent

Reason:

Phase 7.

Do not implement.

---

## Autonomous Reasoning

Reason:

Phase 6.

Do not implement.

---

## LLM-Based Ranking

Reason:

Unnecessary complexity.

Use embeddings only.

---

## LangChain

Do not introduce unless required.

Plain Python implementation preferred.

---

# Definition of Done

Phase 5 is complete when:

✓ Efficient Fetch Service exists

✓ Chunking implemented

✓ Relevance ranking implemented

✓ Query hints supported

✓ Context reduction works

✓ Token metrics recorded

✓ Efficient Fetch contract implemented

✓ New tests pass

✓ Existing tests continue to pass

✓ No Analysis Agent exists

✓ No Findings generated

✓ No Report Agent exists

---

# Success Criteria

At the end of Phase 5:

```text
Recon Data
        ↓

Semantic Memory
        ↓

Efficient Fetch
        ↓

Relevant Context
```

The system can now provide compact, relevant evidence to future reasoning agents while minimizing token consumption.

Phase 6 will consume this output to generate security findings.
