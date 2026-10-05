# Phase 5.1 — Efficient Fetch Optimization

Status: Proposed / Planned

---

## Objective

Optimize the Phase 5 retrieval layer to use **Security Structure Retrieval** rather than raw HTML chunking. This change reduces context sizes further (target $85\text{--}95\%$) and ensures the future Analysis Agent processes intact, atomic security primitives (forms, inputs, endpoints) rather than arbitrary text chunks.

---

## Limitations of Current Approach (v1)

1. **HTML Splitting**: HTML structure can be split across arbitrary chunk boundaries.
2. **Structure Fragmentation**: Forms can be separated from their child inputs, resulting in incomplete security context.
3. **Semantic Inaccuracy**: Embedding algorithms perform poorly on raw, syntax-heavy HTML boilerplate.
4. **Boilerplate Noise**: High token counts are spent on non-functional metadata, style/script files, and headers.
5. **No Recall Evaluation**: Token reduction is tracked, but security information retention is unmeasured.

---

## Proposed Architecture

```text
Raw HTML
    ↓
Stage 1: Boilerplate Removal (strip tags, scripts, CSS)
    ↓
Stage 2: Security Structure Extraction (Forms, Inputs, Endpoints as atomic units)
    ↓
Stage 3: Security Signal Detection (add tagging features like "password_field", "admin_route")
    ↓
Stage 4: Hybrid Scoring (Keyword Score + Structural Score + Embedding Score)
    ↓
Stage 5: Schema Compression (Structured JSON format)
    ↓
Analysis Agent (Phase 6)
```

---

## Architectural Stages

### Stage 1: Boilerplate Removal
Strip out noisy blocks before scoring. This includes:
* `<script>`, `<style>`, `<svg>`, `<iframe>`, `<template>`
* CSS/stylesheet links, DNS prefetch tags
* Analytics and tracking tags

### Stage 2: Security Structure Extraction
Parse HTML into strong typed objects rather than lines or paragraphs. The retrieval units are represented by the `SecurityElement` model:

```python
@dataclass
class SecurityElement:
    type: str  # e.g., 'form', 'input', 'endpoint', 'upload'
    content: dict  # structured details
    security_signals: list[str]  # behavioral indicators
    raw_snippet: str  # raw HTML segment (for fallback)
```

### Stage 3: Security Signal Detection
Tag elements with lightweight signals:
* **Authentication**: `password_field`, `login_form`, `session_endpoint`, `csrf_token`
* **File Upload**: `multipart_form`, `file_input`, `upload_endpoint`
* **Administrative**: `admin_route`, `role_management`, `user_management`

### Stage 4: Hybrid Scoring
Calculate relevance by combining multiple scoring vectors:

$$\text{Final Score} = 0.45 \times \text{Keyword Relevance} + 0.30 \times \text{Semantic Similarity} + 0.25 \times \text{Structural Bonus}$$

### Stage 5: Schema Compression
Instead of returning structured HTML snippets, compile and return a compressed JSON representation containing the relevant schema components:

```json
{
  "feature_context": "authentication",
  "forms": [
    {
      "action": "/session",
      "method": "POST",
      "signals": ["password_field", "session_endpoint"]
    }
  ],
  "hidden_fields": ["_csrf"],
  "detected_endpoints": ["/api/auth"]
}
```

---

## New Evaluation Metric: Security Element Recall

Track the fraction of critical security elements that survived context reduction:

$$\text{Recall} = \frac{\text{Security Elements Retrieved}}{\text{Security Elements Present}}$$
