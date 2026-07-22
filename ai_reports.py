"""
AI Mitigation Report persistence and async job orchestration for BocorCheck.

This module owns everything ai_mitigation.py itself intentionally does NOT:
- Creating/tracking ai_mitigation_reports rows (status: pending/running/complete/failed)
- Running the actual generate_ai_mitigation() call on a background thread so
  Flask requests return immediately instead of blocking for the AI's full latency
- Reading back reports/history/metrics for the web routes in app.py

ai_mitigation.py stays free of any database dependency so it keeps working
exactly as-is for bot.py, which has no DB coupling by design.
"""

import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from mysql.connector import connect

from ai_mitigation import generate_ai_mitigation

logger = logging.getLogger("bocorcheck.ai_reports")


def get_db_config() -> dict:
    """Get database configuration from environment variables (see CLAUDE.md: each feature module owns its own copy)."""
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "fyp_user"),
        "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
        "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
        "use_pure": True,
    }


def create_report_job(investigation_id: Optional[int]) -> int:
    """Insert a pending ai_mitigation_reports row and return its id."""
    with connect(**get_db_config()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO ai_mitigation_reports (investigation_id, status) VALUES (%s, 'pending')",
                (investigation_id,),
            )
            conn.commit()
            return cursor.lastrowid


def _update_report(report_id: int, **fields: Any) -> None:
    if not fields:
        return
    set_clause = ", ".join(f"{key} = %s" for key in fields)
    values = list(fields.values()) + [report_id]
    with connect(**get_db_config()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"UPDATE ai_mitigation_reports SET {set_clause} WHERE id = %s", values)
            conn.commit()


def run_report_job(
    report_id: int,
    email: str,
    breaches: List[Dict[str, Any]],
    phone_number: Optional[str] = None,
    phone_exposed: bool = False,
    risk_score: Optional[int] = None,
    risk_level: Optional[str] = None,
    risk_reduction: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Target function for the background thread: runs the slow, blocking
    generate_ai_mitigation() call, times it, and writes the result back to the
    DB row. Runs outside Flask's request context (no session/request/g access)
    - every value it needs is passed in explicitly. Any exception is caught
    and recorded as a failed job so the polling UI shows a real error instead
    of hanging forever.
    """
    started = time.monotonic()
    try:
        _update_report(report_id, status="running")
        report = generate_ai_mitigation(
            email=email,
            breaches=breaches,
            phone_number=phone_number,
            phone_exposed=phone_exposed,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_reduction=risk_reduction,
        )
        latency_ms = int((time.monotonic() - started) * 1000)
        _update_report(
            report_id,
            status="complete",
            report_json=json.dumps(report),
            ai_powered=1 if report.get("ai_powered") else 0,
            latency_ms=latency_ms,
            completed_at=datetime.now(),
        )
        logger.info(f"AI report job {report_id} complete in {latency_ms}ms (ai_powered={report.get('ai_powered')})")
    except Exception as exc:  # noqa: BLE001 - background thread must never crash silently
        logger.error(f"AI report job {report_id} failed: {exc}", exc_info=True)
        latency_ms = int((time.monotonic() - started) * 1000)
        _update_report(
            report_id,
            status="failed",
            error_message=str(exc)[:2000],
            latency_ms=latency_ms,
            completed_at=datetime.now(),
        )


def start_report_job_async(report_id: int, **kwargs: Any) -> None:
    """Spawn run_report_job() on a daemon background thread."""
    thread = threading.Thread(target=run_report_job, args=(report_id,), kwargs=kwargs, daemon=True)
    thread.start()


def get_report_status(report_id: int) -> Optional[Dict[str, Any]]:
    """Lightweight status-only read for the polling endpoint (no report body)."""
    with connect(**get_db_config()) as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT id, investigation_id, status, ai_powered, latency_ms,
                       error_message, requested_at, completed_at
                FROM ai_mitigation_reports WHERE id = %s
                """,
                (report_id,),
            )
            return cursor.fetchone()


def get_report(report_id: int) -> Optional[Dict[str, Any]]:
    """Return the full report row with report_json parsed into a dict under 'report'."""
    with connect(**get_db_config()) as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM ai_mitigation_reports WHERE id = %s", (report_id,))
            row = cursor.fetchone()
            if row and row.get("report_json"):
                row["report"] = json.loads(row["report_json"])
            return row


def get_latest_report_for_investigation(investigation_id: int) -> Optional[Dict[str, Any]]:
    """Used by the results page to show 'View Report' instead of 'Generate' if one already exists."""
    with connect(**get_db_config()) as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT * FROM ai_mitigation_reports
                WHERE investigation_id = %s
                ORDER BY requested_at DESC LIMIT 1
                """,
                (investigation_id,),
            )
            row = cursor.fetchone()
            if row and row.get("report_json"):
                row["report"] = json.loads(row["report_json"])
            return row


def list_reports_for_user(user_id: Optional[int], is_admin: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
    """
    List past AI reports, newest first. Regular users see only reports tied to
    their own investigations; admins see everything - mirrors the auth pattern
    already used by history() in app.py.
    """
    with connect(**get_db_config()) as conn:
        with conn.cursor(dictionary=True) as cursor:
            if is_admin:
                cursor.execute(
                    """
                    SELECT r.id, r.investigation_id, r.status, r.ai_powered, r.latency_ms,
                           r.requested_at, r.completed_at, il.email, il.risk_level
                    FROM ai_mitigation_reports r
                    LEFT JOIN investigation_logs il ON il.id = r.investigation_id
                    ORDER BY r.requested_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
            else:
                cursor.execute(
                    """
                    SELECT r.id, r.investigation_id, r.status, r.ai_powered, r.latency_ms,
                           r.requested_at, r.completed_at, il.email, il.risk_level
                    FROM ai_mitigation_reports r
                    JOIN investigation_logs il ON il.id = r.investigation_id
                    WHERE il.user_id = %s
                    ORDER BY r.requested_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
            return cursor.fetchall()


def get_metrics_summary() -> Dict[str, Any]:
    """
    Aggregate stats for the AI Metrics Dashboard: total reports, success rate,
    AI-powered vs rule-based-fallback rate, average latency, and a per-day
    trend for the last 14 days.
    """
    with connect(**get_db_config()) as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_reports,
                    SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) AS completed_reports,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_reports,
                    SUM(CASE WHEN ai_powered = 1 THEN 1 ELSE 0 END) AS ai_powered_reports,
                    SUM(CASE WHEN ai_powered = 0 AND status = 'complete' THEN 1 ELSE 0 END) AS fallback_reports,
                    AVG(latency_ms) AS avg_latency_ms
                FROM ai_mitigation_reports
                """
            )
            summary = cursor.fetchone() or {}

            cursor.execute(
                """
                SELECT DATE(requested_at) AS day, COUNT(*) AS report_count,
                       SUM(CASE WHEN ai_powered = 1 THEN 1 ELSE 0 END) AS ai_powered_count
                FROM ai_mitigation_reports
                WHERE requested_at >= DATE_SUB(NOW(), INTERVAL 14 DAY)
                GROUP BY DATE(requested_at)
                ORDER BY day ASC
                """
            )
            trend = cursor.fetchall()

    total = summary.get("total_reports") or 0
    completed = summary.get("completed_reports") or 0
    ai_powered = summary.get("ai_powered_reports") or 0
    fallback = summary.get("fallback_reports") or 0

    return {
        "total_reports": total,
        "completed_reports": completed,
        "failed_reports": summary.get("failed_reports") or 0,
        "ai_powered_reports": ai_powered,
        "fallback_reports": fallback,
        "success_rate_pct": round((completed / total) * 100, 1) if total else 0.0,
        "ai_powered_rate_pct": round((ai_powered / completed) * 100, 1) if completed else 0.0,
        "fallback_rate_pct": round((fallback / completed) * 100, 1) if completed else 0.0,
        "avg_latency_ms": round(summary.get("avg_latency_ms") or 0),
        "avg_latency_seconds": round((summary.get("avg_latency_ms") or 0) / 1000, 1),
        "trend": trend,
    }
