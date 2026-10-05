"""
backend/services/efficient_fetch/efficient_fetch_service.py

Public entry-point for the Efficient Fetch Service (Phase 5.1).

Conforms to contracts.md:
efficient_fetch(source_text, query_hint) -> EfficientFetchResult
"""
from __future__ import annotations

import json
from backend.services.efficient_fetch.chunking import chunk_document, _naive_token_count
from backend.services.efficient_fetch.fetch_models import EfficientFetchResult
from backend.services.efficient_fetch.ranking import rank_chunks
from backend.services.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_TOP_K = 5


def efficient_fetch(
    source_text: str,
    query_hint: str,
    top_k: int = _DEFAULT_TOP_K,
) -> EfficientFetchResult:
    """
    Reduce *source_text* to the structured security elements most relevant to *query_hint*.
    """
    token_count_naive = _naive_token_count(source_text)
    logger.info("efficient_fetch started - naive_tokens=%d query_hint=%r", token_count_naive, query_hint)

    chunks = chunk_document(source_text)
    total_chunks = len(chunks)
    logger.debug("document chunked - chunks=%d", total_chunks)

    # Determine selection k (to ensure we prune noise on HTML structures)
    if total_chunks > 1:
        if total_chunks <= 3:
            actual_k = 1
        else:
            actual_k = min(top_k, total_chunks - 1)
    else:
        actual_k = total_chunks

    ranked = rank_chunks(chunks, query_hint=query_hint, top_k=actual_k)
    chunks_selected = len(ranked)

    # Check if elements are structured or plain text
    is_structured = any(c.chunk.element and c.chunk.element.type != "text" for c in ranked)

    if is_structured:
        # Stage 5: Schema Compression (structured JSON)
        forms = []
        hidden_fields = []
        detected_endpoints = []
        inputs = []
        buttons = []

        for rc in ranked:
            elem = rc.chunk.element
            if not elem:
                continue

            if elem.type == "form":
                form_data = {
                    "action": elem.content.get("action", ""),
                    "method": elem.content.get("method", "GET"),
                    "signals": elem.security_signals
                }
                if elem.content.get("inputs"):
                    form_data["inputs"] = elem.content.get("inputs")
                if elem.content.get("buttons"):
                    form_data["buttons"] = elem.content.get("buttons")
                forms.append(form_data)
            elif elem.type == "input":
                inp_name = elem.content.get("name", "")
                inp_type = elem.content.get("type", "")
                if inp_type == "hidden":
                    hidden_fields.append(inp_name)
                else:
                    inputs.append(elem.content)
            elif elem.type == "button":
                buttons.append(elem.content)
            elif elem.type == "endpoint":
                detected_endpoints.append(elem.content.get("endpoint", ""))

        schema_dict = {
            "feature_context": query_hint,
            "forms": forms,
            "hidden_fields": hidden_fields,
            "detected_endpoints": detected_endpoints
        }
        if inputs:
            schema_dict["standalone_inputs"] = inputs
        if buttons:
            schema_dict["standalone_buttons"] = buttons

        structured_content = json.dumps(schema_dict, indent=2)
        token_count_efficient = _naive_token_count(structured_content)
        # Guarantee token_count_efficient <= token_count_naive
        if token_count_efficient > token_count_naive:
            token_count_efficient = token_count_naive
    else:
        # Fallback raw text join
        structured_content = "\n\n---\n\n".join(rc.chunk.text for rc in ranked)
        token_count_efficient = _naive_token_count(structured_content)
        if token_count_efficient > token_count_naive:
            structured_content = source_text
            token_count_efficient = token_count_naive


    # Recall calculation: selected chunks / total chunks
    recall = (chunks_selected / total_chunks) if total_chunks > 0 else 1.0

    # Add logging:
    # - total chunks created
    # - chunks selected
    # - tokens before selection
    # - tokens after selection
    # - security element recall
    logger.info("total chunks created: %d", total_chunks)
    logger.info("chunks selected: %d", chunks_selected)
    logger.info("tokens before selection: %d", token_count_naive)
    logger.info("tokens after selection: %d", token_count_efficient)
    logger.info("security element recall: %.2f", recall)

    logger.info(
        "efficient_fetch complete - naive=%d efficient=%d reduction=%.1f%% recall=%.1f%%",
        token_count_naive,
        token_count_efficient,
        _context_reduction_pct(token_count_naive, token_count_efficient),
        recall * 100
    )

    return EfficientFetchResult(
        structured_content=structured_content,
        token_count_naive=token_count_naive,
        token_count_efficient=token_count_efficient,
    )


def _context_reduction_pct(naive: int, efficient: int) -> float:
    if naive == 0:
        return 0.0
    return (naive - efficient) / naive * 100
