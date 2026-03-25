"""
Setup script to populate mitigation data into the database
Creates sample breaches and mitigation plans for demonstration
"""

from mysql.connector import connect, Error as MySQLError
import os

def get_db_config():
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "fyp_user"),
        "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
        "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
        "use_pure": True,
    }

def setup_mitigation_data():
    """Setup mitigation plans and resources"""
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            
            # First, create sample breaches if they don't exist
            print("📝 Creating sample breaches...")
            breaches = [
                (1, "LinkedIn 2012", "2012-06-05", 6500000, "User credentials compromised", "HIGH"),
                (2, "Adobe 2013", "2013-10-03", 150000000, "Password hashes and user data", "HIGH"),
                (3, "Yahoo 2014", "2014-12-21", 500000000, "User info including passwords", "HIGH"),
                (4, "Equifax 2017", "2017-07-29", 147000000, "SSN, credit info exposed", "HIGH"),
                (5, "Facebook 2019", "2019-04-03", 100000000, "User personal data leaked", "HIGH"),
            ]
            
            for breach_id, name, date, records, desc, severity in breaches:
                cursor.execute(
                    "INSERT IGNORE INTO breaches (id, name, date, affected_records, description, severity) VALUES (%s, %s, %s, %s, %s, %s)",
                    (breach_id, name, date, records, desc, severity)
                )
            conn.commit()
            print("✅ Breaches created")
            
            # Insert universal mitigation plans (HIGH PRIORITY)
            print("📝 Importing mitigation plans...")
            mitigations = [
                # Password compromised
                (1, "Password Hash", "HIGH", "password_reset", 1, 
                 "Change Your Password Immediately",
                 "Your password hash was included in the breach. Change it immediately.",
                 '["1. Go to account settings","2. Click Change Password","3. Create new strong password (16+ chars)","4. Enable 2FA","5. Logout from all sessions"]',
                 "5 minutes", True),
                
                (1, "Password Hash", "HIGH", "enable_2fa", 1,
                 "Enable Two-Factor Authentication (2FA)",
                 "Two-factor authentication adds extra security layer even if password is compromised.",
                 '["1. Open account security settings","2. Find 2FA option","3. Download authenticator app","4. Scan QR code","5. Save backup codes","6. Enable 2FA"]',
                 "10 minutes", True),
                
                # Email compromised  
                (2, "Email", "HIGH", "monitor_phishing", 1,
                 "Monitor for Phishing Attacks",
                 "Your email is on spam lists. Be vigilant for suspicious emails.",
                 '["1. Be suspicious of urgent emails asking for passwords","2. Never click suspicious links","3. Check sender address carefully","4. Report phishing emails","5. Mark as spam/phishing"]',
                 "ongoing", True),
                
                # Personal data compromised
                (2, "Full Name", "HIGH", "identity_theft_monitoring", 1,
                 "Monitor for Identity Theft (Malaysia-Specific)",
                 "Your personal info could be used to open fraudulent accounts.",
                 '["1. Check MyDebtFreee credit report","2. Review for unauthorized applications","3. Contact Malaysian banks","4. Place fraud alert","5. File PDRM report if fraud suspected"]',
                 "30 minutes", True),
                
                (2, "Date of Birth", "HIGH", "secure_recovery_info", 2,
                 "Secure Your Account Recovery Information",
                 "Update recovery methods to prevent account takeover.",
                 '["1. Update recovery email","2. Update recovery phone","3. Update security questions","4. Remove outdated contacts","5. Save offline backup codes"]',
                 "15 minutes", True),
                
                # Financial data compromised
                (5, "Account Balance", "HIGH", "monitor_fraud", 1,
                 "Monitor Financial Accounts 24/7",
                 "Your account info is exposed. High risk of unauthorized transactions.",
                 '["1. Contact your bank immediately","2. Request transaction history","3. Review for fraud","4. Request fraud alert","5. Enable SMS alerts","6. Change online banking password"]',
                 "15 minutes", True),
            ]
            
            for breach_id, data_type, severity, action_type, priority, title, desc, steps, time, my_context in mitigations:
                cursor.execute("""
                    INSERT INTO mitigation_plans 
                    (breach_id, data_type, severity_level, action_type, priority, title, description, steps, estimated_time, malaysian_context)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (breach_id, data_type, severity, action_type, priority, title, desc, steps, time, my_context))
            
            conn.commit()
            cursor.execute("SELECT COUNT(*) FROM mitigation_plans")
            plan_count = cursor.fetchone()[0]
            print(f"✅ Mitigation plans imported: {plan_count} records")
            
            # Insert Malaysian resources linked to mitigation plans
            print("📝 Adding Malaysian resources...")
            resources = [
                # Get first mitigation plan ID to link resources
            ]
            cursor.execute("SELECT id FROM mitigation_plans LIMIT 1")
            first_plan = cursor.fetchone()
            if first_plan:
                mitigation_id = first_plan[0]
                
                # Malaysian Government & Financial Institutions
                resources_data = [
                    (mitigation_id, "MICC - Malaysian Internet Crime Committee", "Government Agency", 
                     "Official Malaysian agency for cybercrime reporting", "Putrajaya, Malaysia",
                     "www.micc.gov.my", "+603-8000-8000", "contact@micc.gov.my",
                     "Mon-Fri: 9 AM - 5 PM", "24/7 online"),
                    
                    (mitigation_id, "PDRM Cybercrime Division", "Police Department",
                     "Royal Malaysia Police cybercrime unit for formal reports", "IPD Sentosa, KL",
                     "www.rmp.gov.my", "03-2100 5250", "cybercrime@rmp.gov.my",
                     "Mon-Fri: 8 AM - 6 PM", "Emergency: 999"),
                    
                    (mitigation_id, "MyDebtFreee - Credit Bureau", "Credit Bureau",
                     "Malaysia credit information center. Check for identity theft", "Kuala Lumpur",
                     "www.mydebtfreee.com.my", "+603-4101 8888", "info@mydebtfreee.com.my",
                     "Mon-Fri: 9 AM - 5 PM", "24/7 online"),
                    
                    (mitigation_id, "Maybank - 24/7 Hotline", "Bank",
                     "Malaysia largest bank with 24/7 fraud protection hotline", "Kuala Lumpur",
                     "www.maybank.com", "1-300-881-881", "support@maybank.com",
                     "24/7", "24/7"),
                    
                    (mitigation_id, "Bank Negara Malaysia", "Central Bank",
                     "Malaysia Central Bank - Consumer protection & financial regulations", "Kuala Lumpur",
                     "www.bnm.gov.my", "1-300-88-5465", "general@bnm.gov.my",
                     "Mon-Fri: 9 AM - 5 PM", "During business hours"),
                    
                    (mitigation_id, "Jabatan Pendaftaran Negara (JPN)", "Government Agency",
                     "Malaysian National Registration Department - MyKad/IC verification", "Putrajaya",
                     "www.jpn.gov.my", "+603-8000-0000", "info@jpn.gov.my",
                     "Mon-Fri: 8 AM - 5 PM", "During business hours"),
                ]
                
                for resource in resources_data:
                    cursor.execute("""
                        INSERT INTO mitigation_resources 
                        (mitigation_id, resource_name, resource_type, description, contact, website, phone, email, operating_hours, availability)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, resource)
                
                conn.commit()
                cursor.execute("SELECT COUNT(*) FROM mitigation_resources")
                resource_count = cursor.fetchone()[0]
                print(f"✅ Malaysian resources added: {resource_count} records")
            
            cursor.close()
    except MySQLError as e:
        print(f"❌ Database error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Setting up mitigation data...")
    if setup_mitigation_data():
        print("\n✅ Mitigation setup completed successfully!")
    else:
        print("\n❌ Setup failed")
