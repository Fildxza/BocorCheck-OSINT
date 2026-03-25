-- BocorCheck Breach Database Seed Data
-- This file contains all breach data for testing and demonstration
-- Insert this data after running db_setup.py to populate breaches

-- Insert Breach Records
INSERT INTO breaches (name, date, affected_records, description, severity) VALUES
('DataNet Breach', '2024-03-15', 50000000, 'A major data breach affecting 50M users worldwide. Attackers exploited an SQL injection vulnerability.', 'HIGH'),
('ShopMY Compromise', '2023-11-20', 12000000, 'Malaysian e-commerce platform compromised through third-party vendor vulnerability.', 'HIGH'),
('CloudStore Leak', '2023-08-05', 2500000, 'Cloud storage misconfiguration exposed user files and metadata.', 'MEDIUM'),
('GameZone Hack', '2023-02-28', 15000000, 'Gaming platform breached via phishing attack on employees.', 'HIGH'),
('FinanceApp Exposure', '2023-02-28', 15000000, 'Financial application API endpoint left unprotected and publicly accessible.', 'HIGH'),
('HealthPortal Breach', '2022-12-10', 3000000, 'Healthcare portal data exposed through insecure backup on public cloud.', 'HIGH'),
('EduPlatform Leak', '2022-09-18', 1500000, 'Education platform student data leaked through compromised admin account.', 'LOW'),
('TravelBooker Hack', '2022-06-22', 5000000, 'Travel booking site compromised via SQL injection vulnerability.', 'MEDIUM'),
('FoodDelivery Breach', '2022-03-14', 7000000, 'Food delivery app user data exposed due to unpatched server vulnerability.', 'MEDIUM'),
('ISP Data Leak', '2021-11-30', 4000000, 'Internet service provider customer records leaked through insider threat.', 'HIGH'),
('ForumX Dump', '2021-08-15', 2000000, 'Online forum user credentials and private messages exposed.', 'MEDIUM');

-- Insert Data Types for each Breach
-- DataNet Breach (2024-03-15)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(1, 'Email'),
(1, 'Password Hash'),
(1, 'Phone Number'),
(1, 'Address');

-- ShopMY Compromise (2023-11-20)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(2, 'Email'),
(2, 'Full Name'),
(2, 'Date of Birth');

-- CloudStore Leak (2023-08-05)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(3, 'Email'),
(3, 'Files'),
(3, 'API Keys');

-- GameZone Hack (2023-02-28)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(4, 'Email'),
(4, 'Username'),
(4, 'IP Address');

-- FinanceApp Exposure (2023-02-28)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(5, 'Email'),
(5, 'Account Balance'),
(5, 'Transaction History');

-- HealthPortal Breach (2022-12-10)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(6, 'Email'),
(6, 'Medical Records'),
(6, 'IC Number');

-- EduPlatform Leak (2022-09-18)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(7, 'Email'),
(7, 'Student ID'),
(7, 'Grades');

-- TravelBooker Hack (2022-06-22)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(8, 'Email'),
(8, 'Passport Number'),
(8, 'Travel Dates');

-- FoodDelivery Breach (2022-03-14)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(9, 'Email'),
(9, 'Phone'),
(9, 'Address'),
(9, 'Order History');

-- ISP Data Leak (2021-11-30)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(10, 'Email'),
(10, 'IC Number'),
(10, 'Home Address');

-- ForumX Dump (2021-08-15)
INSERT INTO breach_data_types (breach_id, data_type) VALUES
(11, 'Email'),
(11, 'Username'),
(11, 'Private Messages');

-- Summary Statistics Query (for testing - NOT an insert)
-- Run this to verify data is correct:
-- SELECT 
--     COUNT(*) as total_breaches,
--     SUM(affected_records) as total_affected_records,
--     MAX(date) as most_recent_breach,
--     COUNT(CASE WHEN severity='HIGH' THEN 1 END) as high_risk_count,
--     COUNT(CASE WHEN severity='MEDIUM' THEN 1 END) as medium_risk_count,
--     COUNT(CASE WHEN severity='LOW' THEN 1 END) as low_risk_count
-- FROM breaches;
