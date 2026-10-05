"""
backend/agents/efficient_fetch/efficient_fetch_worker.py

Phase 5 worker — wraps EfficientFetchService and returns a WorkerResponse.

Responsibilities
----------------
* Accept a Task with action="RUN_EFFICIENT_FETCH"
* Read source_text and query_hint from task.context
* Call efficient_fetch()
* Return a WorkerResponse that conforms to contracts.md

Out of scope
------------
* No security analysis
* No findings
* No LLM calls
"""
from __future__ import annotations

from backend.models.task import Task
from backend.models.worker_response import WorkerResponse
from backend.services.efficient_fetch import efficient_fetch
from backend.services.logger import get_logger

logger = get_logger(__name__)

_WORKER_NAME = "efficient_fetch_worker"


class EfficientFetchWorker:
    """Executes RUN_EFFICIENT_FETCH tasks and returns a WorkerResponse."""

    async def execute(self, task: Task) -> WorkerResponse:
        """
        Run the Efficient Fetch Service for the given task.

        Expects task.context to contain:
            source_text  (str) – raw text to compress
            query_hint   (str) – what the future agent is interested in

        Returns
        -------
        WorkerResponse
            status="success" with EfficientFetchResult fields in data, or
            status="failure" with error details if an exception is raised.
        """
        source_text: str = task.context.get("source_text", "")
        query_hint: str = task.context.get("query_hint", "security relevant features")

        try:
            result = efficient_fetch(source_text, query_hint)
            logger.info(
                "EfficientFetchWorker succeeded - naive=%d efficient=%d task_id=%s",
                result.token_count_naive,
                result.token_count_efficient,
                task.task_id,
            )
            return WorkerResponse(
                status="success",
                worker=_WORKER_NAME,
                task_id=task.task_id,
                data={
                    "structured_content": result.structured_content,
                    "token_count_naive": result.token_count_naive,
                    "token_count_efficient": result.token_count_efficient,
                },
                new_findings=[],
                errors=[],
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "EfficientFetchWorker failed - task_id=%s error=%s",
                task.task_id,
                exc,
            )
            return WorkerResponse(
                status="failure",
                worker=_WORKER_NAME,
                task_id=task.task_id,
                data={},
                new_findings=[],
                errors=[
                    {
                        "error_type": "EFFICIENT_FETCH_ERROR",
                        "message": str(exc),
                    }
                ],
            )
