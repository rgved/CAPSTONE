from fastapi import APIRouter, Header
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
from backend.memory.sqlite.database import get_connection
from backend.api.routes.missions import get_missions
from backend.api.routes.auth import get_current_user_from_header

logger = logging.getLogger(__name__)
router = APIRouter()

def get_mission_runtimes_map() -> Dict[str, float]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT mission_id, created_at FROM tasks ORDER BY id ASC")
        rows = cursor.fetchall()
        
        times = {}
        for r in rows:
            m_id = r["mission_id"] or "MISSION-001"
            if m_id not in times:
                times[m_id] = []
            try:
                times[m_id].append(datetime.fromisoformat(r["created_at"]))
            except Exception:
                pass
                
        runtimes = {}
        for m_id, t_list in times.items():
            if len(t_list) >= 2:
                duration = max(0.1, (max(t_list) - min(t_list)).total_seconds())
                runtimes[m_id] = round(duration, 1)
        return runtimes
    finally:
        conn.close()

@router.get("/metrics")
def get_metrics_summary(authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    missions = get_missions(authorization=authorization)
    total_missions = len(missions)

    if user and total_missions == 0:
        return {
            "total_missions": 0,
            "total_findings": 0,
            "avg_runtime": 0.0,
            "avg_token_reduction": 0.0,
            "token_reduction_by_mission": [],
            "findings_by_severity": [
                {"severity": "Critical", "count": 0},
                {"severity": "High", "count": 0},
                {"severity": "Medium", "count": 0},
                {"severity": "Low", "count": 0},
                {"severity": "Informational", "count": 0},
            ],
            "feature_distribution": [],
            "mission_runtime_trend": []
        }

    conn = get_connection()
    try:
        cursor = conn.cursor()
        user_mids = [m.get("id") or m.get("mission_id") for m in missions if isinstance(m, dict)]
        
        # 1. Total counts (I7: include all findings)
        if user and user_mids:
            placeholders = ",".join(["?"] * len(user_mids))
            cursor.execute(f"SELECT count(*) FROM findings WHERE mission_id IN ({placeholders})", user_mids)
            total_findings = cursor.fetchone()[0]
            cursor.execute(f"SELECT mission_id, report_json FROM reports WHERE mission_id IN ({placeholders})", user_mids)
            reports = cursor.fetchall()
        else:
            cursor.execute("SELECT count(*) FROM findings")
            total_findings = cursor.fetchone()[0]
            cursor.execute("SELECT mission_id, report_json FROM reports")
            reports = cursor.fetchall()
        
        runtimes_map = get_mission_runtimes_map()
        
        token_reduction_by_mission = []
        mission_runtime_trend = []
        reductions = []
        runtimes = []
        
        # Process reports
        for r in reports:
            m_id = r["mission_id"]
            try:
                rep_data = json.loads(r["report_json"])
                stats = rep_data.get("statistics", {})
                naive = stats.get("token_count_naive", 0)
                efficient = stats.get("token_count_efficient", 0)
                
                reduction = 0.0
                if naive > 0:
                    reduction = ((naive - efficient) / naive) * 100
                    reductions.append(reduction)
                token_reduction_by_mission.append({
                    "mission_id": m_id,
                    "reduction": round(reduction, 1)
                })
            except Exception:
                pass
                
            # Runtime
            if m_id in runtimes_map:
                rt = runtimes_map[m_id]
                runtimes.append(rt)
                mission_runtime_trend.append({
                    "mission_id": m_id,
                    "runtime": rt
                })
            
        avg_runtime = round(sum(runtimes) / len(runtimes), 1) if runtimes else 0.0
        avg_token_reduction = round(sum(reductions) / len(reductions), 1) if reductions else 0.0
        
        # 3. Severity Distribution (I2 & I7: Critical, High, Medium, Low, Informational)
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        if user and user_mids:
            cursor.execute(f"SELECT severity FROM findings WHERE mission_id IN ({placeholders})", user_mids)
        else:
            cursor.execute("SELECT severity FROM findings")
        for row in cursor.fetchall():
            sev = (row["severity"] or "").capitalize()
            if sev in severity_counts:
                severity_counts[sev] += 1
                
        findings_by_severity = [
            {"severity": "Critical", "count": severity_counts["Critical"]},
            {"severity": "High", "count": severity_counts["High"]},
            {"severity": "Medium", "count": severity_counts["Medium"]},
            {"severity": "Low", "count": severity_counts["Low"]},
            {"severity": "Informational", "count": severity_counts["Informational"]},
        ]
        
        # 4. Feature Distribution
        feature_counts = {}
        if user and user_mids:
            cursor.execute(f"SELECT name FROM features WHERE mission_id IN ({placeholders})", user_mids)
        else:
            cursor.execute("SELECT name FROM features")
        for row in cursor.fetchall():
            raw_name = (row["name"] or "").strip().lower()
            if raw_name == "unknown":
                display_name = "General Web Surface"
            elif raw_name == "api":
                display_name = "API"
            else:
                display_name = raw_name.replace("_", " ").title()
            feature_counts[display_name] = feature_counts.get(display_name, 0) + 1
            
        feature_distribution = [{"name": k, "count": v} for k, v in feature_counts.items()]
            
        return {
            "total_missions": total_missions,
            "total_findings": total_findings,
            "avg_runtime": avg_runtime,
            "avg_token_reduction": avg_token_reduction,
            "token_reduction_by_mission": token_reduction_by_mission,
            "findings_by_severity": findings_by_severity,
            "feature_distribution": feature_distribution,
            "mission_runtime_trend": mission_runtime_trend
        }
    finally:
        conn.close()
