#!/usr/bin/env python3
"""
Fixed database setup script for 3 new features
- Removes IF NOT EXISTS from ALTER TABLE (not supported in MySQL < 8.0.15)
- Handles existing columns gracefully
- Provides detailed progress feedback
"""

import mysql.connector
from mysql.connector import Error
import sys

# MySQL Configuration
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'fyp_user',
    'password': 'Admin123!',
    'database': 'fyp_osint',
    'autocommit': True
}

def test_connection():
    """Test MySQL connection"""
    try:
        conn = mysql.connector.connect(**config)
        print("🔄 Connecting to MySQL...")
        print("✅ MySQL connection successful!")
        return conn
    except Error as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def execute_statement(cursor, sql):
    """Execute single SQL statement, handle IF EXISTS gracefully"""
    try:
        cursor.execute(sql)
        return True, None
    except Error as e:
        error_msg = str(e)
        # Ignore "column already exists" errors - we're adding optional columns
        if "already exists" in error_msg or "Duplicate" in error_msg:
            return True, f"(Already exists - skipped): {error_msg}"
        return False, error_msg

def main():
    conn = test_connection()
    cursor = conn.cursor()

    print("\n📊 Setting up 3 new features...\n")

    # ============================================================================
    # CREATE NEW TABLES
    # ============================================================================
    
    create_statements = [
        # Feature 1: Monitoring
        """
        CREATE TABLE IF NOT EXISTS monitoring_subscriptions (
            subscription_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            data_target VARCHAR(255) NOT NULL,
            target_type ENUM('email', 'phone', 'username', 'credit_card') NOT NULL,
            check_frequency ENUM('daily', 'weekly', 'monthly') DEFAULT 'weekly',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_checked_at TIMESTAMP NULL,
            next_check_at TIMESTAMP NULL,
            INDEX idx_user_id (user_id),
            INDEX idx_active (is_active)
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS breach_timeline (
            timeline_id INT PRIMARY KEY AUTO_INCREMENT,
            investigation_log_id INT NOT NULL,
            breach_occurred_date DATE NOT NULL,
            breach_discovered_date DATE NOT NULL,
            days_to_discovery INT GENERATED ALWAYS AS (
                DATEDIFF(breach_discovered_date, breach_occurred_date)
            ) STORED,
            timeline_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_investigation_id (investigation_log_id),
            INDEX idx_breach_date (breach_occurred_date)
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS scheduled_checks (
            check_id INT PRIMARY KEY AUTO_INCREMENT,
            subscription_id INT NOT NULL,
            check_type ENUM('automatic', 'manual') DEFAULT 'automatic',
            executed_at TIMESTAMP NULL,
            found_new_breach BOOLEAN DEFAULT FALSE,
            result_summary TEXT,
            next_scheduled_run TIMESTAMP NULL,
            FOREIGN KEY (subscription_id) REFERENCES monitoring_subscriptions(subscription_id),
            INDEX idx_subscription_id (subscription_id),
            INDEX idx_executed_at (executed_at)
        )
        """,
        
        # Feature 2: Dark Web
        """
        CREATE TABLE IF NOT EXISTS darkweb_findings (
            finding_id INT PRIMARY KEY AUTO_INCREMENT,
            investigation_log_id INT NOT NULL,
            platform_name VARCHAR(100) NOT NULL,
            exposure_type ENUM('breached_database', 'paste_site', 'public_forum', 'marketplace', 'unknown') NOT NULL,
            exposure_snippet VARCHAR(500) NOT NULL,
            severity_level ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW') DEFAULT 'MEDIUM',
            first_detected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_resolved BOOLEAN DEFAULT FALSE,
            resolved_date TIMESTAMP NULL,
            mitigation_notes TEXT,
            INDEX idx_investigation_id (investigation_log_id),
            INDEX idx_severity (severity_level)
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS darkweb_check_history (
            check_history_id INT PRIMARY KEY AUTO_INCREMENT,
            investigation_log_id INT NOT NULL,
            check_performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_findings_count INT DEFAULT 0,
            critical_findings_count INT DEFAULT 0,
            high_findings_count INT DEFAULT 0,
            medium_findings_count INT DEFAULT 0,
            low_findings_count INT DEFAULT 0,
            risk_score_at_check INT DEFAULT 0,
            check_notes TEXT,
            INDEX idx_investigation_id (investigation_log_id),
            INDEX idx_check_date (check_performed_at)
        )
        """,
        
        # Feature 3: Data Analysis
        """
        CREATE TABLE IF NOT EXISTS breach_details_enhanced (
            enhanced_id INT PRIMARY KEY AUTO_INCREMENT,
            investigation_log_id INT NOT NULL,
            hash_algorithm_detected VARCHAR(50),
            hash_detection_confidence INT DEFAULT 0,
            exposed_data_types JSON,
            composite_risk_score INT DEFAULT 0,
            forensic_report TEXT,
            analysis_completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_investigation_id (investigation_log_id)
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS data_type_risk_matrix (
            data_type_id INT PRIMARY KEY AUTO_INCREMENT,
            data_type_name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            risk_score INT DEFAULT 5,
            is_pii BOOLEAN DEFAULT FALSE,
            is_payment_related BOOLEAN DEFAULT FALSE,
            remediation_priority ENUM('critical', 'high', 'medium', 'low') DEFAULT 'medium',
            example_values VARCHAR(255)
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS hash_algorithm_index (
            algorithm_id INT PRIMARY KEY AUTO_INCREMENT,
            algorithm_name VARCHAR(50) NOT NULL UNIQUE,
            is_broken BOOLEAN DEFAULT FALSE,
            vulnerability_year INT,
            crack_speed VARCHAR(100),
            estimated_cost_per_crack_usd DECIMAL(10, 2) DEFAULT 0,
            recommendation VARCHAR(50),
            notes TEXT
        )
        """
    ]
    
    print("Creating new tables...\n")
    success_count = 0
    for i, stmt in enumerate(create_statements, 1):
        try:
            cursor.execute(stmt)
            table_name = stmt.split("CREATE TABLE IF NOT EXISTS")[1].split("(")[0].strip()
            print(f"  ✓ Created table: {table_name}")
            success_count += 1
        except Error as e:
            error_msg = str(e)
            if "already exists" in error_msg:
                table_name = stmt.split("CREATE TABLE IF NOT EXISTS")[1].split("(")[0].strip()
                print(f"  ✓ Table exists: {table_name}")
                success_count += 1
            else:
                print(f"  ❌ Error on statement {i}: {error_msg}")
    
    # ============================================================================
    # INSERT SEED DATA
    # ============================================================================
    
    print("\nInserting seed data...\n")
    
    # Data types reference
    seed_data_types = """
    INSERT INTO data_type_risk_matrix 
    (data_type_name, description, risk_score, is_pii, is_payment_related, remediation_priority, example_values)
    VALUES
    ('Email Address', 'User email used for identification and password recovery', 10, TRUE, FALSE, 'high', 'user@example.com'),
    ('Phone Number', 'Telephone number used for SMS verification and contact', 8, TRUE, FALSE, 'high', '+60123456789'),
    ('Credit Card Number', 'Full or partial card numbers', 25, TRUE, TRUE, 'critical', '****-****-****-1234'),
    ('Bank Account Number', 'Account numbers for financial accounts', 20, TRUE, TRUE, 'critical', '012345678901'),
    ('Passport/ID Number', 'Government identification numbers (MyKad, Passport)', 22, TRUE, FALSE, 'critical', '123456-XX-XXXX'),
    ('Full Name', 'Complete name of individual', 5, TRUE, FALSE, 'medium', 'Ahmad bin Mohamed'),
    ('Date of Birth', 'Birth date potentially linked to password generation', 8, TRUE, FALSE, 'medium', '1990-05-15'),
    ('Address', 'Home or work address', 7, TRUE, FALSE, 'medium', '123 Jalan Merdeka'),
    ('Password Hash', 'Hashed password (difficulty depends on algorithm)', 30, FALSE, FALSE, 'critical', 'sha256hash...'),
    ('Social Security/EPF Number', 'Government benefits or employment ID numbers', 18, TRUE, FALSE, 'critical', 'TP123456789'),
    ('Medical/Health Records', 'Personal health information and medical history', 28, TRUE, FALSE, 'critical', '[Redacted for privacy]')
    ON DUPLICATE KEY UPDATE
        risk_score = VALUES(risk_score),
        is_pii = VALUES(is_pii);
    """
    
    # Hash algorithms reference
    seed_hash_algorithms = """
    INSERT INTO hash_algorithm_index 
    (algorithm_name, is_broken, vulnerability_year, crack_speed, estimated_cost_per_crack_usd, recommendation, notes)
    VALUES
    ('MD5', TRUE, 2004, 'Very Fast (sec)', 0.00, 'DEPRECATED', 'Broken since 2004. Crackable in seconds with GPU. Example: hashcat can try billions per second.'),
    ('SHA1', TRUE, 2017, 'Very Fast (sec)', 0.01, 'DEPRECATED', 'Cryptographically broken. Practical collision attacks proven. Never use for passwords.'),
    ('SHA256', FALSE, NULL, 'Fast (min)', 0.05, 'ACCEPTABLE', 'Secure but no salt. Vulnerable to rainbow tables. Use salted version instead.'),
    ('SHA256 (Salted)', FALSE, NULL, 'Medium (hours)', 1.50, 'ACCEPTABLE', 'Secure with proper salt. Requires more resources but still feasible to crack.'),
    ('PBKDF2', FALSE, NULL, 'Medium (hours)', 2.00, 'ACCEPTABLE', 'Iterative hashing. Security depends on iteration count. Minimum 10,000+ iterations.'),
    ('bcrypt', FALSE, NULL, 'Slow (days)', 100.00, 'RECOMMENDED', 'Adaptive hashing. Built-in salt. Cost factor increases with time. Industry standard.'),
    ('Argon2', FALSE, NULL, 'Very Slow (impossible)', 1000.00, 'RECOMMENDED', 'Modern password hashing. Memory-hard and GPU-resistant. Preferred since 2015.'),
    ('scrypt', FALSE, NULL, 'Very Slow (impossible)', 500.00, 'RECOMMENDED', 'Memory-hard algorithm. Resistant to GPU/ASIC attacks. Good bcrypt alternative.')
    ON DUPLICATE KEY UPDATE
        is_broken = VALUES(is_broken),
        crack_speed = VALUES(crack_speed);
    """
    
    try:
        cursor.execute(seed_data_types)
        print("  ✓ Inserted seed data: 11 data types")
        success_count += 1
    except Error as e:
        print(f"  ❌ Error inserting data types: {e}")
    
    try:
        cursor.execute(seed_hash_algorithms)
        print("  ✓ Inserted seed data: 8 hash algorithms")
        success_count += 1
    except Error as e:
        print(f"  ❌ Error inserting hash algorithms: {e}")
    
    # ============================================================================
    # ALTER EXISTING TABLES (without IF NOT EXISTS - added in MySQL 8.0.15)
    # ============================================================================
    
    print("\nAdding columns to existing tables...\n")
    
    alter_statements = [
        ("ALTER TABLE breach_results ADD COLUMN hash_algorithm VARCHAR(50) NULL", "breach_results: hash_algorithm"),
        ("ALTER TABLE breach_results ADD COLUMN data_types JSON NULL", "breach_results: data_types"),
        ("ALTER TABLE breach_results ADD COLUMN crackability VARCHAR(50) NULL", "breach_results: crackability"),
        ("ALTER TABLE investigation_logs ADD COLUMN is_monitored BOOLEAN DEFAULT FALSE", "investigation_logs: is_monitored"),
        ("ALTER TABLE investigation_logs ADD COLUMN monitoring_subscription_id INT NULL", "investigation_logs: monitoring_subscription_id"),
        ("ALTER TABLE investigation_logs ADD COLUMN has_darkweb_findings BOOLEAN DEFAULT FALSE", "investigation_logs: has_darkweb_findings"),
        ("ALTER TABLE investigation_logs ADD INDEX idx_investigation_monitoring_id (monitoring_subscription_id)", "investigation_logs: index on monitoring_subscription_id"),
    ]
    
    for sql, description in alter_statements:
        success, error = execute_statement(cursor, sql)
        if success:
            if error:
                print(f"  ✓ {description} {error}")
            else:
                print(f"  ✓ Added column: {description}")
            success_count += 1
        else:
            print(f"  ⚠️ Error on {description}: {error}")
    
    # ============================================================================
    # VERIFICATION
    # ============================================================================
    
    print("\n" + "="*70)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*70)
    print(f"\n📊 Operations completed: {success_count}")
    print("\n📋 Tables created:")
    tables_to_check = [
        'monitoring_subscriptions',
        'breach_timeline', 
        'scheduled_checks',
        'darkweb_findings',
        'darkweb_check_history',
        'breach_details_enhanced',
        'data_type_risk_matrix',
        'hash_algorithm_index'
    ]
    
    for table in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            row = cursor.fetchone()
            count = row[0] if row else 0
            print(f"  ✓ {table}: {count} rows")
        except Error as e:
            print(f"  ? {table}: Unable to verify")
    
    print("\n✨ Next steps:")
    print("  1. Restart Flask app: python app.py")
    print("  2. Visit http://localhost:5000/monitoring (Real-Time Monitoring)")
    print("  3. Visit http://localhost:5000/darkweb/check/1 (Dark Web Check)")
    print("  4. Visit http://localhost:5000/analysis/data-types/1 (Data Type Analysis)")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
