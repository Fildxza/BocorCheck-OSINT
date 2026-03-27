-- ============================================================================
-- DECOY BANK BREACHES TABLE FOR ACADEMIC DEMONSTRATION
-- ============================================================================
-- This table contains COMPLETELY FICTIONAL and SYNTHETIC data created for
-- academic thesis demonstration purposes only. No real banking institutions,
-- accounts, or breach events are represented.
-- 
-- This data is intended for:
-- - FYP demonstration and testing
-- - Academic presentation of OSINT capabilities
-- - User interface prototyping
--
-- WARNING: This is NOT real intelligence data. Do NOT use this for any
-- decision-making regarding actual financial accounts or institutions.
-- ============================================================================

SET @old_sql_mode := @@sql_mode;
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

USE fyp_osint;

-- Create the decoy_bank_breaches table
CREATE TABLE IF NOT EXISTS decoy_bank_breaches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    breach_id VARCHAR(100) UNIQUE NOT NULL,
    institution_name VARCHAR(255) NOT NULL,
    institution_type VARCHAR(50) NOT NULL DEFAULT 'Bank',
    country VARCHAR(100) NOT NULL DEFAULT 'Malaysia',
    breach_date DATE NOT NULL,
    discovered_date DATE NOT NULL,
    breach_type VARCHAR(100) NOT NULL,
    severity_level ENUM('Low', 'Medium', 'High') NOT NULL DEFAULT 'Medium',
    affected_accounts INT NOT NULL,
    exposed_data_types TEXT NOT NULL,
    breach_description TEXT,
    data_sample_masked VARCHAR(255),
    source_notes VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_institution_name (institution_name),
    INDEX idx_breach_date (breach_date),
    INDEX idx_severity_level (severity_level),
    INDEX idx_country (country),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- INSERT DECOY BANK BREACH DATA
-- ALL DATA IS FICTIONAL FOR ACADEMIC DEMONSTRATION ONLY
-- ============================================================================

INSERT INTO decoy_bank_breaches (
    breach_id, institution_name, institution_type, country, 
    breach_date, discovered_date, breach_type, severity_level,
    affected_accounts, exposed_data_types, breach_description,
    data_sample_masked, source_notes
) VALUES

-- High Severity Breaches
('DECOY_SBM_2024_001', 'SecureBank Malaysia Berhad', 'Commercial Bank', 'Malaysia',
    '2024-08-15', '2024-08-22', 'SQL Injection + Data Exfiltration', 'High',
    145000, 'Account Numbers, Names, Phone Numbers, Email Addresses, Transaction Amounts',
    'Fictional breach scenario: Unauthorized access to customer database via web application vulnerability.',
    '2815-XXXX-XXXX-0847', 'Academic Demo Database'),

('DECOY_TRB_2024_002', 'TrustBank Regional', 'Investment Bank', 'Malaysia',
    '2024-07-03', '2024-07-10', 'Credential Theft + Insider Access', 'High',
    89500, 'Account Numbers, Full Names, Email, Phone, Investment Portfolio Details',
    'Fictional scenario: Compromised employee credentials used for unauthorized account access.',
    '3421-XXXX-XXXX-5634', 'Academic Demo Database'),

('DECOY_GBH_2024_003', 'Global Banking House', 'Digital Bank', 'Malaysia',
    '2024-09-11', '2024-09-18', 'API Vulnerability + Session Hijacking', 'High',
    267300, 'Account Numbers, Passwords (Hashed), Email Addresses, Phone Numbers, Card Details',
    'Fictional breach: Unprotected API endpoint allowing access to customer financial data.',
    '4891-XXXX-XXXX-7125', 'Academic Demo Database'),

-- Medium Severity Breaches
('DECOY_ESB_2024_004', 'easySecure Banking', 'Digital Bank', 'Malaysia',
    '2024-06-20', '2024-06-27', 'Compromised Third-Party Service', 'Medium',
    56400, 'Account Holders Names, Email Addresses, Phone Numbers',
    'Fictional scenario: Third-party payment processor breach affecting customer data.',
    '5467-XXXX-XXXX-2341', 'Academic Demo Database'),

('DECOY_WMB_2024_005', 'Wealth Management Bank', 'Private Banking', 'Malaysia',
    '2024-05-08', '2024-05-15', 'Unencrypted Data Exposure', 'Medium',
    34200, 'Client Names, Account Types, Email Addresses, Relationship Manager Info',
    'Fictional scenario: Unencrypted backup files exposed on misconfigured storage.',
    '6123-XXXX-XXXX-4567', 'Academic Demo Database'),

('DECOY_CPB_2024_006', 'Community Plus Bank', 'Cooperative Bank', 'Malaysia',
    '2024-04-12', '2024-04-19', 'Malware Infection + Data Harvest', 'Medium',
    78900, 'Account Holder Names, Account Numbers, Phone Numbers, Transaction Summaries',
    'Fictional scenario: Banking system infected with data-harvesting malware.',
    '7234-XXXX-XXXX-8901', 'Academic Demo Database'),

('DECOY_IEB_2024_007', 'International eBank', 'Digital Bank', 'Malaysia',
    '2024-03-25', '2024-04-02', 'Configuration Error + Open Database', 'Medium',
    92100, 'Email Addresses, Account Types, Registration Data, Phone Numbers',
    'Fictional scenario: Improperly configured database exposed on public network.',
    '8345-XXXX-XXXX-0123', 'Academic Demo Database'),

-- Low Severity Breaches
('DECOY_ISH_2024_008', 'Islamic Sharia Bank', 'Islamic Bank', 'Malaysia',
    '2024-02-14', '2024-02-21', 'Phishing + Minor Credential Leak', 'Low',
    12300, 'Email Addresses, Session Tokens (Short-lived), Card Type Information',
    'Fictional scenario: No customer financial data compromised, minimal impact.',
    '9456-XXXX-XXXX-5678', 'Academic Demo Database'),

('DECOY_RTB_2024_009', 'Retail Trading Bank', 'Retail Bank', 'Malaysia',
    '2024-01-30', '2024-02-06', 'Marketing List Exposure', 'Low',
    23100, 'Email Addresses, Phone Numbers, Geographic Information, Product Interests',
    'Fictional scenario: Customer marketing opt-in list accidentally publicized.',
    '0567-XXXX-XXXX-9012', 'Academic Demo Database'),

('DECOY_SDB_2024_010', 'Smart Deposits Bank', 'Savings Bank', 'Malaysia',
    '2024-01-08', '2024-01-15', 'Expired Backup Exposure', 'Low',
    8900, 'Customer Names, Email Addresses (Outdated)', 'Fictional scenario: Old backup file exposed with obsolete customer data.',
    '1234-XXXX-XXXX-5678', 'Academic Demo Database'),

-- Additional September 2024 Breaches
('DECOY_DBX_2024_011', 'Digital Banking Express', 'Digital Bank', 'Malaysia',
    '2024-09-22', '2024-09-29', 'Web Application XSS', 'High',
    156000, 'Account Numbers, Names, Email, Phone, Transaction History',
    'Fictional scenario: Cross-site scripting vulnerability in customer portal.',
    '2345-XXXX-XXXX-6789', 'Academic Demo Database'),

('DECOY_ZBK_2024_012', 'ZeroBound Financial', 'FinTech Bank', 'Malaysia',
    '2024-08-05', '2024-08-12', 'Supply Chain Attack', 'High',
    198500, 'Account Details, Authentication Credentials, KYC Information',
    'Fictional scenario: Compromised software update affecting multiple systems.',
    '3456-XXXX-XXXX-7890', 'Academic Demo Database'),

('DECOY_CFB_2024_013', 'Cashflow Banking', 'SME Bank', 'Malaysia',
    '2024-07-18', '2024-07-25', 'Certificate Mishandling', 'Medium',
    45600, 'Business Account Information, Officer Details, Email Addresses',
    'Fictional scenario: Expired SSL certificate and improper session handling.',
    '4567-XXXX-XXXX-8901', 'Academic Demo Database'),

('DECOY_HPB_2024_014', 'HyperPay Banking', 'Payment Bank', 'Malaysia',
    '2024-06-09', '2024-06-16', 'Weak Password Policy Exploitation', 'Medium',
    67800, 'Account Numbers, Email Addresses, Phone Numbers, Account Tier Info',
    'Fictional scenario: Default/weak passwords discovered in legacy system.',
    '5678-XXXX-XXXX-9012', 'Academic Demo Database'),

('DECOY_NDB_2024_015', 'NeonBank Digital', 'Digital Bank', 'Malaysia',
    '2024-05-20', '2024-05-27', 'Unvalidated Input', 'Low',
    19300, 'Email Addresses, Product Inquiry Forms, Geographic Data',
    'Fictional scenario: Non-sensitive user inquiry data leaked.',
    '6789-XXXX-XXXX-0123', 'Academic Demo Database');

-- ============================================================================
-- VERIFICATION QUERIES (for testing purposes)
-- ============================================================================

-- Check table creation and row count
SELECT COUNT(*) as total_decoy_breaches FROM decoy_bank_breaches;

-- Check severity distribution
SELECT severity_level, COUNT(*) as count FROM decoy_bank_breaches GROUP BY severity_level;

-- Check institution types
SELECT institution_type, COUNT(*) as count FROM decoy_bank_breaches GROUP BY institution_type;

-- Check data by country
SELECT country, COUNT(*) as count FROM decoy_bank_breaches GROUP BY country;

-- Sample ALL decoy breaches (for dashboard verification)
SELECT 
    breach_id,
    institution_name,
    breach_date,
    severity_level,
    affected_accounts,
    exposed_data_types,
    data_sample_masked
FROM decoy_bank_breaches
ORDER BY breach_date DESC, severity_level DESC;

-- ============================================================================
-- Create a view for easy access to decoy bank breaches data
-- ============================================================================

CREATE OR REPLACE VIEW vw_decoy_bank_breaches AS
SELECT 
    id,
    breach_id,
    institution_name,
    institution_type,
    country,
    breach_date,
    discovered_date,
    breach_type,
    severity_level,
    affected_accounts,
    exposed_data_types,
    breach_description,
    data_sample_masked,
    YEAR(breach_date) as breach_year,
    MONTH(breach_date) as breach_month,
    DATEDIFF(NOW(), breach_date) as days_since_breach,
    created_at
FROM decoy_bank_breaches
WHERE is_active = TRUE
ORDER BY breach_date DESC;

RESET QUERY_CACHE;
SET sql_mode = @old_sql_mode;
