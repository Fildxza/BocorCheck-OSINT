-- ============================================================================
-- HEATMAP EXTENSION FOR MySQL Workbench
-- Add location-based monitoring and user activity tracking
-- ============================================================================

USE fyp_osint;
SET SQL_SAFE_UPDATES = 0;

-- ============================================================================
-- TABLE 1: HEATMAP - Geographic Data (Lokasi untuk heatmap visualization)
-- ============================================================================

CREATE TABLE IF NOT EXISTS geographic_heatmap_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    investigation_id INT NOT NULL,
    
    -- Location information
    country VARCHAR(100) NOT NULL,
    state_province VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    
    -- Activity metrics
    breach_count_at_location INT NOT NULL DEFAULT 0,
    avg_risk_score DECIMAL(5, 2) NOT NULL DEFAULT 0,
    risk_level VARCHAR(20) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH'
    
    -- Address/Contact linked
    email VARCHAR(255) NULL,
    phone_number VARCHAR(32) NULL,
    
    -- Timestamp
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_heatmap_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_heatmap_investigation
        FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
    INDEX idx_heatmap_country (country),
    INDEX idx_heatmap_city (city),
    INDEX idx_heatmap_user_id (user_id),
    INDEX idx_heatmap_risk_level (risk_level),
    INDEX idx_heatmap_coordinates (latitude, longitude)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE 2: EMAIL MONITORING REGISTRY
-- Track semua emails yang di-key in untuk monitoring
-- ============================================================================

CREATE TABLE IF NOT EXISTS email_monitoring_registry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    
    -- Monitoring status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    monitoring_type VARCHAR(50) NOT NULL DEFAULT 'standard', -- 'standard', 'premium', 'priority'
    
    -- Breach info linked to email
    active_investigation_id INT NULL,
    breach_count INT NOT NULL DEFAULT 0,
    highest_risk_score INT NOT NULL DEFAULT 0,
    
    -- Frequency preferences
    check_frequency VARCHAR(20) NOT NULL DEFAULT 'weekly', -- 'daily', 'weekly', 'monthly'
    last_check_date DATETIME NULL,
    next_scheduled_check DATETIME NULL,
    
    -- Alert preferences
    send_email_alerts BOOLEAN NOT NULL DEFAULT TRUE,
    send_sms_alerts BOOLEAN NOT NULL DEFAULT FALSE,
    send_push_alerts BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Metadata
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_date DATETIME NULL,
    notes TEXT NULL,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_email_registry_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_email_registry_investigation
        FOREIGN KEY (active_investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE SET NULL,
    INDEX idx_email_registry_user_id (user_id),
    INDEX idx_email_registry_email (email_address),
    INDEX idx_email_registry_active (is_active),
    INDEX idx_email_registry_check_date (last_check_date),
    UNIQUE KEY unique_user_email (user_id, email_address)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE 3: USER EMAIL CHECK ACTIVITY LOG
-- Track every time a user checks their email status
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_email_check_activity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email_registry_id INT NOT NULL,
    email_checked VARCHAR(255) NOT NULL,
    
    -- Check metadata
    check_type VARCHAR(50) NOT NULL, -- 'manual', 'scheduled', 'api', 'batch'
    breach_count_found INT NOT NULL DEFAULT 0,
    new_breaches_found INT NOT NULL DEFAULT 0,
    
    -- Results
    risk_score_before INT NULL,
    risk_score_after INT NOT NULL,
    risk_level_after VARCHAR(20) NOT NULL,
    
    -- Source of check
    check_source VARCHAR(100) NOT NULL DEFAULT 'web', -- 'web', 'api', 'bot', 'mobile'
    ip_address VARCHAR(64) NULL,
    
    -- Execution details
    execution_time_ms INT NULL,
    http_status INT NULL,
    
    -- Alert tracking
    alert_sent BOOLEAN NOT NULL DEFAULT FALSE,
    alert_type VARCHAR(50) NULL, -- 'email', 'sms', 'push', 'none'
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_activity_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_activity_email_registry
        FOREIGN KEY (email_registry_id)
        REFERENCES email_monitoring_registry(id)
        ON DELETE CASCADE,
    INDEX idx_activity_user_id (user_id),
    INDEX idx_activity_email_checked (email_checked),
    INDEX idx_activity_check_type (check_type),
    INDEX idx_activity_created_at (created_at),
    INDEX idx_activity_check_date_range (created_at, user_id)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE 4: EMAIL MONITORING STATISTICS (Aggregated summary)
-- ============================================================================

CREATE TABLE IF NOT EXISTS email_monitoring_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_date DATE NOT NULL UNIQUE,
    
    -- Email registry metrics
    total_emails_registered INT NOT NULL DEFAULT 0,
    active_emails INT NOT NULL DEFAULT 0,
    verified_emails INT NOT NULL DEFAULT 0,
    
    -- User activity metrics
    total_users_monitoring INT NOT NULL DEFAULT 0,
    users_checked_today INT NOT NULL DEFAULT 0,
    users_checked_this_week INT NOT NULL DEFAULT 0,
    users_checked_this_month INT NOT NULL DEFAULT 0,
    
    -- Check activity metrics
    total_checks_performed INT NOT NULL DEFAULT 0,
    manual_checks INT NOT NULL DEFAULT 0,
    scheduled_checks INT NOT NULL DEFAULT 0,
    
    -- Results metrics
    breaches_discovered_today INT NOT NULL DEFAULT 0,
    high_risk_findings INT NOT NULL DEFAULT 0,
    alerts_sent INT NOT NULL DEFAULT 0,
    
    -- Monitoring type breakdown
    standard_monitoring_count INT NOT NULL DEFAULT 0,
    premium_monitoring_count INT NOT NULL DEFAULT 0,
    priority_monitoring_count INT NOT NULL DEFAULT 0,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_stats_date (stat_date)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE 5: HEATMAP DAILY SUMMARY
-- Geographic aggregation for faster heatmap rendering
-- ============================================================================

CREATE TABLE IF NOT EXISTS heatmap_daily_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL,
    
    -- Location info
    country VARCHAR(100) NOT NULL,
    state_province VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    
    -- Aggregated metrics
    total_investigations INT NOT NULL DEFAULT 0,
    total_breaches INT NOT NULL DEFAULT 0,
    high_risk_investigations INT NOT NULL DEFAULT 0,
    medium_risk_investigations INT NOT NULL DEFAULT 0,
    low_risk_investigations INT NOT NULL DEFAULT 0,
    
    -- Average scores
    avg_risk_score DECIMAL(5, 2) NOT NULL DEFAULT 0,
    avg_breach_count DECIMAL(5, 2) NOT NULL DEFAULT 0,
    
    -- Alert info
    alerts_triggered INT NOT NULL DEFAULT 0,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_heatmap_summary_date (summary_date),
    INDEX idx_heatmap_summary_country (country),
    INDEX idx_heatmap_summary_coordinates (latitude, longitude),
    UNIQUE KEY unique_location_date (summary_date, latitude, longitude)
) ENGINE=InnoDB;

-- ============================================================================
-- SEED DATA: Sample Geographic Heatmap Data (Malaysia Locations)
-- ============================================================================

INSERT INTO geographic_heatmap_data 
(user_id, investigation_id, country, state_province, city, latitude, longitude, breach_count_at_location, avg_risk_score, risk_level, email, phone_number)
VALUES
-- Kuala Lumpur & Selangor
(1, 1, 'Malaysia', 'Selangor', 'Shah Alam', 3.0733, 101.5186, 1, 45.00, 'MEDIUM', 'fildza@ur.unirazak.edu.my', NULL),
(2, 2, 'Malaysia', 'Kuala Lumpur', 'Kuala Lumpur', 3.1390, 101.6869, 3, 95.00, 'HIGH', 'amin.demo@gmail.com', NULL),

-- Klang Valley
(3, 3, 'Malaysia', 'Selangor', 'Klang', 3.0304, 101.5446, 0, 10.00, 'LOW', 'nur.safe@example.com', NULL),
(4, 4, 'Malaysia', 'Selangor', 'Petaling Jaya', 3.3270, 101.5505, 1, 55.00, 'MEDIUM', 'amir.jobseek@gmail.com', NULL),

-- Pulau Pinang
(5, 5, 'Malaysia', 'Penang', 'Georgetown', 5.4164, 100.3327, 1, 70.00, 'MEDIUM', 'siti.telco@outlook.com', NULL),

-- Johor
(6, 6, 'Malaysia', 'Johor', 'Johor Bahru', 1.4854, 103.7618, 1, 90.00, 'HIGH', 'farid.wallet@yahoo.com', NULL),

-- Wilayah Persekutuan
(7, 7, 'Malaysia', 'Kuala Lumpur', 'Cheras', 3.0832, 101.7128, 1, 83.00, 'HIGH', 'intan.professional@proton.me', NULL),
(8, 8, 'Malaysia', 'Selangor', 'Ampang', 3.0479, 101.5600, 1, 20.00, 'LOW', 'hafiz.lowrisk@example.com', NULL),

-- Phone number data (another user)
(2, 9, 'Malaysia', 'Kuala Lumpur', 'Puchong', 2.9808, 101.6267, 2, 68.00, 'MEDIUM', NULL, '+601136005936'),
(1, 10, 'Malaysia', 'Selangor', 'Sungai Petani', 5.6486, 100.4847, 2, 82.00, 'HIGH', NULL, '+60135550011');

-- ============================================================================
-- SEED DATA: Email Monitoring Registry (Sample emails being monitored)
-- ============================================================================

INSERT INTO email_monitoring_registry 
(user_id, email_address, is_active, monitoring_type, active_investigation_id, breach_count, highest_risk_score, check_frequency, last_check_date, next_scheduled_check, send_email_alerts, send_sms_alerts, email_verified)
VALUES
-- User 1 (1 email)
(1, 'fildza@ur.unirazak.edu.my', TRUE, 'standard', 1, 1, 45, 'weekly', NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), TRUE, FALSE, TRUE),

-- User 2 (2 emails - active monitoring)
(2, 'amin.demo@gmail.com', TRUE, 'premium', 2, 3, 95, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),
(2, 'amin.backup@yahoo.com', TRUE, 'standard', NULL, 0, 0, 'weekly', NULL, DATE_ADD(NOW(), INTERVAL 7 DAY), TRUE, FALSE, FALSE),

-- User 3 (1 email - low risk)
(3, 'nur.safe@example.com', TRUE, 'standard', 3, 0, 10, 'monthly', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_ADD(NOW(), INTERVAL 30 DAY), TRUE, FALSE, TRUE),

-- User 4 (Job seeker - 1 email)
(4, 'amir.jobseek@gmail.com', TRUE, 'priority', 4, 1, 55, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),

-- User 5 (Telco employee - sensitive)
(5, 'siti.telco@outlook.com', TRUE, 'priority', 5, 1, 70, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),

-- Additional test emails
(6, 'farid.wallet@yahoo.com', TRUE, 'premium', 6, 1, 90, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),
(7, 'intan.professional@proton.me', TRUE, 'premium', 7, 1, 83, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),
(8, 'hafiz.lowrisk@example.com', TRUE, 'standard', 8, 1, 20, 'monthly', NULL, DATE_ADD(NOW(), INTERVAL 30 DAY), TRUE, FALSE, TRUE),
(2, 'mfildxza@gmail.com', TRUE, 'standard', 9, 2, 68, 'weekly', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_ADD(NOW(), INTERVAL 5 DAY), TRUE, FALSE, TRUE);

-- ============================================================================
-- SEED DATA: User Email Check Activity (Simulated check history)
-- ============================================================================

INSERT INTO user_email_check_activity 
(user_id, email_registry_id, email_checked, check_type, breach_count_found, new_breaches_found, risk_score_before, risk_score_after, risk_level_after, check_source, ip_address, execution_time_ms, http_status, alert_sent, alert_type)
VALUES
-- User 1 checks
(1, 1, 'fildza@ur.unirazak.edu.my', 'scheduled', 1, 0, 40, 45, 'MEDIUM', 'web', '192.168.1.100', 245, 200, TRUE, 'email'),
(1, 1, 'fildza@ur.unirazak.edu.my', 'manual', 1, 0, 45, 45, 'MEDIUM', 'web', '192.168.1.100', 198, 200, FALSE, 'none'),

-- User 2 checks
(2, 2, 'amin.demo@gmail.com', 'scheduled', 3, 1, 85, 95, 'HIGH', 'api', '203.0.113.15', 312, 200, TRUE, 'email'),
(2, 2, 'amin.demo@gmail.com', 'scheduled', 3, 0, 95, 95, 'HIGH', 'api', '203.0.113.15', 289, 200, FALSE, 'none'),
(2, 3, 'amin.backup@yahoo.com', 'manual', 0, 0, 0, 0, 'LOW', 'web', '192.168.1.101', 156, 200, FALSE, 'none'),

-- User 3 checks
(3, 4, 'nur.safe@example.com', 'manual', 0, 0, 10, 10, 'LOW', 'web', '192.168.1.102', 134, 200, FALSE, 'none'),

-- User 4 checks
(4, 5, 'amir.jobseek@gmail.com', 'scheduled', 1, 0, 50, 55, 'MEDIUM', 'web', '192.168.1.103', 267, 200, TRUE, 'email'),

-- User 5 checks (frequent due to sensitive data)
(5, 6, 'siti.telco@outlook.com', 'scheduled', 1, 0, 65, 70, 'MEDIUM', 'bot', '10.0.0.50', 189, 200, TRUE, 'email'),

-- User 6 checks (high risk)
(6, 7, 'farid.wallet@yahoo.com', 'scheduled', 1, 0, 85, 90, 'HIGH', 'bot', '10.0.0.50', 234, 200, TRUE, 'email'),

-- User 7 checks
(7, 8, 'intan.professional@proton.me', 'manual', 1, 0, 80, 83, 'HIGH', 'web', '192.168.1.104', 278, 200, TRUE, 'email'),

-- User 8 checks (low risk, infrequent)
(8, 9, 'hafiz.lowrisk@example.com', 'manual', 1, 0, 15, 20, 'LOW', 'web', '192.168.1.105', 145, 200, FALSE, 'none'),

-- User 2's alternate email
(2, 10, 'mfildxza@gmail.com', 'scheduled', 2, 1, 62, 68, 'MEDIUM', 'api', '203.0.113.15', 301, 200, TRUE, 'email');

-- ============================================================================
-- TRUNCATE & REFRESH HEATMAP DAILY SUMMARY (Run this to refresh aggregations)
-- ============================================================================

DELETE FROM heatmap_daily_summary;

INSERT INTO heatmap_daily_summary 
(summary_date, country, state_province, city, latitude, longitude, total_investigations, total_breaches, high_risk_investigations, medium_risk_investigations, low_risk_investigations, avg_risk_score, avg_breach_count, alerts_triggered)
SELECT
    CURDATE() AS summary_date,
    ghd.country,
    ghd.state_province,
    ghd.city,
    ghd.latitude,
    ghd.longitude,
    COUNT(DISTINCT ghd.investigation_id) AS total_investigations,
    SUM(ghd.breach_count_at_location) AS total_breaches,
    SUM(CASE WHEN ghd.risk_level = 'HIGH' THEN 1 ELSE 0 END) AS high_risk_investigations,
    SUM(CASE WHEN ghd.risk_level = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_risk_investigations,
    SUM(CASE WHEN ghd.risk_level = 'LOW' THEN 1 ELSE 0 END) AS low_risk_investigations,
    AVG(ghd.avg_risk_score) AS avg_risk_score,
    AVG(ghd.breach_count_at_location) AS avg_breach_count,
    0 AS alerts_triggered
FROM geographic_heatmap_data ghd
GROUP BY ghd.country, ghd.state_province, ghd.city, ghd.latitude, ghd.longitude;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check 1: Berapa banyak total emails registered untuk monitoring?
SELECT 
    COUNT(*) AS total_emails_registered,
    SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) AS active_emails,
    SUM(CASE WHEN email_verified = TRUE THEN 1 ELSE 0 END) AS verified_emails,
    COUNT(DISTINCT user_id) AS total_users
FROM email_monitoring_registry;

-- Check 2: User check activity summary
SELECT 
    u.username,
    COUNT(DISTINCT ueca.email_registry_id) AS unique_emails_checked,
    COUNT(ueca.id) AS total_checks_performed,
    SUM(CASE WHEN ueca.check_type = 'manual' THEN 1 ELSE 0 END) AS manual_checks,
    SUM(CASE WHEN ueca.check_type = 'scheduled' THEN 1 ELSE 0 END) AS scheduled_checks,
    SUM(ueca.breach_count_found) AS total_breaches_found,
    SUM(ueca.new_breaches_found) AS new_breaches_found,
    MAX(ueca.created_at) AS last_check_date
FROM users u
LEFT JOIN user_email_check_activity ueca ON u.id = ueca.user_id
GROUP BY u.id, u.username
ORDER BY total_checks_performed DESC;

-- Check 3: Heatmap data - Geographic distribution
SELECT 
    ghd.country,
    ghd.state_province,
    ghd.city,
    COUNT(*) AS location_count,
    SUM(ghd.breach_count_at_location) AS total_breaches,
    AVG(ghd.avg_risk_score) AS avg_risk_score,
    SUM(CASE WHEN ghd.risk_level = 'HIGH' THEN 1 ELSE 0 END) AS high_risk_count
FROM geographic_heatmap_data ghd
GROUP BY ghd.country, ghd.state_province, ghd.city
ORDER BY total_breaches DESC;

-- Check 4: Daily heatmap summary for visualization
SELECT 
    hds.country,
    hds.state_province,
    hds.city,
    hds.latitude,
    hds.longitude,
    hds.total_investigations,
    hds.total_breaches,
    hds.high_risk_investigations,
    hds.avg_risk_score,
    hds.alerts_triggered
FROM heatmap_daily_summary hds
ORDER BY hds.total_breaches DESC;

-- Check 5: Email monitoring stats by type
SELECT 
    emr.monitoring_type,
    COUNT(*) AS count_emails,
    SUM(CASE WHEN emr.is_active = TRUE THEN 1 ELSE 0 END) AS active_count,
    AVG(emr.breach_count) AS avg_breaches,
    AVG(emr.highest_risk_score) AS avg_risk_score,
    SUM(CASE WHEN emr.email_verified = TRUE THEN 1 ELSE 0 END) AS verified_count
FROM email_monitoring_registry emr
GROUP BY emr.monitoring_type;

-- Check 6: Recent user check activities (last 7 days)
SELECT 
    u.username,
    ueca.email_checked,
    ueca.check_type,
    ueca.breach_count_found,
    ueca.risk_score_after,
    ueca.alert_sent,
    ueca.created_at
FROM users u
JOIN user_email_check_activity ueca ON u.id = ueca.user_id
WHERE ueca.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY ueca.created_at DESC;

SET SQL_SAFE_UPDATES = 1;
