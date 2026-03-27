-- ============================================================================
-- FYP OSINT DATA BREACH MONITOR - FULL DATABASE SETUP (ASAS + EXTENSION)
-- Untuk MySQL Workbench
-- ============================================================================

CREATE DATABASE IF NOT EXISTS fyp_osint;
USE fyp_osint;
SET SQL_SAFE_UPDATES = 0;
START TRANSACTION;

-- =========================
-- TABLE ASAS
-- =========================
CREATE TABLE IF NOT EXISTS investigation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NULL,
    phone_number VARCHAR(32) NULL,
    breach_count INT NOT NULL,
    risk_score INT NOT NULL,
    risk_level VARCHAR(10) NOT NULL,
    checked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS breach_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investigation_id INT NOT NULL,
    breach_name VARCHAR(255) NOT NULL,
    breach_date DATE NULL,
    data_exposed TEXT,
    CONSTRAINT fk_breach_investigation
        FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_users_email (email),
    INDEX idx_users_username (username),
    INDEX idx_users_created_at (created_at)
) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tambah user_id ke investigation_logs jika belum ada
ALTER TABLE investigation_logs 
ADD COLUMN IF NOT EXISTS user_id INT NULL FIRST,
ADD CONSTRAINT IF NOT EXISTS fk_investigation_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE SET NULL,
ADD INDEX IF NOT EXISTS idx_investigation_user_id (user_id);

-- =========================
-- TABLE EXTENSION (HEATMAP, MONITORING, ACTIVITY, ETC)
-- =========================

CREATE TABLE IF NOT EXISTS geographic_heatmap_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    investigation_id INT NOT NULL,
    country VARCHAR(100) NOT NULL,
    state_province VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    breach_count_at_location INT NOT NULL DEFAULT 0,
    avg_risk_score DECIMAL(5, 2) NOT NULL DEFAULT 0,
    risk_level VARCHAR(20) NOT NULL,
    email VARCHAR(255) NULL,
    phone_number VARCHAR(32) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_heatmap_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_heatmap_investigation FOREIGN KEY (investigation_id) REFERENCES investigation_logs(id) ON DELETE CASCADE,
    INDEX idx_heatmap_country (country),
    INDEX idx_heatmap_city (city),
    INDEX idx_heatmap_user_id (user_id),
    INDEX idx_heatmap_risk_level (risk_level),
    INDEX idx_heatmap_coordinates (latitude, longitude)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS email_monitoring_registry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    monitoring_type VARCHAR(50) NOT NULL DEFAULT 'standard',
    active_investigation_id INT NULL,
    breach_count INT NOT NULL DEFAULT 0,
    highest_risk_score INT NOT NULL DEFAULT 0,
    check_frequency VARCHAR(20) NOT NULL DEFAULT 'weekly',
    last_check_date DATETIME NULL,
    next_scheduled_check DATETIME NULL,
    send_email_alerts BOOLEAN NOT NULL DEFAULT TRUE,
    send_sms_alerts BOOLEAN NOT NULL DEFAULT FALSE,
    send_push_alerts BOOLEAN NOT NULL DEFAULT FALSE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_date DATETIME NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_email_registry_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_email_registry_investigation FOREIGN KEY (active_investigation_id) REFERENCES investigation_logs(id) ON DELETE SET NULL,
    INDEX idx_email_registry_user_id (user_id),
    INDEX idx_email_registry_email (email_address),
    INDEX idx_email_registry_active (is_active),
    INDEX idx_email_registry_check_date (last_check_date),
    UNIQUE KEY unique_user_email (user_id, email_address)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_email_check_activity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email_registry_id INT NOT NULL,
    email_checked VARCHAR(255) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    breach_count_found INT NOT NULL DEFAULT 0,
    new_breaches_found INT NOT NULL DEFAULT 0,
    risk_score_before INT NULL,
    risk_score_after INT NOT NULL,
    risk_level_after VARCHAR(20) NOT NULL,
    check_source VARCHAR(100) NOT NULL DEFAULT 'web',
    ip_address VARCHAR(64) NULL,
    execution_time_ms INT NULL,
    http_status INT NULL,
    alert_sent BOOLEAN NOT NULL DEFAULT FALSE,
    alert_type VARCHAR(50) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_activity_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_activity_email_registry FOREIGN KEY (email_registry_id) REFERENCES email_monitoring_registry(id) ON DELETE CASCADE,
    INDEX idx_activity_user_id (user_id),
    INDEX idx_activity_email_checked (email_checked),
    INDEX idx_activity_check_type (check_type),
    INDEX idx_activity_created_at (created_at),
    INDEX idx_activity_check_date_range (created_at, user_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS email_monitoring_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_date DATE NOT NULL UNIQUE,
    total_emails_registered INT NOT NULL DEFAULT 0,
    active_emails INT NOT NULL DEFAULT 0,
    verified_emails INT NOT NULL DEFAULT 0,
    total_users_monitoring INT NOT NULL DEFAULT 0,
    users_checked_today INT NOT NULL DEFAULT 0,
    users_checked_this_week INT NOT NULL DEFAULT 0,
    users_checked_this_month INT NOT NULL DEFAULT 0,
    total_checks_performed INT NOT NULL DEFAULT 0,
    manual_checks INT NOT NULL DEFAULT 0,
    scheduled_checks INT NOT NULL DEFAULT 0,
    breaches_discovered_today INT NOT NULL DEFAULT 0,
    high_risk_findings INT NOT NULL DEFAULT 0,
    alerts_sent INT NOT NULL DEFAULT 0,
    standard_monitoring_count INT NOT NULL DEFAULT 0,
    premium_monitoring_count INT NOT NULL DEFAULT 0,
    priority_monitoring_count INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stats_date (stat_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS heatmap_daily_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL,
    country VARCHAR(100) NOT NULL,
    state_province VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    total_investigations INT NOT NULL DEFAULT 0,
    total_breaches INT NOT NULL DEFAULT 0,
    high_risk_investigations INT NOT NULL DEFAULT 0,
    medium_risk_investigations INT NOT NULL DEFAULT 0,
    low_risk_investigations INT NOT NULL DEFAULT 0,
    avg_risk_score DECIMAL(5, 2) NOT NULL DEFAULT 0,
    avg_breach_count DECIMAL(5, 2) NOT NULL DEFAULT 0,
    alerts_triggered INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_heatmap_summary_date (summary_date),
    INDEX idx_heatmap_summary_country (country),
    INDEX idx_heatmap_summary_coordinates (latitude, longitude),
    UNIQUE KEY unique_location_date (summary_date, latitude, longitude)
) ENGINE=InnoDB;

COMMIT;
SET SQL_SAFE_UPDATES = 1;

-- =========================
-- VERIFICATION QUERIES
-- =========================

-- 1️⃣ Total emails registered?
SELECT COUNT(*) AS total_emails_registered FROM email_monitoring_registry;

-- 2️⃣ User check activities?
SELECT u.username, COUNT(*) as checks FROM users u 
JOIN user_email_check_activity ueca ON u.id = ueca.user_id 
GROUP BY u.id;

-- 3️⃣ Heatmap geographic distribution?
SELECT country, state_province, city, COUNT(*) FROM geographic_heatmap_data 
GROUP BY country, state_province, city;

-- 4️⃣ Risk level breakdown?
SELECT risk_level, COUNT(*) FROM geographic_heatmap_data GROUP BY risk_level;

-- 5️⃣ Activity by type (manual vs scheduled)?
SELECT check_type, COUNT(*) FROM user_email_check_activity GROUP BY check_type;

-- 6️⃣ Heatmap data ready?
SELECT * FROM heatmap_daily_summary LIMIT 5;
