# Phase 6 — Analysis Agent

Status: Completed

---

# Objective

Implement the Analysis Agent.

This is the first phase where the system performs security reasoning.

The Analysis Agent receives:

* Feature information
* Recon data
* Semantic memory
* Efficient Fetch output

and determines whether sufficient evidence exists to generate a security observation.

The Analysis Agent does NOT perform exploitation.

The Analysis Agent does NOT attack the target.

The Analysis Agent only reasons over collected evidence.

---

# Architecture Context

Current System

```text
Recon Agent
        ↓

Feature Extraction Agent
        ↓

Semantic Memory
        ↓

Efficient Fetch
```

After Phase 6

```text
Recon Agent
        ↓

Feature Extraction Agent
        ↓

Semantic Memory
        ↓

Efficient Fetch
        ↓

Analysis Agent
        ↓

Findings
```

---

# Required Reading

Before implementation:

1. AGENTS.md
2. architecture.md
3. contracts.md
4. phase1.md
5. phase2.md
6. phase3.md
7. phase4.md
8. phase5.md

---

# Core Principle

The Analysis Agent must be evidence-first.

Never generate findings from assumptions.

Bad:

```text
This looks like a login form.
Probably vulnerable.
```

Good:

```text
Authentication form detected.

No CSRF token detected.

Observation generated.
```

Every finding must be traceable to evidence.

---

# Inputs

The Analysis Agent receives:

## ReconResult

```json
{
  "forms": [],
  "inputs": [],
  "buttons": [],
  "scripts": []
}
```

---

## Feature

Example:

```json
{
  "name": "authentication"
}
```

---

## Efficient Fetch Output

```json
{
  "structured_content": "...",
  "token_count_efficient": 997
}
```

---

## Semantic Memory

Retrieved:

* similar routes
* similar features
* previous findings

---

# New Components

Create:

```text
backend/

├── agents/
│   └── analysis/
│
├── prompts/
│
└── models/
```

---

# Folder Structure

```text
backend/

├── agents/
│   └── analysis/
│       └── analysis_agent.py
│
├── prompts/
│   └── analysis_prompt.txt
│
├── models/
│   └── finding.py
```

---

# Finding Model

Create:

```python
Finding
```

Example:

```json
{
  "finding_id": "FIND-001",
  "title": "Potential Missing CSRF Protection",
  "description": "...",
  "severity": "low",
  "confidence": 0.82,
  "evidence": [],
  "route_id": 3
}
```

---

# Supported Severities

Only:

```text
informational
low
medium
high
```

No critical severity in Phase 6.

Critical requires validation.

---

# Supported Finding Categories

Closed set:

```text
missing_csrf
weak_authentication
exposed_endpoint
file_upload_risk
missing_security_headers
admin_surface
sensitive_input
unknown
```

Do not invent new categories.

---

# Analysis Flow

```text
Feature
      ↓

Retrieve Context
      ↓

Build Evidence Package
      ↓

LLM Analysis
      ↓

Structured Finding
      ↓

Store Finding
```

---

# Evidence Package

Before calling the LLM:

Construct:

```json
{
  "feature": "...",
  "forms": [],
  "inputs": [],
  "routes": [],
  "retrieved_context": []
}
```

The LLM receives evidence only.

No raw HTML dumps.

---

# Prompt Strategy

The LLM must:

1. Analyze evidence
2. Explain reasoning
3. Produce structured JSON

The LLM must not:

* exploit targets
* invent evidence
* speculate

---

# Required Output

The model must return:

```json
{
  "finding_category": "missing_csrf",
  "title": "Potential Missing CSRF Protection",
  "description": "...",
  "severity": "low",
  "confidence": 0.82,
  "evidence": [
    "POST form detected",
    "No CSRF token observed"
  ]
}
```

JSON only.

---

# Confidence Rules

Confidence reflects evidence strength.

Examples:

```text
Observed directly
→ 0.80 - 0.95

Partial evidence
→ 0.50 - 0.79

Weak evidence
→ <0.50
```

---

# Finding Creation Threshold

Only persist findings if:

```text
confidence >= 0.70
```

Otherwise:

```text
informational observation only
```

This reduces hallucinated findings.

---

# SQLite Integration

Begin using:

```text
findings
```

table created earlier.

Implement:

```python
save_finding()
```

```python
get_findings()
```

---

# Chroma Integration

Begin using:

```text
findings collection
```

Store:

```text
title
+
description
+
evidence
```

as embedding content.

---

# Orchestrator Changes

Add:

```text
RUN_ANALYSIS
```

Mission flow becomes:

```text
RUN_RECON
        ↓

EXTRACT_FEATURES
        ↓

RUN_EFFICIENT_FETCH
        ↓

RUN_ANALYSIS
        ↓

STOP
```

---

# Worker Response

Must follow contracts.md

Example:

```json
{
  "status": "success",
  "worker": "analysis",
  "task_id": "TASK-007",
  "data": {},
  "new_findings": [],
  "errors": []
}
```

---

# Testing Requirements

Create:

```text
tests/

├── test_analysis_agent.py
├── test_findings_storage.py
```

---

## test_analysis_agent.py

Mock LLM responses.

Verify:

* valid finding creation
* confidence threshold logic
* JSON parsing
* failure handling

No real API calls.

---

## test_findings_storage.py

Verify:

* save_finding()
* get_findings()

---

# Failure Handling

If analysis fails:

Return:

```json
{
  "status": "failure",
  "worker": "analysis",
  "errors": [...]
}
```

Never crash the mission.

---

# Out Of Scope

The following are prohibited.

---

## Active Exploitation

No:

* SQL injection testing
* XSS execution
* authentication bypass attempts
* file upload execution

Reason:

Reconnaissance only.

---

## Automatic Remediation

Do not generate fixes.

That belongs to future phases.

---

## Report Generation

Reason:

Phase 7.

Do not implement.

---

## Multi-Agent Debate

Reason:

Unnecessary complexity.

Single Analysis Agent only.

---

## LangChain

Do not introduce unless necessary.

Plain Python preferred.

---

# Definition of Done

Phase 6 is complete when:

✓ Analysis Agent exists

✓ Evidence package created

✓ LLM analysis works

✓ Structured findings generated

✓ Findings persisted

✓ Findings indexed in semantic memory

✓ Confidence threshold implemented

✓ Tests pass

✓ Existing tests continue to pass

✓ No Report Agent exists

✓ No Active Exploitation exists

---

# Success Criteria

At the end of Phase 6:

```text
Website
      ↓

Recon
      ↓

Feature Extraction
      ↓

Semantic Memory
      ↓

Efficient Fetch
      ↓

Analysis Agent
      ↓

Finding
```

Example:

```text
Feature:
authentication

Evidence:
POST login form
password field
missing csrf token

↓

Finding:
Potential Missing CSRF Protection
Severity: Low
Confidence: 0.84
```

The system can now transform observations into evidence-backed security findings.
