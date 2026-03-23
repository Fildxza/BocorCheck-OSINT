-- FYP OSINT Breach Monitor - Proper MySQL script
-- Purpose:
-- 1) Keep compatibility with app.py tables.
-- 2) Add proper storage for "who tested" and test session metadata.
-- 3) Provide sample data and reporting queries for university demo.
-- MySQL version: 8.x

CREATE DATABASE IF NOT EXISTS fyp_osint
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fyp_osint;

-- -------------------------------------------------------------------------
-- A) Core tables required by app.py (do not remove)
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS investigation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NULL,
    phone_number VARCHAR(32) NULL,
    breach_count INT NOT NULL,
    risk_score INT NOT NULL,
    risk_level VARCHAR(10) NOT NULL,
    checked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_checked_at (checked_at),
    INDEX idx_risk_level (risk_level),
    INDEX idx_email (email)
);

CREATE TABLE IF NOT EXISTS breach_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investigation_id INT NOT NULL,
    breach_name VARCHAR(255) NOT NULL,
    breach_date DATE NULL,
    data_exposed TEXT,
    FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
    INDEX idx_investigation_id (investigation_id),
    INDEX idx_breach_name (breach_name),
    INDEX idx_breach_date (breach_date)
);

-- -------------------------------------------------------------------------
-- B) Extra storage for tester/operator and session metadata
-- -------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS test_operators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    student_id VARCHAR(40) NULL,
    university_email VARCHAR(255) NULL,
    role_label VARCHAR(60) NOT NULL DEFAULT 'Student Tester',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_operator_student_id (student_id),
    UNIQUE KEY uq_operator_email (university_email)
);

CREATE TABLE IF NOT EXISTS investigation_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    investigation_id INT NOT NULL,
    operator_id INT NULL,
    target_bank_account_input VARCHAR(40) NULL,
    normalized_bank_account VARCHAR(20) NULL,
    api_mode VARCHAR(16) NOT NULL DEFAULT 'auto',
    effective_data_mode VARCHAR(16) NOT NULL DEFAULT 'Mock',
    telegram_test_sent TINYINT(1) NOT NULL DEFAULT 0,
    notes VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
    FOREIGN KEY (operator_id)
        REFERENCES test_operators(id)
        ON DELETE SET NULL,
    INDEX idx_session_investigation_id (investigation_id),
    INDEX idx_session_operator_id (operator_id),
    INDEX idx_session_api_mode (api_mode),
    INDEX idx_session_data_mode (effective_data_mode)
);

-- Add optional columns directly in investigation_logs for quick filtering.
-- Safe to run repeatedly in MySQL 8.
ALTER TABLE investigation_logs
    ADD COLUMN IF NOT EXISTS source_mode VARCHAR(16) NULL AFTER risk_level,
    ADD COLUMN IF NOT EXISTS checked_by VARCHAR(120) NULL AFTER source_mode,
    ADD COLUMN IF NOT EXISTS checked_by_email VARCHAR(255) NULL AFTER checked_by;

-- -------------------------------------------------------------------------
-- C) Demo seed data (who tested, test email, and storage examples)
-- -------------------------------------------------------------------------
INSERT INTO test_operators (full_name, student_id, university_email, role_label)
VALUES
    ('Norha Test User', 'FYP2026-001', 'norha@student.unirazak.edu.my', 'FYP Presenter'),
    ('Amin Demo User', 'FYP2026-002', 'amin.demo@unirazak.edu.my', 'Demo Assistant')
ON DUPLICATE KEY UPDATE
    full_name = VALUES(full_name),
    role_label = VALUES(role_label);

START TRANSACTION;

-- Investigation 1 (high risk)
INSERT INTO investigation_logs (
    email,
    phone_number,
    breach_count,
    risk_score,
    risk_level,
    source_mode,
    checked_by,
    checked_by_email
)
VALUES (
    'fildza@ur.unirazak.edu.my',
    '+60123456789',
    2,
    65,
    'HIGH',
    'Mock',
    'Norha Test User',
    'norha@student.unirazak.edu.my'
);

SET @inv_id_1 = LAST_INSERT_ID();

INSERT INTO breach_results (investigation_id, breach_name, breach_date, data_exposed)
VALUES
    (@inv_id_1, 'EduForumDemo', '2024-02-11', 'Email addresses, Passwords'),
    (@inv_id_1, 'MobileMart', '2024-07-20', 'Phone numbers, Email addresses');

INSERT INTO investigation_sessions (
    investigation_id,
    operator_id,
    target_bank_account_input,
    normalized_bank_account,
    api_mode,
    effective_data_mode,
    telegram_test_sent,
    notes
)
SELECT
    @inv_id_1,
    o.id,
    '1234-5678-9012',
    '123456789012',
    'mock',
    'Mock',
    1,
    'University presentation dry run'
FROM test_operators o
WHERE o.student_id = 'FYP2026-001';

-- Investigation 2 (low risk)
INSERT INTO investigation_logs (
    email,
    phone_number,
    breach_count,
    risk_score,
    risk_level,
    source_mode,
    checked_by,
    checked_by_email
)
VALUES (
    'nur.safe@example.com',
    '+60135550011',
    0,
    10,
    'LOW',
    'Mock',
    'Amin Demo User',
    'amin.demo@unirazak.edu.my'
);

SET @inv_id_2 = LAST_INSERT_ID();

INSERT INTO investigation_sessions (
    investigation_id,
    operator_id,
    target_bank_account_input,
    normalized_bank_account,
    api_mode,
    effective_data_mode,
    telegram_test_sent,
    notes
)
SELECT
    @inv_id_2,
    o.id,
    '987654321098',
    '987654321098',
    'auto',
    'Mock',
    0,
    'Safe profile validation case'
FROM test_operators o
WHERE o.student_id = 'FYP2026-002';

COMMIT;

-- -------------------------------------------------------------------------
-- D) Core reports (for dashboard/reporting evidence)
-- -------------------------------------------------------------------------

-- D1) Quick table health check
SELECT 'investigation_logs' AS table_name, COUNT(*) AS total_rows FROM investigation_logs
UNION ALL
SELECT 'breach_results' AS table_name, COUNT(*) AS total_rows FROM breach_results
UNION ALL
SELECT 'test_operators' AS table_name, COUNT(*) AS total_rows FROM test_operators
UNION ALL
SELECT 'investigation_sessions' AS table_name, COUNT(*) AS total_rows FROM investigation_sessions;

-- D2) Full joined view: who tested what, email/phone, risk, breach details
SELECT
    il.id AS investigation_id,
    il.checked_at,
    il.email,
    il.phone_number,
    il.breach_count,
    il.risk_score,
    il.risk_level,
    COALESCE(o.full_name, il.checked_by, 'Unknown Tester') AS tested_by,
    COALESCE(o.university_email, il.checked_by_email, 'N/A') AS tester_email,
    s.api_mode,
    s.effective_data_mode,
    s.target_bank_account_input,
    s.telegram_test_sent,
    br.breach_name,
    br.breach_date,
    br.data_exposed
FROM investigation_logs il
LEFT JOIN investigation_sessions s
    ON s.investigation_id = il.id
LEFT JOIN test_operators o
    ON o.id = s.operator_id
LEFT JOIN breach_results br
    ON br.investigation_id = il.id
ORDER BY il.checked_at DESC, br.breach_date DESC;

-- D3) Daily stats by risk level
SELECT
    DATE(il.checked_at) AS day,
    COUNT(*) AS total_investigations,
    SUM(CASE WHEN il.risk_level = 'LOW' THEN 1 ELSE 0 END) AS low_count,
    SUM(CASE WHEN il.risk_level = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_count,
    SUM(CASE WHEN il.risk_level = 'HIGH' THEN 1 ELSE 0 END) AS high_count,
    ROUND(AVG(il.risk_score), 2) AS avg_risk_score
FROM investigation_logs il
GROUP BY DATE(il.checked_at)
ORDER BY day DESC;

-- D4) Most frequent breach source
SELECT
    br.breach_name,
    COUNT(*) AS occurrences
FROM breach_results br
GROUP BY br.breach_name
ORDER BY occurrences DESC, br.breach_name ASC;

-- D5) Filter example: only HIGH risk in selected date range
SELECT
    il.id,
    il.checked_at,
    il.email,
    il.phone_number,
    il.risk_score,
    il.risk_level,
    il.source_mode,
    il.checked_by,
    il.checked_by_email
FROM investigation_logs il
WHERE il.risk_level = 'HIGH'
  AND DATE(il.checked_at) BETWEEN '2026-01-01' AND '2026-12-31'
ORDER BY il.checked_at DESC;

-- D6) Single investigation detail (replace value as needed)
SELECT
    il.id,
    il.checked_at,
    il.email,
    il.phone_number,
    il.risk_score,
    il.risk_level,
    il.source_mode,
    il.checked_by,
    il.checked_by_email,
    s.target_bank_account_input,
    s.normalized_bank_account,
    s.api_mode,
    s.effective_data_mode,
    s.telegram_test_sent,
    s.notes,
    br.breach_name,
    br.breach_date,
    br.data_exposed
FROM investigation_logs il
LEFT JOIN investigation_sessions s
    ON s.investigation_id = il.id
LEFT JOIN breach_results br
    ON br.investigation_id = il.id
WHERE il.id = 1;

-- -------------------------------------------------------------------------
-- E) Cleanup helpers (optional)
-- -------------------------------------------------------------------------
-- Delete one investigation and all child rows
-- DELETE FROM investigation_logs WHERE id = 1;

-- Clear all demo data but keep structure
-- TRUNCATE TABLE investigation_sessions;
-- TRUNCATE TABLE breach_results;
-- TRUNCATE TABLE investigation_logs;
-- TRUNCATE TABLE test_operators;

-- -------------------------------------------------------------------------
-- F) Optional CSV export from MySQL server side (requires FILE privilege)
-- -------------------------------------------------------------------------
-- SELECT
--     il.id,
--     il.checked_at,
--     il.email,
--     il.phone_number,
--     il.risk_score,
--     il.risk_level,
--     COALESCE(o.full_name, il.checked_by) AS tested_by,
--     COALESCE(o.university_email, il.checked_by_email) AS tester_email,
--     s.api_mode,
--     s.effective_data_mode,
--     s.target_bank_account_input,
--     br.breach_name,
--     br.breach_date,
--     br.data_exposed
-- FROM investigation_logs il
-- LEFT JOIN investigation_sessions s ON s.investigation_id = il.id
-- LEFT JOIN test_operators o ON o.id = s.operator_id
-- LEFT JOIN breach_results br ON br.investigation_id = il.id
-- INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/fyp_investigation_export.csv'
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';
