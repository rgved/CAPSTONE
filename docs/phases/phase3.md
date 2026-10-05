# Phase 3 — Feature Extraction Agent

Status: Completed

---

# Objective

Introduce the first AI-powered component in the system.

This phase implements the Feature Extraction Agent.

The purpose of this agent is to transform Recon observations into structured application capabilities.

The Feature Extraction Agent answers:

```text id="0q5m8x"
What functionality does this represent?
```

It does NOT answer:

```text id="jv4x6e"
Is this vulnerable?
```

That belongs to the Analysis Agent in a later phase.

---

# Architecture Context

Current System:

```text id="9zttve"
Orchestrator
    ↓

Recon Agent
```

After Phase 3:

```text id="g1ivb7"
Orchestrator
    ↓

Recon Agent
    ↓

Feature Extraction Agent
```

The Feature Extraction Agent becomes the first worker that uses an LLM.

---

# Required Reading

Before implementation:

1. AGENTS.md
2. docs/contracts.md
3. docs/architecture.md
4. docs/phases/phase1.md
5. docs/phases/phase2.md

All code must remain compliant with those documents.

---

# Purpose

Input:

```json id="w6ey5x"
{
  "inputs": [
    "username",
    "password"
  ],
  "buttons": [
    "Login"
  ]
}
```

Output:

```json id="l0uktx"
{
  "feature": "authentication",
  "classification_confidence": 0.96
}
```

The agent identifies application functionality.

Nothing more.

---

# Supported Feature Types

The LLM must classify into one of the following:

```text id="q6o4m9"
authentication
registration
password_reset
search
file_upload
api
user_profile
admin_panel
dashboard
settings
unknown
```

No additional feature types may be introduced.

The classification set is closed.

---

# New Components

Create:

```text id="cz3u6d"
backend/

├── agents/
│   └── feature_extraction/
│
├── prompts/
│
└── models/
```

---

# New Folder Structure

```text id="d7w6vb"
backend/

├── agents/
│   └── feature_extraction/
│       └── feature_extraction_agent.py
│
├── prompts/
│   └── feature_classification_prompt.txt
│
├── models/
│   └── feature.py
```

---

# Feature Object

Implement contract from architecture.

```json id="5h9muu"
{
  "feature_id": "AUTH-001",
  "name": "authentication",
  "routes": [],
  "classification_confidence": 0.96,
  "analyzed": false
}
```

Store this in SQLite.

---

# SQLite Integration

Phase 1 created:

```text id="s9whvq"
features
```

table.

Phase 3 begins using it.

Implement:

```python id="r1uqkw"
save_feature()
```

```python id="k1xvji"
get_features()
```

---

# Feature Extraction Agent

Create:

```python id="7w8h7k"
FeatureExtractionAgent
```

Responsibilities:

1. Receive ReconResult
2. Build classification prompt
3. Call LLM
4. Parse response
5. Return Feature object

---

# LLM Provider

Use one provider only.

Examples:

```text id="smjntq"
OpenAI
Groq
Anthropic
```

Do not build multi-provider support yet.

Keep implementation simple.

---

# Prompt Design

The LLM receives:

```json id="jjlwm0"
{
  "forms": [],
  "inputs": [],
  "buttons": [],
  "links": []
}
```

and must return:

```json id="s7zyf4"
{
  "feature": "...",
  "confidence": 0.0
}
```

Output must always be valid JSON.

---

# Orchestrator Changes

Phase 2 supported:

```text id="ew0hjf"
RUN_RECON
STOP
```

Phase 3 adds:

```text id="8hmv7v"
EXTRACT_FEATURES
```

---

# New Mission Flow

```text id="d4hjy2"
RUN_RECON
        ↓

Recon Result
        ↓

EXTRACT_FEATURES
        ↓

Feature Extraction Agent
        ↓

Feature Object
        ↓

SQLite
        ↓

STOP
```

---

# Worker Response Contract

Feature Extraction Agent must return:

```json id="qrb4hc"
{
  "status": "success",
  "worker": "feature_extraction",
  "task_id": "TASK-002",
  "data": {},
  "new_findings": [],
  "errors": []
}
```

Same contract as Recon Agent.

---

# Testing Requirements

Create:

```text id="6t9mqi"
tests/

├── test_feature_extraction.py
├── test_feature_storage.py
```

---

## test_feature_extraction.py

Verify:

* authentication classification
* search classification
* upload classification
* unknown classification

Use mocked LLM responses.

Do NOT call the real API during tests.

---

## test_feature_storage.py

Verify:

* save_feature()
* get_features()

---

# Out Of Scope

The following are prohibited.

---

## ChromaDB

Reason:

Phase 4.

Do not install.

Do not configure.

---

## Semantic Retrieval

Reason:

Phase 4.

Do not implement.

---

## Efficient Fetch Service

Reason:

Phase 5.

Do not implement.

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
* severities
* attack paths
* recommendations

---

## Report Agent

Reason:

Phase 7.

Do not implement.

---

# Definition of Done

Phase 3 is complete when:

✓ FeatureExtractionAgent exists

✓ First LLM integration exists

✓ Feature object exists

✓ Features can be stored

✓ EXTRACT_FEATURES task exists

✓ Orchestrator can dispatch Feature Extraction

✓ Feature classifications persist to SQLite

✓ New tests pass

✓ Existing Phase 1 tests pass

✓ Existing Phase 2 tests pass

✓ No ChromaDB exists

✓ No Analysis Agent exists

✓ No Security Findings exist

✓ No Report Agent exists

---

# Success Criteria

At the end of Phase 3:

```text id="9s9e5g"
User URL
    ↓

Orchestrator
    ↓

RUN_RECON
    ↓

Recon Agent
    ↓

EXTRACT_FEATURES
    ↓

Feature Extraction Agent
    ↓

Feature Inventory
    ↓

SQLite
```

The system can now understand what functionality exists within the application, but it still performs no security reasoning.
