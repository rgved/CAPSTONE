# Intelligent Agent for Automated Web Application Security Testing

## Complete MVP Architecture Specification (Current Version)

---

# 1. Project Vision

The goal of this project is to build an Agentic AI-powered Web Application Security Reconnaissance Platform capable of:

* Exploring web applications autonomously
* Understanding application functionality
* Mapping attack surfaces
* Identifying potential security weaknesses
* Correlating findings across pages
* Producing structured security reports

while simultaneously

* Minimizing LLM token usage
* Measuring token efficiency
* Evaluating retrieval quality

---

# 2. Core Product Goal

The user should be able to provide a URL and receive:

* Application capability inventory
* Attack surface map
* Security findings
* Risk assessment
* Recommendations
* Token efficiency metrics

---

# 3. Core Research Goal

The research contribution is:

> Can an agentic cybersecurity system maintain useful security analysis quality while significantly reducing LLM token consumption using selective retrieval?

The project compares:

### Baseline

Full page HTML → LLM

versus

### Proposed

Structure Extraction → Relevance Filtering → Targeted Context → LLM

---

# 4. System Philosophy

The system is NOT:

* A vulnerability scanner
* A penetration testing tool
* An exploitation framework

The system IS:

* A security reconnaissance platform
* A security understanding platform
* An AI security analyst

---

# 5. High-Level Architecture

```text
User
 │
 ▼

Orchestrator Agent
(Brain)

 │
 ▼

Worker Layer

 ├── Recon Agent
 ├── Feature Extraction Agent
 ├── Analysis Agent
 └── Report Agent

 │
 ▼

Shared Memory

 ├── SQLite
 └── ChromaDB

 │
 ▼

Dashboard
```

---

# 6. Agent Design Philosophy

The architecture follows:

```text
Smart Orchestrator
        +
Focused Workers
```

NOT:

```text
Dumb Orchestrator
        +
Super Smart Workers
```

---

The Orchestrator decides:

> What should happen next?

Workers decide:

> How do I perform this task?

---

# 7. Orchestrator Agent

## Purpose

The Orchestrator is the brain.

It never:

* Parses HTML
* Detects vulnerabilities
* Generates reports
* Crawls websites

Instead it answers:

> Given everything I know, what should I learn next?

---

# 8. Orchestrator ReAct Loop

The Orchestrator continuously performs:

```text
Observe
↓
Plan
↓
Dispatch Task
↓
Observe Results
↓
Update Knowledge
↓
Replan
```

---

# 9. Orchestrator Inputs

The orchestrator receives:

### Goal

Example:

```json
{
  "goal": "Assess security posture"
}
```

---

### Coverage State

```json
{
  "authentication": {
    "discovered": true,
    "analyzed": false
  }
}
```

---

### Findings Summary

```json
{
  "critical_findings": 2,
  "high_findings": 4
}
```

---

### Memory Summary

Retrieved from:

* SQLite
* ChromaDB

---

# 10. Orchestrator Available Actions

The orchestrator can choose:

### RUN_RECON

Discover routes and structure.

---

### INVESTIGATE_ROUTE

Deep dive a route.

Example:

```text
/admin
```

---

### ANALYZE_AUTH

Authentication-focused analysis.

---

### ANALYZE_FEATURE

Analyze:

* Search
* Upload
* API
* Admin

---

### ANALYZE_FINDINGS

Correlate discoveries.

---

### FINAL_RECON_SWEEP

Search for hidden functionality.

---

### GENERATE_REPORT

Produce final report.

---

### STOP

Terminate mission.

---

# 11. Orchestrator Completion Criteria

Stop only when:

### Rule 1

All discovered features analyzed.

---

### Rule 2

No high-priority routes remain.

---

### Rule 3

No critical low-confidence findings remain.

---

### Rule 4

Final Recon Sweep completed.

---

### Rule 5

No significant new findings discovered.

---

### Rule 6

Safety Limits Reached

```text
Max Iterations = 30
OR
Max Runtime = 10 Minutes
```

---

# 12. Recon Agent

## Purpose

Collect observations.

No reasoning.

No security analysis.

---

## Uses LLM?

NO

---

## Technologies

* Playwright
* BeautifulSoup
* Regex

---

## Responsibilities

Discover:

* Routes
* Pages
* Forms
* Inputs
* Buttons
* Links
* Scripts
* Meta Tags
* Hidden Elements

---

## Output Example

```json
{
  "route": "/login",
  "forms": 1,
  "inputs": [
    "username",
    "password"
  ],
  "buttons": [
    "Login"
  ]
}
```

---

## Recon Does NOT

* Identify vulnerabilities
* Classify features
* Assign risk
* Generate recommendations

---

# 13. Feature Extraction Agent

## Purpose

Convert observations into application capabilities.

Answers:

> What functionality does this represent?

---

## Uses LLM?

YES

---

## Input

Recon observations.

---

## Example

Input:

```json
{
  "inputs": [
    "username",
    "password"
  ]
}
```

Output:

```json
{
  "feature": "authentication",
  "classification_confidence": 0.96
}
```

---

# 14. Feature Inventory

The Feature Extraction Agent creates:

```json
{
  "authentication": {
    "discovered": true,
    "analyzed": false
  },
  "search": {
    "discovered": true,
    "analyzed": false
  }
}
```

---

# 15. Feature Types

Examples:

* Authentication
* Registration
* Password Reset
* Search
* File Upload
* API
* User Profile
* Admin Panel
* Dashboard
* Settings

---

# 16. Analysis Agent

## Purpose

Security reasoning.

This is the primary cybersecurity intelligence component.

---

## Uses LLM?

YES

Heavy usage.

---

## Responsibilities

* Correlate findings
* Assess risk
* Generate confidence
* Identify attack paths
* Produce insights

---

# 17. Analysis Retrieval Strategy

Before reasoning:

## Retrieval Pass 1

Structured Lookup

Example:

```text
feature = authentication
```

Returns:

```text
Login
JWT
Password Reset
```

---

## Retrieval Pass 2

Semantic Lookup

Using ChromaDB.

Example:

```text
Privilege Escalation
```

Returns:

```text
Admin Route
Missing Authorization
Hidden Admin Button
```

---

## Then Reason

```text
Structured Context
+
Semantic Context
↓
LLM Analysis
```

---

# 18. Analysis Output

Example:

```json
{
  "finding": "Missing CSRF Protection",
  "severity": "High",
  "security_confidence": 0.87,
  "evidence": [
    "Login Form",
    "No CSRF Token"
  ]
}
```

---

# 19. Security Confidence

Security confidence is generated ONLY by Analysis Agent.

It represents:

> How confident the system is that this finding is meaningful.

It is NOT a probability.

It is a heuristic confidence score.

---

# 20. Report Agent

## Purpose

Generate final report.

---

## Uses LLM?

HYBRID

---

# 21. Deterministic Report Tasks

Performed in code.

Examples:

```python
group_findings_by_severity()
calculate_metrics()
build_statistics()
```

---

# 22. LLM Report Tasks

Single LLM call:

Generate:

* Executive Summary
* Recommendations
* Security Narrative

---

# 23. Efficient Fetch Service
Purpose

The Efficient Fetch Service is the core research contribution of the project.

It acts as a shared infrastructure component used by all agents that require web content.

It is NOT an agent.

It is a reusable service.

Function Interface

All workers interact with the service through a common interface:

efficient_fetch(url, query_hint)
Parameters
url

Target URL to analyze.

Example:

/login
query_hint

Describes what the calling worker is attempting to find.

Examples:

authentication forms
admin functionality
file upload components
hidden elements
search functionality

The query hint is used during relevance filtering.

Return Object
{
  "structured_content": {},
  "token_count_naive": 0,
  "token_count_efficient": 0
}
structured_content

Filtered content returned to the requesting worker.

Example:

{
  "forms": [...],
  "inputs": [...],
  "buttons": [...]
}
token_count_naive

Estimated token count if the full page HTML had been sent to the LLM.

token_count_efficient

Estimated token count after selective retrieval.

Research Benefit

Every call automatically generates token-efficiency measurements.

This allows token metrics to accumulate passively throughout the entire system.

No special instrumentation is required later.

# 24. Stage 1

Structure Extraction

Extract:

* Headings
* Forms
* Inputs
* Buttons
* Navigation
* Metadata

---

# 25. Stage 2

Relevance Filtering

Using:

* Embeddings
* Similarity Search

---

# 26. Stage 3

Targeted Context Generation

Only useful context survives.

Example:

```text
50KB HTML
↓
2KB Context
```

---

# 27. Memory Architecture

The system uses:

```text
SQLite
+
ChromaDB
```

---

# 28. SQLite Responsibilities

Stores structured data.

Examples:

* Scan History
* Tasks
* Coverage State
* Routes
* Timestamps
* Agent Logs

---

# 29. ChromaDB Responsibilities

Stores semantic data.

Examples:

* Findings
* Feature Summaries
* Route Summaries
* Analysis Results

---

# 30: ChromaDB Collections
ChromaDB Collections

The system uses three collections.

Collection: findings

Purpose:

Store security findings.

Metadata Stored:

{
  "finding_id": "F-001",
  "feature": "authentication",
  "severity": "high"
}

Embedded Text:

title + evidence

Example:

Missing CSRF Protection.
Evidence:
Login form detected.
CSRF token not present.
Collection: features

Purpose:

Store application capabilities.

Metadata Stored:

{
  "feature": "authentication"
}

Embedded Text:

feature_name + associated_route_summaries

Example:

Authentication.
Routes:
Login page.
Registration page.
Password reset page.
Collection: routes

Purpose:

Store semantic route descriptions.

Metadata Stored:

{
  "route": "/admin"
}

Embedded Text:

route + structural_summary

Example:

/admin

Administrative interface.
Contains management controls.
Contains hidden navigation elements.
Add New Section: Ground Truth Dataset
Ground Truth Dataset

To support evaluation metrics such as:

Precision
Recall
F1 Score

the project maintains a manually labelled ground truth dataset.

Purpose

The ground truth dataset represents the known true findings for each benchmark application.

It serves as the reference against which both:

Naive Pipeline
Efficient Pipeline

are evaluated.

Initial Benchmark Applications
DVWA
OWASP Juice Shop
WebGoat
Dataset Format

Example:

{
  "application": "DVWA",
  "known_findings": [
    "SQL Injection",
    "Stored XSS",
    "Reflected XSS",
    "Weak Authentication"
  ]
}
Creation Method

The dataset will be generated through manual validation using:

Burp Suite
OWASP ZAP
Application Documentation
Research Usage

The dataset enables calculation of:

Precision
Recall
F1 Score
Coverage

for both retrieval approaches.

This ensures that token savings are evaluated alongside security analysis quality.

---

# 31. JSON Contract Philosophy

All agents communicate through structured contracts.

---

# 32. Universal Task Contract

Orchestrator → Worker

```json
{
  "task_id": "123",
  "action": "RUN_RECON",
  "target": "/login",
  "context": {},
  "priority": "high"
}
```

---

# 33. Universal Response Contract

Worker → Orchestrator

```json
{
  "status": "success",
  "worker": "recon",
  "task_id": "123",
  "data": {},
  "new_findings": [],
  "errors": []
}
```

---

# 34. Finding Object

Core system object.

```json
{
  "finding_id": "F-001",
  "type": "missing_csrf",
  "title": "Missing CSRF Protection",
  "feature": "authentication",
  "severity": "high",
  "security_confidence": 0.87,
  "evidence": [
    "/login"
  ]
}
```

---

# 35. Feature Object

```json
{
  "feature_id": "AUTH-001",
  "name": "authentication",
  "routes": [
    "/login"
  ],
  "classification_confidence": 0.96,
  "analyzed": false
}
```

---

# 36. Coverage Object

Used by Orchestrator.

```json
{
  "authentication": {
    "discovered": true,
    "analyzed": true
  }
}
```

---

# 37. Failure Handling

Every worker returns:

---

## Success

```json
{
  "status": "success"
}
```

---

## Failure

```json
{
  "status": "failure",
  "error_type": "403_FORBIDDEN",
  "message": "Access denied"
}
```

---

# 38. Orchestrator Error Decisions

The orchestrator can:

* Retry
* Skip
* Escalate
* Terminate

based on worker responses.

---

# 39. Security Findings Scope

MVP findings include:

### Authentication

* Login Forms
* Registration Forms
* Password Reset

---

### Security Hygiene

* Missing CSP
* Missing HSTS
* Missing X-Frame-Options
* Missing X-Content-Type-Options

---

### Hidden Functionality

* Hidden Buttons
* Hidden Links
* Hidden Forms

---

### Sensitive Information

* API Keys
* Internal URLs
* Debug Information
* Stack Traces

---

### Administrative Functionality

* Admin Routes
* Hidden Admin Controls
* Authorization Issues

---

### Attack Surface

* Search Inputs
* File Uploads
* APIs
* User-Controlled Inputs

---

# 40. Final Recon Sweep

Before report generation:

The orchestrator runs:

```text
FINAL_RECON_SWEEP
```

Purpose:

Find:

* Hidden Routes
* Hidden Forms
* Hidden Buttons
* Debug Pages
* Unlinked Functionality

This serves as the final outlier detection phase.

---

# 41. MVP User Interface

Only two screens.

---

## Screen 1 — Scan Console

Displays:

* URL Input
* Current Task
* Current Agent
* Coverage Progress
* Agent Logs
* Token Usage

---

## Screen 2 — Results Dashboard

Tabs:

### Attack Surface

Routes
Forms
Features

---

### Findings

Security Findings

---

### Recommendations

Remediation Advice

---

### Analytics

Token Reduction
Latency
Precision
Recall
F1 Score

---
# 42: Final MVP Workflow
Actual System Workflow

The system does NOT operate as a linear pipeline.

Workers are invoked dynamically based on orchestrator decisions.

The orchestrator continuously replans throughout the scan.

Orchestrator Loop
Initialize Mission
        ↓

WHILE mission not complete

    Read Coverage State
            ↓

    Read Findings Memory
            ↓

    Build Current State
            ↓

    Choose Next Action
            ↓

    Dispatch Worker
            ↓

    Receive Result
            ↓

    Update SQLite
            ↓

    Update ChromaDB
            ↓

    Replan

END WHILE

        ↓

Generate Report
        ↓

Return Results
Example Execution
RUN_RECON
        ↓

Feature Extraction
        ↓

Authentication Discovered
        ↓

Replan
        ↓

ANALYZE_AUTH
        ↓

Finding Generated
        ↓

Replan
        ↓

RUN_RECON
        ↓

Admin Panel Discovered
        ↓

Replan
        ↓

INVESTIGATE_ROUTE(/admin)
        ↓

Replan
        ↓

ANALYZE_FINDINGS
        ↓

Replan
        ↓

FINAL_RECON_SWEEP
        ↓

GENERATE_REPORT
Important Note

Recon, Feature Extraction, Analysis, and Report Generation are NOT executed exactly once.

The orchestrator may invoke:

Recon multiple times
Analysis multiple times
Route investigation multiple times

depending on the current knowledge state and discovered features.

The system is therefore a dynamic reasoning loop rather than a fixed workflow pipeline.d
```

---

# 43. Final MVP Definition

An agentic web application security reconnaissance platform where an LLM-driven orchestrator maintains a dynamic security knowledge model of a target application, delegates tasks to specialized worker agents, stores structured and semantic findings in shared memory, continuously replans based on discovered capabilities, and produces actionable security assessments while minimizing LLM token consumption through a selective retrieval pipeline.
