-- ============================================================================
-- SEED DATA UNTUK TABLE EXTENSION (HEATMAP, MONITORING, ACTIVITY, ETC)
-- ============================================================================

-- Email Monitoring Registry
INSERT INTO email_monitoring_registry (user_id, email_address, is_active, monitoring_type, active_investigation_id, breach_count, highest_risk_score, check_frequency, last_check_date, next_scheduled_check, send_email_alerts, send_sms_alerts, email_verified)
VALUES
(1, 'fildza@ur.unirazak.edu.my', TRUE, 'standard', 1, 1, 45, 'weekly', NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), TRUE, FALSE, TRUE),
(2, 'amin.demo@gmail.com', TRUE, 'premium', 2, 3, 95, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),
(3, 'nur.safe@example.com', TRUE, 'standard', 3, 0, 10, 'monthly', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_ADD(NOW(), INTERVAL 30 DAY), TRUE, FALSE, TRUE),
(4, 'amir.jobseek@gmail.com', TRUE, 'priority', 4, 1, 55, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),
(5, 'siti.telco@outlook.com', TRUE, 'priority', 5, 1, 70, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),
(6, 'farid.wallet@yahoo.com', TRUE, 'premium', 6, 1, 90, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),
(7, 'intan.professional@proton.me', TRUE, 'premium', 7, 1, 83, 'daily', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY), TRUE, TRUE, TRUE),
(8, 'hafiz.lowrisk@example.com', TRUE, 'standard', 8, 1, 20, 'monthly', NULL, DATE_ADD(NOW(), INTERVAL 30 DAY), TRUE, FALSE, TRUE),
(2, 'mfildxza@gmail.com', TRUE, 'standard', 9, 2, 68, 'weekly', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_ADD(NOW(), INTERVAL 5 DAY), TRUE, FALSE, TRUE);

-- User Email Check Activity
INSERT INTO user_email_check_activity (user_id, email_registry_id, email_checked, check_type, breach_count_found, new_breaches_found, risk_score_before, risk_score_after, risk_level_after, check_source, ip_address, execution_time_ms, http_status, alert_sent, alert_type)
VALUES
(1, 1, 'fildza@ur.unirazak.edu.my', 'scheduled', 1, 0, 40, 45, 'MEDIUM', 'web', '192.168.1.100', 245, 200, TRUE, 'email'),
(1, 1, 'fildza@ur.unirazak.edu.my', 'manual', 1, 0, 45, 45, 'MEDIUM', 'web', '192.168.1.100', 198, 200, FALSE, 'none'),
(2, 2, 'amin.demo@gmail.com', 'scheduled', 3, 1, 85, 95, 'HIGH', 'api', '203.0.113.15', 312, 200, TRUE, 'email'),
(2, 2, 'amin.demo@gmail.com', 'scheduled', 3, 0, 95, 95, 'HIGH', 'api', '203.0.113.15', 289, 200, FALSE, 'none'),
(2, 3, 'amin.backup@yahoo.com', 'manual', 0, 0, 0, 0, 'LOW', 'web', '192.168.1.101', 156, 200, FALSE, 'none'),
(3, 4, 'nur.safe@example.com', 'manual', 0, 0, 10, 10, 'LOW', 'web', '192.168.1.102', 134, 200, FALSE, 'none'),
(4, 5, 'amir.jobseek@gmail.com', 'scheduled', 1, 0, 50, 55, 'MEDIUM', 'web', '192.168.1.103', 267, 200, TRUE, 'email'),
(5, 6, 'siti.telco@outlook.com', 'scheduled', 1, 0, 65, 70, 'MEDIUM', 'bot', '10.0.0.50', 189, 200, TRUE, 'email'),
(6, 7, 'farid.wallet@yahoo.com', 'scheduled', 1, 0, 85, 90, 'HIGH', 'bot', '10.0.0.50', 234, 200, TRUE, 'email'),
(7, 8, 'intan.professional@proton.me', 'manual', 1, 0, 80, 83, 'HIGH', 'web', '192.168.1.104', 278, 200, TRUE, 'email'),
(8, 9, 'hafiz.lowrisk@example.com', 'manual', 1, 0, 15, 20, 'LOW', 'web', '192.168.1.105', 145, 200, FALSE, 'none'),
(2, 10, 'mfildxza@gmail.com', 'scheduled', 2, 1, 62, 68, 'MEDIUM', 'api', '203.0.113.15', 301, 200, TRUE, 'email');

-- Geographic Heatmap Data
INSERT INTO geographic_heatmap_data (user_id, investigation_id, country, state_province, city, latitude, longitude, breach_count_at_location, avg_risk_score, risk_level, email, phone_number)
VALUES
(1, 1, 'Malaysia', 'Selangor', 'Shah Alam', 3.0733, 101.5186, 1, 45.00, 'MEDIUM', 'fildza@ur.unirazak.edu.my', NULL),
(2, 2, 'Malaysia', 'Kuala Lumpur', 'Kuala Lumpur', 3.1390, 101.6869, 3, 95.00, 'HIGH', 'amin.demo@gmail.com', NULL),
(3, 3, 'Malaysia', 'Selangor', 'Klang', 3.0304, 101.5446, 0, 10.00, 'LOW', 'nur.safe@example.com', NULL),
(4, 4, 'Malaysia', 'Selangor', 'Petaling Jaya', 3.3270, 101.5505, 1, 55.00, 'MEDIUM', 'amir.jobseek@gmail.com', NULL),
(5, 5, 'Malaysia', 'Penang', 'Georgetown', 5.4164, 100.3327, 1, 70.00, 'MEDIUM', 'siti.telco@outlook.com', NULL),
(6, 6, 'Malaysia', 'Johor', 'Johor Bahru', 1.4854, 103.7618, 1, 90.00, 'HIGH', 'farid.wallet@yahoo.com', NULL),
(7, 7, 'Malaysia', 'Kuala Lumpur', 'Cheras', 3.0832, 101.7128, 1, 83.00, 'HIGH', 'intan.professional@proton.me', NULL),
(8, 8, 'Malaysia', 'Selangor', 'Ampang', 3.0479, 101.5600, 1, 20.00, 'LOW', 'hafiz.lowrisk@example.com', NULL),
(2, 9, 'Malaysia', 'Kuala Lumpur', 'Puchong', 2.9808, 101.6267, 2, 68.00, 'MEDIUM', NULL, '+601136005936'),
(1, 10, 'Malaysia', 'Selangor', 'Sungai Petani', 5.6486, 100.4847, 2, 82.00, 'HIGH', NULL, '+60135550011');

