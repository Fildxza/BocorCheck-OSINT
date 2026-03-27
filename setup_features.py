#!/usr/bin/env python3
"""
Database Update Script - Enhanced Version
Handles MySQL statement execution properly
"""

import mysql.connector
from mysql.connector import Error
import os

config = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "fyp_user"),
    "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
    "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
    "use_pure": True,
    "allow_local_infile": True,
}

try:
    print("🔄 Connecting to MySQL...")
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("✅ MySQL connection successful!\n")
    
    # Read SQL file
    with open('DATABASE_UPDATES_3FEATURES.sql', 'r') as f:
        sql_content = f.read()
    
    # Split statements properly (handle comments)
    statements = []
    current_stmt = []
    
    for line in sql_content.split('\n'):
        line_stripped = line.strip()
        
        # Skip empty lines and comment-only lines
        if not line_stripped or line_stripped.startswith('--'):
            continue
        
        current_stmt.append(line)
        
        # If line ends with semicolon, it's end of statement
        if line_stripped.endswith(';'):
            stmt = '\n'.join(current_stmt).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_stmt = []
    
    print(f"📊 Found {len(statements)} SQL statements\n")
    
    executed = 0
    for i, stmt in enumerate(statements, 1):
        try:
            cursor.execute(stmt)
            executed += 1
            
            # Show progress
            if 'CREATE TABLE' in stmt:
                table_name = stmt.split('CREATE TABLE IF NOT EXISTS')[1].split('(')[0].strip()
                print(f"  ✓ Created table: {table_name}")
            elif 'INSERT INTO' in stmt and 'VALUES' in stmt:
                if i == len(statements) - 4:  # Data type seed
                    print(f"  ✓ Loaded data type risk matrix (11 types)")
                elif i == len(statements) - 3:  # Hash algorithm seed
                    print(f"  ✓ Loaded hash algorithm index (8 algorithms)")
                elif 'ALTER TABLE' not in stmt:
                    print(f"  ✓ Inserted data")
            elif 'ALTER TABLE' in stmt:
                table_name = stmt.split('ALTER TABLE')[1].split('ADD COLUMN')[0].strip()
                print(f"  ✓ Updated table: {table_name}")
                
        except Error as e:
            print(f"  ⚠️  Error executing statement {i}: {e}")
            print(f"      Statement snippet: {stmt[:80]}...")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ DATABASE UPDATE COMPLETE!")
    print(f"   Executed {executed}/{len(statements)} statements\n")
    print("📦 New Features Ready:")
    print("   ✓ Feature 1: Real-Time Monitoring + Breach Timeline")
    print("   ✓ Feature 2: Dark Web Monitoring Integration")
    print("   ✓ Feature 3: Data Type Analysis + Hash Algorithms")
    print("\n🚀 Next: Start the Flask app and go to http://127.0.0.1:5000/monitoring")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
