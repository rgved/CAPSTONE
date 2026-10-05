from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import logging
from backend.models.finding import get_default_reasoning
from backend.memory.sqlite.database import get_connection

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/reports")
def get_reports_list():
    conn = get_connection()
    try:
        cursor = conn.cursor()
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
                for f in report_data["findings"]:
                    if isinstance(f, dict):
                        if not f.get("reasoning"):
                            f["reasoning"] = get_default_reasoning(f.get("category", ""), f.get("description", ""))
            return report_data
        except Exception as e:
            logger.error(f"Error parsing report JSON: {e}")
            raise HTTPException(status_code=500, detail="Failed to load report data")
    finally:
        conn.close()
