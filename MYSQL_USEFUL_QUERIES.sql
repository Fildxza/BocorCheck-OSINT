-- =====================================================================
-- BocorCheck - Useful MySQL Queries for Management & Troubleshooting
-- =====================================================================
-- Use these queries to manage users, verify data, and troubleshoot issues

-- =====================================================================
-- USER MANAGEMENT QUERIES
-- =====================================================================

-- 1. List all users with their role and status
SELECT 
    id, 
    username, 
    email, 
    role, 
    is_active,
    created_at,
    updated_at
FROM users
ORDER BY created_at DESC;

-- 2. List admin users only
SELECT 
    id, 
    username, 
    email, 
    role, 
    created_at
FROM users
WHERE role = 'admin'
ORDER BY created_at DESC;

-- 3. List active/inactive users
SELECT 
    id, 
    username, 
    email, 
    is_active,
    created_at
FROM users
WHERE is_active = TRUE
ORDER BY username ASC;

-- 4. Find user by email
SELECT * FROM users WHERE email = 'admin@bocorcheck.local';

-- 5. Find user by username
SELECT * FROM users WHERE username = 'admin';

-- 6. Count total users
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_count,
    SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as regular_users,
    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users
FROM users;

-- =====================================================================
-- USER INVESTIGATION QUERIES
-- =====================================================================

-- 7. Show all investigations with user info
SELECT 
    il.id,
    u.username as user,
    il.email,
    il.phone_number,
    il.breach_count,
    il.risk_level,
    il.risk_score,
    il.checked_at
FROM investigation_logs il
LEFT JOIN users u ON il.user_id = u.id
ORDER BY il.checked_at DESC LIMIT 50;

-- 8. Show investigations for specific user
SELECT 
    id, 
    email, 
    phone_number, 
    breach_count, 
    risk_level, 
    risk_score,
    checked_at
FROM investigation_logs
WHERE user_id = 1  -- Replace 1 with actual user_id
ORDER BY checked_at DESC;

-- 9. Count investigations per user
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(il.id) as investigation_count
FROM users u
LEFT JOIN investigation_logs il ON u.id = il.user_id
GROUP BY u.id, u.username, u.email
ORDER BY investigation_count DESC;

-- 10. Find investigations with HIGH risk
SELECT 
    il.id,
    COALESCE(u.username, 'Anonymous') as user,
    il.email,
    il.breach_count,
    il.risk_score,
    il.checked_at
FROM investigation_logs il
LEFT JOIN users u ON il.user_id = u.id
WHERE il.risk_level = 'HIGH'
ORDER BY il.checked_at DESC;

-- 11. Get statistics of all investigations
SELECT 
    COUNT(*) as total_investigations,
    AVG(risk_score) as avg_risk_score,
    MAX(risk_score) as max_risk_score,
    MIN(risk_score) as min_risk_score,
    SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high_risk_count,
    SUM(CASE WHEN risk_level = 'MEDIUM' THEN 1 ELSE 0 END) as medium_risk_count,
    SUM(CASE WHEN risk_level = 'LOW' THEN 1 ELSE 0 END) as low_risk_count
FROM investigation_logs;

-- =====================================================================
-- LOGIN AUDIT QUERIES
-- =====================================================================

-- 12. View recent login activity
SELECT 
    id,
    username,
    action,
    role,
    ip_address,
    created_at
FROM login_logs
ORDER BY created_at DESC LIMIT 50;

-- 13. View failed login attempts
SELECT 
    id,
    username,
    action,
    ip_address,
    created_at
FROM login_logs
WHERE action = 'failed_login'
ORDER BY created_at DESC LIMIT 20;

-- 14. Count login attempts by user (last 7 days)
SELECT 
    username,
    COUNT(*) as login_count,
    MAX(created_at) as last_login
FROM login_logs
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
AND action IN ('login', 'logout')
GROUP BY username
ORDER BY login_count DESC;

-- 15. Find suspicious IP addresses (multiple failed attempts)
SELECT 
    ip_address,
    COUNT(*) as failed_attempts,
    MAX(created_at) as last_attempt
FROM login_logs
WHERE action = 'failed_login'
AND created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
GROUP BY ip_address
HAVING COUNT(*) > 5
ORDER BY failed_attempts DESC;

-- =====================================================================
-- BREACH DATA QUERIES
-- =====================================================================

-- 16. List all breaches with statistics
SELECT 
    id,
    name,
    date,
    affected_records,
    severity,
    (SELECT COUNT(*) FROM breach_data_types WHERE breach_id = breaches.id) as data_types_exposed
FROM breaches
ORDER BY date DESC;

-- 17. Count total affected records across all breaches
SELECT 
    SUM(affected_records) as total_affected_records,
    COUNT(*) as total_breaches,
    AVG(affected_records) as average_per_breach
FROM breaches;

-- 18. Show data types exposed by each breach
SELECT 
    b.name as breach,
    GROUP_CONCAT(bdt.data_type SEPARATOR ', ') as data_types_exposed
FROM breaches b
LEFT JOIN breach_data_types bdt ON b.id = bdt.breach_id
GROUP BY b.id, b.name
ORDER BY b.date DESC;

-- 19. Find which breaches exposed sensitive data
SELECT 
    b.id,
    b.name,
    b.date,
    GROUP_CONCAT(bdt.data_type SEPARATOR ', ') as sensitive_data
FROM breaches b
JOIN breach_data_types bdt ON b.id = bdt.breach_id
WHERE bdt.data_type IN ('Password', 'IC Number', 'Payment Info', 'Medical Records')
GROUP BY b.id, b.name
ORDER BY b.date DESC;

-- =====================================================================
-- USER-BREACH MATCHING QUERIES
-- =====================================================================

-- 20. Show which breaches matched which investigations
SELECT 
    ubm.id,
    il.email,
    b.name as breach_name,
    b.date,
    ubm.data_type,
    ubm.matched_at
FROM user_breach_matches ubm
JOIN investigation_logs il ON ubm.investigation_id = il.id
JOIN breaches b ON ubm.breach_id = b.id
ORDER BY ubm.matched_at DESC LIMIT 30;

-- 21. Count of breaches per investigation
SELECT 
    il.id as investigation_id,
    il.email,
    COUNT(ubm.breach_id) as total_breaches_matched,
    GROUP_CONCAT(b.name SEPARATOR '; ') as breach_names
FROM investigation_logs il
LEFT JOIN user_breach_matches ubm ON il.id = ubm.investigation_id
LEFT JOIN breaches b ON ubm.breach_id = b.id
GROUP BY il.id
HAVING total_breaches_matched > 0
ORDER BY total_breaches_matched DESC;

-- =====================================================================
-- MITIGATION PLAN QUERIES
-- =====================================================================

-- 22. View all mitigation plans
SELECT 
    id,
    title,
    severity_level,
    action_type,
    priority,
    estimated_time
FROM mitigation_plans
ORDER BY severity_level DESC, priority ASC;

-- 23. Get CRITICAL mitigation actions
SELECT 
    CONCAT('[Priority ', priority, '] ', title) as action,
    description,
    estimated_time
FROM mitigation_plans
WHERE severity_level = 'HIGH' AND priority = 1
ORDER BY priority ASC;

-- 24. Show mitigation actions for specific breach
SELECT 
    m.title,
    m.description,
    m.estimated_time,
    m.priority
FROM mitigation_plans m
JOIN breaches b ON m.breach_id = b.id
WHERE b.name = 'DataNet Breach'
ORDER BY m.priority ASC;

-- 25. Get Malaysian resources by type
SELECT 
    resource_name,
    resource_type,
    phone,
    website,
    operating_hours
FROM mitigation_resources
WHERE resource_type IN ('Government Agency', 'Commercial Bank')
ORDER BY resource_type, resource_name;

-- =====================================================================
-- SYSTEM HEALTH & STATISTICS
-- =====================================================================

-- 26. Overall system statistics
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM investigation_logs) as total_investigations,
    (SELECT COUNT(*) FROM breaches) as total_breaches,
    (SELECT COUNT(*) FROM login_logs) as total_login_events,
    (SELECT COUNT(*) FROM mitigation_plans) as total_mitigations,
    (SELECT COUNT(*) FROM mitigation_resources) as total_resources;

-- 27. Database size and table information
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb,
    table_rows as row_count
FROM information_schema.TABLES
WHERE table_schema = 'fyp_osint'
ORDER BY (data_length + index_length) DESC;

-- 28. Check foreign key integrity
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    REFERENCED_TABLE_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'fyp_osint'
AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME;

-- =====================================================================
-- MAINTENANCE & CLEANUP QUERIES
-- =====================================================================

-- 29. Find old login logs (for archival/cleanup)
SELECT 
    COUNT(*) as old_log_count,
    MIN(created_at) as oldest_entry
FROM login_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- 30. Check for potential data issues (orphaned records)
SELECT 
    COUNT(*) as orphaned_investigations
FROM investigation_logs il
WHERE il.user_id IS NOT NULL
AND il.user_id NOT IN (SELECT id FROM users);

-- =====================================================================
-- USEFUL ADMINISTRATIVE TASKS
-- =====================================================================

-- TASK 1: Temporarily disable a user account
-- UPDATE users SET is_active = FALSE WHERE username = 'username_here';
-- COMMIT;

-- TASK 2: Reactivate a user account
-- UPDATE users SET is_active = TRUE WHERE username = 'username_here';
-- COMMIT;

-- TASK 3: Delete all login logs older than 90 days
-- DELETE FROM login_logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
-- COMMIT;

-- TASK 4: Reset a user's investigation history
-- DELETE FROM investigation_logs WHERE user_id = 1;
-- COMMIT;

-- TASK 5: Clear user breach matches (useful for retesting)
-- DELETE FROM user_breach_matches WHERE investigation_id IN (
--     SELECT id FROM investigation_logs WHERE user_id = 1
-- );
-- COMMIT;

-- =====================================================================
-- BACKUP / EXPORT QUERIES
-- =====================================================================

-- TASK 6: Export all users (for backup/analysis)
-- SELECT id, username, email, role, created_at INTO OUTFILE '/tmp/users_backup.csv'
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- FROM users;

-- TASK 7: Export investigation statistics
-- SELECT 
--     checked_at, email, breach_count, risk_score, risk_level
-- INTO OUTFILE '/tmp/investigations_report.csv'
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- FROM investigation_logs
-- WHERE checked_at >= DATE_SUB(NOW(), INTERVAL 30 DAY);

-- =====================================================================
-- NOTE: These queries are examples for FYP administration
-- Use with caution in production environments
-- Always backup before running DELETE or UPDATE queries
-- =====================================================================
