import asyncio

import pytest

from backend.agents.feature_extraction.feature_extraction_agent import FeatureExtractionAgent, GroqChatClient
from backend.config import ConfigurationError
from backend.models.form import Form
from backend.models.recon_result import ReconResult
from backend.models.task import Task


class StubLLMClient:
    def __init__(self, response: str) -> None:
        self._response = response

    def complete(self, prompt: str) -> str:
        return self._response


def make_task(recon_result: ReconResult) -> Task:
    return Task(
        task_id="TASK-002",
        action="EXTRACT_FEATURES",
        target=recon_result.url,
        context={"recon_result": recon_result.model_dump()},
        priority="high",
    )


class TestFeatureExtractionAgent:
    def test_authentication_classification(self) -> None:
        recon_result = ReconResult(
            url="https://example.com/login",
            forms=[Form(action="/login", method="POST")],
            inputs=["username", "password"],
            buttons=["Login"],
            links=["/register"],
        )
        agent = FeatureExtractionAgent(llm_client=StubLLMClient('{"feature":"authentication","confidence":0.96}'))

        response = asyncio.run(agent.execute(make_task(recon_result)))

        assert response.status == "success"
        assert response.worker == "feature_extraction"
        assert response.data["name"] == "authentication"
        assert response.data["classification_confidence"] == 0.96
        assert response.data["routes"] == ["https://example.com/login"]

    def test_search_classification(self) -> None:
        recon_result = ReconResult(
            url="https://example.com/search",
            forms=[Form(action="/search", method="GET")],
            inputs=["q"],
            buttons=["Search"],
        )
        agent = FeatureExtractionAgent(llm_client=StubLLMClient('{"feature":"search","confidence":0.91}'))

        response = asyncio.run(agent.execute(make_task(recon_result)))

        assert response.status == "success"
        assert response.data["name"] == "search"

    def test_upload_classification(self) -> None:
        recon_result = ReconResult(
            url="https://example.com/upload",
            forms=[Form(action="/upload", method="POST")],
            inputs=["file"],
            buttons=["Upload"],
        )
        agent = FeatureExtractionAgent(llm_client=StubLLMClient('{"feature":"file_upload","confidence":0.88}'))

        response = asyncio.run(agent.execute(make_task(recon_result)))

        assert response.status == "success"
        assert response.data["name"] == "file_upload"

    def test_unknown_classification(self) -> None:
        recon_result = ReconResult(
            url="https://example.com/misc",
            forms=[],
            inputs=["token"],
            buttons=["Continue"],
            links=["/next"],
        )
        agent = FeatureExtractionAgent(llm_client=StubLLMClient('{"feature":"unknown","confidence":0.52}'))

        response = asyncio.run(agent.execute(make_task(recon_result)))

        assert response.status == "success"
        assert response.data["name"] == "unknown"

    def test_missing_groq_api_key_raises_configuration_error(self) -> None:
        with pytest.raises(ConfigurationError):
            GroqChatClient(api_key="", model="openai/gpt-oss-120b", base_url="https://api.groq.com/openai/v1")
