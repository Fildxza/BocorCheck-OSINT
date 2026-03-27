-- ============================================================================
-- FYP OSINT - Database Schema Updates for 3 New Features
-- ============================================================================
-- Features:
-- 1. Real-Time Monitoring + Breach Timeline
-- 2. Dark Web Monitoring Integration
-- 3. Data Type Analysis + Hashing Algorithm Detector
-- ============================================================================

USE fyp_osint;

-- ============================================================================
-- FEATURE 1: Real-Time Monitoring + Breach Timeline
-- ============================================================================

-- Table 1.1: User Monitoring Subscriptions
CREATE TABLE IF NOT EXISTS monitoring_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(32) NULL,
    bank_account VARCHAR(50) NULL,
    
    -- Monitoring preferences
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    check_frequency VARCHAR(20) NOT NULL DEFAULT 'weekly', -- 'daily', 'weekly', 'monthly'
    last_checked DATETIME NULL,
    next_scheduled_check DATETIME NULL,
    
    -- Notification preferences
    notify_telegram BOOLEAN NOT NULL DEFAULT FALSE,
    notify_email BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_monitoring_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    INDEX idx_monitoring_user_id (user_id),
    INDEX idx_monitoring_active (is_active),
    INDEX idx_monitoring_next_check (next_scheduled_check),
    UNIQUE KEY unique_monitoring_user_email (user_id, email)
) ENGINE=InnoDB;

-- Table 1.2: Breach Timeline (Historical tracking)
CREATE TABLE IF NOT EXISTS breach_timeline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investigation_id INT NOT NULL,
    breach_name VARCHAR(255) NOT NULL,
    breach_date DATE NOT NULL,
    discovery_date DATE NOT NULL,
    
    -- Timeline metadata
    days_to_discovery INT NULL, -- How many days from breach to discovery
    status VARCHAR(50) NOT NULL DEFAULT 'confirmed', -- 'rumored', 'confirmed', 'patched'
    
    -- Risk tracking
    initial_risk_score INT NOT NULL,
    current_risk_score INT NOT NULL,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_timeline_investigation
        FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
    INDEX idx_timeline_investigation_id (investigation_id),
    INDEX idx_timeline_breach_date (breach_date),
    INDEX idx_timeline_discovery_date (discovery_date),
    INDEX idx_timeline_status (status)
) ENGINE=InnoDB;

-- Table 1.3: Scheduled Checks (Background job tracking)
CREATE TABLE IF NOT EXISTS scheduled_checks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_subscription_id INT NOT NULL,
    user_id INT NOT NULL,
    
    -- Check details
    check_type VARCHAR(50) NOT NULL, -- 'email', 'phone', 'bank', 'all'
    scheduled_time DATETIME NOT NULL,
    executed_time DATETIME NULL,
    
    -- Execution status
    status VARCHAR(30) NOT NULL DEFAULT 'pending', -- 'pending', 'executing', 'completed', 'failed'
    breach_count_found INT NULL,
    error_message TEXT NULL,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_scheduled_monitoring
        FOREIGN KEY (monitoring_subscription_id)
        REFERENCES monitoring_subscriptions(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_scheduled_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    INDEX idx_scheduled_user_id (user_id),
    INDEX idx_scheduled_status (status),
    INDEX idx_scheduled_time (scheduled_time),
    INDEX idx_scheduled_executed_time (executed_time)
) ENGINE=InnoDB;

-- ============================================================================
-- FEATURE 2: Dark Web Monitoring Integration
-- ============================================================================

-- Table 2.1: Dark Web Findings
CREATE TABLE IF NOT EXISTS darkweb_findings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investigation_id INT NOT NULL,
    user_id INT NOT NULL,
    
    -- What was found
    query_term VARCHAR(255) NOT NULL, -- email, phone, username, etc.
    found_on_platform VARCHAR(100) NOT NULL, -- 'pastebin', 'paste_site_x', etc.
    source_url VARCHAR(500) NULL,
    
    -- Finding details
    snippet TEXT NOT NULL, -- Preview of where it appears
    full_content LONGTEXT NULL, -- Full paste content (optional, for analysis)
    
    -- Risk assessment
    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    risk_reason TEXT NULL, -- Why this is risky
    
    -- Detection tracking
    first_detected DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_date DATETIME NULL,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_darkweb_investigation
        FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_darkweb_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    INDEX idx_darkweb_user_id (user_id),
    INDEX idx_darkweb_investigation_id (investigation_id),
    INDEX idx_darkweb_severity (severity),
    INDEX idx_darkweb_first_detected (first_detected),
    INDEX idx_darkweb_resolved (is_resolved)
) ENGINE=InnoDB;

-- Table 2.2: Dark Web Check History (Track monitoring activities)
CREATE TABLE IF NOT EXISTS darkweb_check_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_subscription_id INT NOT NULL,
    user_id INT NOT NULL,
    
    -- Check execution
    check_date DATETIME NOT NULL,
    scan_duration_seconds INT NULL,
    
    -- Results summary
    total_findings INT NOT NULL DEFAULT 0,
    critical_findings INT NOT NULL DEFAULT 0,
    high_findings INT NOT NULL DEFAULT 0,
    medium_findings INT NOT NULL DEFAULT 0,
    
    -- Status
    status VARCHAR(30) NOT NULL DEFAULT 'completed', -- 'pending', 'running', 'completed', 'failed'
    error_message TEXT NULL,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_darkweb_history_monitoring
        FOREIGN KEY (monitoring_subscription_id)
        REFERENCES monitoring_subscriptions(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_darkweb_history_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    INDEX idx_darkweb_history_user_id (user_id),
    INDEX idx_darkweb_history_check_date (check_date),
    INDEX idx_darkweb_history_status (status)
) ENGINE=InnoDB;

-- ============================================================================
-- FEATURE 3: Data Type Analysis + Hashing Algorithm Detector
-- ============================================================================

-- Table 3.1: Enhanced Breach Details (What data was exposed + hash type)
CREATE TABLE IF NOT EXISTS breach_details_enhanced (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investigation_id INT NOT NULL,
    breach_name VARCHAR(255) NOT NULL,
    
    -- Data types exposed
    data_types JSON NOT NULL, -- ["Email", "Password", "IC Number", "Credit Card"] etc
    
    -- Password hashing info
    hash_algorithm VARCHAR(50) NULL, -- 'MD5', 'SHA1', 'SHA256', 'bcrypt', 'PBKDF2', 'Unknown'
    hash_salted BOOLEAN NULL, -- Whether salt was used
    hash_iterations INT NULL, -- For iterative algorithms like PBKDF2
    
    -- Risk assessment per data type
    crackability VARCHAR(50) NULL, -- 'Very High', 'High', 'Medium', 'Low', 'Very Low'
    crackability_explanation TEXT NULL,
    
    -- Additional forensic info
    breach_source_country VARCHAR(100) NULL,
    estimated_exposure_count INT NULL,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_breach_details_investigation
        FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
    INDEX idx_breach_details_investigation_id (investigation_id),
    INDEX idx_breach_details_hash_algorithm (hash_algorithm),
    INDEX idx_breach_details_crackability (crackability)
) ENGINE=InnoDB;

-- Table 3.2: Data Type Risk Matrix (Reference table for risk assessment)
CREATE TABLE IF NOT EXISTS data_type_risk_matrix (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_type VARCHAR(100) NOT NULL UNIQUE,
    
    -- Risk scoring
    base_risk_score INT NOT NULL, -- 0-100
    risk_level VARCHAR(20) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    
    -- Description
    description TEXT,
    remediation_steps TEXT,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_datatype (data_type),
    INDEX idx_risk_level (risk_level)
) ENGINE=InnoDB;

-- Table 3.3: Hash Algorithm Vulnerability Index
CREATE TABLE IF NOT EXISTS hash_algorithm_index (
    id INT AUTO_INCREMENT PRIMARY KEY,
    algorithm_name VARCHAR(50) NOT NULL UNIQUE,
    
    -- Algorithm properties
    is_broken BOOLEAN NOT NULL DEFAULT FALSE,
    vulnerability_year INT NULL,
    
    -- Cracking difficulty
    crack_speed VARCHAR(50) NOT NULL, -- 'Very Fast (sec)', 'Fast (min)', 'Medium (hours)', 'Slow (days)', 'Very Slow (impossible)'
    estimated_cost_per_crack_usd DECIMAL(10, 2) NULL,
    
    -- Modern status
    recommendation VARCHAR(100) NOT NULL, -- 'DEPRECATED', 'LEGACY', 'ACCEPTABLE', 'RECOMMENDED'
    notes TEXT,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_algorithm_name (algorithm_name),
    INDEX idx_is_broken (is_broken)
) ENGINE=InnoDB;

-- ============================================================================
-- SEED DATA: Data Type Risk Matrix
-- ============================================================================

INSERT INTO data_type_risk_matrix (data_type, base_risk_score, risk_level, description, remediation_steps)
VALUES
    ('Email Address', 40, 'MEDIUM', 'Used for account recovery and spam. Can lead to phishing attacks.', 'Watch for phishing emails, enable 2FA on important accounts'),
    ('Password (Plaintext)', 100, 'CRITICAL', 'Direct access to account. Highest risk if reused across sites.', 'Change password immediately on all platforms that use same password'),
    ('Password (Weak Hash: MD5/SHA1)', 90, 'CRITICAL', 'Can be cracked in seconds. Use rainbow tables or GPU cracking.', 'Change password immediately, assume compromised'),
    ('Password (Salted Hash: bcrypt)', 20, 'LOW', 'Very difficult to crack (brute force takes years). Secure if strong password.', 'No immediate action needed if password is strong'),
    ('Name', 20, 'LOW', 'Can be used for social engineering but not directly harmful.', 'Monitor for impersonation'),
    ('Phone Number', 45, 'MEDIUM', 'Can be used for SIM swapping, spam, harassment.', 'Change number if actively used in attacks, enable SIM lock with carrier'),
    ('IC Number / SSN', 85, 'CRITICAL', 'Foundation for identity theft. Used for financial fraud.', 'Monitor credit score, freeze credit, file identity theft report'),
    ('Credit Card Number', 95, 'CRITICAL', 'Direct financial loss. CVV/CVC if also exposed = immediate fraud risk.', 'Contact bank immediately, cancel card, monitor transactions'),
    ('Bank Account Number', 80, 'CRITICAL', 'Enables fraudulent transfers and direct financial loss.', 'Contact bank immediately, enable additional security'),
    ('Date of Birth', 30, 'LOW', 'Used for identity verification and social engineering.', 'Monitor for identity theft attempts'),
    ('Address', 25, 'LOW', 'Used for phishing and physical threats. Moderate risk.', 'Monitor mail, watch for packages you didn\'t order')
ON DUPLICATE KEY UPDATE
    base_risk_score = VALUES(base_risk_score),
    risk_level = VALUES(risk_level);

-- ============================================================================
-- SEED DATA: Hash Algorithm Vulnerability Index
-- ============================================================================

INSERT INTO hash_algorithm_index (algorithm_name, is_broken, vulnerability_year, crack_speed, estimated_cost_per_crack_usd, recommendation, notes)
VALUES
    ('MD5', TRUE, 2004, 'Very Fast (sec)', 0.00, 'DEPRECATED', 'Broken since 2004. Can be cracked in seconds using GPU. Example: hashcat can try billions per second.'),
    ('SHA1', TRUE, 2017, 'Very Fast (sec)', 0.01, 'DEPRECATED', 'Cryptographically broken. Practical collision attacks proven. Should never be used for passwords.'),
    ('SHA256', FALSE, NULL, 'Fast (min)', 0.05, 'ACCEPTABLE', 'Secure but no salt. Still vulnerable to rainbow tables. Better to use salted version.'),
    ('SHA256 (Salted)', FALSE, NULL, 'Medium (hours)', 1.50, 'ACCEPTABLE', 'Secure with proper salt. Requires more resources to crack but still feasible.'),
    ('PBKDF2', FALSE, NULL, 'Medium (hours)', 2.00, 'ACCEPTABLE', 'Iterative hashing. Security depends on iteration count. Default 10,000 iterations is minimum.'),
    ('bcrypt', FALSE, NULL, 'Slow (days)', 100.00, 'RECOMMENDED', 'Adaptive hashing algorithm. Built-in salt. Cost factor increases difficulty with time. Industry standard.'),
    ('Argon2', FALSE, NULL, 'Very Slow (impossible)', 1000.00, 'RECOMMENDED', 'Modern password hash function. Memory-hard and GPU-resistant. Preferred for new systems since 2015.'),
    ('scrypt', FALSE, NULL, 'Very Slow (impossible)', 500.00, 'RECOMMENDED', 'Memory-hard algorithm. Resistant to GPU/ASIC attacks. Good alternative to bcrypt.')
ON DUPLICATE KEY UPDATE
    is_broken = VALUES(is_broken),
    crack_speed = VALUES(crack_speed);

-- ============================================================================
-- ALTER EXISTING TABLES: Add new columns to support enhanced tracking
-- ============================================================================

-- Update breach_results to store password hash info
ALTER TABLE breach_results
    ADD COLUMN IF NOT EXISTS hash_algorithm VARCHAR(50) NULL AFTER data_exposed,
    ADD COLUMN IF NOT EXISTS data_types JSON NULL AFTER hash_algorithm,
    ADD COLUMN IF NOT EXISTS crackability VARCHAR(50) NULL AFTER data_types;

-- Update investigation_logs to track monitoring
ALTER TABLE investigation_logs
    ADD COLUMN IF NOT EXISTS is_monitored BOOLEAN DEFAULT FALSE AFTER risk_level,
    ADD COLUMN IF NOT EXISTS monitoring_subscription_id INT NULL AFTER is_monitored,
    ADD COLUMN IF NOT EXISTS has_darkweb_findings BOOLEAN DEFAULT FALSE AFTER monitoring_subscription_id;

-- Add index to the new monitoring_subscription_id column
ALTER TABLE investigation_logs
    ADD INDEX IF NOT EXISTS idx_investigation_monitoring_id (monitoring_subscription_id);

-- ============================================================================
-- DDL VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify all tables were created successfully:
/*

-- View all tables
SHOW TABLES;

-- Count rows in new tables (should be 0 initially except seed data)
SELECT 'monitoring_subscriptions' as table_name, COUNT(*) as row_count FROM monitoring_subscriptions
UNION ALL
SELECT 'breach_timeline' as table_name, COUNT(*) as row_count FROM breach_timeline
UNION ALL
SELECT 'scheduled_checks' as table_name, COUNT(*) as row_count FROM scheduled_checks
UNION ALL
SELECT 'darkweb_findings' as table_name, COUNT(*) as row_count FROM darkweb_findings
UNION ALL
SELECT 'darkweb_check_history' as table_name, COUNT(*) as row_count FROM darkweb_check_history
UNION ALL
SELECT 'breach_details_enhanced' as table_name, COUNT(*) as row_count FROM breach_details_enhanced
UNION ALL
SELECT 'data_type_risk_matrix' as table_name, COUNT(*) as row_count FROM data_type_risk_matrix
UNION ALL
SELECT 'hash_algorithm_index' as table_name, COUNT(*) as row_count FROM hash_algorithm_index;

-- View data type risk matrix (seed data)
SELECT * FROM data_type_risk_matrix;

-- View hash algorithm index (seed data)
SELECT * FROM hash_algorithm_index;

*/

-- ============================================================================
-- SUMMARY OF CHANGES
-- ============================================================================
/*

FEATURE 1: Real-Time Monitoring + Breach Timeline
- monitoring_subscriptions: User setup monitoring for email/phone/bank account
- breach_timeline: Timeline view of when breaches happened vs when discovered
- scheduled_checks: Background jobs for automatic daily/weekly/monthly checks

FEATURE 2: Dark Web Monitoring Integration
- darkweb_findings: Detection results from dark web scanning
- darkweb_check_history: Track when dark web scans were performed + results

FEATURE 3: Data Type Analysis + Hashing Algorithm Detector
- breach_details_enhanced: Store what data types exposed + hash algorithm used
- data_type_risk_matrix: Reference table for risk scoring per data type
- hash_algorithm_index: Reference table for hash cracking difficulty

Updated columns:
- breach_results: Added hash_algorithm, data_types, crackability
- investigation_logs: Added is_monitored, monitoring_subscription_id, has_darkweb_findings

Seed data:
- 11 data types with risk scores
- 8 hash algorithms with vulnerability/cracking info

*/
