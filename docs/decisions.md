<!-- # decisions.md

# Architecture Decision Records (ADR)

This document records major architectural decisions made during development.

Purpose:

* Preserve architectural reasoning.
* Avoid revisiting solved problems.
* Help future contributors understand design choices.
* Provide justification for capstone evaluations.

---

# ADR-001

Date: 2026-06-06

Decision:

Use a Smart Orchestrator with Focused Workers.

```text
Smart Orchestrator
        +
Focused Workers
```

Reason:

The orchestrator is responsible for planning and task delegation.

Workers are responsible only for execution.

This separation reduces worker complexity and allows centralized decision-making.

Alternatives Considered:

```text
Dumb Orchestrator
        +
Smart Workers
```

Rejected Because:

Decision-making becomes fragmented across agents and makes coordination more difficult.

Status:

Accepted

---

# ADR-002

Date: 2026-06-06

Decision:

Use a ReAct-style orchestration loop.

Reason:

The system continuously discovers new information.

A fixed pipeline cannot adapt to newly discovered routes, features, or findings.

The ReAct loop allows dynamic replanning after every worker result.

Alternatives Considered:

Linear Pipeline

```text
Recon
↓
Feature Extraction
↓
Analysis
↓
Report
```

Rejected Because:

New discoveries cannot influence earlier stages.

Status:

Accepted

---

# ADR-003

Date: 2026-06-06

Decision:

Recon Agent will not use an LLM.

Reason:

Reconnaissance is deterministic.

HTML extraction, route discovery, form discovery, and metadata collection can be performed reliably using code.

Removing the LLM reduces cost, latency, and hallucination risk.

Alternatives Considered:

LLM-assisted reconnaissance.

Rejected Because:

No measurable benefit for MVP requirements.

Status:

Accepted

---

# ADR-004

Date: 2026-06-06

Decision:

Use SQLite for structured memory.

Reason:

The MVP is a single-user research system.

SQLite provides:

* Zero configuration
* Fast development
* Easy local deployment
* Sufficient scale for the capstone

Alternatives Considered:

PostgreSQL

Rejected Because:

Additional infrastructure complexity without MVP value.

Status:

Accepted

---

# ADR-005

Date: 2026-06-06

Decision:

Use ChromaDB for semantic memory.

Reason:

The Analysis Agent requires semantic retrieval of findings, routes, and feature summaries.

ChromaDB provides local vector search without requiring cloud services.

Alternatives Considered:

Pinecone
Weaviate
FAISS

Rejected Because:

Cloud dependency or additional operational complexity.

Status:

Accepted

---

# ADR-006

Date: 2026-06-06

Decision:

Separate memory into SQLite and ChromaDB.

Reason:

Different data types require different retrieval mechanisms.

SQLite stores:

* Routes
* Tasks
* Coverage State
* Agent Logs

ChromaDB stores:

* Findings
* Feature Summaries
* Route Summaries

This prevents forcing semantic retrieval onto structured data.

Status:

Accepted

---

# ADR-007

Date: 2026-06-06

Decision:

Efficient Fetch Service will be a shared infrastructure component rather than an agent.

Reason:

The service performs retrieval and token reduction.

It does not make decisions.

Only decision-making components should be modeled as agents.

Status:

Accepted

---

# ADR-008

Date: 2026-06-06

Decision:

Security confidence scores are heuristic confidence values.

Reason:

The system cannot calculate true probabilities.

Confidence scores represent analyst confidence based on available evidence.

They are intended to assist prioritization rather than provide statistical certainty.

Status:

Accepted

---

# ADR-009

Date: 2026-06-06

Decision:

The MVP will support only two user interfaces.

1. Scan Console
2. Results Dashboard

Reason:

The primary goal is validating the agentic architecture and retrieval strategy.

Additional UI complexity does not contribute to research outcomes.

Status:

Accepted

---

# ADR-010

Date: 2026-06-06

Decision:

Ground truth datasets will be manually created.

Initial benchmark targets:

* DVWA
* OWASP Juice Shop
* WebGoat

Reason:

Precision, Recall, and F1 Score require known true findings.

The project research contribution depends on measuring retrieval quality against verified results.

Status:

Accepted -->
# decisions.md

## ADR-001
Decision: Smart Orchestrator + Focused Workers
Reason: Centralized planning, simpler workers.
Rejected: Smart Workers + Dumb Orchestrator.

## ADR-002
Decision: ReAct orchestration loop.
Reason: Supports dynamic replanning from new discoveries.
Rejected: Linear pipeline.

## ADR-003
Decision: Recon Agent uses deterministic code only.
Reason: Lower cost, latency, and hallucination risk.
Rejected: LLM-assisted recon.

## ADR-004
Decision: SQLite for structured memory.
Reason: Simple, local, sufficient for MVP.
Rejected: PostgreSQL.

## ADR-005
Decision: ChromaDB for semantic memory.
Reason: Local vector search.
Rejected: Pinecone, Weaviate, FAISS.

## ADR-006
Decision: Dual-memory architecture.
SQLite: routes, tasks, coverage, logs.
ChromaDB: findings, summaries.

## ADR-007
Decision: Efficient Fetch Service is infrastructure, not an agent.
Reason: Performs retrieval, not decisions.

## ADR-008
Decision: Confidence scores are heuristic.
Reason: Prioritization aid, not statistical probability.

## ADR-009
Decision: MVP UI = Scan Console + Results Dashboard.
Reason: Focus on architecture validation.

## ADR-010
Decision: Manual benchmark datasets.
Targets: DVWA, Juice Shop, WebGoat.
Reason: Needed for Precision, Recall, F1 evaluation.