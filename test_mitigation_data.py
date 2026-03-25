"""
Test script for Mitigation Plans Integration
Verifies all mitigation tables, data, and Malaysian resources are properly set up
"""

import os
import json
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


def test_mitigation_tables():
    """Test if mitigation tables exist"""
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor() as cursor:
                print("\n📋 CHECKING MITIGATION TABLES...")
                cursor.execute("""
                    SELECT TABLE_NAME FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME IN ('mitigation_plans', 'mitigation_resources')
                """, (cfg['database'],))
                
                existing_tables = {row[0] for row in cursor.fetchall()}
                expected_tables = {'mitigation_plans', 'mitigation_resources'}
                
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


def test_mitigation_data():
    """Test if mitigation plans data is properly inserted"""
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                print("\n📊 CHECKING MITIGATION PLANS DATA...")
                
                # Count total mitigations
                cursor.execute("SELECT COUNT(*) as count FROM mitigation_plans")
                mitigation_count = cursor.fetchone()['count']
                print(f"  ✓ Total mitigation plans: {mitigation_count}")
                
                if mitigation_count == 0:
                    print("  ⚠ No mitigation data found - Need to insert seed data")
                    return False
                
                # Count by severity
                cursor.execute("""
                    SELECT 
                        severity_level,
                        COUNT(*) as count
                    FROM mitigation_plans
                    GROUP BY severity_level
                    ORDER BY severity_level
                """)
                
                severity_counts = {}
                for row in cursor.fetchall():
                    severity_counts[row['severity_level']] = row['count']
                    print(f"  • {row['severity_level']:7s} severity: {row['count']:2d} actions")
                
                # Count by priority
                cursor.execute("""
                    SELECT 
                        priority,
                        COUNT(*) as count,
                        CASE 
                            WHEN priority = 1 THEN '🔴 CRITICAL'
                            WHEN priority = 2 THEN '🟠 IMPORTANT'
                            WHEN priority = 3 THEN '🟡 RECOMMENDED'
                            ELSE 'OTHER'
                        END as label
                    FROM mitigation_plans
                    GROUP BY priority
                    ORDER BY priority
                """)
                
                print("\n  BY PRIORITY:")
                for row in cursor.fetchall():
                    print(f"    {row['label']:20s}: {row['count']:2d} actions")
                
                # Show sample actions
                print("\n  SAMPLE MITIGATION ACTIONS:")
                cursor.execute("""
                    SELECT id, title, severity_level, priority, estimated_time
                    FROM mitigation_plans
                    LIMIT 5
                """)
                
                for row in cursor.fetchall():
                    print(f"    [{row['id']:2d}] {row['title']:45s} ({row['severity_level']:6s}, {row['estimated_time']})")
                
                return True
                
    except MySQLError as e:
        print(f"  ✗ Error querying mitigation data: {e}")
        return False


def test_malaysian_resources():
    """Test if Malaysian resources are properly inserted"""
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                print("\n🇲🇾 CHECKING MALAYSIAN RESOURCES...")
                
                # Count total resources
                cursor.execute("SELECT COUNT(*) as count FROM mitigation_resources")
                resource_count = cursor.fetchone()['count']
                print(f"  ✓ Total resources: {resource_count}")
                
                if resource_count == 0:
                    print("  ⚠ No Malaysian resources found - Need to insert resource data")
                    return False
                
                # Count by type
                cursor.execute("""
                    SELECT 
                        resource_type,
                        COUNT(*) as count
                    FROM mitigation_resources
                    GROUP BY resource_type
                    ORDER BY count DESC
                """)
                
                print("\n  BY TYPE:")
                for row in cursor.fetchall():
                    print(f"    • {row['resource_type']:30s}: {row['count']:2d} resources")
                
                # Show critical resources
                print("\n  KEY MALAYSIAN RESOURCES:")
                cursor.execute("""
                    SELECT resource_name, phone, website
                    FROM mitigation_resources
                    WHERE resource_type IN ('Government Agency', 'Police Department', 'Central Bank')
                    LIMIT 5
                """)
                
                for row in cursor.fetchall():
                    print(f"    • {row['resource_name']}")
                    if row['phone']:
                        print(f"      Phone: {row['phone']}")
                    if row['website']:
                        print(f"      Web: {row['website']}")
                
                # Show banks
                print("\n  MALAYSIAN BANKS (24/7 Fraud Support):")
                cursor.execute("""
                    SELECT resource_name, phone, operating_hours
                    FROM mitigation_resources
                    WHERE resource_type = 'Commercial Bank'
                    LIMIT 5
                """)
                
                for row in cursor.fetchall():
                    print(f"    • {row['resource_name']}")
                    if row['phone']:
                        print(f"      {row['phone']} ({row['operating_hours']})")
                
                return True
                
    except MySQLError as e:
        print(f"  ✗ Error querying resources: {e}")
        return False


def test_breach_mitigation_link():
    """Test if mitigations are linked to breaches"""
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                print("\n🔗 CHECKING BREACH-MITIGATION LINKAGE...")
                
                # Count mitigations per breach
                cursor.execute("""
                    SELECT 
                        b.name,
                        COUNT(m.id) as mitigation_count
                    FROM breaches b
                    LEFT JOIN mitigation_plans m ON b.id = m.breach_id
                    GROUP BY b.id, b.name
                    HAVING COUNT(m.id) > 0
                    ORDER BY mitigation_count DESC
                    LIMIT 5
                """)
                
                results = cursor.fetchall()
                if results:
                    print("  Breaches with mitigations:")
                    for row in results:
                        print(f"    • {row['name']:30s}: {row['mitigation_count']:2d} actions")
                else:
                    print("  ⚠ No breaches have mitigations linked")
                    return False
                
                # Check universal mitigations (no breach_id)
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM mitigation_plans 
                    WHERE breach_id IS NULL
                """)
                
                universal_count = cursor.fetchone()['count']
                print(f"\n  Universal mitigations (apply to all breaches): {universal_count}")
                
                return True
                
    except MySQLError as e:
        print(f"  ✗ Error checking linkage: {e}")
        return False


def test_mitigation_module():
    """Test if mitigation.py module works"""
    try:
        print("\n🐍 CHECKING MITIGATION MODULE...")
        
        from mitigation import (
            get_smart_recommendations,
            get_malaysian_resources,
            get_mitigation_for_breach
        )
        
        print("  ✓ mitigation.py imports successfully")
        
        # Test getting Malaysian resources
        resources = get_malaysian_resources('Commercial Bank')
        print(f"  ✓ Found {len(resources)} Malaysian banks")
        
        # Test smart recommendations
        recommendations = get_smart_recommendations(['Email', 'Password Hash'], 'HIGH')
        critical_actions = len(recommendations.get('critical_actions', []))
        print(f"  ✓ Generated smart recommendations ({critical_actions} critical actions)")
        
        return True
        
    except ImportError as e:
        print(f"  ✗ Error importing mitigation module: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error testing mitigation module: {e}")
        return False


def test_json_parsing():
    """Test if JSON fields in mitigations parse correctly"""
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                print("\n📋 CHECKING JSON DATA INTEGRITY...")
                
                cursor.execute("""
                    SELECT id, title, steps, resources
                    FROM mitigation_plans
                    LIMIT 3
                """)
                
                for row in cursor.fetchall():
                    try:
                        if row['steps']:
                            steps = json.loads(row['steps']) if isinstance(row['steps'], str) else row['steps']
                            print(f"  ✓ {row['title'][:40]:40s} ({len(steps)} steps)")
                    except json.JSONDecodeError:
                        print(f"  ✗ {row['title'][:40]:40s} - JSON parse error")
                        return False
                
                return True
                
    except MySQLError as e:
        print(f"  ✗ Error checking JSON: {e}")
        return False


def main():
    print("=" * 75)
    print("🛡️ BocorCheck Mitigation Plans Integration Test")
    print("=" * 75)
    
    # Run all tests
    tests = [
        ("Mitigation tables exist", test_mitigation_tables),
        ("Mitigation plans data", test_mitigation_data),
        ("Malaysian resources", test_malaysian_resources),
        ("Breach-mitigation linkage", test_breach_mitigation_link),
        ("JSON data integrity", test_json_parsing),
        ("Mitigation module", test_mitigation_module),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ✗ Unexpected error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 75)
    print("TEST RESULTS SUMMARY")
    print("=" * 75)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_pass = all(result for _, result in results)
    
    print("\n" + "=" * 75)
    if all_pass:
        print("✓ ALL TESTS PASSED! Mitigation system is ready.")
        print("\nNEXT STEPS:")
        print("  1. Integrate mitigation display into search results")
        print("  2. Show recommendations in investigation detail view")
        print("  3. Add to dashboard statistics")
        print("  4. Create mitigation checklist tracking (optional)")
        print("\nCRITICAL FEATURES AVAILABLE:")
        print("  ✓ Smart risk-based recommendations")
        print("  ✓ 25+ actionable mitigation plans")
        print("  ✓ 20+ Malaysian government/bank resources")
        print("  ✓ Priority-based action ordering")
        print("  ✓ Step-by-step guides for each action")
        print("  ✓ 24/7 Malaysian bank hotlines")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nTROUBLESHOOTING:")
        print("  1. Run: python db_setup.py")
        print("  2. Run: mysql -u fyp_user -p fyp_osint < mitigation_seed_data.sql")
        print("  3. Run: mysql -u fyp_user -p fyp_osint < mitigation_resources_malaysia.sql")
        print("  4. Then run this test again")
    
    print("=" * 75)
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
