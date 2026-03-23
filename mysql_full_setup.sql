-- FYP OSINT - Full MySQL Setup (idempotent)

CREATE DATABASE IF NOT EXISTS fyp_osint
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fyp_osint;

CREATE TABLE IF NOT EXISTS investigation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NULL,
    phone_number VARCHAR(32) NULL,
    breach_count INT NOT NULL,
    risk_score INT NOT NULL,
    risk_level VARCHAR(10) NOT NULL,
    checked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_investigation_checked_at (checked_at),
    INDEX idx_investigation_risk_level (risk_level),
    INDEX idx_investigation_email (email)
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
        ON DELETE CASCADE,
    INDEX idx_breach_investigation_id (investigation_id),
    INDEX idx_breach_date (breach_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS login_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    ip_address VARCHAR(64) NOT NULL,
    user_agent VARCHAR(512) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_login_logs_username (username),
    INDEX idx_login_logs_action (action),
    INDEX idx_login_logs_created_at (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS risk_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investigation_id INT NOT NULL,
    breach_count INT,
    sensitive_data BOOLEAN,
    risk_score INT,
    risk_level VARCHAR(10),
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_risk_scores_investigation
        FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
    INDEX idx_risk_scores_investigation_id (investigation_id),
    INDEX idx_risk_scores_level (risk_level),
    INDEX idx_risk_scores_created_at (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investigation_id INT NOT NULL,
    alert_type VARCHAR(50),
    message TEXT,
    status VARCHAR(20),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alerts_investigation
        FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
    INDEX idx_alerts_investigation_id (investigation_id),
    INDEX idx_alerts_status (status),
    INDEX idx_alerts_sent_at (sent_at),
    UNIQUE KEY uq_alert_per_investigation_type (investigation_id, alert_type)
) ENGINE=InnoDB;

-- Quick health checks
SELECT 'investigation_logs' AS table_name, COUNT(*) AS total_rows FROM investigation_logs
UNION ALL
SELECT 'breach_results', COUNT(*) FROM breach_results
UNION ALL
SELECT 'login_logs', COUNT(*) FROM login_logs
UNION ALL
SELECT 'risk_scores', COUNT(*) FROM risk_scores
UNION ALL
SELECT 'alerts', COUNT(*) FROM alerts;
