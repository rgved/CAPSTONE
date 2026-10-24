from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import json
import logging
import contextvars
import re

from backend.orchestrator.orchestrator import Orchestrator
from backend.services.storage_service import current_mission_id
from backend.memory.sqlite.database import get_connection
from backend.services.risk_scorer import prioritize_routes
from backend.models.finding import get_default_reasoning

logger = logging.getLogger(__name__)

router = APIRouter()

class ScanRequest(BaseModel):
    url: str

class ScanResponse(BaseModel):
    mission_id: str

async def run_scan_background(url: str, mission_id: str, offset: int):
    # Set coroutine context var for mission_id
    current_mission_id.set(mission_id)
    
    orchestrator = Orchestrator(max_crawl_routes=5)
    orchestrator._mission_counter = offset
    try:
        logger.info(f"Starting background scan for {mission_id} on target {url}")
        await orchestrator.run(url)
        logger.info(f"Completed background scan for {mission_id}")
    except Exception as e:
        logger.error(f"Error running background scan for {mission_id}: {e}", exc_info=True)

def get_max_mission_counter() -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Get from reports
        cursor.execute("SELECT mission_id FROM reports")
        reports_ids = [row["mission_id"] for row in cursor.fetchall() if row["mission_id"]]
        
        # Get from tasks
        cursor.execute("SELECT mission_id FROM tasks WHERE mission_id IS NOT NULL")
        tasks_ids = [row["mission_id"] for row in cursor.fetchall()]
        
        all_ids = set(reports_ids).union(tasks_ids)
        
        max_counter = 0
        for m_id in all_ids:
            # Parse f"MISSION-{counter:03d}"
            match = re.match(r"MISSION-(\d+)", m_id)
            if match:
                val = int(match.group(1))
                if val > max_counter:
                    max_counter = val
        return max_counter
    except Exception as e:
        logger.error(f"Error getting max mission counter: {e}")
        return 0
    finally:
        conn.close()

@router.post("/scan", response_model=ScanResponse)
def start_scan(payload: ScanRequest, background_tasks: BackgroundTasks):
    url = payload.url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
        
    # Determine next mission ID
    max_counter = get_max_mission_counter()
    next_counter = max_counter + 1
    next_mission_id = f"MISSION-{next_counter:03d}"
    
    # Launch in background
    background_tasks.add_task(run_scan_background, url, next_mission_id, max_counter)
    
    return {"mission_id": next_mission_id}

@router.get("/missions")
def get_missions():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Get all reports
        cursor.execute("SELECT mission_id, target_url, generated_at, report_json FROM reports")
        reports_rows = cursor.fetchall()
        reports_map = {r["mission_id"]: r for r in reports_rows if r["mission_id"]}
            
        # Get all tasks grouped by mission_id
        cursor.execute("SELECT mission_id, action, status, created_at, target FROM tasks ORDER BY id ASC")
        tasks_rows = cursor.fetchall()
        
        missions_tasks = {}
        for t in tasks_rows:
            m_id = t["mission_id"] or "MISSION-001"
            if m_id not in missions_tasks:
                missions_tasks[m_id] = []
            missions_tasks[m_id].append(t)

        # Get all routes mission IDs
        cursor.execute("SELECT DISTINCT mission_id FROM routes WHERE mission_id IS NOT NULL")
        routes_mission_ids = [row["mission_id"] for row in cursor.fetchall() if row["mission_id"]]
            
        # Compile all unique mission IDs
        all_ids = set(reports_map.keys()).union(missions_tasks.keys()).union(routes_mission_ids)
        
        missions = []
        for m_id in sorted(all_ids):
            status = "completed"
            target = ""
            created_at = None
            findings_count = 0
            
            # If report exists
            if m_id in reports_map:
                r = reports_map[m_id]
                try:
                    rep_data = json.loads(r["report_json"])
                    findings_count = len(rep_data.get("findings", []))
                    target = r["target_url"] or rep_data.get("target_url", "")
                except Exception:
                    findings_count = 0
                    target = r["target_url"] or ""
                created_at = r["generated_at"]
                status = "completed"
            
            # If tasks exist, extract target or timestamp if missing
            if m_id in missions_tasks:
                m_tasks = missions_tasks[m_id]
                if not target:
                    target = next((t["target"] for t in m_tasks if t["target"]), "")
                if not created_at and m_tasks:
                    created_at = m_tasks[0]["created_at"]
                    
                # Determine status if no report exists
                if m_id not in reports_map:
                    has_stop_completed = any(t["action"] == "STOP" and t["status"] == "completed" for t in m_tasks)
                    has_failed = any(t["status"] == "failed" for t in m_tasks)
                    
                    if has_failed:
                        status = "failed"
                    elif has_stop_completed:
                        status = "completed"
                    else:
                        try:
                            last_time = datetime.fromisoformat(m_tasks[-1]["created_at"])
                            if (datetime.now(timezone.utc) - last_time).total_seconds() > 600:
                                status = "failed"
                            else:
                                status = "running"
                        except Exception:
                            status = "running"
            
            # Fallback target from routes if still blank
            if not target:
                cursor.execute("SELECT url, discovered_at FROM routes WHERE mission_id = ? ORDER BY id ASC LIMIT 1", (m_id,))
                m_r = cursor.fetchone()
                if m_r:
                    target = m_r["url"]
                    if not created_at and "discovered_at" in m_r.keys():
                        created_at = str(m_r["discovered_at"])
                        
            if not target:
                cursor.execute("SELECT url FROM routes ORDER BY id ASC LIMIT 1")
                first_r = cursor.fetchone()
                if first_r:
                    target = first_r["url"]

            # Formulate the response item
            missions.append({
                "mission_id": m_id,
                "target": target or "https://target-app.local",
                "status": status,
                "created_at": created_at,
                "findings_count": findings_count
            })
            
        return missions
    finally:
        conn.close()

from urllib.parse import urlparse, urljoin

def _get_recommendation_by_category(category: str) -> str:
    recommendations = {
        "missing_csrf": "Implement anti-CSRF tokens on state-changing forms.",
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

def get_mission_routes(target: str, rep_data: dict, cursor, mission_id: str = "") -> list[str]:
    target_netloc = urlparse(target).netloc.lower() if target else ""
    routes_set = set()
    if target:
        routes_set.add(target)
        
    # 1. Check routes explicitly recorded in report
    for r in rep_data.get("routes", []):
        u = r.get("url") if isinstance(r, dict) else str(r)
        if u:
            if u.startswith("/"):
                u = urljoin(target, u)
            if not target_netloc or urlparse(u).netloc.lower() == target_netloc:
                routes_set.add(u)
                
    # 2. Check form actions or links extracted in findings evidence
    for f in rep_data.get("findings", []):
        for ev in f.get("evidence", []):
            if "action:" in ev.lower():
                parts = ev.split("action:", 1)[1].split(",")[0].strip()
                if parts:
                    joined = urljoin(target, parts)
                    if not target_netloc or urlparse(joined).netloc.lower() == target_netloc:
                        routes_set.add(joined)

    # 3. Check SQLite routes table for routes matching THIS mission_id and domain
    if mission_id:
        cursor.execute("SELECT url FROM routes WHERE mission_id = ?", (mission_id,))
        m_routes = cursor.fetchall()
        if not m_routes and mission_id == "MISSION-001":
            cursor.execute("SELECT url FROM routes WHERE mission_id IS NULL")
            m_routes = cursor.fetchall()
        for r_row in m_routes:
            u = r_row["url"]
            if u and target_netloc and urlparse(u).netloc.lower() == target_netloc:
                routes_set.add(u)
    else:
        cursor.execute("SELECT url FROM routes")
        for r_row in cursor.fetchall():
            u = r_row["url"]
            if u and target_netloc and urlparse(u).netloc.lower() == target_netloc:
                routes_set.add(u)
            
    return list(routes_set)

@router.get("/missions/{id}")
def get_mission_detail(id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Check if report exists
        cursor.execute("SELECT report_id, target_url, generated_at, report_json FROM reports WHERE mission_id = ?", (id,))
        report_row = cursor.fetchone()
        
        # Get tasks for this mission
        cursor.execute("SELECT action, status, created_at, target FROM tasks WHERE mission_id = ? ORDER BY id ASC", (id,))
        task_rows = cursor.fetchall()
        
        # Fallback to legacy default for MISSION-001 if task_rows is empty and it matches
        if not task_rows and id == "MISSION-001":
            cursor.execute("SELECT action, status, created_at, target FROM tasks WHERE mission_id IS NULL ORDER BY id ASC")
            task_rows = cursor.fetchall()
            
        if not task_rows and not report_row:
            cursor.execute("SELECT url, discovered_at FROM routes WHERE mission_id = ?", (id,))
            m_routes = cursor.fetchall()
            if not m_routes:
                raise HTTPException(status_code=404, detail="Mission not found")
            
        target = ""
        created_at = None
        
        if report_row:
            try:
                rep_data = json.loads(report_row["report_json"])
                target = report_row["target_url"] or rep_data.get("target_url", "")
            except Exception:
                rep_data = {}
                target = report_row["target_url"] or ""
            created_at = report_row["generated_at"]
        else:
            rep_data = {}
            
        if not target and task_rows:
            target = next((t["target"] for t in task_rows if t["target"]), "")
            if not created_at:
                created_at = task_rows[0]["created_at"]
                
        if not target and id:
            cursor.execute("SELECT url, discovered_at FROM routes WHERE mission_id = ? ORDER BY id ASC LIMIT 1", (id,))
            first_m_r = cursor.fetchone()
            if first_m_r:
                target = first_m_r["url"]
                if not created_at and "discovered_at" in first_m_r.keys():
                    created_at = str(first_m_r["discovered_at"])

        if not target:
            cursor.execute("SELECT url FROM routes ORDER BY id ASC LIMIT 1")
            first_r = cursor.fetchone()
            if first_r:
                target = first_r["url"]
                
        target = target or "https://target-app.local"
            
        # Determine status
        if report_row:
            status = "completed"
        elif task_rows:
            has_stop_completed = any(t["action"] == "STOP" and t["status"] == "completed" for t in task_rows)
            has_failed = any(t["status"] == "failed" for t in task_rows)
            if has_failed:
                status = "failed"
            elif has_stop_completed:
                status = "completed"
            else:
                try:
                    last_time = datetime.fromisoformat(task_rows[-1]["created_at"])
                    if (datetime.now(timezone.utc) - last_time).total_seconds() > 600:
                        status = "failed"
                    else:
                        status = "running"
                except Exception:
                    status = "running"
        else:
            status = "completed"
                    
        runtime_str = "0s"
        if task_rows:
            try:
                start_time = datetime.fromisoformat(task_rows[0]["created_at"])
                if status == "running":
                    end_time = datetime.now(timezone.utc)
                else:
                    end_time = datetime.fromisoformat(task_rows[-1]["created_at"])
                diff = max(0.1, (end_time - start_time).total_seconds())
                runtime_str = f"{diff:.1f}s"
            except Exception:
                runtime_str = "unknown"
                
        # If completed, extract everything from the report!
        if report_row:
            stats = rep_data.get("statistics", {})
            original_tokens = stats.get("token_count_naive", 2297)
            reduced_tokens = stats.get("token_count_efficient", 997)
            reduction_percentage = 0.0
            if original_tokens > 0:
                reduction_percentage = ((original_tokens - reduced_tokens) / original_tokens) * 100
                
            features_list = []
            if rep_data.get("features"):
                for f in rep_data.get("features", []):
                    conf = f.get("confidence") or f.get("classification_confidence", 0.0)
                    if conf <= 1.0:
                        conf = conf * 100
                    features_list.append({
                        "name": f.get("name", "unknown"),
                        "confidence": conf
                    })
            if not features_list:
                target_netloc = urlparse(target).netloc.lower() if target else ""
                cursor.execute("SELECT name, classification_confidence, routes, mission_id FROM features WHERE mission_id = ?", (id,))
                feat_rows = cursor.fetchall()
                if not feat_rows:
                    cursor.execute("SELECT name, classification_confidence, routes, mission_id FROM features")
                    all_feat = cursor.fetchall()
                    feat_rows = [
                        r for r in all_feat 
                        if (r["mission_id"] == id) or 
                           (target_netloc and target_netloc in (r["routes"] or "").lower())
                    ]
                for row in feat_rows:
                    conf = row["classification_confidence"] or 0.0
                    if conf <= 1.0:
                        conf = conf * 100
                    features_list.append({
                        "name": row["name"],
                        "confidence": conf
                    })
                
            findings_list = []
            for f in rep_data.get("findings", []):
                findings_list.append({
                    "finding_id": f.get("finding_id", ""),
                    "title": f.get("title", ""),
                    "category": f.get("category", ""),
                    "severity": f.get("severity", ""),
                    "confidence": f.get("confidence", 0.0),
                    "evidence": f.get("evidence", []),
                    "description": f.get("description", ""),
                    "reasoning": f.get("reasoning") or get_default_reasoning(f.get("category", ""), f.get("description", "")),
                    "recommendation": f.get("recommendation", "") or _get_recommendation_by_category(f.get("category", ""))
                })
                
            sev_order = {"high": 3, "medium": 2, "low": 1, "informational": 0}
            findings_list.sort(
                key=lambda item: sev_order.get((item.get("severity") or "").lower(), 0),
                reverse=True,
            )

            # Ensure capabilities reflect all evaluated functional surfaces from findings
            feature_names = {feat["name"].lower() for feat in features_list}
            category_to_capability = {
                "missing_csrf": "authentication",
                "weak_authentication": "authentication",
                "vulnerable_dependency": "client_side_libraries",
                "missing_subresource_integrity": "cdn_subresources",
                "missing_security_headers": "security_headers",
                "verbose_error_leak": "error_handling",
                "sensitive_input": "input_handling",
                "file_upload_risk": "file_upload",
                "exposed_endpoint": "api",
                "admin_surface": "admin_panel",
            }
            for f in findings_list:
                cat = f.get("category", "").lower()
                cap = category_to_capability.get(cat)
                if cap and cap not in feature_names:
                    features_list.append({
                        "name": cap,
                        "confidence": 100.0
                    })
                    feature_names.add(cap)

            # Compute prioritized attack surface strictly for this target and mission
            route_urls = get_mission_routes(target, rep_data, cursor, mission_id=id)
            prioritized_surface = [
                item.model_dump() for item in prioritize_routes(route_urls, seed_url=target)
            ]
                
            return {
                "mission_id": id,
                "target_url": target,
                "status": status,
                "runtime": runtime_str,
                "generated_at": report_row["generated_at"],
                "recon_summary": {
                    "routes": stats.get("routes_discovered", len(route_urls)) or 1,
                    "forms": stats.get("forms_count", 0),
                    "inputs": stats.get("inputs_count", 0),
                    "buttons": stats.get("buttons_count", 0),
                    "scripts": stats.get("scripts_count", 0),
                    "links": stats.get("links_count", len(route_urls) or 1),
                    "meta_tags": stats.get("meta_tags_count", 0)
                },
                "features": features_list,
                "token_reduction": {
                    "original_tokens": original_tokens,
                    "reduced_tokens": reduced_tokens,
                    "reduction_percentage": round(reduction_percentage, 1)
                },
                "findings": findings_list,
                "prioritized_attack_surface": prioritized_surface,
                "report_id": report_row["report_id"]
            }
            
        # If running or failed
        # Retrieve routes and findings strictly related to this mission target and mission_id
        target_netloc = urlparse(target).netloc.lower() if target else ""
        if id:
            cursor.execute("SELECT id, url FROM routes WHERE mission_id = ?", (id,))
            m_routes = cursor.fetchall()
            if not m_routes and id == "MISSION-001":
                cursor.execute("SELECT id, url FROM routes WHERE mission_id IS NULL")
                m_routes = cursor.fetchall()
            all_routes = m_routes
        else:
            cursor.execute("SELECT id, url FROM routes")
            all_routes = cursor.fetchall()

        mission_route_rows = [r for r in all_routes if target_netloc and urlparse(r["url"]).netloc.lower() == target_netloc]
        mission_route_ids = [r["id"] for r in mission_route_rows]
        route_urls = [r["url"] for r in mission_route_rows] or ([target] if target else [])
        
        prioritized_surface = [
            item.model_dump() for item in prioritize_routes(route_urls, seed_url=target)
        ]

        features_list = []
        if id:
            cursor.execute("SELECT name, classification_confidence, routes, mission_id FROM features WHERE mission_id = ?", (id,))
            feat_rows = cursor.fetchall()
            if not feat_rows:
                cursor.execute("SELECT name, classification_confidence, routes, mission_id FROM features")
                all_feat = cursor.fetchall()
                feat_rows = [
                    r for r in all_feat 
                    if (r["mission_id"] == id) or 
                       (target_netloc and target_netloc in (r["routes"] or "").lower())
                ]
            for row in feat_rows:
                conf = row["classification_confidence"] or 0.0
                if conf <= 1.0:
                    conf = conf * 100
                features_list.append({
                    "name": row["name"],
                    "confidence": conf
                })
        
        findings_list = []
        finding_rows = []
        if id:
            cursor.execute("SELECT * FROM findings WHERE mission_id = ?", (id,))
            finding_rows = cursor.fetchall()
            if not finding_rows and id == "MISSION-001":
                cursor.execute("SELECT * FROM findings WHERE mission_id IS NULL")
                finding_rows = cursor.fetchall()
        elif mission_route_ids:
            placeholders = ",".join("?" for _ in mission_route_ids)
            cursor.execute(f"SELECT * FROM findings WHERE route_id IN ({placeholders})", mission_route_ids)
            finding_rows = cursor.fetchall()

        for f in finding_rows:
            try:
                ev = json.loads(f["evidence"])
            except Exception:
                ev = []
            reasoning_val = f["reasoning"] if "reasoning" in f.keys() and f["reasoning"] else ""
            if not reasoning_val:
                reasoning_val = get_default_reasoning(f["type"], f["description"])
            findings_list.append({
                "finding_id": f["finding_id"] or f"FIND-{f['id']:03d}",
                "title": f["title"],
                "category": f["type"],
                "severity": f["severity"],
                "confidence": f["security_confidence"],
                "evidence": ev,
                "description": f["description"],
                "reasoning": reasoning_val,
                "recommendation": _get_recommendation_by_category(f["type"])
            })
            
        sev_order = {"high": 3, "medium": 2, "low": 1, "informational": 0}
        findings_list.sort(
            key=lambda item: sev_order.get((item.get("severity") or "").lower(), 0),
            reverse=True,
        )

        # Ensure capabilities reflect all evaluated functional surfaces from findings
        feature_names = {feat["name"].lower() for feat in features_list}
        category_to_capability = {
            "missing_csrf": "authentication",
            "weak_authentication": "authentication",
            "vulnerable_dependency": "client_side_libraries",
            "missing_subresource_integrity": "cdn_subresources",
            "missing_security_headers": "security_headers",
            "verbose_error_leak": "error_handling",
            "sensitive_input": "input_handling",
            "file_upload_risk": "file_upload",
            "exposed_endpoint": "api",
            "admin_surface": "admin_panel",
        }
        for f in findings_list:
            cat = f.get("category", "").lower()
            cap = category_to_capability.get(cat)
            if cap and cap not in feature_names:
                features_list.append({
                    "name": cap,
                    "confidence": 100.0
                })
                feature_names.add(cap)

        return {
            "mission_id": id,
            "target_url": target,
            "status": status,
            "runtime": runtime_str,
            "generated_at": created_at,
            "recon_summary": {
                "routes": len(mission_route_ids) or 1,
                "forms": 0,
                "inputs": 0,
                "buttons": 0,
                "scripts": 0,
                "links": 0,
                "meta_tags": 0
            },
            "features": features_list,
            "token_reduction": {
                "original_tokens": 0,
                "reduced_tokens": 0,
                "reduction_percentage": 0.0
            },
            "findings": findings_list,
            "prioritized_attack_surface": prioritized_surface,
            "report_id": None
        }
    finally:
        conn.close()

@router.get("/missions/{id}/timeline")
def get_mission_timeline(id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Get tasks for this mission
        cursor.execute("SELECT action, status, created_at FROM tasks WHERE mission_id = ? ORDER BY id ASC", (id,))
        rows = cursor.fetchall()
        
        # Fallback to legacy default for MISSION-001 if empty
        if not rows and id == "MISSION-001":
            cursor.execute("SELECT action, status, created_at FROM tasks WHERE mission_id IS NULL ORDER BY id ASC")
            rows = cursor.fetchall()
            
        timeline = []
        for r in rows:
            timeline.append({
                "task": r["action"],
                "status": r["status"],
                "timestamp": r["created_at"]
            })
            
        return timeline
    finally:
        conn.close()
