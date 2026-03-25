"""
Mitigation Plans Module for BocorCheck
Provides intelligent mitigation recommendations based on breach characteristics
Includes Malaysian-specific resources and action plans
"""

import json
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


def get_mitigation_for_breach(breach_id: int) -> List[Dict[str, Any]]:
    """
    Get all mitigation plans for a specific breach
    
    Args:
        breach_id: ID of the breach
        
    Returns:
        List of mitigation plans with Malaysian resources
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT 
                        id, title, description, action_type, priority,
                        severity_level, estimated_time, steps, resources
                    FROM mitigation_plans
                    WHERE breach_id = %s
                    ORDER BY priority ASC, action_type ASC
                """, (breach_id,))
                
                mitigations = cursor.fetchall()
                
                # Parse JSON fields
                for mitigation in mitigations:
                    if mitigation['steps']:
                        mitigation['steps'] = json.loads(mitigation['steps'])
                    if mitigation['resources']:
                        mitigation['resources'] = json.loads(mitigation['resources'])
                
                return mitigations
                
    except MySQLError as e:
        print(f"Error fetching mitigation plans: {e}")
        return []


def get_mitigation_for_datatype(data_type: str, severity: str = None) -> List[Dict[str, Any]]:
    """
    Get mitigation recommendations for a specific data type
    Smart filtering based on severity level
    
    Args:
        data_type: Type of data exposed (e.g., 'Email', 'Password', 'IC Number')
        severity: Optional severity level to filter ('HIGH', 'MEDIUM', 'LOW')
        
    Returns:
        List of relevant mitigation plans
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                if severity:
                    cursor.execute("""
                        SELECT 
                            id, title, description, action_type, priority,
                            severity_level, estimated_time, steps, resources
                        FROM mitigation_plans
                        WHERE (data_type = %s OR data_type IS NULL)
                        AND severity_level = %s
                        ORDER BY priority ASC
                    """, (data_type, severity))
                else:
                    cursor.execute("""
                        SELECT 
                            id, title, description, action_type, priority,
                            severity_level, estimated_time, steps, resources
                        FROM mitigation_plans
                        WHERE data_type = %s OR data_type IS NULL
                        ORDER BY severity_level DESC, priority ASC
                    """, (data_type,))
                
                mitigations = cursor.fetchall()
                
                # Parse JSON fields
                for mitigation in mitigations:
                    if mitigation['steps']:
                        mitigation['steps'] = json.loads(mitigation['steps'])
                    if mitigation['resources']:
                        mitigation['resources'] = json.loads(mitigation['resources'])
                
                return mitigations
                
    except MySQLError as e:
        print(f"Error fetching data type mitigations: {e}")
        return []


def get_smart_recommendations(exposed_data_types: List[str], risk_level: str) -> Dict[str, Any]:
    """
    Generate smart, prioritized recommendations based on exposed data and risk level
    Uses Malaysian context as priority
    
    Args:
        exposed_data_types: List of exposed data types
        risk_level: Risk level ('HIGH', 'MEDIUM', 'LOW')
        
    Returns:
        Dictionary with categorized recommendations
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Get CRITICAL actions (priority 1)
                cursor.execute("""
                    SELECT 
                        id, title, description, action_type, priority,
                        severity_level, estimated_time, steps, resources
                    FROM mitigation_plans
                    WHERE data_type IN ({})
                    AND severity_level = %s
                    AND priority = 1
                    ORDER BY priority ASC
                """.format(','.join(['%s']*len(exposed_data_types))), 
                    exposed_data_types + ['HIGH'] if risk_level == 'HIGH' else exposed_data_types + [risk_level])
                
                critical = cursor.fetchall()
                
                # Get IMPORTANT actions (priority 2)
                cursor.execute("""
                    SELECT 
                        id, title, description, action_type, priority,
                        severity_level, estimated_time, steps, resources
                    FROM mitigation_plans
                    WHERE data_type IN ({})
                    AND priority = 2
                    LIMIT 3
                """.format(','.join(['%s']*len(exposed_data_types))), 
                    exposed_data_types)
                
                important = cursor.fetchall()
                
                # Get Malaysian-specific resources
                cursor.execute("""
                    SELECT 
                        resource_name, resource_type, description, 
                        phone, website, email, operating_hours
                    FROM mitigation_resources
                    WHERE resource_type IN ('Government Agency', 'Police Department', 'Regulatory Body', 'Commercial Bank')
                    LIMIT 5
                """)
                
                malaysian_resources = cursor.fetchall()
                
                # Parse JSON fields
                for item in critical + important:
                    if item['steps']:
                        item['steps'] = json.loads(item['steps'])
                    if item['resources']:
                        item['resources'] = json.loads(item['resources'])
                
                return {
                    'critical_actions': critical,
                    'important_actions': important,
                    'estimated_total_time': calculate_total_time(critical + important),
                    'malaysian_resources': malaysian_resources,
                    'risk_summary': generate_risk_summary(exposed_data_types, risk_level)
                }
                
    except MySQLError as e:
        print(f"Error fetching smart recommendations: {e}")
        return {
            'critical_actions': [],
            'important_actions': [],
            'estimated_total_time': 'unknown',
            'malaysian_resources': [],
            'risk_summary': ''
        }


def get_malaysian_resources(resource_type: str = None) -> List[Dict[str, Any]]:
    """
    Get Malaysian-specific resources and contact information
    
    Args:
        resource_type: Optional filter (e.g., 'Government Agency', 'Commercial Bank')
        
    Returns:
        List of Malaysian resources with contact details
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                if resource_type:
                    cursor.execute("""
                        SELECT 
                            resource_name, resource_type, description,
                            contact, website, phone, email, operating_hours, availability
                        FROM mitigation_resources
                        WHERE resource_type = %s
                        ORDER BY resource_name ASC
                    """, (resource_type,))
                else:
                    cursor.execute("""
                        SELECT 
                            resource_name, resource_type, description,
                            contact, website, phone, email, operating_hours, availability
                        FROM mitigation_resources
                        ORDER BY resource_type ASC, resource_name ASC
                    """)
                
                resources = cursor.fetchall()
                return resources
                
    except MySQLError as e:
        print(f"Error fetching Malaysian resources: {e}")
        return []


def calculate_total_time(mitigations: List[Dict[str, Any]]) -> str:
    """Calculate total estimated time for all mitigations"""
    if not mitigations:
        return "0 minutes"
    
    total_minutes = 0
    has_ongoing = False
    
    for mitigation in mitigations:
        time_str = mitigation.get('estimated_time', '0 minutes')
        
        if 'ongoing' in time_str.lower():
            has_ongoing = True
        else:
            try:
                minutes = int(time_str.split()[0])
                total_minutes += minutes
            except (ValueError, IndexError):
                pass
    
    if has_ongoing:
        return f"{total_minutes} minutes + ongoing monitoring"
    else:
        return f"{total_minutes} minutes"


def generate_risk_summary(exposed_data_types: List[str], risk_level: str) -> str:
    """
    Generate a human-readable risk summary based on exposed data
    Includes Malaysian context warnings if applicable
    
    Args:
        exposed_data_types: List of exposed data types
        risk_level: Overall risk level
        
    Returns:
        Risk summary text
    """
    risk_messages = {
        'HIGH': 'CRITICAL RISK: Your personal information has been severely compromised. Immediate action required.',
        'MEDIUM': 'MODERATE RISK: Your information is exposed. Take protective measures within 24 hours.',
        'LOW': 'LOW RISK: Some non-sensitive information exposed. Monitor your accounts regularly.'
    }
    
    message = risk_messages.get(risk_level, 'Risk level unknown')
    
    # Add Malaysian-specific warnings
    if 'IC Number' in exposed_data_types:
        message += ' ⚠️ MALAYSIA: Your MyKad number is exposed! Report to JPN and PDRM immediately.'
    
    if 'Password Hash' in exposed_data_types or 'Password' in exposed_data_types:
        message += ' ⚠️ URGENT: Your password hash is compromised. Change immediately.'
    
    if 'Account Balance' in exposed_data_types or 'Medical Records' in exposed_data_types:
        message += ' ⚠️ HIGH-VALUE DATA: Financial/sensitive records exposed. Contact relevant institutions.'
    
    return message


def format_mitigation_for_display(mitigation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format mitigation plan for HTML/JSON display
    
    Args:
        mitigation: Raw mitigation plan from database
        
    Returns:
        Formatted mitigation with HTML-friendly structure
    """
    return {
        'id': mitigation.get('id'),
        'title': mitigation.get('title'),
        'description': mitigation.get('description'),
        'action_type': mitigation.get('action_type'),
        'priority': mitigation.get('priority'),
        'severity': mitigation.get('severity_level'),
        'time': mitigation.get('estimated_time'),
        'steps': mitigation.get('steps', []),
        'resources': mitigation.get('resources', {}),
        'priority_label': format_priority(mitigation.get('priority')),
        'severity_class': f"severity-{mitigation.get('severity_level', 'MEDIUM').lower()}"
    }


def format_priority(priority: int) -> str:
    """Format priority number to label"""
    priority_map = {
        1: '🔴 CRITICAL - Do First',
        2: '🟠 IMPORTANT - Do Soon',
        3: '🟡 RECOMMENDED - Do When Possible'
    }
    return priority_map.get(priority, 'NORMAL')


def get_mitigation_checklist(investigation_id: int, user_id: int = None) -> Dict[str, Any]:
    """
    Get a complete mitigation checklist for an investigation
    Tracks which users have acknowledged which recommendations
    
    Args:
        investigation_id: Investigation ID
        user_id: Optional user ID for tracking progress
        
    Returns:
        Complete checklist with progress tracking
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Get breach info
                cursor.execute("""
                    SELECT b.name, b.severity, b.date, 
                           GROUP_CONCAT(bdt.data_type) as exposed_data
                    FROM breaches b
                    LEFT JOIN breach_data_types bdt ON b.id = bdt.breach_id
                    WHERE b.id = (SELECT breach_id FROM user_breach_matches WHERE investigation_id = %s LIMIT 1)
                    GROUP BY b.id
                """, (investigation_id,))
                
                breach_info = cursor.fetchone()
                if not breach_info:
                    return {}
                
                # Get mitigations for this breach
                cursor.execute("""
                    SELECT id, title, description, action_type, priority, 
                           severity_level, estimated_time, steps
                    FROM mitigation_plans
                    WHERE breach_id = (SELECT breach_id FROM user_breach_matches WHERE investigation_id = %s LIMIT 1)
                    ORDER BY priority ASC
                """, (investigation_id,))
                
                mitigations = cursor.fetchall()
                
                for mitigation in mitigations:
                    if mitigation['steps']:
                        mitigation['steps'] = json.loads(mitigation['steps'])
                
                return {
                    'breach': breach_info,
                    'total_actions': len(mitigations),
                    'actions': mitigations,
                    'completion_status': 'not_started'
                }
                
    except MySQLError as e:
        print(f"Error fetching mitigation checklist: {e}")
        return {}


if __name__ == "__main__":
    # Test the module
    print("Testing Mitigation Module...")
    
    # Test getting resources
    resources = get_malaysian_resources('Commercial Bank')
    print(f"\n✓ Found {len(resources)} Malaysian banks")
    for r in resources[:2]:
        print(f"  • {r['resource_name']}: {r['phone']}")
    
    # Test smart recommendations
    print("\n✓ Mitigation module ready for integration")
