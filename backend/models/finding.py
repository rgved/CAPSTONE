"""
backend/models/finding.py

Pydantic model for a Phase 6 security finding.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

FindingCategory = Literal[
    "missing_csrf",
    "weak_authentication",
    "exposed_endpoint",
    "file_upload_risk",
    "missing_security_headers",
    "admin_surface",
    "sensitive_input",
    "vulnerable_dependency",
    "missing_subresource_integrity",
    "verbose_error_leak",
    "unknown",
]

FindingSeverity = Literal["informational", "low", "medium", "high"]


class Finding(BaseModel):
    finding_id: Optional[str] = None
    type: FindingCategory
    title: str
    feature: str
    severity: FindingSeverity
    security_confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    description: str = ""
    reasoning: str = ""
    route_id: Optional[int] = None


_DEFAULT_REASONINGS: dict[str, str] = {
    "missing_csrf": "State-changing POST request submission identified on an interactive form without anti-CSRF token verification or nonce validation, enabling unauthorized cross-site action execution on behalf of authenticated users.",
    "weak_authentication": "Authentication endpoint transmits credentials without sufficient transport encryption, lockout protections, or strict complexity requirements, creating high risk for brute-force and credential intercept attacks.",
    "exposed_endpoint": "Sensitive internal or API endpoint is exposed directly to unauthenticated clients without role-based access control or network isolation.",
    "file_upload_risk": "File ingestion boundary allows multipart/form-data upload without strict server-side MIME type or extension whitelist enforcement, creating potential for arbitrary file execution.",
    "missing_security_headers": "HTTP response headers lack essential defensive policies (such as HSTS, Content-Security-Policy, or X-Frame-Options), leaving the client browser exposed to framing, downgrade, and injection attacks.",
    "admin_surface": "Administrative interface components are reachable from public network routes without multi-factor authentication or source IP filtering.",
    "sensitive_input": "Form inputs accept unconstrained user data without input sanitization or validation, increasing the likelihood of injection attacks.",
    "vulnerable_dependency": "Third-party client library with known public CVEs is embedded directly without version pinning or security patching, exposing the application to client-side exploitation.",
    "missing_subresource_integrity": "External script or stylesheet is fetched from an untrusted third-party CDN without cryptographic subresource integrity (SRI) hash verification, allowing arbitrary script injection if the CDN is compromised.",
    "verbose_error_leak": "Server responses or unhandled exceptions leak stack traces, database schema details, or environment diagnostics, enabling targeted exploit generation.",
}


def get_default_reasoning(category: str, description: str = "") -> str:
    if category in _DEFAULT_REASONINGS:
        return _DEFAULT_REASONINGS[category]
    return description or "Security finding identified based on contextual analysis of response headers, form structures, and input boundaries."

