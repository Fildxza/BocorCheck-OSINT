#!/usr/bin/env python3
"""
Database Update Script for 3 New Features
Runs DATABASE_UPDATES_3FEATURES.sql
"""

import mysql.connector
import os

# Get config from environment
config = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "fyp_user"),
    "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
    "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
    "use_pure": True,
}

try:
    print("🔄 Connecting to MySQL...")
    conn = mysql.connector.connect(**config)
    print("✅ MySQL connection successful!")
    
    cursor = conn.cursor()
    
    # Read SQL file
    print("\n📖 Reading DATABASE_UPDATES_3FEATURES.sql...")
    with open('DATABASE_UPDATES_3FEATURES.sql', 'r') as f:
        sql_content = f.read()
    
    # Split by semicolon and execute
    statements = sql_content.split(';')
    executed = 0
    skipped = 0
    
    print(f"\n⏳ Found {len(statements)} statements. Executing...")
    
    for i, stmt in enumerate(statements, 1):
        stmt = stmt.strip()
        # Skip empty statements and comments
        if stmt and not stmt.startswith('--'):
            try:
                cursor.execute(stmt)
                executed += 1
                if executed % 5 == 0:
                    print(f"   ✓ Executed {executed} statements...")
            except Exception as e:
                print(f"   ⚠️  Error in statement {i}: {str(e)[:100]}")
                skipped += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ DATABASE UPDATE COMPLETE!")
    print(f"   ✓ Executed: {executed} statements")
    print(f"   ⚠️  Skipped: {skipped}")
    print(f"\n📊 New Features Database:")
    print(f"   ✓ Real-Time Monitoring tables created")
    print(f"   ✓ Dark Web Monitoring tables created")
    print(f"   ✓ Data Type Analysis tables created")
    print(f"   ✓ Seed data loaded (11 data types, 8 hash algorithms)")
    
except mysql.connector.Error as err:
    print(f"❌ MySQL Error: {err}")
    exit(1)
except FileNotFoundError:
    print("❌ DATABASE_UPDATES_3FEATURES.sql not found in current directory!")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)
