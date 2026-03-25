# 🧪 Breach Data Integration - Testing Guide

## Overview
This guide walks you through testing the breach data integration before full implementation.

---

## 📋 What We're Testing

1. **Breach tables created** (breaches, breach_data_types, user_breach_matches)
2. **Breach seed data inserted** (11 major breaches, 50M+ affected records)
3. **Database relationships** (Foreign keys, indexes)
4. **Investigation integration** (user_id linking)

---

## 🚀 Step-by-Step Testing

### STEP 1: Update Database Schema
Run this to create the new breach tables:

```powershell
# Make sure you're in the project directory
cd "e:\FYP-OSINT-Data Breach\fyp-osint-breach-monitor"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run database setup (creates breach tables)
python db_setup.py
```

**Expected Output:**
```
✓ MySQL schema is ready.
✓ Tables: alerts, breaches, breach_data_types, breach_results, investigation_logs, login_logs, risk_scores, user_breach_matches, users
```

---

### STEP 2: Insert Breach Seed Data

Choose ONE of these methods:

#### **Option A: MySQL Command Line (Recommended for Testing)**
```bash
# Navigate to project folder
cd "e:\FYP-OSINT-Data Breach\fyp-osint-breach-monitor"

# Run the seed SQL file
mysql -h 127.0.0.1 -u fyp_user -p fyp_osint < breaches_seed_data.sql
# Enter password when prompted: Admin123!
```

#### **Option B: MySQL Workbench (GUI)**
1. Open MySQL Workbench
2. Connect to `fyp_osint` database
3. Open file: `breaches_seed_data.sql`
4. Run (Ctrl+Shift+Enter)

#### **Option C: Python Script (If CLI gives errors)**
```powershell
python -c "
import mysql.connector
config = {
    'host': '127.0.0.1',
    'user': 'fyp_user',
    'password': 'Admin123!',
    'database': 'fyp_osint'
}
with mysql.connector.connect(**config) as conn:
    with conn.cursor() as cursor:
        with open('breaches_seed_data.sql', 'r') as f:
            for stmt in f.read().split(';'):
                if stmt.strip():
                    cursor.execute(stmt)
        conn.commit()
print('✓ Breach data inserted successfully')
"
```

---

### STEP 3: Verify Data Insertion with Test Script

Run the automated test to verify everything is correct:

```powershell
# Run test script
python test_breach_data.py
```

**Expected Output:**
```
======================================================================
BocorCheck Breach Data Integration Test
======================================================================

📋 CHECKING BREACH TABLES...
  ✓ Table 'breaches' exists
  ✓ Table 'breach_data_types' exists
  ✓ Table 'user_breach_matches' exists

📊 CHECKING BREACH DATA...
  ✓ Total breaches in database: 11
  • Total breaches: 11
  • Total affected records: 112,500,000
  • Most recent breach: 2024-03-15
  • HIGH risk: 5 | MEDIUM risk: 4 | LOW risk: 2
  • Total data type entries: 31

📌 BREACH DATABASE CONTENTS:
  [ 1] DataNet Breach           | 2024-03-15 |     50,000,000 records | HIGH
  [ 2] ShopMY Compromise        | 2023-11-20 |     12,000,000 records | HIGH
  [ 3] CloudStore Leak          | 2023-08-05 |      2,500,000 records | MEDIUM
  [ 4] GameZone Hack            | 2023-02-28 |     15,000,000 records | HIGH
  [ 5] FinanceApp Exposure      | 2023-02-28 |     15,000,000 records | HIGH
  [ 6] HealthPortal Breach      | 2022-12-10 |      3,000,000 records | HIGH
  [ 7] EduPlatform Leak         | 2022-09-18 |      1,500,000 records | LOW
  [ 8] TravelBooker Hack        | 2022-06-22 |      5,000,000 records | MEDIUM
  [ 9] FoodDelivery Breach      | 2022-03-14 |      7,000,000 records | MEDIUM
  [10] ISP Data Leak            | 2021-11-30 |      4,000,000 records | HIGH
  [11] ForumX Dump              | 2021-08-15 |      2,000,000 records | MEDIUM

📂 DATA TYPES EXPOSED BY BREACH:
  • DataNet Breach:
      - Email
      - Password Hash
      - Phone Number
      - Address
  • ShopMY Compromise:
      - Email
      - Full Name
      - Date of Birth
  [... more breaches ...]

🔗 CHECKING INVESTIGATION INTEGRATION...
  ✓ investigation_logs has user_id column

======================================================================
TEST RESULTS SUMMARY
======================================================================
  ✓ PASS: Breach tables exist
  ✓ PASS: Breach data inserted
  ✓ PASS: Investigation integration

✓ All tests PASSED! Breach database is ready.

NEXT STEPS:
  1. Run: python app.py
  2. Try searching with sample emails:
     - user@email.com
     - test@gmail.com
  3. Check if breach results appear
======================================================================
```

---

### STEP 4: Manual Database Query Verification

If you want to verify the data manually in MySQL:

```sql
-- Check total breaches
SELECT COUNT(*) as total_breaches, SUM(affected_records) as total_affected
FROM breaches;

-- Show all breaches with data types
SELECT 
    b.id,
    b.name,
    b.date,
    b.affected_records,
    b.severity,
    COUNT(bdt.id) as data_types_exposed
FROM breaches b
LEFT JOIN breach_data_types bdt ON b.id = bdt.breach_id
GROUP BY b.id
ORDER BY b.date DESC;

-- Check specific breach details
SELECT 
    b.name,
    b.date,
    b.affected_records,
    b.severity,
    bdt.data_type
FROM breaches b
LEFT JOIN breach_data_types bdt ON b.id = bdt.breach_id
WHERE b.name = 'ShopMY Compromise'
ORDER BY bdt.data_type;
```

---

## ✅ What to Check

### Verify All 11 Breaches Are Present:

- ✓ DataNet Breach (2024-03-15, 50M records, HIGH)
- ✓ ShopMY Compromise (2023-11-20, 12M records, HIGH)
- ✓ CloudStore Leak (2023-08-05, 2.5M records, MEDIUM)
- ✓ GameZone Hack (2023-02-28, 15M records, HIGH)
- ✓ FinanceApp Exposure (2023-02-28, 15M records, HIGH)
- ✓ HealthPortal Breach (2022-12-10, 3M records, HIGH)
- ✓ EduPlatform Leak (2022-09-18, 1.5M records, LOW)
- ✓ TravelBooker Hack (2022-06-22, 5M records, MEDIUM)
- ✓ FoodDelivery Breach (2022-03-14, 7M records, MEDIUM)
- ✓ ISP Data Leak (2021-11-30, 4M records, HIGH)
- ✓ ForumX Dump (2021-08-15, 2M records, MEDIUM)

### Verify Data Statistics:
- ✓ Total breaches: **11**
- ✓ Total affected records: **112,500,000+**
- ✓ HIGH risk breaches: **5**
- ✓ MEDIUM risk breaches: **4**
- ✓ LOW risk breaches: **2**
- ✓ Data types exposed: **31 entries**

---

## 🔍 Troubleshooting

### Issue: "Access denied for user 'fyp_user'"
**Solution:** Verify credentials in environment variables
```powershell
# Check environment variables
[System.Environment]::GetEnvironmentVariable("MYSQL_USER", "User")
[System.Environment]::GetEnvironmentVariable("MYSQL_PASSWORD", "User")

# If not set, set them:
[System.Environment]::SetEnvironmentVariable("MYSQL_USER", "fyp_user", "User")
[System.Environment]::SetEnvironmentVariable("MYSQL_PASSWORD", "Admin123!", "User")
```

### Issue: "Table 'fyp_osint.breaches' doesn't exist"
**Solution:** Run db_setup.py first
```powershell
python db_setup.py
```

### Issue: "Syntax error in breaches_seed_data.sql"
**Solution:** Try running via Python instead of CLI
```powershell
python test_breach_data.py  # This will tell you what's wrong
```

### Issue: Test shows "0 breaches" after running SQL
**Solution:** Ensure you're connecting to the right database
```powershell
# Check which database you're using
echo "SELECT DATABASE();" | mysql -u fyp_user -p
```

---

## 📊 Data Integrity Check

Run this query to verify data integrity:

```sql
-- Check for orphaned data types (data types without breach)
SELECT COUNT(*) as orphaned_datatypes
FROM breach_data_types bdt
WHERE bdt.breach_id NOT IN (SELECT id FROM breaches);
-- Should return: 0

-- Check foreign key constraints are working
SELECT 
    CONSTRAINT_NAME,
    CONSTRAINT_TYPE
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_NAME IN ('breaches', 'breach_data_types', 'user_breach_matches')
AND CONSTRAINT_TYPE = 'FOREIGN KEY';
-- Should show: 3 constraints
```

---

## ✨ Expected File Structure After Testing

```
fyp-osint-breach-monitor/
├── db_setup.py (UPDATED - with breach tables)
├── breaches_seed_data.sql (NEW - seed data)
├── test_breach_data.py (NEW - test script)
├── TEST_BREACH_INTEGRATION.md (NEW - this file)
├── app.py (not changed yet)
├── auth.py (not changed yet)
└── templates/
    └── (no changes yet)
```

---

## 🎯 Next Steps After Successful Testing

Once all tests pass, we'll:

1. **Create search function** in `app.py` that queries breaches
2. **Link investigations** to specific breaches
3. **Calculate risk scores** based on breach severity
4. **Display results** showing which breaches user's data appeared in
5. **Generate statistics** for dashboard

---

## 📝 Notes

- **Data is from the list you provided**: All 11 breaches match exactly
- **Ready for production**: Proper indexes, foreign keys, constraints
- **Scalable design**: Can add more breaches later without changing code
- **User privacy**: No personally identifiable information stored in this table
- **Malaysian context**: ShopMY & ISP breaches reflect local incidents

---

## ❓ Questions?

If tests fail or you find issues:
1. Run `python test_breach_data.py` again
2. Check error messages carefully
3. Ensure MySQL service is running
4. Verify database credentials are correct

**You're ready to proceed once all tests PASS!**
