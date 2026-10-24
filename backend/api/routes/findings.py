from fastapi import APIRouter, Query
from typing import Optional, List
import json
import logging
from backend.models.finding import get_default_reasoning
from backend.memory.sqlite.database import get_connection

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/findings")
def get_findings_list(
    severity: Optional[str] = Query(None, description="Filter by severity: high, medium, low, informational, all"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search term in title or description")
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        findings_map = {}
        
        # 1. Fetch reports to build findings and mission mapping
        cursor.execute("SELECT mission_id, generated_at, target_url, report_json FROM reports")
        reports = cursor.fetchall()
        for r in reports:
            m_id = r["mission_id"]
            date_str = r["generated_at"]
            try:
                rep_data = json.loads(r["report_json"])
                for f in rep_data.get("findings", []):
                    fid = f.get("finding_id")
                    if fid and fid not in findings_map:
                        reasoning_val = f.get("reasoning") or get_default_reasoning(f.get("category", ""), f.get("description", ""))
                        findings_map[fid] = {
                            "finding_id": fid,
                            "title": f.get("title", ""),
                            "category": f.get("category", "unknown"),
                            "severity": f.get("severity", "medium").lower(),
                            "confidence": f.get("confidence", 0.0),
                            "evidence": f.get("evidence", []),
                            "description": f.get("description", ""),
                            "reasoning": reasoning_val,
                            "mission": m_id,
                            "date": date_str,
                            "recommendation": _get_recommendation_by_category(f.get("category", ""))
                        }
            except Exception:
                pass
                
        # 2. Query any findings from the findings table that might not be in reports
        cursor.execute("""
            SELECT f.id, f.finding_id, f.type, f.title, f.feature, f.severity, 
                   f.security_confidence, f.evidence, f.description, f.reasoning, f.route_id, f.mission_id,
                   r.url, r.discovered_at
            FROM findings f
            LEFT JOIN routes r ON f.route_id = r.id
            ORDER BY f.id DESC
        """)
        finding_rows = cursor.fetchall()
        for row in finding_rows:
            fid = row["finding_id"] or f"FIND-{row['id']:03d}"
            if fid not in findings_map:
                try:
                    evidence_list = json.loads(row["evidence"])
                except Exception:
                    evidence_list = []
                    
                reasoning_text = row["reasoning"] if "reasoning" in row.keys() and row["reasoning"] else ""
                if not reasoning_text:
                    reasoning_text = get_default_reasoning(row["type"], row["description"])

                m_id = row["mission_id"] if "mission_id" in row.keys() and row["mission_id"] else ("MISSION-004" if "testfire" in (row["url"] or "") else "MISSION-001")
                findings_map[fid] = {
                    "finding_id": fid,
                    "title": row["title"],
                    "category": row["type"],
                    "severity": row["severity"].lower(),
                    "confidence": row["security_confidence"],
                    "evidence": evidence_list,
                    "description": row["description"],
                    "reasoning": reasoning_text,
                    "mission": m_id,
                    "date": row["discovered_at"],
                    "recommendation": _get_recommendation_by_category(row["type"])
                }

        findings = list(findings_map.values())
            
        # 3. Apply Filters
        filtered_findings = []
        for f in findings:
            # Severity filter
            if severity and severity.lower() != "all":
                if f["severity"] != severity.lower():
                    continue
                    
            # Category filter
            if category and category.lower() != "all":
                if f["category"].lower() != category.lower():
                    continue
                    
            # Search filter
            if search:
                query = search.lower()
                title_match = query in f["title"].lower()
                desc_match = query in f["description"].lower()
                id_match = query in f["finding_id"].lower()
                if not (title_match or desc_match or id_match):
                    continue
                    
            filtered_findings.append(f)
            
        sev_order = {"high": 3, "medium": 2, "low": 1, "informational": 0}
        filtered_findings.sort(
            key=lambda f: sev_order.get((f.get("severity") or "").lower(), 0),
            reverse=True,
        )
        return filtered_findings
    finally:
        conn.close()

def _get_recommendation_by_category(category: str) -> str:
    recommendations = {
        "missing_csrf": "Implement state-changing anti-CSRF token check on all state-changing endpoints.",
        "weak_authentication": "Strengthen authentication parameters, use HTTPS, lockout mechanisms, and complexity requirements.",
        "exposed_endpoint": "Restrict access to sensitive pathways with proper IP filtering and role checks.",
        "file_upload_risk": "Enforce server-side file ext validations, upload size constraints, and change filename on save.",
        "missing_security_headers": "Ensure modern security headers (HSTS, CSP, X-Frame-Options, XSS protection) are present.",
        "admin_surface": "Block public routing to administration components, enforce MFA and audit logging.",
        "sensitive_input": "Ensure input forms validate parameters strictly, sanitizing special chars before handling.",
        "vulnerable_dependency": "Upgrade outdated client-side libraries to modern patched releases.",
        "missing_subresource_integrity": "Add integrity and crossorigin attributes to external third-party CDN scripts.",
        "verbose_error_leak": "Disable verbose debugging and configure generic error pages in production.",
    }
    return recommendations.get(category, "Review the capability structure and enforce strict access authorization.")
