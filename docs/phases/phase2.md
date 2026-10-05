# Phase 2 — Orchestrator Foundation

Status: Completed

---

# Objective

Build the orchestration framework that will coordinate all future agents.

This phase introduces the Orchestrator and the task execution model.

The goal is NOT to add intelligence.

The goal is to establish the execution loop that future intelligent agents will use.

At the end of Phase 2, the system should be capable of:

1. Creating a mission
2. Creating tasks
3. Dispatching tasks
4. Receiving worker responses
5. Updating mission state
6. Terminating correctly

Only one worker exists in the system:

```text
Recon Agent
```

No other workers should be implemented.

---

# Architecture Context

The final architecture follows:

```text
Orchestrator
    ↓

Workers

 ├── Recon Agent
 ├── Feature Extraction Agent
 ├── Analysis Agent
 └── Report Agent
```

However, during Phase 2:

```text
Orchestrator
    ↓

Recon Agent
```

Only.

The purpose of this phase is to establish orchestration mechanics before introducing intelligence.

---

# Required Reading

Before implementation:

1. AGENTS.md
2. docs/architecture.md
3. docs/contracts.md
4. docs/phases/phase1.md

All code must remain compliant with those documents.

---

# Scope

## In Scope

### Orchestrator

Create:

```python
Orchestrator
```

Responsibilities:

* Create mission
* Create tasks
* Dispatch tasks
* Receive responses
* Update state
* Terminate mission

The orchestrator must be deterministic.

No LLMs.

No reasoning.

No planning beyond simple state transitions.

---

### Task Dispatcher

Create:

```python
TaskDispatcher
```

Responsibilities:

* Receive task
* Route task to worker
* Return worker response

Example:

```python
dispatch(task)
```

If:

```python
task.action == "RUN_RECON"
```

then:

```python
recon_agent.run(...)
```

is executed.

---

### Mission State

Create:

```python
MissionState
```

Purpose:

Track overall mission progress.

Example:

```json
{
  "mission_id": "MISSION-001",
  "status": "running",
  "recon_completed": false
}
```

---

### Coverage State

Create:

```python
CoverageState
```

Phase 2 version:

```json
{
  "recon_completed": false
}
```

Do NOT add:

* authentication
* search
* upload
* admin

Those belong to future phases.

---

### Worker Response

Implement the Worker Response contract defined in:

```text
docs/contracts.md
```

Example:

```json
{
  "status": "success",
  "worker": "recon",
  "task_id": "TASK-001",
  "data": {},
  "new_findings": [],
  "errors": []
}
```

The orchestrator must operate exclusively through worker responses.

---

# New Folder Structure

Create:

```text
backend/

├── orchestrator/
│
├── orchestrator/
│   ├── orchestrator.py
│   ├── task_dispatcher.py
│   └── mission_state.py
│
├── models/
│   ├── worker_response.py
│   └── coverage_state.py
```

---

# Task System

The orchestrator creates tasks.

Phase 2 supports only:

```text
RUN_RECON
STOP
```

No additional actions.

---

### Task Example

```json
{
  "task_id": "TASK-001",
  "action": "RUN_RECON",
  "target": "https://example.com",
  "context": {},
  "priority": "high"
}
```

---

# Orchestrator Loop

Implement:

```python
while mission_running:

    task = choose_next_task()

    result = dispatcher.dispatch(task)

    update_state(result)

    if mission_complete:
        break
```

The loop should behave as a deterministic state machine.

No AI.

No LLM.

No autonomous reasoning.

---

# Mission Lifecycle

Phase 2 Mission Lifecycle:

```text
Mission Created
        ↓

RUN_RECON Task Created
        ↓

Task Dispatched
        ↓

Recon Agent Executes
        ↓

Worker Response Returned
        ↓

Coverage Updated
        ↓

Mission Complete
        ↓

STOP
```

---

# Database Integration

The `tasks` table created during Phase 1 must now be used.

Store:

```json
{
  "task_id": "TASK-001",
  "action": "RUN_RECON",
  "status": "completed"
}
```

The orchestrator should persist task execution history.

---

# Main Entry Point Changes

Phase 1:

```python
ReconAgent.run(url)
```

Phase 2:

```python
Orchestrator.run(url)
```

The orchestrator becomes the system entry point.

The orchestrator internally invokes the Recon Agent.

---

# Testing Requirements

Create:

```text
tests/

├── test_orchestrator.py
├── test_dispatcher.py
└── test_worker_response.py
```

---

## test_orchestrator.py

Verify:

* mission creation
* task generation
* state updates
* mission completion

---

## test_dispatcher.py

Verify:

* RUN_RECON dispatches correctly
* invalid actions handled correctly

---

## test_worker_response.py

Verify:

* contract compliance
* success responses
* failure responses

---

# Out Of Scope

The following are strictly prohibited during Phase 2.

---

## Feature Extraction Agent

Reason:

Phase 3.

Do not implement.

---

## LLM Integration

Reason:

Phase 3.

Do not implement.

---

## ChromaDB

Reason:

Phase 4.

Do not install.

Do not configure.

Do not reference.

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
* confidence scores

---

## Report Agent

Reason:

Phase 7.

Do not implement.

---

# Definition of Done

Phase 2 is complete when:

✓ Orchestrator exists

✓ TaskDispatcher exists

✓ MissionState exists

✓ CoverageState exists

✓ WorkerResponse exists

✓ RUN_RECON tasks can be created

✓ RUN_RECON tasks can be dispatched

✓ Recon Agent executes through dispatcher

✓ WorkerResponse returned successfully

✓ Mission state updates correctly

✓ Tasks are persisted

✓ Orchestrator terminates correctly

✓ New tests pass

✓ Existing Phase 1 tests continue to pass

✓ No LLMs exist

✓ No ChromaDB exists

✓ No Feature Extraction Agent exists

✓ No Analysis Agent exists

✓ No Report Agent exists

---

# Deliverables

Expected new files:

```text
backend/

├── orchestrator/
│   ├── orchestrator.py
│   ├── task_dispatcher.py
│   └── mission_state.py

├── models/
│   ├── worker_response.py
│   └── coverage_state.py

tests/

├── test_orchestrator.py
├── test_dispatcher.py
└── test_worker_response.py
```

Existing Phase 1 code should remain unchanged except where necessary to integrate with the orchestrator.

---

# Success Criteria

At the end of Phase 2:

```text
User URL
    ↓

Orchestrator
    ↓

RUN_RECON Task
    ↓

Task Dispatcher
    ↓

Recon Agent
    ↓

Worker Response
    ↓

Mission State Update
    ↓

STOP
```

The system now possesses an execution engine.

Future phases will add intelligence and additional workers on top of this foundation.
