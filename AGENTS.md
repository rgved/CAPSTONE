# AGENTS.md

## Project Overview

This repository implements an Agentic Web Application Security Reconnaissance Platform.

The full architecture is documented in:

* docs/architecture.md
* docs/contracts.md
* docs/roadmap.md

Read these files before making changes.

---

## Development Rules

1. Follow contracts.md exactly.
2. Do not invent alternative schemas.
3. Do not rename fields.
4. Do not modify contracts without explicit instruction.
5. Do not implement future phases.

---

## Current Development Phase

The active phase is:

phase8


Agents must only implement the active phase.

Future phases are out of scope.

---

## Architecture Rules

The system follows:

Smart Orchestrator
+
Focused Workers

Workers must not perform responsibilities assigned to other workers.

Examples:

Recon Agent:

* Allowed: HTML extraction
* Not Allowed: Security analysis

Feature Extraction Agent:

* Allowed: Feature classification
* Not Allowed: Vulnerability assessment

Analysis Agent:

* Allowed: Security reasoning
* Not Allowed: HTML parsing

---

## Code Quality Rules

* Use type hints.
* Use Pydantic models where applicable.
* Write unit tests for new functionality.
* Prefer composition over inheritance.
* Keep functions small and focused.

---

## Database Rules

SQLite is the source of truth for structured data.

Do not introduce additional databases without explicit approval.

---

## Scope Control

When implementing a phase:

Allowed:

* Build only what is requested.

Not Allowed:

* Pre-build future architecture.
* Add speculative abstractions.
* Implement unfinished phases.

If a requested task requires functionality from a future phase, stop and explain why.
