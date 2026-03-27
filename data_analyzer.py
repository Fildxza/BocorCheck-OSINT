"""
Data Type Analysis + Hashing Algorithm Detector Module
Analyzes what data types were exposed and password crackability
Perfect for forensic-level breach analysis
"""

from typing import List, Dict, Any, Optional, Tuple
from mysql.connector import connect, Error as MySQLError
import os
import json
import re


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
# FEATURE 1: Analyze Breach Data Types
# ============================================================================

def analyze_breach_datatypes(
    investigation_id: int,
    breach_name: str,
    data_exposed_text: str
) -> Dict[str, Any]:
    """
    Analyze what types of data were exposed in a breach
    Returns categorized data types with risk scores
    
    Args:
        investigation_id: Investigation ID
        breach_name: Name of breach
        data_exposed_text: Description of exposed data
        
    Returns:
        Dictionary with identified data types and risks
    """
    
    # Data type patterns (what to look for)
    data_type_patterns = {
        'Email Address': [r'email', r'mail address', r'user email'],
        'Password': [r'password', r'pwd', r'pass', r'hash', r'plaintext'],
        'Name': [r'\bname\b', r'full name', r'first name', r'last name'],
        'Phone Number': [r'phone', r'mobile', r'cellphone', r'tel'],
        'IC Number': [r'\bic\b', r'identification number', r'id number', r'nric'],
        'Credit Card': [r'credit card', r'card number', r'cc number', r'visa'],
        'Bank Account': [r'bank account', r'account number', r'iban'],
        'Date of Birth': [r'dob', r'birth date', r'birthday'],
        'Address': [r'address', r'street', r'zip code', r'postal'],
        'Username': [r'username', r'userid', r'user id', r'login name'],
        'IP Address': [r'ip address', r'ip\s+addr', r'ipv4', r'ipv6'],
        'Social Media': [r'twitter', r'facebook', r'instagram', r'tiktok', r'reddit'],
    }
    
    found_types = []
    
    # Search for each data type
    for data_type, patterns in data_type_patterns.items():
        for pattern in patterns:
            if re.search(pattern, data_exposed_text, re.IGNORECASE):
                if data_type not in found_types:
                    found_types.append(data_type)
                break
    
    # If no specific types found, make educated guesses
    if not found_types:
        found_types = ['Email Address', 'Username']
    
    # Get risk scores for each data type
    cfg = get_db_config()
    risk_data = {}
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            for data_type in found_types:
                cursor.execute("""
                    SELECT base_risk_score, risk_level, description
                    FROM data_type_risk_matrix
                    WHERE data_type = %s
                """, (data_type,))
                
                result = cursor.fetchone()
                if result:
                    risk_data[data_type] = {
                        'risk_score': result['base_risk_score'],
                        'risk_level': result['risk_level'],
                        'description': result['description']
                    }
    
    except MySQLError as e:
        print(f"Error fetching risk data: {e}")
    
    # Calculate composite risk score
    total_risk = sum(data.get('risk_score', 50) for data in risk_data.values())
    avg_risk = total_risk / len(risk_data) if risk_data else 50
    
    return {
        'data_types': found_types,
        'data_type_risks': risk_data,
        'composite_risk_score': int(avg_risk),
        'count': len(found_types)
    }


# ============================================================================
# FEATURE 2: Detect Hash Algorithm from Breach Info
# ============================================================================

def detect_hash_algorithm(
    password_samples: Optional[List[str]] = None,
    breach_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Detect hash algorithm used in a breach based on:
    1. Hash format/length (if samples available)
    2. Keywords in breach description
    
    Args:
        password_samples: List of password hashes from breach
        breach_description: Description mentioning hash type
        
    Returns:
        Dictionary with detected algorithm and confidence
    """
    
    detected = {
        'algorithm': 'Unknown',
        'confidence': 0,
        'is_salted': False,
        'is_broken': True,
        'crackability': 'Very High',
        'evidence': []
    }
    
    # Check breach description for hash mentions
    if breach_description:
        description = breach_description.lower()
        
        hash_keywords = {
            'MD5': ['md5', 'md-5'],
            'SHA1': ['sha1', 'sha-1'],
            'SHA256': ['sha256', 'sha-256', 'sha2'],
            'bcrypt': ['bcrypt', 'blowfish'],
            'PBKDF2': ['pbkdf2', 'pbkdf'],
            'Argon2': ['argon2'],
            'scrypt': ['scrypt']
        }
        
        for algo, keywords in hash_keywords.items():
            for keyword in keywords:
                if keyword in description:
                    detected['algorithm'] = algo
                    detected['confidence'] = 85
                    detected['evidence'].append(f"Keyword: {keyword}")
                    break
    
    # Analyze password samples if provided
    if password_samples and len(password_samples) > 0:
        sample = password_samples[0]
        sample_len = len(sample)
        
        # Hash length analysis
        hash_patterns = {
            32: {'algo': 'MD5', 'confidence': 90},
            40: {'algo': 'SHA1', 'confidence': 90},
            44: {'algo': 'bcrypt', 'confidence': 85},
            60: {'algo': 'bcrypt', 'confidence': 95},
            64: {'algo': 'SHA256', 'confidence': 85},
            128: {'algo': 'SHA512', 'confidence': 85},
        }
        
        if sample_len in hash_patterns:
            pattern = hash_patterns[sample_len]
            if detected['confidence'] < pattern['confidence']:
                detected['algorithm'] = pattern['algo']
                detected['confidence'] = pattern['confidence']
                detected['evidence'].append(f"Hash length: {sample_len} chars")
        
        # Check for bcrypt prefix
        if sample.startswith('$2a$') or sample.startswith('$2b$') or sample.startswith('$2x$'):
            detected['algorithm'] = 'bcrypt'
            detected['confidence'] = 99
            detected['is_salted'] = True
            detected['evidence'].append("bcrypt prefix detected ($2a$/$2b$/$2x$)")
        
        # Check for other prefixed algorithms
        if sample.startswith('$'):
            detected['is_salted'] = True
    
    # Get vulnerability info from database
    if detected['algorithm'] != 'Unknown':
        try:
            cfg = get_db_config()
            with connect(**cfg) as conn:
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT is_broken, crack_speed, recommendation, notes
                    FROM hash_algorithm_index
                    WHERE algorithm_name = %s
                """, (detected['algorithm'],))
                
                result = cursor.fetchone()
                if result:
                    detected['is_broken'] = result['is_broken']
                    detected['crackability'] = result['crack_speed']
                    detected['recommendation'] = result['recommendation']
                    detected['notes'] = result['notes']
        
        except MySQLError as e:
            print(f"Error fetching algorithm info: {e}")
    
    return detected


# ============================================================================
# FEATURE 3: Calculate Password Crackability Score
# ============================================================================

def calculate_crack_risk(algorithm_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate how vulnerable passwords are to cracking
    Based on algorithm, salt, and iterations
    
    Args:
        algorithm_info: Result from detect_hash_algorithm()
        
    Returns:
        Crackability assessment
    """
    
    algorithm = algorithm_info.get('algorithm', 'Unknown')
    
    # Cracking difficulty scores (0-100, higher = easier to crack)
    crack_scores = {
        'MD5': 95,        # Can crack in seconds
        'SHA1': 90,       # Can crack in minutes
        'SHA256': 70,     # Takes hours without GPU
        'PBKDF2': 40,     # Iterative, much slower
        'bcrypt': 10,     # Very slow, adaptive
        'Argon2': 5,      # Memory-hard, very slow
        'scrypt': 8,      # Memory-hard, very slow
        'Unknown': 50     # Assume medium difficulty
    }
    
    base_score = crack_scores.get(algorithm, 50)
    
    # Adjust if salted (makes it harder)
    if algorithm_info.get('is_salted'):
        base_score *= 0.7  # 30% harder if salted
    
    # Adjust if broken (easier)
    if algorithm_info.get('is_broken'):
        base_score *= 1.2  # 20% easier if cryptographically broken
    
    # Round and cap
    final_score = min(int(base_score), 100)
    
    # Determine crackability level
    if final_score >= 80:
        level = "🔴 VERY HIGH - Can crack in seconds"
        recommendation = "URGENT: Change password immediately"
    elif final_score >= 60:
        level = "🟠 HIGH - Can crack in minutes/hours"
        recommendation = "Change password soon"
    elif final_score >= 40:
        level = "🟡 MEDIUM - Can crack in hours/days"
        recommendation = "Monitor account activity"
    elif final_score >= 20:
        level = "🟢 LOW - Would take days/weeks"
        recommendation = "Monitor account, but acceptable risk"
    else:
        level = "🟢 VERY LOW - Would take months/years"
        recommendation = "Minimal risk, but stay vigilant"
    
    return {
        'crackability_score': final_score,
        'crackability_level': level,
        'recommendation': recommendation,
        'algorithm': algorithm,
        'factors': {
            'hash_algorithm': base_score,
            'is_salted': algorithm_info.get('is_salted'),
            'is_broken': algorithm_info.get('is_broken')
        }
    }


# ============================================================================
# FEATURE 4: Generate Forensic Report
# ============================================================================

def generate_forensic_report(
    investigation_id: int,
    breach_name: str,
    data_exposed_text: str
) -> Dict[str, Any]:
    """
    Generate comprehensive forensic report for a breach
    Combines data type analysis + hash algorithm detection + risk scoring
    
    Args:
        investigation_id: Investigation ID
        breach_name: Name of breach
        data_exposed_text: Description of exposed data
        
    Returns:
        Complete forensic report
    """
    
    # Analyze data types
    datatype_analysis = analyze_breach_datatypes(
        investigation_id, breach_name, data_exposed_text
    )
    
    # Detect hash algorithms (using description only)
    hash_analysis = detect_hash_algorithm(
        breach_description=data_exposed_text
    )
    
    # Calculate crack risk
    crack_risk = calculate_crack_risk(hash_analysis)
    
    # Calculate overall risk
    datatype_risk = datatype_analysis.get('composite_risk_score', 50)
    crack_risk_factor = crack_risk.get('crackability_score', 50)
    
    # Weighted composite: 60% data type, 40% crackability
    overall_risk = (datatype_risk * 0.6) + (crack_risk_factor * 0.4)
    overall_risk = int(overall_risk)
    
    if overall_risk >= 80:
        overall_level = "CRITICAL"
    elif overall_risk >= 60:
        overall_level = "HIGH"
    elif overall_risk >= 40:
        overall_level = "MEDIUM"
    else:
        overall_level = "LOW"
    
    report = {
        'breach_name': breach_name,
        'investigation_id': investigation_id,
        'timestamp': str(__import__('datetime').datetime.now()),
        
        'data_types': datatype_analysis['data_types'],
        'datatype_risks': datatype_analysis['data_type_risks'],
        'datatype_composite_score': datatype_analysis['composite_risk_score'],
        
        'hash_algorithm': hash_analysis['algorithm'],
        'hash_confidence': hash_analysis['confidence'],
        'hash_is_salted': hash_analysis['is_salted'],
        'hash_is_broken': hash_analysis['is_broken'],
        'hash_crackability': hash_analysis.get('crackability', 'Unknown'),
        
        'password_crack_risk': crack_risk,
        
        'overall_risk_score': overall_risk,
        'overall_risk_level': overall_level,
        
        'forensic_summary': generate_summary(datatype_analysis, hash_analysis, crack_risk)
    }
    
    return report


# ============================================================================
# FEATURE 5: Generate Forensic Summary (Human-Readable)
# ============================================================================

def generate_summary(
    datatype_analysis: Dict,
    hash_analysis: Dict,
    crack_risk: Dict
) -> str:
    """
    Generate human-readable forensic summary
    """
    
    summary = []
    
    # Data types
    summary.append("📊 DATA TYPES EXPOSED:")
    for dtype, risk_info in datatype_analysis['data_type_risks'].items():
        summary.append(f"  • {dtype}: {risk_info['risk_level']} Risk (Score: {risk_info['risk_score']}/100)")
        summary.append(f"    - {risk_info.get('description', 'N/A')}")
    
    # Hash algorithm
    summary.append(f"\n🔐 PASSWORD HASH ALGORITHM:")
    summary.append(f"  • Detected: {hash_analysis['algorithm']}")
    summary.append(f"  • Confidence: {hash_analysis['confidence']}%")
    summary.append(f"  • Salted: {'Yes ✓' if hash_analysis['is_salted'] else 'No ✗'}")
    summary.append(f"  • Cryptographically Broken: {'Yes ⚠️' if hash_analysis['is_broken'] else 'No ✓'}")
    
    # Crackability
    summary.append(f"\n⚡ PASSWORD CRACKABILITY:")
    summary.append(f"  • {crack_risk['crackability_level']}")
    summary.append(f"  • Score: {crack_risk['crackability_score']}/100")
    summary.append(f"  • Recommendation: {crack_risk['recommendation']}")
    
    return "\n".join(summary)


# ============================================================================
# FEATURE 6: Store Enhanced Breach Details
# ============================================================================

def store_enhanced_breach_details(
    investigation_id: int,
    breach_name: str,
    data_types: List[str],
    hash_algorithm: Optional[str] = None,
    hash_salted: Optional[bool] = None,
    crackability: Optional[str] = None,
    crackability_explanation: Optional[str] = None
) -> bool:
    """
    Store enhanced breach details in database for later retrieval
    
    Args:
        investigation_id: Investigation ID
        breach_name: Name of breach
        data_types: List of exposed data types
        hash_algorithm: Detected hash algorithm
        hash_salted: Whether password was salted
        crackability: Estimated crackability level
        crackability_explanation: Explanation of risk
        
    Returns:
        Success status
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            
            # Convert list to JSON
            data_types_json = json.dumps(data_types)
            
            cursor.execute("""
                INSERT INTO breach_details_enhanced 
                (investigation_id, breach_name, data_types, hash_algorithm, 
                 hash_salted, crackability, crackability_explanation)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    data_types = VALUES(data_types),
                    hash_algorithm = VALUES(hash_algorithm),
                    hash_salted = VALUES(hash_salted),
                    crackability = VALUES(crackability),
                    crackability_explanation = VALUES(crackability_explanation),
                    updated_at = CURRENT_TIMESTAMP
            """, (investigation_id, breach_name, data_types_json, hash_algorithm,
                  hash_salted, crackability, crackability_explanation))
            
            conn.commit()
            return True
            
    except MySQLError as e:
        print(f"Error storing breach details: {e}")
        return False


# ============================================================================
# FEATURE 7: Get All Data Type Risk Matrix (For Reference)
# ============================================================================

def get_data_type_risk_reference() -> List[Dict[str, Any]]:
    """
    Get complete data type risk matrix for display
    
    Returns:
        List of all data types with risk info
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    data_type, base_risk_score, risk_level,
                    description, remediation_steps
                FROM data_type_risk_matrix
                ORDER BY base_risk_score DESC
            """)
            
            return cursor.fetchall()
            
    except MySQLError as e:
        print(f"Error fetching risk matrix: {e}")
        return []


# ============================================================================
# FEATURE 8: Get Hash Algorithm Reference
# ============================================================================

def get_hash_algorithm_reference() -> List[Dict[str, Any]]:
    """
    Get complete hash algorithm vulnerability info
    
    Returns:
        List of all algorithms with vulnerability info
    """
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    algorithm_name, is_broken, vulnerability_year,
                    crack_speed, estimated_cost_per_crack_usd,
                    recommendation, notes
                FROM hash_algorithm_index
                ORDER BY is_broken DESC, crack_speed ASC
            """)
            
            return cursor.fetchall()
            
    except MySQLError as e:
        print(f"Error fetching algorithm reference: {e}")
        return []
