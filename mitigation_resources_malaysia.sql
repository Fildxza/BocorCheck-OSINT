-- Malaysian Resources for Mitigation Plans
-- This file contains all contacts and resources for Malaysian users
-- Insert this BEFORE mitigation_seed_data.sql for proper resource linking

-- Note: Mitigation plan IDs need to be obtained from actual insert operations
-- This version uses realistic structure that can be adapted based on actual IDs

-- MITIGATION RESOURCES - MALAYSIAN GOVERNMENT & FINANCIAL INSTITUTIONS

-- MICC (Malaysian Internet Crime Committee)
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('MICC - Malaysian Internet Crime Committee', 'Government Agency', 
 'Official Malaysian agency for cybercrime reporting. File breach and fraud reports here.',
 'Putrajaya, Malaysia',
 'www.micc.gov.my',
 '+603-8000-8000',
 'contact@micc.gov.my',
 'Monday-Friday: 9 AM - 5 PM (Malaysian Time)',
 '24/7 online reporting available');

-- PDRM Cybercrime Division
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('PDRM Cybercrime Investigation Division', 'Police Department',
 'Royal Malaysia Police cybercrime unit. File formal police reports for breach-related crimes.',
 'IPD Sentosa, Kuala Lumpur',
 'www.rmp.gov.my',
 '03-2100 5250',
 'cybercrime@rmp.gov.my',
 'Monday-Friday: 8 AM - 6 PM, Saturday: 8 AM - 1 PM',
 'Emergency: 999 available 24/7');

-- e-Aduan (Government Complaints Portal)
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('e-Aduan Portal (Malaysia Government Complaints)', 'Government Service',
 'Official online portal for filing complaints against government agencies. Can be used for fraud/breach reports.',
 'Federal Government Administrative Centre',
 'www.eaduan.gov.my',
 '03-8000 8000',
 'support@eaduan.gov.my',
 '24/7 online access',
 '24/7');

-- Bank Negara Malaysia
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Bank Negara Malaysia - Consumer Protection', 'Central Bank',
 'Malaysia Central Bank. Oversees financial regulations and consumer protection in banking sector.',
 'Kuala Lumpur Financial Centre, Jalan Dato\'' Onn',
 'www.bnm.gov.my',
 '1-300-88-5465 (toll-free)',
 'general@bnm.gov.my',
 'Monday-Friday: 9 AM - 5 PM',
 'Online services 24/7');

-- PDPA Commissioner
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Personal Data Protection Act (PDPA) Commissioner', 'Regulatory Body',
 'Handles personal data protection complaints. File if your data was mishandled under PDPA.',
 'Ministry of Communications, Cyberjaya',
 'www.pdp.gov.my',
 '+603-8319 8800',
 'enquiry@pdp.gov.my',
 'Monday-Friday: 9 AM - 5 PM',
 'Monday-Friday business hours');

-- JPN (National Registration Department)
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('JPN - Jabatan Pendaftaran Negara (National Registration Dept)', 'Government Agency',
 'Manages MyKad and IC records. Check IC status and report suspicious activities related to your MyKad.',
 'Multiple offices nationwide',
 'www.jpn.gov.my',
 '1-300-888-811 (toll-free)',
 'jpn@jpn.gov.my',
 'Monday-Friday: 8:30 AM - 4:30 PM, Saturday: 9 AM - 1 PM',
 'Limited weekend hours');

-- MALAYSIAN BANKS - Consumer Helplines

-- Maybank
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Maybank - Fraud & Security', 'Commercial Bank',
 'Malaysia\'s largest bank. Report fraudulent transactions and request fraud protection immediately.',
 'Multiple branches nationwide',
 'www.maybank.com.my',
 '1-300-888-627 (toll-free)',
 'fraud@maybank.com.my',
 '24 hours daily',
 '24/7 hotline available');

-- CIMB Bank
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('CIMB - Customer Service & Fraud', 'Commercial Bank',
 'Major Malaysian bank providing fraud protection and dispute resolution services.',
 'Multiple branches nationwide',
 'www.cimb.com.my',
 '1-300-300-300 (toll-free)',
 'ccs@cimb.com.my',
 '24 hours daily',
 '24/7 available');

-- Bank Islam
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Bank Islam - Customer Assistance', 'Islamic Bank',
 'Islamic bank in Malaysia. Report fraud and request account protection.',
 'Multiple branches nationwide',
 'www.bankislam.com.my',
 '+603-2786 3636',
 'customercare@bankislam.com.my',
 'Monday-Friday: 8 AM - 5 PM, Saturday: 9 AM - 2 PM',
 'Business hours + mobile app 24/7');

-- Public Bank
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Public Bank - Fraud & Dispute', 'Commercial Bank',
 'Major Malaysian bank group. Report unauthorized transactions and request fraud freeze.',
 'Multiple branches nationwide',
 'www.publicbank.com.my',
 '+603-2171 2222',
 'fraud@publicbank.com.my',
 '24 hours daily',
 'Fraud hotline 24/7');

-- AmBank
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('AmBank - Security & Complaints', 'Commercial Bank',
 'AmBank Malaysia. File fraud claims and request account security enhancements.',
 'Multiple branches nationwide',
 'www.ambank.com.my',
 '+603-4050 1188',
 'complaints@ambank.com.my',
 'Monday-Friday: 8:30 AM - 5:30 PM, Saturday: 8:30 AM - 1 PM',
 '24/7 emergency line available');

-- CREDIT BUREAU & FINANCIAL MONITORING

-- MyDebtFreee
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('MyDebtFreee (Credit Bureau Malaysia)', 'Credit Information',
 'Malaysia\'s credit information bureau. Check your credit report for unauthorized applications or fraud.',
 'Kuala Lumpur',
 'www.mydebtfreee.com.my',
 '+603-2860 7788',
 'info@mydebtfreee.com.my',
 'Monday-Friday: 9 AM - 5 PM',
 'Website 24/7 for report requests');

-- CCRIS
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('CCRIS (Central Credit Reference Information System)', 'Credit System',
 'Maintained by BNM. Check central credit records for unauthorized loans or credit facilities.',
 'Kuala Lumpur',
 'www.ccris.bnm.gov.my',
 '1-300-300-300',
 'ccris@bnm.gov.my',
 'Monday-Friday: 9 AM - 5 PM',
 'Online portal Monday-Friday 8 AM - 6 PM');

-- INSURANCE & FINANCIAL PROTECTION

-- PIDM (Perbadanan Insurans Deposit Malaysia)
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('PIDM - Deposit Insurance', 'Insurance Corporation',
 'Protects bank deposits in Malaysia up to RM250,000. Verify your account protection coverage.',
 'Kuala Lumpur',
 'www.pidm.gov.my',
 '+603-2601 0000',
 'feedback@pidm.gov.my',
 'Monday-Friday: 9 AM - 5 PM',
 'Online info 24/7');

-- TELECOMMUNICATIONS & IDENTITY

-- Telekom Malaysia
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Telekom Malaysia - Customer Protection', 'Telecom Provider',
 'If your phone number was exposed, report to TMU and request SIM swap protection.',
 'Multiple locations nationwide',
 'www.tm.com.my',
 '+603-2201 9201',
 'ccare@tm.com.my',
 'Monday-Friday: 8 AM - 6 PM, Saturday: 9 AM - 1 PM',
 'Billing/fraud department available extended hours');

-- MAXIS
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Maxis - Account & SIM Security', 'Telecom Provider',
 'If your phone number is with Maxis, request SIM card protection and verify no unauthorized changes.',
 'Multiple locations nationwide',
 'www.maxis.com.my',
 '123 (from Maxis phone) or +603-2167 3123',
 'customer.care@maxis.com.my',
 'Monday-Friday: 8:30 AM - 6 PM, Saturday: 10 AM - 3 PM',
 'Emergency number available 24/7');

-- DIGI
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('DiGi - Security & Protection', 'Telecom Provider',
 'If your phone number is with DiGi, verify SIM and request account security measures.',
 'Multiple locations nationwide',
 'www.digi.com.my',
 '+603-2628 0900',
 'cs@digi.com.my',
 'Monday-Friday: 8 AM - 6 PM, Saturday: 9 AM - 1 PM',
 '24/7 emergency support');

-- CYBERSECURITY & MONITORING SERVICES

-- Have I Been Pwned
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Have I Been Pwned (HIBP)', 'Cybersecurity Service',
 'International breach database. Check if your email appears in other breaches. Free service by Troy Hunt.',
 'International Service',
 'www.haveibeenpwned.com',
 'N/A - Online only',
 'N/A - Online only',
 '24/7 online',
 '24/7');

-- Google Account Security
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Google Account Security & Recovery', 'Tech Company',
 'If using Google services, use their security tools to review account access and recovery options.',
 'International',
 'www.google.com/account/security',
 'N/A - Online support form',
 'support-form via website',
 '24/7 online',
 '24/7 online form');

-- Microsoft Account Security
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Microsoft Account Security & Protection', 'Tech Company',
 'If using Microsoft services, review account compromises and set up recovery options.',
 'International',
 'www.account.microsoft.com/security',
 'N/A - Online support',
 'support@microsoft.com',
 '24/7 online',
 '24/7');

-- HEALTHCARE SPECIFIC

-- Private Health Association Malaysia
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Malaysian Medical Device Authority (MMDA)', 'Healthcare Regulator',
 'If healthcare data exposed, report to healthcare regulator for investigation.',
 'Kuala Lumpur',
 'www.mmda.gov.my',
 '+603-2720 8000',
 'info@mmda.gov.my',
 'Monday-Friday: 8:30 AM - 5:30 PM',
 'Business hours');

-- FRAUD SPECIFIC HOTLINES

-- Scam Alert Team
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('PDRM Anti-Scam Call Centre', 'Police Service',
 'Report if you become victim of scams following breach. Provide details of fraudsters.',
 'Nationwide service through PDRM',
 'www.rmp.gov.my',
 '999 (Emergency) or 03-2100 5250',
 'cybercrime@rmp.gov.my',
 '24 hours',
 '24/7 for emergencies');

-- LEGAL & CONSULTATION

-- Malaysian Bar Council
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Malaysian Bar Council - Legal Aid', 'Legal Organization',
 'If you need legal advice regarding breach claims or fraud. Provides legal assistance programs.',
 'Kuala Lumpur',
 'www.malaysianbar.org.my',
 '+603-2050 3011',
 'general@malaysianbar.org.my',
 'Monday-Friday: 9 AM - 5 PM',
 'Business hours');

-- FREE MONITORING TOOLS

-- FTP Checker (Temp credentials check)
INSERT INTO mitigation_resources (resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability) VALUES
('Password Strength Tester', 'Online Tool',
 'Test password strength to ensure your new passwords are secure.',
 'Various providers available',
 'www.howsecureismypassword.net',
 'N/A - Web tool',
 'N/A - Web tool',
 '24/7 online',
 '24/7');

-- USEFUL CONTACTS SUMMARY FOR QUICK REFERENCE

-- Note: These resources can be filtered and displayed based on:
-- 1. Type of breach (financial, medical, identity, general)
-- 2. Severity level (HIGH, MEDIUM, LOW)
-- 3. User preference (show top 3, all resources, Malaysian-specific only)
-- 4. Recommended action type

-- The mitigation_resources table allows flexible display of relevant resources
-- based on user's specific breach situation
