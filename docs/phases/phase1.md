# Phase 1 — Reconnaissance Foundation

Status: Completed

---

# Objective

Build the foundational reconnaissance pipeline for the Agentic Web Application Security Reconnaissance Platform.

This phase establishes:

* Project structure
* SQLite storage
* Core models
* Recon Agent
* Basic execution flow
* Unit tests

At the end of this phase the system should be capable of:

1. Accepting a URL
2. Visiting the target page
3. Extracting structural observations
4. Storing discovered routes
5. Displaying a summary of results

No reasoning, classification, or security analysis should exist yet.

---

# Phase Goal

Target Workflow

```text
User URL
    ↓

Recon Agent
    ↓

Recon Result
    ↓

SQLite Storage
    ↓

Console Output
```

Example:

```bash
python main.py https://example.com
```

Output:

```text
URL: https://example.com

Routes Found: 12
Forms Found: 1
Inputs Found: 3
Buttons Found: 2
Scripts Found: 8
```

---

# Architecture Context

The final system contains:

* Orchestrator
* Recon Agent
* Feature Extraction Agent
* Analysis Agent
* Report Agent

However Phase 1 implements ONLY:

```text
Recon Agent
+
SQLite
```

All other components are future work.

---

# Required Reading

Before implementing Phase 1:

1. docs/architecture.md
2. docs/contracts.md
3. AGENTS.md

All implementations must conform to those documents.

---

# Scope

## In Scope

### Project Structure

Create:

```text
project/

├── backend/
│
├── backend/agents/
│   └── recon/
│
├── backend/memory/
│   └── sqlite/
│
├── backend/models/
│
├── backend/services/
│
├── tests/
│
├── docs/
│
└── main.py
```

---

### Recon Agent

Implement:

```python
ReconAgent
```

Responsibilities:

* Visit page
* Retrieve HTML
* Parse HTML
* Extract observations

Must use:

* Playwright
* BeautifulSoup

May use:

* Regex

Must NOT use:

* LLMs
* AI APIs
* Vector databases

---

### Extraction Targets

The Recon Agent must discover:

#### Links

Example:

```html
<a href="/login">
```

Extract:

```json
"/login"
```

---

#### Forms

Example:

```html
<form action="/login" method="POST">
```

Extract:

```json
{
  "action": "/login",
  "method": "POST"
}
```

---

#### Inputs

Example:

```html
<input name="username">
```

Extract:

```json
"username"
```

---

#### Buttons

Example:

```html
<button>Login</button>
```

Extract:

```json
"Login"
```

---

#### Scripts

Example:

```html
<script src="app.js">
```

Extract:

```json
"app.js"
```

---

#### Meta Tags

Example:

```html
<meta name="generator" content="WordPress">
```

Extract relevant metadata.

---

# SQLite Layer

Create database initialization.

Create tables exactly as defined in:

```text
docs/contracts.md
```

Required tables:

* routes
* features
* findings
* tasks

Only route persistence is required during Phase 1.

---

# Models

Create strongly typed models.

Minimum:

```python
Route
Form
ReconResult
Task
```

Use:

```text
Pydantic
```

preferred.

Dataclasses acceptable.

---

# Storage Service

Implement:

```python
save_route(route)
```

```python
get_routes()
```

No other persistence required yet.

---

# Main Execution Script

Create:

```python
main.py
```

Usage:

```bash
python main.py https://example.com
```

Flow:

1. Receive URL
2. Run Recon Agent
3. Save routes
4. Print summary

---

# Unit Testing

Create tests for:

### HTML Parsing

Verify:

* forms extracted correctly
* inputs extracted correctly
* links extracted correctly

---

### Route Storage

Verify:

* route saved
* route retrieved

---

### Recon Result

Verify returned object matches contract.

---

# Out Of Scope

The following are prohibited during Phase 1.

## Orchestrator

Do not create:

```python
OrchestratorAgent
```

Reason:

Introduced in Phase 2.

---

## Feature Extraction

Do not create:

```python
FeatureExtractionAgent
```

Reason:

Introduced in Phase 3.

---

## ChromaDB

Do not install.

Do not configure.

Do not reference.

Reason:

Introduced in Phase 4.

---

## Efficient Fetch Service

Do not implement.

Reason:

Introduced in Phase 5.

---

## Analysis Agent

Do not implement.

Reason:

Introduced in Phase 6.

---

## Security Findings

Do not create:

* vulnerability detection
* severity assignment
* confidence scoring

Reason:

Requires Analysis Agent.

---

## Reporting

Do not generate:

* summaries
* recommendations
* reports

Reason:

Introduced in Phase 7.

---

# Definition of Done

Phase 1 is complete when:

✓ Project structure exists

✓ SQLite initializes successfully

✓ Recon Agent can visit a URL

✓ Recon Agent extracts links

✓ Recon Agent extracts forms

✓ Recon Agent extracts inputs

✓ Recon Agent extracts buttons

✓ Recon Agent extracts scripts

✓ Routes are persisted

✓ Tests pass

✓ Running:

```bash
python main.py https://example.com
```

produces a valid summary

✓ No LLMs exist

✓ No ChromaDB exists

✓ No Analysis Agent exists

✓ No Feature Extraction Agent exists

✓ No Report Agent exists

---

# Deliverables

Expected files:

```text
backend/
│
├── agents/recon/recon_agent.py
│
├── memory/sqlite/database.py
│
├── models/
│   ├── route.py
│   ├── form.py
│   ├── recon_result.py
│   └── task.py
│
├── services/storage_service.py
│
tests/
│
├── test_recon.py
├── test_storage.py
└── test_models.py

main.py
```

No additional architecture should be implemented in this phase.
