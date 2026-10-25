"""
backend/services/risk_scorer.py

Risk Scoring Engine for Prioritized Scanning (Feature #3).

Formula:
    Risk = Exposure × Sensitivity × Reachability

Normalizes to a clean 0.0 - 10.0 scale:
    - High-value authentication/admin endpoints (e.g. /login, /admin, /api/v1/users) -> ~9.0 - 9.8
    - User/interactive profile endpoints (e.g. /profile, /settings, /dashboard) -> ~6.5 - 7.5
    - Informational/static endpoints (e.g. /faq, /about, /terms, static assets) -> ~0.5 - 2.0
"""
from __future__ import annotations

import re
from typing import Any, Literal
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, Field

from backend.models.route import Route


def normalize_url(base_url: str, link: str) -> str:
    """Resolve relative URLs against base_url and strip fragments."""
    if not link or link.startswith("javascript:") or link.startswith("mailto:") or link.startswith("tel:"):
        return ""
    joined = urljoin(base_url, link.strip())
    parsed = urlparse(joined)
    if parsed.scheme not in {"http", "https"}:
        return ""
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        clean_url += f"?{parsed.query}"
    return clean_url


def is_same_domain(base_url: str, target_url: str) -> bool:
    """Return True if target_url belongs to the same netloc/domain as base_url."""
    base_netloc = urlparse(base_url).netloc.lower()
    target_netloc = urlparse(target_url).netloc.lower()
    if not base_netloc or not target_netloc:
        return False
    return base_netloc == target_netloc


class EndpointRisk(BaseModel):
    url: str
    risk_score: float = Field(ge=0.0, le=10.0)
    priority: Literal["critical", "high", "medium", "low"]
    exposure: float
    sensitivity: float
    reachability: float
    reason: str


# High sensitivity patterns: admin, authentication, credentials, data management, file uploads, Java framework routes, interactive user forms
_CRITICAL_SENSITIVITY_PATTERNS: list[tuple[re.Pattern[str], float, str]] = [
    (re.compile(r"/(?:admin|administrator|cpanel|root|superadmin)(?:/|$|\.|\?)", re.IGNORECASE), 3.5, "Administrative Interface"),
    (re.compile(r"/(?:login|signin|auth|authenticate|oauth|token|jwt|session|sign-in|log-in)(?:/|$|\.|\?)", re.IGNORECASE), 3.4, "Authentication Boundary"),
    (re.compile(r"/(?:actuator)(?:/(?:env|health|metrics|beans|mappings|configprops|heapdump|threaddump|loggers|info)?)?(?:/|$|\.|\?)", re.IGNORECASE), 3.5, "Spring Actuator Management Endpoint"),
    (re.compile(r"(?:/WEB-INF/|WEB-INF)", re.IGNORECASE), 3.5, "Java Web Configuration (WEB-INF)"),
    (re.compile(r"/(?:swagger-ui(?:.html)?|swagger|v[23]/api-docs|api-docs|openapi\.json)(?:/|$|\.|\?)", re.IGNORECASE), 3.3, "API Documentation & Schema Interface"),
    (re.compile(r"/(?:register|signup|create-account|join|sign-up)(?:/|$|\.|\?)", re.IGNORECASE), 3.2, "User Registration Flow"),
    (re.compile(r"/(?:password|reset-password|forgot-password|change-password)(?:/|$|\.|\?)", re.IGNORECASE), 3.3, "Credential Recovery Boundary"),
    (re.compile(r"/api/(?:v\d+/)?(?:users?|accounts?|customers?|members?)(?:/|$|\.|\?)", re.IGNORECASE), 3.3, "User Data API"),
    (re.compile(r"/(?:comment|feedback|contact|messages?|inquiry|inquiries|support|customer-support)(?:/|$|\.|\?)", re.IGNORECASE), 3.0, "User Input / Contact Form Boundary"),
    (re.compile(r"/(?:upload|import|file-upload|attachment)(?:/|$|\.|\?)", re.IGNORECASE), 3.1, "File Ingestion Boundary"),
    (re.compile(r"/(?:checkout|payment|billing|stripe|order|invoice)(?:/|$|\.|\?)", re.IGNORECASE), 3.2, "Financial / Billing Boundary"),
    (re.compile(r"/(?:[\w-]+)\.(?:do|action|jsp)(?:/|$|\?)", re.IGNORECASE), 3.2, "Java Action/Servlet Controller"),
]

# Medium sensitivity patterns: dashboard, profile, search, settings, general APIs
_MEDIUM_SENSITIVITY_PATTERNS: list[tuple[re.Pattern[str], float, str]] = [
    (re.compile(r"/(?:profile|account|my-account|user-settings)(?:/|$|\.|\?)", re.IGNORECASE), 2.5, "User Profile / Account Area"),
    (re.compile(r"/(?:dashboard|console|panel|overview)(?:/|$|\.|\?)", re.IGNORECASE), 2.4, "User Dashboard"),
    (re.compile(r"/(?:settings|config|preferences)(?:/|$|\.|\?)", re.IGNORECASE), 2.3, "Configuration / Settings"),
    (re.compile(r"/api/(?:v\d+/)?", re.IGNORECASE), 2.3, "REST API Surface"),
    (re.compile(r"/(?:search|query|filter|find)(?:/|$|\.|\?)", re.IGNORECASE), 2.0, "Search / Query Vector"),
]

# Low sensitivity patterns: documentation, marketing, static informational pages, SPA bundles
_LOW_SENSITIVITY_PATTERNS: list[tuple[re.Pattern[str], float, str]] = [
    (re.compile(r"/(?:faq|frequently-asked-questions)(?:/|$|\.|\?)", re.IGNORECASE), 0.3, "Static FAQ / Help Page"),
    (re.compile(r"/(?:about|about-us|team|careers|jobs|press)(?:/|$|\.|\?)", re.IGNORECASE), 0.4, "Public Informational Page"),
    (re.compile(r"/(?:terms|privacy|legal|disclaimer|policy|tos|license)(?:/|$|\.|\?)", re.IGNORECASE), 0.3, "Legal / Policy Document"),
    (re.compile(r"(?:_next/static/|main(?:\.[a-f0-9]+)?\.chunk\.js|bundle\.js|\.chunk\.js)", re.IGNORECASE), 0.2, "React SPA Client Bundle"),
    (re.compile(r"/manifest\.json", re.IGNORECASE), 0.3, "Web Application Manifest"),
    (re.compile(r"\.(?:css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)(?:\?|$)", re.IGNORECASE), 0.2, "Static Asset"),
]

# Q4: Dangerous query parameter names that indicate high-risk input vectors.
# These boost exposure significantly beyond the generic +0.1 for any query string.
_DANGEROUS_PARAM_PATTERNS: list[tuple[re.Pattern[str], float, str]] = [
    (re.compile(r"(?:^|&)(?:redirect|return|next|url|callback|continue|dest|destination)=", re.IGNORECASE), 0.5, "Open Redirect Parameter"),
    (re.compile(r"(?:^|&)(?:file|path|dir|folder|include|template|page|view|load)=", re.IGNORECASE), 0.5, "Path Traversal / LFI Parameter"),
    (re.compile(r"(?:^|&)(?:cmd|exec|command|shell|run|eval|code)=", re.IGNORECASE), 0.6, "Command Injection Parameter"),
    (re.compile(r"(?:^|&)(?:sql|query|q|search|filter|where|order|sort)=", re.IGNORECASE), 0.3, "SQL / Search Injection Parameter"),
    (re.compile(r"(?:^|&)(?:token|key|secret|apikey|api_key|access_token|auth)=", re.IGNORECASE), 0.4, "Credential / Token Parameter"),
    (re.compile(r"(?:^|&)(?:id|user_id|account_id|uid|pid|item_id|record_id)=", re.IGNORECASE), 0.25, "IDOR Enumeration Parameter"),
]


def calculate_endpoint_risk(
    url: str,
    forms_count: int = 0,
    has_post_method: bool = False,
    inputs_count: int = 0,
    depth: int = 0,
) -> EndpointRisk:
    """
    Calculate the risk score of an endpoint using the formula:
        Risk = Exposure × Sensitivity × Reachability (scaled to 0.0 - 10.0)

    Parameters:
        url: Full URL or relative path of the endpoint.
        forms_count: Number of forms found on the page (if known).
        has_post_method: Whether any form uses POST/PUT state-changing methods.
        inputs_count: Number of inputs found on the page (if known).
        depth: Crawl depth from seed target (0 = root, 1 = 1 click away, etc.).
    """
    parsed = urlparse(url)
    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path

    # 1. Sensitivity Determination (0.2 to 3.5)
    sensitivity = 1.0
    reason = "General Web Endpoint"

    # Check high sensitivity patterns
    for pattern, score, label in _CRITICAL_SENSITIVITY_PATTERNS:
        if pattern.search(path) or (parsed.query and pattern.search(parsed.query)):
            sensitivity = score
            reason = label
            break
    else:
        # Check medium patterns
        for pattern, score, label in _MEDIUM_SENSITIVITY_PATTERNS:
            if pattern.search(path) or (parsed.query and pattern.search(parsed.query)):
                sensitivity = score
                reason = label
                break
        else:
            # Check low patterns
            for pattern, score, label in _LOW_SENSITIVITY_PATTERNS:
                if pattern.search(path):
                    sensitivity = score
                    reason = label
                    break

    # 2. Exposure Determination (0.5 to 1.5)
    # Factors: presence of forms, state-changing POST methods, input density, query parameters
    exposure = 1.0
    if has_post_method:
        exposure += 0.3
    if forms_count > 0:
        exposure += min(0.2, forms_count * 0.1)
    if inputs_count > 0:
        exposure += min(0.2, inputs_count * 0.05)

    # Q4: Dangerous query parameter names boost exposure based on attack vector severity.
    # Previously all query strings only got a flat +0.1; now specific risky param names
    # get a meaningful boost proportional to their actual attack surface.
    if parsed.query:
        dangerous_boost = 0.0
        dangerous_reason_suffix = ""
        for pattern, boost, label in _DANGEROUS_PARAM_PATTERNS:
            if pattern.search(parsed.query):
                if boost > dangerous_boost:
                    dangerous_boost = boost
                    dangerous_reason_suffix = f" [{label}]"
        if dangerous_boost > 0:
            exposure += dangerous_boost
            reason = reason + dangerous_reason_suffix
        else:
            exposure += 0.1  # generic query string bump

    # Static assets have lower exposure to dynamic vulnerability
    if any(path.endswith(ext) for ext in [".css", ".png", ".jpg", ".svg", ".ico", ".woff"]):
        exposure = 0.5

    exposure = max(0.5, min(1.5, exposure))

    # 3. Reachability Determination (0.5 to 1.0)
    # Direct seed or top-level route = 1.0, 1 click away = 0.95, deeper = 0.7 - 0.85
    if depth == 0 or path == "/":
        reachability = 1.0
    elif depth == 1:
        reachability = 0.95
    elif depth == 2:
        reachability = 0.85
    else:
        reachability = max(0.6, 1.0 - (depth * 0.1))

    # 4. Total Risk Computation
    # Scale product to a clean 0.0 - 10.0 scale
    raw_risk = exposure * sensitivity * reachability * 2.1
    risk_score = round(max(0.1, min(10.0, raw_risk)), 1)

    # Classify Priority
    if risk_score >= 8.5:
        priority = "critical"
    elif risk_score >= 6.5:
        priority = "high"
    elif risk_score >= 3.5:
        priority = "medium"
    else:
        priority = "low"

    return EndpointRisk(
        url=url,
        risk_score=risk_score,
        priority=priority,
        exposure=round(exposure, 2),
        sensitivity=round(sensitivity, 2),
        reachability=round(reachability, 2),
        reason=reason,
    )


def prioritize_routes(
    routes: list[str | Route | dict[str, Any]],
    seed_url: str = "",
) -> list[EndpointRisk]:
    """
    Given a collection of routes/URLs, computes risk scores for each and returns
    a list of EndpointRisk models sorted descending by risk score.
    """
    scored: list[EndpointRisk] = []
    seen_urls: set[str] = set()

    for item in routes:
        if isinstance(item, str):
            raw_url = item
            forms_cnt = 0
            has_post = False
            inputs_cnt = 0
        elif isinstance(item, Route):
            raw_url = item.url
            forms_cnt = 0
            has_post = False
            inputs_cnt = 0
        elif isinstance(item, dict):
            raw_url = item.get("url") or item.get("target") or ""
            forms_cnt = len(item.get("forms", []))
            has_post = any(
                isinstance(f, dict) and f.get("method", "").upper() in {"POST", "PUT"}
                or getattr(f, "method", "") in {"POST", "PUT"}
                for f in item.get("forms", [])
            )
            inputs_cnt = len(item.get("inputs", []))
        else:
            continue

        if not raw_url or raw_url in seen_urls:
            continue

        seen_urls.add(raw_url)

        # Depth heuristic: if path has multiple segments relative to seed
        path = urlparse(raw_url).path or "/"
        segments = [s for s in path.split("/") if s]
        depth = len(segments)

        risk_meta = calculate_endpoint_risk(
            url=raw_url,
            forms_count=forms_cnt,
            has_post_method=has_post,
            inputs_count=inputs_cnt,
            depth=depth,
        )
        scored.append(risk_meta)

    # Sort descending by risk score
    scored.sort(key=lambda x: x.risk_score, reverse=True)
    return scored
