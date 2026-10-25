from fastapi import APIRouter, HTTPException, Header
from typing import List, Dict, Any, Optional
import json
import logging
from backend.models.finding import get_default_reasoning
from backend.memory.sqlite.database import get_connection
from backend.api.routes.auth import get_current_user_from_header

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/reports")
def get_reports_list(authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if user:
            cursor.execute("SELECT mission_id FROM missions WHERE username = ?", (user["username"],))
            user_mids = [r["mission_id"] for r in cursor.fetchall() if r["mission_id"]]
            if not user_mids:
                return []
            placeholders = ",".join(["?"] * len(user_mids))
            cursor.execute(
                f"SELECT report_id, mission_id, target_url, generated_at FROM reports WHERE mission_id IN ({placeholders}) ORDER BY id DESC",
                user_mids,
            )
        else:
            cursor.execute("SELECT report_id, mission_id, target_url, generated_at FROM reports ORDER BY id DESC")
        rows = cursor.fetchall()
        
        reports = []
        for r in rows:
            reports.append({
                "report_id": r["report_id"],
                "mission_id": r["mission_id"],
                "target": r["target_url"],
                "generated_at": r["generated_at"]
            })
        return reports
    finally:
        conn.close()

@router.get("/reports/{id}")
def get_report_detail(id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT report_json FROM reports WHERE report_id = ? OR mission_id = ?", (id, id))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Report not found")
            
        try:
            report_data = json.loads(row["report_json"])
            if isinstance(report_data, dict) and "findings" in report_data and isinstance(report_data["findings"], list):
                sev_order = {"high": 3, "medium": 2, "low": 1, "informational": 0}
                for f in report_data["findings"]:
                    if isinstance(f, dict):
                        if not f.get("reasoning"):
                            f["reasoning"] = get_default_reasoning(f.get("category", ""), f.get("description", ""))
                report_data["findings"].sort(
                    key=lambda f: sev_order.get((f.get("severity", "") if isinstance(f, dict) else "").lower(), 0),
                    reverse=True,
                )
            return report_data
        except Exception as e:
            logger.error(f"Error parsing report JSON: {e}")
            raise HTTPException(status_code=500, detail="Failed to load report data")
    finally:
        conn.close()
