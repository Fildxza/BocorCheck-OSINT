"""
Seed Timeline Data Script
This script populates the database with sample breach timeline and results data
for a specific user and investigation to ensure the timeline visualization can be tested.
"""

import os
from mysql.connector import connect, Error as MySQLError
from datetime import datetime, timedelta

def get_db_config() -> dict:
    """Get database configuration from environment variables"""
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "fyp_user"),
        "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
        "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
        "use_pure": True,
    }

def seed_data():
    """Connects to the database and inserts sample data."""
    cfg = get_db_config()
    
    # --- CONFIGURATION ---
    # IMPORTANT: Change these IDs to match your local database
    TARGET_USER_ID = 1  # The user_id you are logged in as
    TARGET_INVESTIGATION_ID = 1 # The investigation_id you are viewing
    # ---------------------

    # Sample data to be inserted
    sample_breaches = [
        {
            "name": "MyFitnessPal (2018)",
            "date": "2018-02-20",
            "discovery": "2018-03-25",
            "risk": 85,
            "exposed": "Usernames, Email addresses, IP addresses, Passwords",
            "crackability": "High"
        },
        {
            "name": "Canva (2019)",
            "date": "2019-05-24",
            "discovery": "2019-05-24",
            "risk": 90,
            "exposed": "Usernames, Email addresses, Geographic locations, Passwords",
            "crackability": "Medium"
        },
        {
            "name": "Zynga (2019)",
            "date": "2019-09-01",
            "discovery": "2019-09-12",
            "risk": 70,
            "exposed": "Usernames, Email addresses, Phone numbers, Passwords",
            "crackability": "Low"
        },
        {
            "name": "Wattpad (2020)",
            "date": "2020-06-15",
            "discovery": "2020-07-13",
            "risk": 75,
            "exposed": "Usernames, Email addresses, IP addresses, Passwords",
            "crackability": "Medium"
        },
        {
            "name": "Microsoft (2021)",
            "date": "2021-01-05",
            "discovery": "2021-03-02",
            "risk": 88,
            "exposed": "Email addresses, Email content, User files",
            "crackability": "N/A"
        }
    ]

    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            print("✅ Successfully connected to the database.")

            # Check if user and investigation exist
            cursor.execute("SELECT id FROM users WHERE id = %s", (TARGET_USER_ID,))
            if not cursor.fetchone():
                print(f"❌ Error: User with ID {TARGET_USER_ID} not found. Please update TARGET_USER_ID in the script.")
                return

            cursor.execute("SELECT id FROM investigation_logs WHERE id = %s AND user_id = %s", (TARGET_INVESTIGATION_ID, TARGET_USER_ID))
            if not cursor.fetchone():
                print(f"❌ Error: Investigation with ID {TARGET_INVESTIGATION_ID} for user {TARGET_USER_ID} not found.")
                print("   Please create an investigation first or update the IDs in the script.")
                return

            print(f"🌱 Seeding data for User ID: {TARGET_USER_ID}, Investigation ID: {TARGET_INVESTIGATION_ID}")

            for breach in sample_breaches:
                # Insert into breach_timeline
                try:
                    timeline_sql = """
                        INSERT INTO breach_timeline 
                        (investigation_id, breach_name, breach_date, discovery_date, status, initial_risk_score, current_risk_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            discovery_date = VALUES(discovery_date),
                            current_risk_score = VALUES(current_risk_score);
                    """
                    discovery_date = datetime.strptime(breach["discovery"], "%Y-%m-%d")
                    days_diff = (discovery_date - datetime.strptime(breach["date"], "%Y-%m-%d")).days
                    
                    cursor.execute(timeline_sql, (
                        TARGET_INVESTIGATION_ID,
                        breach["name"],
                        breach["date"],
                        breach["discovery"],
                        "confirmed",
                        breach["risk"],
                        breach["risk"]
                    ))
                    print(f"  -> Inserted '{breach['name']}' into breach_timeline.")
                except MySQLError as e:
                    print(f"  -> ⚠️ Error inserting into breach_timeline for '{breach['name']}': {e}")


                # Insert into breach_results
                try:
                    results_sql = """
                        INSERT INTO breach_results
                        (investigation_id, breach_name, breach_date, data_exposed, crackability, source)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            data_exposed = VALUES(data_exposed);
                    """
                    cursor.execute(results_sql, (
                        TARGET_INVESTIGATION_ID,
                        breach["name"],
                        breach["date"],
                        breach["exposed"],
                        breach["crackability"],
                        "Seed Script"
                    ))
                    print(f"  -> Inserted '{breach['name']}' into breach_results.")
                except MySQLError as e:
                    print(f"  -> ⚠️ Error inserting into breach_results for '{breach['name']}': {e}")

            conn.commit()
            print("\n✅✅✅ Database seeding complete! Please refresh the timeline page.")

    except MySQLError as e:
        print(f"❌ Database connection or operation failed: {e}")

if __name__ == "__main__":
    seed_data()
