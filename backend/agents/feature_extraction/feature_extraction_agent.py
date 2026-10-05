"""
backend/agents/feature_extraction/feature_extraction_agent.py

Phase 3 Feature Extraction Agent.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from openai import OpenAI

from backend.config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODEL,
    GROQ_PROVIDER_NAME,
    ConfigurationError,
    validate_groq_config,
)
from backend.models.feature import Feature, FeatureName
from backend.models.recon_result import ReconResult
from backend.models.task import Task
from backend.models.worker_response import WorkerError, WorkerResponse
from backend.services.logger import get_logger

logger = get_logger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "feature_classification_prompt.txt"
_ALLOWED_FEATURES: set[str] = {
    "authentication",
    "registration",
    "password_reset",
    "search",
    "file_upload",
    "api",
    "user_profile",
    "admin_panel",
    "dashboard",
    "settings",
    "unknown",
}


class FeatureClassificationClient(Protocol):
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
            "Configured LLM provider - provider=%s model=%s endpoint=%s",
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
                    "content": "You classify application functionality and return valid JSON only.",
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


class FeatureExtractionAgent:
    def __init__(
        self,
        llm_client: FeatureClassificationClient | None = None,
        prompt_path: Path | None = None,
    ) -> None:
        if llm_client is None:
            validate_groq_config()
        self._llm_client = llm_client or GroqChatClient()
        self._prompt_path = prompt_path or _PROMPT_PATH

    async def execute(self, task: Task) -> WorkerResponse:
        if task.task_id is None:
            raise ValueError("Task must have task_id before feature extraction execution")

        logger.info("FeatureExtractionAgent starting - task_id=%s target=%s", task.task_id, task.target)

        recon_payload = task.context.get("recon_result")
        if not isinstance(recon_payload, dict):
            return self._failure_response(
                task.task_id,
                WorkerError(
                    error_type="INVALID_TASK_CONTEXT",
                    message="Task context must include recon_result",
                ),
            )

        try:
            recon_result = ReconResult.model_validate(recon_payload)
            feature = self.classify(recon_result)
        except ValueError as exc:
            return self._failure_response(
                task.task_id,
                WorkerError(error_type="FEATURE_CLASSIFICATION_FAILED", message=str(exc)),
            )
        except Exception as exc:
            logger.exception("Unexpected feature extraction failure - task_id=%s", task.task_id)
            return self._failure_response(
                task.task_id,
                WorkerError(error_type="FEATURE_EXTRACTION_FAILURE", message=self._safe_message(exc)),
            )

        logger.info(
            "FeatureExtractionAgent complete - task_id=%s feature=%s confidence=%.2f",
            task.task_id,
            feature.name,
            feature.classification_confidence,
        )
        return WorkerResponse(
            status="success",
            worker="feature_extraction",
            task_id=task.task_id,
            data=feature.model_dump(),
            new_findings=[],
            errors=[],
        )

    def classify(self, recon_result: ReconResult) -> Feature:
        prompt = self._build_prompt(recon_result)
        raw_response = self._llm_client.complete(prompt)
        response_data = self._parse_llm_response(raw_response)

        return Feature(
            name=response_data["feature"],
            routes=[recon_result.url],
            classification_confidence=response_data["confidence"],
            analyzed=False,
        )

    def _build_prompt(self, recon_result: ReconResult) -> str:
        template = self._prompt_path.read_text(encoding="utf-8")
        meta_list = [
            m if isinstance(m, dict) else m.model_dump()
            for m in (recon_result.meta_tags or [])
        ]
        form_list = [
            form.model_dump() if hasattr(form, "model_dump") else form
            for form in (recon_result.forms or [])
        ]
        observations = json.dumps(
            {
                "route": recon_result.url,
                "forms": form_list[:15],
                "inputs": (recon_result.inputs or [])[:30],
                "buttons": (recon_result.buttons or [])[:20],
                "links": (recon_result.links or [])[:30],
                "meta_tags": meta_list[:10],
            },
            indent=2,
        )
        return template.replace("{{RECON_OBSERVATIONS}}", observations)

    def _parse_llm_response(self, raw_response: str) -> dict[str, FeatureName | float]:
        text = raw_response.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM response was not valid JSON") from exc

        feature = parsed.get("feature")
        confidence = parsed.get("confidence")

        if feature not in _ALLOWED_FEATURES:
            raise ValueError("LLM response returned an unsupported feature type")

        if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            raise ValueError("LLM response returned an invalid confidence value")

        return {
            "feature": feature,
            "confidence": float(confidence),
        }

    def _failure_response(self, task_id: str, error_obj: WorkerError) -> WorkerResponse:
        logger.warning("FeatureExtractionAgent failure - task_id=%s error_type=%s", task_id, error_obj.error_type)
        return WorkerResponse(
            status="failure",
            worker="feature_extraction",
            task_id=task_id,
            data={},
            new_findings=[],
            errors=[error_obj],
        )

    def _safe_message(self, exc: Exception) -> str:
        message = str(exc).strip()
        return message or "Feature extraction failed"
