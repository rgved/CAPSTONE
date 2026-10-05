# Phase 4 — Semantic Memory Foundation (ChromaDB)

Status: Active

---

# Objective

Introduce semantic memory into the system.

This phase establishes the retrieval foundation required by future agents.

The goal is NOT to perform analysis.

The goal is NOT to generate findings.

The goal is simply:

```text
Store
Retrieve
Remember
```

At the end of Phase 4, the system should be capable of:

1. Storing features in ChromaDB
2. Storing route summaries in ChromaDB
3. Performing semantic retrieval
4. Returning the most relevant memories

No reasoning should occur.

---

# Architecture Context

Current System:

```text
Orchestrator
    ↓

Recon Agent
    ↓

Feature Extraction Agent
    ↓

SQLite
```

After Phase 4:

```text
Orchestrator
    ↓

Recon Agent
    ↓

Feature Extraction Agent
    ↓

SQLite
    ↓

ChromaDB
```

SQLite remains the source of truth.

ChromaDB becomes semantic memory.

---

# Required Reading

Before implementation:

1. AGENTS.md
2. docs/architecture.md
3. docs/contracts.md
4. docs/phases/phase1.md
5. docs/phases/phase2.md
6. docs/phases/phase3.md

---

# Scope

## In Scope

### ChromaDB Integration

Install:

```text
chromadb
```

Create:

```text
backend/memory/chroma/
```

---

### Memory Collections

Create exactly three collections.

---

#### features

Embedding Source:

```text
feature name
```

Example:

```text
authentication
search
admin_panel
```

---

#### routes

Embedding Source:

```text
route url
```

Example:

```text
/login
/admin
/profile
```

---

#### findings

Create collection only.

Do not use yet.

Reason:

Future phases depend on it.

---

# New Folder Structure

```text
backend/

├── memory/
│
├── chroma/
│   ├── chroma_client.py
│   ├── feature_memory.py
│   └── route_memory.py
```

---

# Chroma Client

Create:

```python
ChromaClient
```

Responsibilities:

* Initialize database
* Create collections
* Provide collection access

No business logic.

---

# Feature Memory

Create:

```python
FeatureMemory
```

Methods:

```python
add_feature()
```

```python
search_features()
```

---

Example:

```python
add_feature(
    feature_name="authentication"
)
```

---

Example:

```python
search_features(
    query="login functionality"
)
```

Returns:

```python
["authentication"]
```

---

# Route Memory

Create:

```python
RouteMemory
```

Methods:

```python
add_route()
```

```python
search_routes()
```

---

Example:

```python
search_routes(
    query="admin page"
)
```

Returns:

```python
["/admin"]
```

---

# SQLite Remains Source Of Truth

Do not replace SQLite.

Store data in both systems.

```text
SQLite
    ↓
Structured Records

ChromaDB
    ↓
Semantic Retrieval
```

---

# Orchestrator Changes

None.

Phase 4 does not introduce new tasks.

Current flow remains:

```text
RUN_RECON
    ↓

EXTRACT_FEATURES
    ↓

STOP
```

---

# Testing Requirements

Create:

```text
tests/

├── test_feature_memory.py
├── test_route_memory.py
```

---

## test_feature_memory.py

Verify:

```python
add_feature()
```

works.

Verify:

```python
search_features()
```

returns expected results.

---

## test_route_memory.py

Verify:

```python
add_route()
```

works.

Verify:

```python
search_routes()
```

returns expected results.

---

# Out Of Scope

The following are prohibited.

---

## Analysis Agent

Reason:

Phase 6.

Do not implement.

---

## Findings Generation

Reason:

Analysis Agent not implemented.

Do not generate:

* vulnerabilities
* severities
* recommendations

---

## Efficient Fetch

Reason:

Phase 5.

Do not implement.

---

## RAG

Reason:

Phase 6.

Do not implement.

---

## Retrieval-Augmented Analysis

Reason:

Phase 6.

Do not implement.

---

## LangChain

Do not introduce unless absolutely required.

Plain ChromaDB is sufficient.

---

# Definition of Done

Phase 4 is complete when:

✓ ChromaDB installed

✓ Chroma client exists

✓ Features stored in ChromaDB

✓ Routes stored in ChromaDB

✓ Feature retrieval works

✓ Route retrieval works

✓ Tests pass

✓ Existing Phase 1 tests pass

✓ Existing Phase 2 tests pass

✓ Existing Phase 3 tests pass

✓ No Analysis Agent exists

✓ No Findings generated

✓ No Efficient Fetch exists

✓ No RAG exists

---

# Success Criteria

At the end of Phase 4:

```text
Website
    ↓

Recon Agent
    ↓

Feature Extraction Agent
    ↓

SQLite

    +
    
ChromaDB
```

The system now possesses memory.

Future phases will use this memory for retrieval and reasoning.
