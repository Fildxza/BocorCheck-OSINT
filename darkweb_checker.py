"""
Dark Web Monitoring Integration Module
Checks if user credentials appear on dark web, pastebin, and other exposed data sites
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from mysql.connector import connect, Error as MySQLError
import os
import requests
import json
from telegram.ext import CommandHandler
from telegram.ext import Application
import logging

logger = logging.getLogger(__name__)


def get_db_config() -> dict:
    """Get database configuration from environment variables"""
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "fyp_user"),
        "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
        "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
        "use_pure": True,
    }


# ============================================================================
# FEATURE 1: Mock Dark Web Checker (For FYP Demo)
# ============================================================================

def check_darkweb_mock(query_term: str) -> List[Dict[str, Any]]:
    """
    Mock dark web checker - Returns simulated findings
    Perfect for FYP demo without real dark web API
    
    Args:
        query_term: Email, phone, or credential to search
        
    Returns:
        List of mock findings
    """
    
    # Simulated dark web findings database
    mock_findings = {
        "common_emails": [
            {
                "platform": "Pastebin",
                "snippet": "admin123:exposed_password_123",
                "severity": "CRITICAL",
                "found_date": "2024-11-15",
                "risk_reason": "Plaintext password found alongside email"
            },
            {
                "platform": "Dark Web Market",
                "snippet": "seller_username with verified email list",
                "severity": "HIGH",
                "found_date": "2024-10-20",
                "risk_reason": "Email in verified seller database"
            }
        ],
        "leaked_passwords": [
            {
                "platform": "Combo Lists (Dark Web)",
                "snippet": "email:password combination in sale",
                "severity": "CRITICAL",
                "found_date": "2024-09-15",
                "risk_reason": "Active credential pair for sale"
            }
        ],
        "phone_numbers": [
            {
                "platform": "Telegram Seller Bot",
                "snippet": "Phone number with SIM swap offers",
                "severity": "HIGH",
                "found_date": "2024-10-01",
                "risk_reason": "Target of SIM swap attack"
            }
        ]
    }
    
    # Return based on query type
    findings = []
    
    # Simulate probability (50/50 for demo)
    import random
    if random.random() > 0.5:
        if "@" in query_term:
            findings = mock_findings.get("common_emails", [])
        elif any(c.isdigit() and len(query_term) > 7 for c in query_term):
            findings = mock_findings.get("phone_numbers", [])
        else:
            findings = mock_findings.get("leaked_passwords", [])
    
    return findings


# ============================================================================
# FEATURE 2: Record Dark Web Finding
# ============================================================================

def record_darkweb_finding(
    investigation_id: int,
    user_id: int,
    query_term: str,
    platform: str,
    snippet: str,
    severity: str = "MEDIUM",
    risk_reason: Optional[str] = None,
    full_content: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Record a dark web finding in the database
    
    Args:
        investigation_id: Investigation ID
        user_id: User ID
        query_term: What was searched (email, phone, etc.)
        platform: Where found (Pastebin, Dark Web, etc.)
        snippet: Preview of finding
        severity: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
        risk_reason: Explanation of risk
        full_content: Full content (optional)
        
    Returns:
        Tuple[success, message]
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO darkweb_findings 
                (investigation_id, user_id, query_term, found_on_platform, 
                 snippet, severity, risk_reason, full_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (investigation_id, user_id, query_term, platform, 
                  snippet, severity, risk_reason, full_content))
            
            # Update investigation to mark it has dark web findings
            cursor.execute("""
                UPDATE investigation_logs
                SET has_darkweb_findings = TRUE
                WHERE id = %s
            """, (investigation_id,))
            
            conn.commit()
            return True, f"✅ Finding recorded on {platform}"
            
    except MySQLError as e:
        return False, f"❌ Error: {str(e)}"


# ============================================================================
# FEATURE 3: Get Dark Web Findings for User
# ============================================================================

def get_darkweb_findings(user_id: int, unresolved_only: bool = True) -> List[Dict[str, Any]]:
    """
    Get all dark web findings for a user
    
    Args:
        user_id: User ID
        unresolved_only: Only show unresolved findings if True
        
    Returns:
        List of dark web findings
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            if unresolved_only:
                cursor.execute("""
                    SELECT 
                        id, investigation_id, query_term, found_on_platform,
                        snippet, severity, risk_reason,
                        first_detected, last_seen, is_resolved, resolved_date,
                        created_at
                    FROM darkweb_findings
                    WHERE user_id = %s AND is_resolved = FALSE
                    ORDER BY severity DESC, first_detected DESC
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT 
                        id, investigation_id, query_term, found_on_platform,
                        snippet, severity, risk_reason,
                        first_detected, last_seen, is_resolved, resolved_date,
                        created_at
                    FROM darkweb_findings
                    WHERE user_id = %s
                    ORDER BY severity DESC, first_detected DESC
                """, (user_id,))
            
            findings = cursor.fetchall()
            
            # Calculate risk score
            severity_scores = {
                'LOW': 10,
                'MEDIUM': 40,
                'HIGH': 70,
                'CRITICAL': 100
            }
            
            for finding in findings:
                finding['risk_score'] = severity_scores.get(finding['severity'], 50)
            
            return findings
            
    except MySQLError as e:
        print(f"Error fetching dark web findings: {e}")
        return []


# ============================================================================
# FEATURE 4: Get Dark Web Findings for Investigation
# ============================================================================

def get_investigation_darkweb_findings(investigation_id: int) -> List[Dict[str, Any]]:
    """
    Get dark web findings for specific investigation
    
    Args:
        investigation_id: Investigation ID
        
    Returns:
        List of findings
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    id, query_term, found_on_platform, snippet, severity,
                    risk_reason, first_detected, is_resolved
                FROM darkweb_findings
                WHERE investigation_id = %s
                ORDER BY severity DESC, first_detected DESC
            """, (investigation_id,))
            
            return cursor.fetchall()
            
    except MySQLError as e:
        print(f"Error fetching investigation findings: {e}")
        return []


# ============================================================================
# FEATURE 5: Record Dark Web Check History
# ============================================================================

def record_darkweb_check(
    monitoring_subscription_id: int,
    user_id: int,
    total_findings: int,
    critical_count: int,
    high_count: int,
    medium_count: int,
    status: str = "completed",
    error_message: Optional[str] = None,
    scan_duration_seconds: Optional[int] = None
) -> bool:
    """
    Record dark web scan in history
    
    Args:
        monitoring_subscription_id: Monitoring subscription ID
        user_id: User ID
        total_findings: Total findings found
        critical_count: Critical severity count
        high_count: High severity count
        medium_count: Medium severity count
        status: 'pending', 'running', 'completed', 'failed'
        error_message: Error if failed
        scan_duration_seconds: How long scan took
        
    Returns:
        Success status
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO darkweb_check_history
                (monitoring_subscription_id, user_id, check_date, 
                 total_findings, critical_findings, high_findings, 
                 medium_findings, status, error_message, scan_duration_seconds)
                VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s)
            """, (monitoring_subscription_id, user_id, total_findings, 
                  critical_count, high_count, medium_count, status, 
                  error_message, scan_duration_seconds))
            
            conn.commit()
            return True
            
    except MySQLError as e:
        print(f"Error recording check history: {e}")
        return False


# ============================================================================
# FEATURE 6: Get Dark Web Check History
# ============================================================================

def get_darkweb_check_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get dark web scan history for user
    
    Args:
        user_id: User ID
        limit: Maximum results
        
    Returns:
        List of scan history
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    id, check_date, total_findings, critical_findings, 
                    high_findings, medium_findings, status, scan_duration_seconds
                FROM darkweb_check_history
                WHERE user_id = %s
                ORDER BY check_date DESC
                LIMIT %s
            """, (user_id, limit))
            
            return cursor.fetchall()
            
    except MySQLError as e:
        print(f"Error fetching check history: {e}")
        return []


# ============================================================================
# FEATURE 7: Calculate Dark Web Risk Score
# ============================================================================

def calculate_darkweb_risk_score(user_id: int) -> Dict[str, Any]:
    """
    Calculate overall dark web risk for user based on findings
    
    Args:
        user_id: User ID
        
    Returns:
        Risk score and breakdown
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get counts by severity
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_findings,
                    SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical_count,
                    SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) as high_count,
                    SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) as medium_count,
                    SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) as low_count,
                    SUM(CASE WHEN is_resolved = FALSE THEN 1 ELSE 0 END) as unresolved_count
                FROM darkweb_findings
                WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            
            # Calculate risk score
            critical = result['critical_count'] or 0
            high = result['high_count'] or 0
            medium = result['medium_count'] or 0
            low = result['low_count'] or 0
            
            risk_score = (critical * 25) + (high * 15) + (medium * 5) + (low * 1)
            risk_score = min(risk_score, 100)  # Cap at 100
            
            if risk_score >= 80:
                risk_level = "CRITICAL"
            elif risk_score >= 60:
                risk_level = "HIGH"
            elif risk_score >= 40:
                risk_level = "MEDIUM"
            elif risk_score >= 20:
                risk_level = "LOW"
            else:
                risk_level = "MINIMAL"
            
            return {
                'total_findings': result['total_findings'] or 0,
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': low,
                'unresolved': result['unresolved_count'] or 0,
                'risk_score': risk_score,
                'risk_level': risk_level
            }
            
    except MySQLError as e:
        print(f"Error calculating risk: {e}")
        return {'risk_score': 0, 'risk_level': 'UNKNOWN'}


# ============================================================================
# FEATURE 8: Mark Finding as Resolved
# ============================================================================

def mark_finding_resolved(finding_id: int, user_id: int) -> Tuple[bool, str]:
    """
    Mark a dark web finding as resolved (mitigated)
    
    Args:
        finding_id: Finding ID
        user_id: User ID (for verification)
        
    Returns:
        Tuple[success, message]
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            
            # Verify ownership
            cursor.execute("""
                SELECT user_id FROM darkweb_findings WHERE id = %s
            """, (finding_id,))
            
            result = cursor.fetchone()
            if not result or result[0] != user_id:
                return False, "❌ Not authorized"
            
            cursor.execute("""
                UPDATE darkweb_findings
                SET is_resolved = TRUE, resolved_date = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (finding_id,))
            
            conn.commit()
            return True, "✅ Finding marked as resolved"
            
    except MySQLError as e:
        return False, f"❌ Error: {str(e)}"


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

def start(update, context):
    """Start command handler"""
    update.message.reply_text("Hello! This is the Dark Web Monitoring Integration Module. Use /check to search for user credentials on the dark web.")

def check(update, context):
    """Check command handler"""
    user_input = update.message.text
    if user_input.startswith("/check"):
        query_term = user_input[6:]
        findings = check_darkweb_mock(query_term)
        update.message.reply_text(f"Mock findings for {query_term}: {findings}")
    else:
        update.message.reply_text("Please use /check followed by a query term (email, phone, etc.)")


application = Application.builder().token("YOUR_BOT_TOKEN").build()
