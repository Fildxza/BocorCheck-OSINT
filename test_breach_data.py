"""
Test script for Breach Data Integration
Helps verify that breach tables are created and data is properly inserted
"""

import os
from mysql.connector import connect, Error as MySQLError


def get_db_config() -> dict:
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "fyp_user"),
        "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
        "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
        "use_pure": True,
    }


def test_breach_tables():
    """Test if breach tables exist and have correct structure"""
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor() as cursor:
                # Check if tables exist
                print("\n📋 CHECKING BREACH TABLES...")
                cursor.execute("""
                    SELECT TABLE_NAME FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME IN ('breaches', 'breach_data_types', 'user_breach_matches')
                """, (cfg['database'],))
                
                existing_tables = {row[0] for row in cursor.fetchall()}
                expected_tables = {'breaches', 'breach_data_types', 'user_breach_matches'}
                
                for table in expected_tables:
                    if table in existing_tables:
                        print(f"  ✓ Table '{table}' exists")
                    else:
                        print(f"  ✗ Table '{table}' MISSING - Run db_setup.py first!")
                        return False
                
                return True
                
    except MySQLError as e:
        print(f"  ✗ Database connection failed: {e}")
        return False


def test_breach_data():
    """Test if breach data is properly inserted"""
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor() as cursor:
                print("\n📊 CHECKING BREACH DATA...")
                
                # Count breaches
                cursor.execute("SELECT COUNT(*) FROM breaches")
                breach_count = cursor.fetchone()[0]
                print(f"  ✓ Total breaches in database: {breach_count}")
                
                if breach_count == 0:
                    print("  ⚠ No breach data found - Need to insert seed data")
                    return False
                
                # Get statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_breaches,
                        SUM(affected_records) as total_affected_records,
                        MAX(date) as most_recent_breach,
                        COUNT(CASE WHEN severity='HIGH' THEN 1 END) as high_risk_count,
                        COUNT(CASE WHEN severity='MEDIUM' THEN 1 END) as medium_risk_count,
                        COUNT(CASE WHEN severity='LOW' THEN 1 END) as low_risk_count
                    FROM breaches
                """)
                
                stats = cursor.fetchone()
                total, affected, recent, high, medium, low = stats
                
                print(f"  • Total breaches: {total}")
                print(f"  • Total affected records: {affected:,}")
                print(f"  • Most recent breach: {recent}")
                print(f"  • HIGH risk: {high} | MEDIUM risk: {medium} | LOW risk: {low}")
                
                # Count data types
                cursor.execute("SELECT COUNT(*) FROM breach_data_types")
                datatype_count = cursor.fetchone()[0]
                print(f"  • Total data type entries: {datatype_count}")
                
                # Show breach list
                print("\n📌 BREACH DATABASE CONTENTS:")
                cursor.execute("""
                    SELECT id, name, date, affected_records, severity 
                    FROM breaches 
                    ORDER BY date DESC
                """)
                
                for row in cursor.fetchall():
                    breach_id, name, date, records, severity = row
                    print(f"  [{breach_id:2d}] {name:25s} | {date} | {records:>10,} records | {severity}")
                
                # Show data types per breach
                print("\n📂 DATA TYPES EXPOSED BY BREACH:")
                cursor.execute("""
                    SELECT b.name, GROUP_CONCAT(bdt.data_type SEPARATOR ', ')
                    FROM breaches b
                    LEFT JOIN breach_data_types bdt ON b.id = bdt.breach_id
                    GROUP BY b.id, b.name
                    ORDER BY b.date DESC
                """)
                
                for row in cursor.fetchall():
                    breach_name, datatypes = row
                    print(f"  • {breach_name}:")
                    if datatypes:
                        for dt in datatypes.split(', '):
                            print(f"      - {dt}")
                
                return True
                
    except MySQLError as e:
        print(f"  ✗ Error querying breach data: {e}")
        return False


def test_investigation_integration():
    """Test if investigation_logs table has user_id column"""
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor() as cursor:
                print("\n🔗 CHECKING INVESTIGATION INTEGRATION...")
                
                cursor.execute("""
                    SELECT COLUMN_NAME FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'investigation_logs' 
                    AND COLUMN_NAME = 'user_id'
                """, (cfg['database'],))
                
                if cursor.fetchone():
                    print("  ✓ investigation_logs has user_id column")
                    return True
                else:
                    print("  ✗ investigation_logs missing user_id column")
                    return False
                    
    except MySQLError as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    print("=" * 70)
    print("BocorCheck Breach Data Integration Test")
    print("=" * 70)
    
    # Run all tests
    test1 = test_breach_tables()
    test2 = test_breach_data() if test1 else False
    test3 = test_investigation_integration()
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    results = [
        ("Breach tables exist", test1),
        ("Breach data inserted", test2),
        ("Investigation integration", test3),
    ]
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_pass = all(result for _, result in results)
    
    print("\n" + "=" * 70)
    if all_pass:
        print("✓ All tests PASSED! Breach database is ready.")
        print("\nNEXT STEPS:")
        print("  1. Run: python app.py")
        print("  2. Try searching with sample emails:")
        print("     - user@email.com")
        print("     - test@gmail.com")
        print("  3. Check if breach results appear")
    else:
        print("✗ Some tests FAILED. Please:")
        print("  1. Run: python db_setup.py")
        print("  2. Then run this test again: python test_breach_data.py")
        if not test2:
            print("  3. If tables exist but no data, run:")
            print("     mysql -u fyp_user -p fyp_osint < breaches_seed_data.sql")
    
    print("=" * 70)
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
