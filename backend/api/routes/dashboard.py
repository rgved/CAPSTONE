from fastapi import APIRouter, Header
from typing import List, Dict, Any, Optional
import json
import logging
from backend.memory.sqlite.database import get_connection
from backend.api.routes.missions import get_missions, CATEGORY_TO_CAPABILITY

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard")
def get_dashboard_summary(authorization: Optional[str] = Header(None)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Missions List & Assets
        missions = get_missions(authorization)
        total_missions = len(missions)
        unique_targets = set(m.get("target") for m in missions if m.get("target"))
        assets_scanned = len(unique_targets)
        
        # 2. Total findings from SQLite table (vulnerabilities: excludes informational)
        cursor.execute("SELECT count(*) FROM findings WHERE lower(severity) != 'informational'")
        total_findings = cursor.fetchone()[0]

        # 3. Severity breakdown & risk scoring
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        cursor.execute("SELECT severity FROM findings")
        for row in cursor.fetchall():
            sev = (row["severity"] or "").capitalize()
            if sev in severity_counts:
                severity_counts[sev] += 1
            else:
                severity_counts["Informational"] += 1

        # 4. Synthesize capabilities discovered across features AND evaluated findings
        feature_counts: dict[str, int] = {}
        cursor.execute("SELECT name FROM features")
        for row in cursor.fetchall():
            raw_name = (row["name"] or "").strip().lower()
            if not raw_name:
                continue
            if raw_name == "unknown":
                display_name = "General Web Surface"
            elif raw_name == "api":
                display_name = "API Gateway"
            else:
                display_name = raw_name.replace("_", " ").title()
            feature_counts[display_name] = feature_counts.get(display_name, 0) + 1

        # Pull surface capabilities from findings
        cursor.execute("SELECT DISTINCT type FROM findings")
        for row in cursor.fetchall():
            cat = (row["type"] or "").strip().lower()
            cap = CATEGORY_TO_CAPABILITY.get(cat)
            if cap:
                display_name = cap.replace("_", " ").title()
                feature_counts[display_name] = feature_counts.get(display_name, 0) + 1

        features_identified = len(feature_counts)
        feature_distribution = [{"name": k, "value": v} for k, v in feature_counts.items()]

        # 5. Average Token Reduction (legacy backward compatibility)
        cursor.execute("SELECT report_json FROM reports")
        reports = cursor.fetchall()
        reductions = []
        for r in reports:
            try:
                rep_data = json.loads(r["report_json"])
                stats = rep_data.get("statistics", {})
                naive = stats.get("token_count_naive", 0)
                efficient = stats.get("token_count_efficient", 0)
                if naive > 0:
                    reductions.append(((naive - efficient) / naive) * 100)
            except Exception:
                pass
        avg_token_reduction = round(sum(reductions) / len(reductions), 1) if reductions else 0.0

        # High/Critical count for dashboard bar chart compatibility (maps Critical to High)
        mapped_high = severity_counts["High"] + severity_counts["Critical"]

        # Calculate security posture score (0 - 100, 100 being best)
        penalty = (severity_counts["Critical"] * 25) + (severity_counts["High"] * 15) + (severity_counts["Medium"] * 8) + (severity_counts["Low"] * 3)
        security_score = max(10, 100 - penalty) if total_missions > 0 else 100

        # Format recent missions (latest first)
        sorted_missions = sorted(missions, key=lambda m: m.get("created_at") or "", reverse=True)
        recent_missions = []
        for m in sorted_missions[:5]:
            recent_missions.append({
                "mission_id": m["mission_id"],
                "target": m["target"],
                "status": m["status"],
                "date": m["created_at"],
                "findings": m["findings_count"]
            })
            
        return {
            "stats": {
                "total_missions": total_missions,
                "assets_scanned": assets_scanned,
                "total_findings": total_findings,
                "critical_findings": severity_counts["Critical"],
                "high_findings": severity_counts["High"],
                "security_score": security_score,
                "avg_token_reduction": avg_token_reduction,
                "features_identified": features_identified
            },
            "recent_missions": recent_missions,
            "findings_severity": [
                {"severity": "High", "count": mapped_high},
                {"severity": "Medium", "count": severity_counts["Medium"]},
                {"severity": "Low", "count": severity_counts["Low"]}
            ],
            "findings_breakdown_full": [
                {"severity": "Critical", "count": severity_counts["Critical"]},
                {"severity": "High", "count": severity_counts["High"]},
                {"severity": "Medium", "count": severity_counts["Medium"]},
                {"severity": "Low", "count": severity_counts["Low"]}
            ],
            "feature_distribution": feature_distribution
        }
    finally:
        conn.close()
