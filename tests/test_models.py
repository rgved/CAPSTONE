"""
tests/test_models.py

Unit tests verifying that all Pydantic models conform to their contracts.

Contract source: docs/contracts.md

Coverage (docs/phases/phase1.md — Unit Testing / Recon Result):
  - Route: field presence, optionality of route_id
  - Form: valid methods, default method, rejection of invalid methods
  - ReconResult: all contract fields present, correct defaults, field types
  - Task: field presence, default values, valid priorities
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.models.route import Route
from backend.models.coverage_state import CoverageState
from backend.models.feature import Feature
from backend.models.form import Form
from backend.models.recon_result import ReconResult
from backend.models.task import Task
from backend.models.worker_response import WorkerError, WorkerResponse


# ── Route (contracts.md §3) ───────────────────────────────────────────────────

class TestRouteModel:
    def test_route_id_is_none_before_save(self) -> None:
        route = Route(url="/login", discovered_at=datetime.now(timezone.utc))
        assert route.route_id is None

    def test_route_id_accepts_integer(self) -> None:
        route = Route(route_id=42, url="/login", discovered_at=datetime.now(timezone.utc))
        assert route.route_id == 42

    def test_url_field_required(self) -> None:
        with pytest.raises(ValidationError):
            Route(discovered_at=datetime.now(timezone.utc))  # type: ignore[call-arg]

    def test_discovered_at_field_required(self) -> None:
        with pytest.raises(ValidationError):
            Route(url="/login")  # type: ignore[call-arg]

    def test_url_value_stored_correctly(self) -> None:
        route = Route(url="https://example.com/admin", discovered_at=datetime.now(timezone.utc))
        assert route.url == "https://example.com/admin"


# ── Form (contracts.md §4) ────────────────────────────────────────────────────

class TestFormModel:
    def test_post_method_accepted(self) -> None:
        form = Form(action="/login", method="POST")
        assert form.method == "POST"

    def test_get_method_accepted(self) -> None:
        form = Form(action="/search", method="GET")
        assert form.method == "GET"

    def test_put_method_accepted(self) -> None:
        form = Form(action="/resource", method="PUT")
        assert form.method == "PUT"

    def test_delete_method_accepted(self) -> None:
        form = Form(action="/resource", method="DELETE")
        assert form.method == "DELETE"

    def test_unknown_method_accepted(self) -> None:
        form = Form(action="/upload", method="UNKNOWN")
        assert form.method == "UNKNOWN"

    def test_default_method_is_get(self) -> None:
        form = Form(action="/search")
        assert form.method == "GET"

    def test_invalid_method_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Form(action="/upload", method="PATCH")

    def test_action_field_required(self) -> None:
        with pytest.raises(ValidationError):
            Form()  # type: ignore[call-arg]


# ── ReconResult (contracts.md §5) ────────────────────────────────────────────

class TestReconResultModel:
    def test_all_contract_fields_present(self) -> None:
        """Verify every field from contracts.md §5 exists on the model."""
        result = ReconResult(url="https://example.com")
        assert hasattr(result, "url")
        assert hasattr(result, "forms")
        assert hasattr(result, "inputs")
        assert hasattr(result, "buttons")
        assert hasattr(result, "links")
        assert hasattr(result, "scripts")
        assert hasattr(result, "meta_tags")

    def test_url_field_required(self) -> None:
        with pytest.raises(ValidationError):
            ReconResult()  # type: ignore[call-arg]

    def test_all_list_fields_default_to_empty(self) -> None:
        result = ReconResult(url="https://example.com")
        assert result.forms == []
        assert result.inputs == []
        assert result.buttons == []
        assert result.links == []
        assert result.scripts == []
        assert result.meta_tags == []

    def test_forms_accept_form_objects(self) -> None:
        result = ReconResult(
            url="/login",
            forms=[Form(action="/login", method="POST")],
        )
        assert len(result.forms) == 1
        assert result.forms[0].action == "/login"

    def test_full_contract_example(self) -> None:
        """Reproduce the exact example from contracts.md §5."""
        result = ReconResult(
            url="/login",
            forms=[Form(action="/login", method="POST")],
            inputs=["username", "password"],
            buttons=["Login"],
            links=["/register"],
            scripts=[],
            meta_tags=[],
        )
        assert result.url == "/login"
        assert len(result.forms) == 1
        assert result.inputs == ["username", "password"]
        assert result.buttons == ["Login"]
        assert result.links == ["/register"]
        assert result.scripts == []
        assert result.meta_tags == []

    def test_list_fields_are_independent_instances(self) -> None:
        """
        Ensure list defaults are not shared across instances
        (guards against mutable default anti-pattern).
        """
        r1 = ReconResult(url="https://a.com")
        r2 = ReconResult(url="https://b.com")
        r1.inputs.append("email")
        assert "email" not in r2.inputs


# ── Task (contracts.md §1) ────────────────────────────────────────────────────

class TestTaskModel:
    def test_task_id_is_none_before_save(self) -> None:
        task = Task(action="RUN_RECON", target="https://example.com")
        assert task.task_id is None

    def test_task_id_accepts_contract_string(self) -> None:
        task = Task(task_id="TASK-001", action="RUN_RECON", target="https://example.com")
        assert task.task_id == "TASK-001"

    def test_required_fields(self) -> None:
        task = Task(action="RUN_RECON", target="https://example.com")
        assert task.action == "RUN_RECON"
        assert task.target == "https://example.com"

    def test_default_priority_is_medium(self) -> None:
        task = Task(action="RUN_RECON", target="https://example.com")
        assert task.priority == "medium"

    def test_high_priority_accepted(self) -> None:
        task = Task(action="RUN_RECON", target="https://example.com", priority="high")
        assert task.priority == "high"

    def test_invalid_priority_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Task(action="RUN_RECON", target="https://example.com", priority="critical")

    def test_default_status_is_pending(self) -> None:
        task = Task(action="RUN_RECON", target="https://example.com")
        assert task.status == "pending"

    def test_context_defaults_to_empty_dict(self) -> None:
        task = Task(action="RUN_RECON", target="https://example.com")
        assert task.context == {}

    def test_created_at_auto_populated(self) -> None:
        task = Task(action="RUN_RECON", target="https://example.com")
        assert isinstance(task.created_at, datetime)

    def test_action_required(self) -> None:
        with pytest.raises(ValidationError):
            Task(target="https://example.com")  # type: ignore[call-arg]


class TestCoverageStateModel:
    def test_default_recon_completed_is_false(self) -> None:
        coverage = CoverageState()
        assert coverage.recon_completed is False


class TestFeatureModel:
    def test_feature_contract_fields_present(self) -> None:
        feature = Feature(name="authentication", routes=["/login"], classification_confidence=0.96)
        assert feature.feature_id is None
        assert feature.name == "authentication"
        assert feature.routes == ["/login"]
        assert feature.classification_confidence == 0.96
        assert feature.analyzed is False

    def test_invalid_feature_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Feature(name="login", routes=["/login"], classification_confidence=0.80)  # type: ignore[arg-type]

    def test_confidence_must_be_between_zero_and_one(self) -> None:
        with pytest.raises(ValidationError):
            Feature(name="authentication", routes=["/login"], classification_confidence=1.5)


class TestWorkerResponseModel:
    def test_success_response_contract_fields_present(self) -> None:
        response = WorkerResponse(status="success", worker="recon", task_id="TASK-001")
        assert response.status == "success"
        assert response.worker == "recon"
        assert response.task_id == "TASK-001"
        assert response.data == {}
        assert response.new_findings == []
        assert response.errors == []

    def test_failure_response_accepts_structured_errors(self) -> None:
        response = WorkerResponse(
            status="failure",
            worker="recon",
            task_id="TASK-001",
            errors=[WorkerError(error_type="REQUEST_TIMEOUT", message="Request timed out")],
        )
        assert response.errors[0].error_type == "REQUEST_TIMEOUT"
        assert response.errors[0].message == "Request timed out"
