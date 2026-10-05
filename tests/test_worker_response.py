from backend.models.worker_response import WorkerError, WorkerResponse


class TestWorkerResponse:
    def test_success_response_matches_contract(self) -> None:
        response = WorkerResponse(
            status="success",
            worker="recon",
            task_id="TASK-001",
            data={"url": "https://example.com"},
            new_findings=[],
            errors=[],
        )
        assert response.status == "success"
        assert response.worker == "recon"
        assert response.task_id == "TASK-001"
        assert response.data["url"] == "https://example.com"
        assert response.new_findings == []
        assert response.errors == []

    def test_failure_response_matches_contract(self) -> None:
        response = WorkerResponse(
            status="failure",
            worker="dispatcher",
            task_id="TASK-002",
            data={},
            new_findings=[],
            errors=[WorkerError(error_type="UNSUPPORTED_ACTION", message="Unsupported action: STOP")],
        )
        assert response.status == "failure"
        assert response.errors[0].error_type == "UNSUPPORTED_ACTION"
        assert response.errors[0].message == "Unsupported action: STOP"

    def test_defaults_for_optional_collections(self) -> None:
        response = WorkerResponse(status="success", worker="recon", task_id="TASK-003")
        assert response.data == {}
        assert response.new_findings == []
        assert response.errors == []
