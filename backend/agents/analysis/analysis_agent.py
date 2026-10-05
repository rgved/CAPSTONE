"""
backend/agents/analysis/analysis_agent.py

Phase 6 Analysis Agent.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Protocol

from openai import OpenAI

from backend.config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODEL,
    GROQ_PROVIDER_NAME,
    ConfigurationError,
    validate_groq_config,
)
from backend.models.feature import Feature
from backend.models.finding import Finding, FindingCategory, FindingSeverity
from backend.models.recon_result import ReconResult
from backend.models.task import Task
from backend.models.worker_response import WorkerError, WorkerResponse
from backend.services.logger import get_logger

logger = get_logger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "analysis_prompt.txt"
_ALLOWED_CATEGORIES: set[str] = {
    "missing_csrf",
    "weak_authentication",
    "exposed_endpoint",
    "file_upload_risk",
    "missing_security_headers",
    "admin_surface",
    "sensitive_input",
    "unknown",
}
_ALLOWED_SEVERITIES: set[str] = {"informational", "low", "medium", "high"}
_FINDING_THRESHOLD = 0.70


class AnalysisClient(Protocol):
    def complete(self, prompt: str) -> str:
        """Return the raw JSON string from the provider."""


class GroqChatClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self._api_key = GROQ_API_KEY if api_key is None else api_key
        self._model = GROQ_MODEL if model is None else model
        self._base_url = (GROQ_BASE_URL if base_url is None else base_url).rstrip("/")
        self._provider_name = GROQ_PROVIDER_NAME

        if not self._api_key:
            raise ConfigurationError("GROQ_API_KEY is not configured")

        logger.info(
            "Configured analysis LLM provider - provider=%s model=%s endpoint=%s",
            self._provider_name,
            self._model,
            self._base_url,
        )
        self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)

    def complete(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "You analyze security evidence and return valid JSON only.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        message_content = response.choices[0].message.content
        if not message_content:
            raise RuntimeError("LLM response did not include chat completion content")
        return message_content


_SECURITY_HEADER_KEYS: set[str] = {
    "content-security-policy",
    "content-security-policy-report-only",
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "x-xss-protection",
    "access-control-allow-origin",
    "access-control-allow-credentials",
    "access-control-allow-methods",
    "access-control-allow-headers",
    "referrer-policy",
    "permissions-policy",
    "feature-policy",
    "x-permitted-cross-domain-policies",
    "cross-origin-embedder-policy",
    "cross-origin-opener-policy",
    "cross-origin-resource-policy",
    "server",
    "x-powered-by",
    "content-type",
    "location",
    "set-cookie",
}


def _filter_security_headers(headers: dict[str, Any] | None) -> dict[str, Any]:
    if not headers or not isinstance(headers, dict):
        return {}
    if len(headers) <= 5:
        return headers
    filtered = {k: v for k, v in headers.items() if str(k).lower() in _SECURITY_HEADER_KEYS}
    return filtered if filtered else headers


class AnalysisAgent:
    def __init__(
        self,
        llm_client: AnalysisClient | None = None,
        prompt_path: Path | None = None,
    ) -> None:
        if llm_client is None:
            validate_groq_config()
        self._llm_client = llm_client or GroqChatClient()
        self._prompt_path = prompt_path or _PROMPT_PATH

    async def execute(self, task: Task) -> WorkerResponse:
        if task.task_id is None:
            raise ValueError("Task must have task_id before analysis execution")

        logger.info("AnalysisAgent starting - task_id=%s target=%s", task.task_id, task.target)

        try:
            feature = self._parse_feature(task.context.get("feature"))
            recon_result = self._parse_recon_result(task.context.get("recon_result"))
            efficient_fetch_result = self._parse_mapping(task.context.get("efficient_fetch_result"), "efficient_fetch_result")
            semantic_context = self._parse_semantic_context(task.context.get("semantic_context"))
        except ValueError as exc:
            return self._failure_response(
                task.task_id,
                WorkerError(error_type="INVALID_TASK_CONTEXT", message=str(exc)),
            )

        try:
            evidence_package = self._build_evidence_package(
                feature=feature,
                recon_result=recon_result,
                efficient_fetch_result=efficient_fetch_result,
                semantic_context=semantic_context,
            )
            raw_response = self._llm_client.complete(self._build_prompt(evidence_package))
            analysis = self._parse_llm_response(raw_response)
            route_id = self._parse_optional_int(task.context.get("route_id"))
            finding = self._build_finding(analysis, feature, route_id)
        except ValueError as exc:
            return self._failure_response(
                task.task_id,
                WorkerError(error_type="ANALYSIS_FAILED", message=str(exc)),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected analysis failure - task_id=%s", task.task_id)
            return self._failure_response(
                task.task_id,
                WorkerError(error_type="ANALYSIS_FAILURE", message=self._safe_message(exc)),
            )

        new_findings: list[dict[str, Any]] = []
        persisted = False
        if finding.security_confidence >= _FINDING_THRESHOLD:
            new_findings.append(finding.model_dump())
            persisted = True

        logger.info(
            "AnalysisAgent complete - task_id=%s category=%s confidence=%.2f persisted=%s",
            task.task_id,
            finding.type,
            finding.security_confidence,
            persisted,
        )
        return WorkerResponse(
            status="success",
            worker="analysis",
            task_id=task.task_id,
            data={
                "analysis": analysis,
                "evidence_package": evidence_package,
                "persisted": persisted,
            },
            new_findings=new_findings,
            errors=[],
        )

    def _build_prompt(self, evidence_package: dict[str, Any]) -> str:
        template = self._prompt_path.read_text(encoding="utf-8")
        return template.replace("{{EVIDENCE_PACKAGE}}", json.dumps(evidence_package, indent=2))

    def _build_evidence_package(
        self,
        feature: Feature,
        recon_result: ReconResult,
        efficient_fetch_result: dict[str, Any],
        semantic_context: dict[str, Any],
    ) -> dict[str, Any]:
        retrieved_context: list[dict[str, Any]] = []

        for route in semantic_context.get("similar_routes", []):
            retrieved_context.append({"kind": "route", "data": route})

        for previous_feature in semantic_context.get("similar_features", []):
            retrieved_context.append({"kind": "feature", "data": previous_feature})

        for finding in semantic_context.get("previous_findings", []):
            retrieved_context.append({"kind": "finding", "data": finding})

        headers = _filter_security_headers(recon_result.headers)

        package: dict[str, Any] = {
            "feature": feature.name,
            "routes": feature.routes or [recon_result.url],
            "status_code": recon_result.status_code,
            "headers": headers,
            "retrieved_context": retrieved_context[:5],
        }

        # Check if efficient_fetch provided compact structured content
        structured_content = ""
        if isinstance(efficient_fetch_result, dict):
            structured_content = efficient_fetch_result.get("structured_content", "")

        if structured_content:
            # Efficient fetch content is available: avoid duplicating raw recon structures
            try:
                parsed_structure = json.loads(structured_content)
                if isinstance(parsed_structure, dict):
                    # Merge structured forms, hidden fields, endpoints, standalone inputs/buttons
                    for key, val in parsed_structure.items():
                        if key != "feature_context" and val:
                            package[key] = val
                else:
                    package["structured_content"] = structured_content
            except (json.JSONDecodeError, TypeError):
                package["structured_content"] = structured_content
        else:
            # Fallback when efficient fetch is absent (e.g. legacy tasks or test stubs)
            package["forms"] = [form.model_dump() for form in recon_result.forms]
            package["inputs"] = recon_result.inputs[:30] if recon_result.inputs else []
            package["input_fields"] = recon_result.input_fields[:20] if recon_result.input_fields else []
            if recon_result.comments:
                package["comments"] = [c[:300] for c in recon_result.comments[:5]]
            if recon_result.inline_scripts:
                package["inline_scripts"] = [s[:400] for s in recon_result.inline_scripts[:3]]

        return package

    def _parse_llm_response(self, raw_response: str) -> dict[str, Any]:
        parsed = self._load_json(raw_response)

        category = parsed.get("finding_category")
        title = parsed.get("title")
        description = parsed.get("description")
        reasoning = parsed.get("reasoning", "")
        severity = parsed.get("severity")
        confidence = parsed.get("confidence")
        evidence = parsed.get("evidence")

        if category not in _ALLOWED_CATEGORIES:
            raise ValueError("LLM response returned an unsupported finding category")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("LLM response returned an invalid title")
        if not isinstance(description, str):
            raise ValueError("LLM response returned an invalid description")
        if not isinstance(reasoning, str):
            reasoning = str(reasoning)
        if severity not in _ALLOWED_SEVERITIES:
            raise ValueError("LLM response returned an invalid severity")
        if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            raise ValueError("LLM response returned an invalid confidence value")
        if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
            raise ValueError("LLM response returned invalid evidence")

        return {
            "finding_category": category,
            "title": title.strip(),
            "description": description.strip(),
            "reasoning": reasoning.strip(),
            "severity": severity,
            "confidence": float(confidence),
            "evidence": [item.strip() for item in evidence if item.strip()],
        }

    def _build_finding(
        self,
        analysis: dict[str, Any],
        feature: Feature,
        route_id: int | None,
    ) -> Finding:
        return Finding(
            type=analysis["finding_category"],
            title=analysis["title"],
            feature=feature.name,
            severity=analysis["severity"],
            security_confidence=analysis["confidence"],
            evidence=analysis["evidence"],
            description=analysis["description"],
            reasoning=analysis.get("reasoning", ""),
            route_id=route_id,
        )

    def _parse_feature(self, value: Any) -> Feature:
        mapping = self._parse_mapping(value, "feature")
        return Feature.model_validate(mapping)

    def _parse_recon_result(self, value: Any) -> ReconResult:
        mapping = self._parse_mapping(value, "recon_result")
        return ReconResult.model_validate(mapping)

    def _parse_semantic_context(self, value: Any) -> dict[str, Any]:
        mapping = self._parse_mapping(value, "semantic_context", allow_empty=True)
        return {
            "similar_routes": self._ensure_list(mapping.get("similar_routes")),
            "similar_features": self._ensure_list(mapping.get("similar_features")),
            "previous_findings": self._ensure_list(mapping.get("previous_findings")),
        }

    def _parse_optional_int(self, value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    def _parse_mapping(self, value: Any, field_name: str, allow_empty: bool = False) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if allow_empty and value is None:
            return {}
        if hasattr(value, "model_dump"):
            return value.model_dump()
        raise ValueError(f"Task context must include {field_name}")

    def _ensure_list(self, value: Any) -> list[dict[str, Any]]:
        if value is None:
            return []
        if not isinstance(value, list):
            return []
        items: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                items.append(item)
            elif hasattr(item, "model_dump"):
                items.append(item.model_dump())
        return items

    def _load_json(self, raw_response: str) -> dict[str, Any]:
        candidate = raw_response.strip()
        if candidate.startswith("```"):
            candidate = self._strip_fence(candidate)
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM response was not valid JSON") from exc
        if not isinstance(parsed, dict):
            raise ValueError("LLM response must be a JSON object")
        return parsed

    def _strip_fence(self, text: str) -> str:
        fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            return fenced.group(1)
        return text

    def _failure_response(self, task_id: str, error_obj: WorkerError) -> WorkerResponse:
        logger.warning("AnalysisAgent failure - task_id=%s error_type=%s", task_id, error_obj.error_type)
        return WorkerResponse(
            status="failure",
            worker="analysis",
            task_id=task_id,
            data={},
            new_findings=[],
            errors=[error_obj],
        )

    def _safe_message(self, exc: Exception) -> str:
        message = str(exc).strip()
        return message or "Analysis failed"
