"""
tests/test_risk_scorer.py

Unit tests for the Risk Scoring Engine (Feature #3).
"""
from datetime import datetime, timezone
import pytest
from backend.models.route import Route
from backend.services.risk_scorer import (
    calculate_endpoint_risk,
    prioritize_routes,
)


def test_critical_endpoint_risk_scoring() -> None:
    # Test high-sensitivity endpoints: login, admin, user api
    login_risk = calculate_endpoint_risk("https://example.com/login", forms_count=1, has_post_method=True, inputs_count=2, depth=1)
    admin_risk = calculate_endpoint_risk("https://example.com/admin/dashboard", forms_count=0, depth=1)
    user_api_risk = calculate_endpoint_risk("https://example.com/api/v1/users", depth=1)

    assert login_risk.risk_score >= 8.5
    assert login_risk.priority in {"critical", "high"}
    assert login_risk.sensitivity >= 3.0
    assert login_risk.reason == "Authentication Boundary"

    assert admin_risk.risk_score >= 6.5
    assert admin_risk.sensitivity >= 3.0
    assert admin_risk.reason == "Administrative Interface"

    assert user_api_risk.risk_score >= 6.5
    assert user_api_risk.sensitivity >= 3.0


def test_medium_endpoint_risk_scoring() -> None:
    profile_risk = calculate_endpoint_risk("https://example.com/profile", forms_count=1, has_post_method=False, inputs_count=1, depth=1)
    search_risk = calculate_endpoint_risk("https://example.com/search", forms_count=1, depth=1)

    assert 4.0 <= profile_risk.risk_score <= 8.0
    assert profile_risk.priority in {"high", "medium"}
    assert profile_risk.reason == "User Profile / Account Area"

    assert 3.5 <= search_risk.risk_score <= 7.0
    assert search_risk.reason == "Search / Query Vector"


def test_low_sensitivity_endpoint_risk_scoring() -> None:
    faq_risk = calculate_endpoint_risk("https://example.com/faq", depth=1)
    about_risk = calculate_endpoint_risk("https://example.com/about-us", depth=1)
    static_risk = calculate_endpoint_risk("https://example.com/static/style.css", depth=2)

    assert faq_risk.risk_score <= 2.5
    assert faq_risk.priority == "low"
    assert faq_risk.reason == "Static FAQ / Help Page"

    assert about_risk.risk_score <= 2.5
    assert about_risk.priority == "low"

    assert static_risk.risk_score <= 1.5
    assert static_risk.priority == "low"


def test_exposure_and_reachability_adjustments() -> None:
    # POST form with inputs increases exposure
    base_risk = calculate_endpoint_risk("https://example.com/contact", depth=1)
    active_form_risk = calculate_endpoint_risk("https://example.com/contact", forms_count=2, has_post_method=True, inputs_count=4, depth=1)

    assert active_form_risk.exposure > base_risk.exposure
    assert active_form_risk.risk_score > base_risk.risk_score

    # Deeper URL reduces reachability slightly
    shallow_risk = calculate_endpoint_risk("https://example.com/settings", depth=1)
    deep_risk = calculate_endpoint_risk("https://example.com/a/b/c/d/settings", depth=5)

    assert deep_risk.reachability < shallow_risk.reachability


def test_prioritize_routes_sorting_and_deduplication() -> None:
    raw_urls = [
        "https://example.com/faq",
        "https://example.com/login",
        "https://example.com/about",
        "https://example.com/admin",
        "https://example.com/profile",
        "https://example.com/login",  # Duplicate
    ]

    prioritized = prioritize_routes(raw_urls)

    assert len(prioritized) == 5  # Duplicate removed
    # First item should be the highest risk (login or admin)
    assert prioritized[0].url in {"https://example.com/login", "https://example.com/admin"}
    # Last item should be low risk (faq or about)
    assert prioritized[-1].url in {"https://example.com/faq", "https://example.com/about"}

    # Verify descending sort
    scores = [p.risk_score for p in prioritized]
    assert scores == sorted(scores, reverse=True)


def test_prioritize_routes_with_route_objects_and_dicts() -> None:
    items = [
        Route(url="https://example.com/faq", discovered_at=datetime.now(timezone.utc)),
        {"url": "https://example.com/login", "forms": [{"method": "POST"}]},
        {"target": "https://example.com/dashboard", "forms": []},
    ]

    prioritized = prioritize_routes(items)
    assert len(prioritized) == 3
    assert prioritized[0].url == "https://example.com/login"
    assert prioritized[-1].url == "https://example.com/faq"


def test_java_spring_and_framework_endpoint_scoring() -> None:
    # Java Actuator
    actuator_env = calculate_endpoint_risk("https://example.com/actuator/env", depth=1)
    actuator_health = calculate_endpoint_risk("https://example.com/actuator/health", depth=1)
    # Swagger UI
    swagger = calculate_endpoint_risk("https://example.com/swagger-ui.html", depth=1)
    # WEB-INF
    web_inf = calculate_endpoint_risk("https://example.com/WEB-INF/web.xml", depth=1)
    # Java legacy routes
    login_jsp = calculate_endpoint_risk("https://example.com/login.jsp", forms_count=1, has_post_method=True, depth=1)
    admin_do = calculate_endpoint_risk("https://example.com/admin.do", depth=1)

    assert actuator_env.risk_score >= 7.0
    assert actuator_env.reason == "Spring Actuator Management Endpoint"

    assert actuator_health.risk_score >= 7.0
    assert actuator_health.reason == "Spring Actuator Management Endpoint"

    assert swagger.risk_score >= 6.5
    assert swagger.reason == "API Documentation & Schema Interface"

    assert web_inf.risk_score >= 7.0
    assert web_inf.reason == "Java Web Configuration (WEB-INF)"

    assert login_jsp.risk_score >= 8.5
    assert login_jsp.reason == "Authentication Boundary"

    assert admin_do.risk_score >= 6.5
    assert admin_do.reason == "Administrative Interface"


def test_react_spa_and_bundle_endpoint_scoring() -> None:
    api_v1 = calculate_endpoint_risk("https://example.com/api/v1/data", depth=1)
    react_chunk = calculate_endpoint_risk("https://example.com/_next/static/chunks/main.chunk.js", depth=2)
    manifest = calculate_endpoint_risk("https://example.com/manifest.json", depth=1)

    assert api_v1.risk_score >= 4.5
    assert api_v1.reason == "REST API Surface"

    assert react_chunk.risk_score <= 1.5
    assert react_chunk.priority == "low"
    assert react_chunk.reason == "React SPA Client Bundle"

    assert manifest.risk_score <= 2.5
    assert manifest.priority == "low"
    assert manifest.reason == "Web Application Manifest"

