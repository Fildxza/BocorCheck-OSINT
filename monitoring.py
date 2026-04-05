"""
Real-Time Monitoring + Breach Timeline Module
Handles automatic email/phone/bank monitoring and breach timeline tracking
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from mysql.connector import connect, Error as MySQLError
import os


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
# FEATURE 1: Create Monitoring Subscription
# ============================================================================

def create_monitoring_subscription(
    user_id: int,
    email: str,
    phone_number: Optional[str] = None,
    bank_account: Optional[str] = None,
    check_frequency: str = "weekly",
    notify_telegram: bool = False,
    notify_email: bool = True
) -> Tuple[bool, str]:
    """
    Create a monitoring subscription for automatic breach checking
    
    Args:
        user_id: User ID
        email: Email to monitor
        phone_number: Optional phone to monitor
        bank_account: Optional bank account to monitor
        check_frequency: 'daily', 'weekly', or 'monthly'
        notify_telegram: Enable Telegram notifications
        notify_email: Enable email notifications
        
    Returns:
        Tuple[success, message]
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            
            # Calculate next scheduled check
            freq_map = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30
            }
            days_offset = freq_map.get(check_frequency, 7)
            next_check = datetime.now() + timedelta(days=days_offset)
            
            cursor.execute("""
                INSERT INTO monitoring_subscriptions 
                (user_id, email, phone_number, bank_account, check_frequency, 
                 notify_telegram, notify_email, next_scheduled_check)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    check_frequency = VALUES(check_frequency),
                    is_active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, email, phone_number, bank_account, check_frequency, 
                  notify_telegram, notify_email, next_check))
            
            conn.commit()
            return True, f"✅ Monitoring added for {email}"
            
    except MySQLError as e:
        return False, f"❌ Error: {str(e)}"


# ============================================================================
# FEATURE 2: Get User's Active Monitoring
# ============================================================================

def get_user_monitoring(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all active monitoring subscriptions for a user
    
    Args:
        user_id: User ID
        
    Returns:
        List of monitoring subscriptions
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    id, email, phone_number, bank_account,
                    check_frequency, is_active,
                    last_checked, next_scheduled_check,
                    notify_telegram, notify_email,
                    created_at, updated_at
                FROM monitoring_subscriptions
                WHERE user_id = %s AND is_active = TRUE
                ORDER BY next_scheduled_check ASC
            """, (user_id,))
            
            return cursor.fetchall()
            
    except MySQLError as e:
        print(f"Error fetching monitoring: {e}")
        return []


# ============================================================================
# FEATURE 3: Get Breach Timeline for Visualization
# ============================================================================

def get_breach_timeline(investigation_id: int) -> List[Dict[str, Any]]:
    """
    Get breach timeline showing when breaches occurred and were discovered
    Perfect for visual timeline display
    
    Args:
        investigation_id: Investigation ID
        
    Returns:
        List of breaches with timeline data
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    bt.id,
                    bt.breach_name,
                    bt.breach_date,
                    bt.discovery_date,
                    bt.days_to_discovery,
                    bt.status,
                    bt.initial_risk_score,
                    bt.current_risk_score,
                    br.data_exposed,
                    br.hash_algorithm,
                    br.crackability
                FROM breach_timeline bt
                LEFT JOIN breach_results br ON bt.breach_name = br.breach_name COLLATE utf8mb4_unicode_ci
                WHERE bt.investigation_id = %s
                ORDER BY bt.breach_date DESC
            """, (investigation_id,))
            
            timeline = cursor.fetchall()
            
            # Calculate timeline metrics
            for event in timeline:
                if event['breach_date'] and event['discovery_date']:
                    delta = (event['discovery_date'] - event['breach_date']).days
                    event['time_to_discovery'] = delta
                    event['discovery_status'] = 'Quick' if delta < 30 else 'Delayed' if delta > 365 else 'Normal'
            
            return timeline
            
    except MySQLError as e:
        print(f"Error fetching breach timeline: {e}")
        return []


# ============================================================================
# FEATURE 4: Record Breach in Timeline
# ============================================================================

def record_breach_in_timeline(
    investigation_id: int,
    breach_name: str,
    breach_date: str,
    discovery_date: Optional[str] = None,
    status: str = "confirmed"
) -> bool:
    """
    Record a breach in the timeline for forensic analysis
    
    Args:
        investigation_id: Investigation ID
        breach_name: Name of breach
        breach_date: When breach occurred (format: YYYY-MM-DD)
        discovery_date: When it was discovered (format: YYYY-MM-DD)
        status: 'rumored', 'confirmed', 'patched'
        
    Returns:
        Success status
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            
            # Get current investigation risk score
            cursor.execute(
                "SELECT risk_score FROM investigation_logs WHERE id = %s",
                (investigation_id,)
            )
            result = cursor.fetchone()
            current_risk = result[0] if result else 50
            
            # Use discovery_date if provided, otherwise use today
            disc_date = discovery_date or datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute("""
                INSERT INTO breach_timeline 
                (investigation_id, breach_name, breach_date, discovery_date, 
                 status, initial_risk_score, current_risk_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    status = VALUES(status),
                    current_risk_score = VALUES(current_risk_score)
            """, (investigation_id, breach_name, breach_date, disc_date, 
                  status, 50, current_risk))
            
            conn.commit()
            return True
            
    except MySQLError as e:
        print(f"Error recording breach timeline: {e}")
        return False


# ============================================================================
# FEATURE 5: Get Timeline Statistics for Dashboard
# ============================================================================

def get_timeline_statistics(user_id: int) -> Dict[str, Any]:
    """
    Get statistics for dashboard: total breaches over time, risk trends, etc.
    
    Args:
        user_id: User ID
        
    Returns:
        Statistics dictionary
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get all breaches for this user
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_breaches,
                    MIN(bt.breach_date) as oldest_breach,
                    MAX(bt.breach_date) as newest_breach,
                    ROUND(AVG(DATEDIFF(bt.discovery_date, bt.breach_date))) as avg_discovery_days,
                    SUM(CASE WHEN bt.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_count,
                    ROUND(AVG(bt.current_risk_score)) as avg_risk_score
                FROM breach_timeline bt
                JOIN investigation_logs il ON bt.investigation_id = il.id
                WHERE il.user_id = %s
            """, (user_id,))
            
            stats = cursor.fetchone() or {}
            
            # Get breaches by year for timeline visualization
            cursor.execute("""
                SELECT 
                    YEAR(bt.breach_date) as year,
                    COUNT(*) as breach_count,
                    ROUND(AVG(bt.current_risk_score)) as avg_risk
                FROM breach_timeline bt
                JOIN investigation_logs il ON bt.investigation_id = il.id
                WHERE il.user_id = %s
                GROUP BY YEAR(bt.breach_date)
                ORDER BY year ASC
            """, (user_id,))
            
            yearly_stats = cursor.fetchall()
            stats['yearly_breakdown'] = yearly_stats
            
            return stats
            
    except MySQLError as e:
        print(f"Error fetching timeline stats: {e}")
        return {}


# ============================================================================
# FEATURE 6: Update Monitoring Check Status
# ============================================================================

def update_monitoring_check(
    subscription_id: int,
    breach_count: int,
    check_result: str = "completed"
) -> bool:
    """
    Update monitoring subscription after a check is performed
    
    Args:
        subscription_id: Monitoring subscription ID
        breach_count: Number of new breaches found
        check_result: 'completed', 'failed', 'skipped'
        
    Returns:
        Success status
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            
            # Get current frequency
            cursor.execute(
                "SELECT check_frequency FROM monitoring_subscriptions WHERE id = %s",
                (subscription_id,)
            )
            freq_result = cursor.fetchone()
            
            if not freq_result:
                return False
            
            check_frequency = freq_result[0]
            freq_map = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30
            }
            days_offset = freq_map.get(check_frequency, 7)
            next_check = datetime.now() + timedelta(days=days_offset)
            
            # Update last_checked and next_scheduled_check
            cursor.execute("""
                UPDATE monitoring_subscriptions
                SET 
                    last_checked = CURRENT_TIMESTAMP,
                    next_scheduled_check = %s
                WHERE id = %s
            """, (next_check, subscription_id))
            
            # Record in scheduled_checks table
            cursor.execute("""
                SELECT user_id FROM monitoring_subscriptions WHERE id = %s
            """, (subscription_id,))
            user_result = cursor.fetchone()
            
            if user_result:
                cursor.execute("""
                    INSERT INTO scheduled_checks 
                    (monitoring_subscription_id, user_id, check_type, 
                     scheduled_time, executed_time, status, breach_count_found)
                    VALUES (%s, %s, 'all', %s, CURRENT_TIMESTAMP, %s, %s)
                """, (subscription_id, user_result[0], datetime.now(), 
                      check_result, breach_count))
            
            conn.commit()
            return True
            
    except MySQLError as e:
        print(f"Error updating monitoring check: {e}")
        return False


# ============================================================================
# FEATURE 7: Get Pending Scheduled Checks
# ============================================================================

def get_pending_checks() -> List[Dict[str, Any]]:
    """
    Get all pending scheduled checks (for background job processing)
    
    Returns:
        List of pending checks
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    sc.id,
                    sc.monitoring_subscription_id,
                    sc.user_id,
                    ms.email,
                    ms.phone_number,
                    ms.bank_account,
                    sc.check_type,
                    sc.scheduled_time,
                    sc.status
                FROM scheduled_checks sc
                JOIN monitoring_subscriptions ms ON sc.monitoring_subscription_id = ms.id
                WHERE sc.status = 'pending'
                AND sc.scheduled_time <= CURRENT_TIMESTAMP
                ORDER BY sc.scheduled_time ASC
                LIMIT 10
            """)
            
            return cursor.fetchall()
            
    except MySQLError as e:
        print(f"Error fetching pending checks: {e}")
        return []


# ============================================================================
# FEATURE 8: Disable Monitoring
# ============================================================================

def disable_monitoring(subscription_id: int, user_id: int) -> Tuple[bool, str]:
    """
    Disable a monitoring subscription (soft delete)
    
    Args:
        subscription_id: Monitoring subscription ID
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
                SELECT user_id FROM monitoring_subscriptions 
                WHERE id = %s
            """, (subscription_id,))
            
            result = cursor.fetchone()
            if not result or result[0] != user_id:
                return False, "❌ Not authorized"
            
            cursor.execute("""
                UPDATE monitoring_subscriptions
                SET is_active = FALSE
                WHERE id = %s
            """, (subscription_id,))
            
            conn.commit()
            return True, "✅ Monitoring disabled"
            
    except MySQLError as e:
        return False, f"❌ Error: {str(e)}"
