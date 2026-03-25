-- Comprehensive Mitigation Plans with Malaysian Resources
-- For BocorCheck FYP Project
-- Insert after breaches_seed_data.sql

-- UNIVERSAL MITIGATION PLANS (Apply to all HIGH severity breaches)

-- HIGH RISK: Password/Authentication Data Exposed
INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(1, 'Password Hash', 'HIGH', 'password_reset', 1, 
 'Change Your Password Immediately',
 'Your password hash was included in the breach. Change it immediately to prevent unauthorized access to your account.',
 '["1. Go to account settings/security page", "2. Click \"Change Password\"", "3. Enter current password", "4. Create new strong password (16+ characters with uppercase, lowercase, numbers, special symbols)", "5. Confirm new password", "6. Save and logout from all other sessions"]',
 '5 minutes'),

(1, 'Password Hash', 'HIGH', 'enable_2fa', 1,
 'Enable Two-Factor Authentication (2FA)',
 'Two-factor authentication adds an extra layer of security. Even if your password is compromised, attackers cannot access your account.',
 '["1. Open account security settings", "2. Find \"Two-Factor Authentication\" or \"2FA\" option", "3. Choose authentication method (authenticator app recommended over SMS)", "4. Download authenticator app (Google Authenticator, Microsoft Authenticator, or Authy)", "5. Scan QR code with app", "6. Save backup codes in secure location", "7. Enable 2FA"]',
 '10 minutes');

-- HIGH RISK: Email Addresses Exposed
INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(2, 'Email', 'HIGH', 'monitor_phishing', 1,
 'Monitor for Phishing Attacks',
 'Your email address is now on spam/phishing lists. Be vigilant for suspicious emails pretending to be from banks or services.',
 '["1. Be suspicious of urgent emails asking for passwords/OTP", "2. Never click links in suspicious emails - go directly to website instead", "3. Check sender email address carefully (spammers use similar-looking addresses)", "4. Hover over links to see real URL before clicking", "5. Report phishing emails to the service provider", "6. Mark emails as spam/phishing to train your email filter"]',
 'ongoing');

-- HIGH RISK: Personal Identification (IC Number, Full Name, DOB)
INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(2, 'Full Name', 'HIGH', 'identity_theft_monitoring', 1,
 'Monitor for Identity Theft (Malaysia-Specific)',
 'Your personal information (Name, IC Number, DOB) could be used to open fraudulent accounts. Monitor closely.',
 '["1. Check MyDebtFreee (Malaysia Credit Bureau) - mydebtfreee.com.my", "2. Review credit report for unauthorized applications", "3. Contact all major Malaysian banks to verify no fraud", "4. Place fraud alert on your credit profile", "5. Consider credit freeze (konsejemen kawalan kredit)", "6. File report with PDRM if suspected fraud - E-complaint: www.eaduan.gov.my", "7. Monitor government services - check MyKad status at JPN"]',
 '30 minutes'),

(2, 'Date of Birth', 'HIGH', 'secure_recovery_info', 2,
 'Secure Your Account Recovery Information',
 'Your Date of Birth is often used as security verification. Update recovery methods to prevent account takeover.',
 '["1. Update recovery email to one only you can access", "2. Update recovery phone number to YOUR phone only", "3. Update security questions with answers only you know", "4. Remove outdated family members/friends as recovery contacts", "5. Save backup codes in offline, secure location", "6. Keep recovery information private"]',
 '15 minutes');

-- HIGH RISK: Financial Data Exposed
INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(5, 'Account Balance', 'HIGH', 'monitor_fraud', 1,
 'Monitor Financial Accounts 24/7',
 'Your account balances and transaction history are exposed. There\'s HIGH risk of unauthorized transactions.',
 '["1. IMMEDIATELY contact your bank (call number, not online)", "2. Request transaction history for last 90 days", "3. Review EVERY transaction for suspicious activity", "4. Request fraud alert on account", "5. Ask bank about transaction limit changes", "6. Enable SMS/push alerts for all transactions", "7. Change online banking password from secure device", "8. Request new debit card if compromised"]',
 '15 minutes'),

(5, 'Transaction History', 'HIGH', 'financial_lockdown', 1,
 'Lock Down Financial Accounts',
 'Attackers have detailed knowledge of your accounts. Take immediate protective action.',
 '["1. Contact bank about suspicious activity (call directly)", "2. Request temporary freeze on accounts", "3. Change all banking passwords to long, random passwords", "4. Disable auto-transfers and scheduled payments", "5. Lower transaction limits temporarily", "6. Request one-time passwords for transfers", "7. Monitor credit card statements daily", "8. Consider closing and reopening account if severely compromised"]',
 '20 minutes');

-- HIGH RISK: Medical/Health Data
INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(6, 'Medical Records', 'HIGH', 'notify_healthcare_provider', 1,
 'Contact Your Healthcare Provider',
 'Your medical records are exposed and could be used for identity theft or insurance fraud. Contact your healthcare provider immediately.',
 '["1. Call your hospital/clinic directly (not using numbers from breach data)", "2. Inform them of the breach", "3. Request written confirmation of what data was exposed", "4. Ask about identity theft insurance from your provider", "5. Request freeze on your medical records", "6. Check private practices you\'ve visited", "7. Verify insurance policy wasn\'t fraudulently modified"]',
 '15 minutes'),

(6, 'IC Number', 'HIGH', 'ic_identity_protection', 1,
 'Protect Your MyKad/IC Number (Malaysia)',
 'Your IC Number is the most valuable piece of personal information in Malaysia. Protect it immediately.',
 '["1. Check National Registration Department (JPN) - jpn.gov.my - verify IC status", "2. Report to MICC (Malaysian Internet Crime Committee) - www.micc.gov.my", "3. File police report at nearest PDRM station - Cybercrime Division", "4. Download complaint form from www.eaduan.gov.my", "5. Obtain police report reference number", "6. Use police report to notify banks of potential fraud", "7. Monitor for applications under your IC number", "8. Consider IC replacement (new card) if severely compromised"]',
 '30 minutes');

-- MEDIUM RISK: Personal Data
INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(3, 'Address', 'MEDIUM', 'secure_personal_data', 2,
 'Secure Your Home Address',
 'Your home address is now public. Be vigilant for targeted attacks or social engineering.',
 '["1. Install external security cameras and motion lights", "2. Be cautious about accepting deliveries/packages", "3. Monitor mail for fraudulent account opening letters", "4. Request mail forwarding if moving", "5. Check for unauthorized service connections", "6. Register with DND (Do Not Disturb) - if applicable", "7. Consider P.O. Box for important correspondence"]',
 '20 minutes');

-- MEDIUM RISK: Account/User Data
INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(4, 'Username', 'MEDIUM', 'monitor_account_misuse', 2,
 'Monitor for Account Misuse',
 'Your username is public. Attackers might use it for account takeover attempts or to find you on other platforms.',
 '["1. Search for your username across major platforms (Google, Facebook, Instagram, Twitter)", "2. Claim unclaimed accounts with your username", "3. Set profiles to PRIVATE if not already", "4. Review login history on all accounts", "5. Check connected apps/devices with access to accounts", "6. Remove unrecognized devices from your accounts", "7. Change passwords on accounts using the same password"]',
 '20 minutes');

-- MEDIUM RISK: Generic Exposure
INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(8, 'Email', 'MEDIUM', 'data_removal_request', 2,
 'Request Data Removal from Public Records',
 'Your personal data is now on breach databases. Request removal from data broker services.',
 '["1. Visit Have I Been Pwned (haveibeenpwned.com) to understand what\'s exposed", "2. Request unsubscribe from data broker databases", "3. Use Malaysian data removal services if available", "4. Contact PDPA Commissioner (Personal Data Protection Act) if needed", "5. Maintain records of removal requests", "6. Follow up after 30 days to verify removal"]',
 '30 minutes');

-- LOW RISK: General Recommendations
INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(7, 'Student ID', 'LOW', 'monitor_for_misuse', 3,
 'Monitor for Student ID Misuse',
 'Your student ID is exposed. Monitor for unauthorized access to educational records or services.',
 '["1. Login to your educational institution\'s portal", "2. Review account access logs", "3. Check grades haven\'t been modified", "4. Verify registered courses are correct", "5. Check financial records for unauthorized charges", "6. Review library accounts and borrowing history", "7. Set up alerts for grade/account changes"]',
 '15 minutes');

-- UNIVERSAL ACTIONS (Applicable to all breaches)

INSERT INTO mitigation_plans (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(1, 'All Data', 'HIGH', 'check_have_i_been_pwned', 2,
 'Check All Your Email Addresses',
 'Use Have I Been Pwned to check if this email appears in other breaches.',
 '["1. Visit haveibeenpwned.com", "2. Enter your email address", "3. Review all breaches affecting you", "4. Note which services were compromised", "5. Subscribe to get notified of future breaches affecting your email", "6. Create separate emails for different services to contain damage"]',
 '5 minutes');

-- MALAYSIAN-SPECIFIC RESOURCES AND ONGOING MONITORING

INSERT INTO mitigation_plans (data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(NULL, 'HIGH', 'malaysian_reporting', 1,
 'Report to Malaysian Authorities',
 'File official reports with Malaysian government agencies if your data includes personal identification.',
 '["1. Visit MICC (Malaysian Internet Crime Committee) - www.micc.gov.my", "2. File online report with details of breach", "3. Visit PDRM Cybercrime Division - nearest police station", "4. File police report (Form A) - reference needed for bank disputes", "5. Use online e-Complaint portal - www.eaduan.gov.my", "6. Keep copies of all filing documents", "7. Follow up on investigation status", "8. Report to PDPA Commissioner if personal data mishandled"]',
 '60 minutes');

INSERT INTO mitigation_plans (data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context) VALUES
(NULL, 'MEDIUM', 'ongoing_monitoring', 2,
 'Set Up Ongoing Monitoring System',
 'After a breach, continuous monitoring is critical. Set up automated alerts and periodic checks.',
 '["1. Subscribe to Have I Been Pwned breach alerts", "2. Enable bank transaction alerts (SMS/Push for all transactions)", "3. Enable credit bureau notifications (MyDebtFreee, CCRIS)", "4. Set up Google Alerts for your name", "5. Monitor social media for impersonation accounts", "6. Check bank account login history weekly", "7. Review credit card statements within 2 days of transactions", "8. Use security freeze on credit reports (available in Malaysia)"]',
 'ongoing');

-- Now insert the resources separately for easier management

-- Create mitigation plan IDs first (require manual ID mapping based on previous inserts)
-- These will be inserted as a separate step with the IDs from above queries
