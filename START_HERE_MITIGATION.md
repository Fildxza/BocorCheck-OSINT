# 🛡️ MITIGATION PLANS - START HERE

## What's Included?

**Complete mitigation system for BocorCheck:**
- 25+ smart mitigation actions (password reset, 2FA, monitoring, etc.)
- Smart priority system (do CRITICAL first, then IMPORTANT)
- 20+ Malaysian government & bank resources with phone numbers
- Step-by-step guides for each action
- Risk-based recommendations (HIGH/MEDIUM/LOW)

---

## ⚡ Quick 3-Step Setup

### Step 1️⃣: Create Mitigation Tables
Run db_setup.py (if not already done):

```powershell
python db_setup.py
```

**Verify output includes:**
```
✓ Tables: ... mitigation_plans, mitigation_resources ...
```

---

### Step 2️⃣: Insert Mitigation Data

**Via MySQL** (pick one method):

**Method A - CLI (Recommended):**
```bash
mysql -h 127.0.0.1 -u fyp_user -p fyp_osint < mitigation_seed_data.sql
mysql -h 127.0.0.1 -u fyp_user -p fyp_osint < mitigation_resources_malaysia.sql
# Password: Admin123!
```

**Method B - Python:**
```powershell
python -c "
import mysql.connector as mc
cfg = {'host':'127.0.0.1','user':'fyp_user','password':'Admin123!','database':'fyp_osint'}
with mc.connect(**cfg) as conn:
    with conn.cursor() as cur:
        for file in ['mitigation_seed_data.sql', 'mitigation_resources_malaysia.sql']:
            with open(file) as f:
                for stmt in f.read().split(';'):
                    if stmt.strip(): cur.execute(stmt)
        conn.commit()
print('✓ Inserted!')
"
```

---

### Step 3️⃣: Verify Everything

```powershell
python test_mitigation_data.py
```

**Expected Output:**
```
✓ PASS: Mitigation tables exist
✓ PASS: Mitigation plans data (25+ actions)
✓ PASS: Malaysian resources (20+ contacts)
✓ PASS: Breach-mitigation linkage
✓ PASS: JSON data integrity
✓ PASS: Mitigation module

✓ ALL TESTS PASSED!
```

---

## 📊 What Gets Inserted

### Mitigation Actions (25+)

| Level | Count | Examples |
|-------|-------|----------|
| 🔴 CRITICAL | 8 | Change password, Enable 2FA, Report to PDRM, Check credit |
| 🟠 IMPORTANT | 10 | Monitor fraud, Notify banks, File reports, Secure recovery |
| 🟡 RECOMMENDED | 7 | Monitor phishing, Monitor accounts, Data removal |

### Malaysian Resources (20+)

#### Government Agencies:
- ✓ MICC (Cybercrime) - www.micc.gov.my
- ✓ PDRM Cybercrime - +603-2100-5250 (24/7)
- ✓ JPN (IC Issues) - 1-300-888-811
- ✓ Bank Negara - 1-300-88-5465 (24/7)
- ✓ e-Aduan Portal - www.eaduan.gov.my

#### Malaysian Banks (24/7 Hotlines):
- Maybank: 1-300-888-627
- CIMB: 1-300-300-300
- Public Bank: +603-2171-2222
- AmBank: +603-4050-1188
- Bank Islam: +603-2786-3636

#### Financial Services:
- MyDebtFreee (Credit Check)
- CCRIS (Credit Records)
- PIDM (Deposit Insurance)

#### Telecom (SIM Protection):
- Telekom Malaysia, Maxis, DiGi

---

## 🎯 Example: What User Sees

### When someone's email is in a breach:

```
Your email was found in 3 breaches

🔴 CRITICAL ACTIONS (Do Now - 15 minutes):

1. Change Your Password [5 mins]
   Steps:
   • Go to account settings
   • Click "Change Password"
   • Create 16+ character password
   • Save in password manager

2. Enable Two-Factor Authentication [10 mins]
   Steps:
   • Download Google Authenticator
   • Scan QR code
   • Save backup codes
   
3. Monitor for Identity Theft [Malaysia] [0 mins]
   Resources:
   ✓ MyDebtFreee.com.my - Check credit report
   ✓ PDRM: +603-2100-5250 - Report cyber crime
   ✓ JPN.gov.my - Verify MyKad status

⚠️ WARNINGS FOR YOUR DATA:
   • Password hash compromised - CHANGE NOW
   • Full name exposed - Monitor credit
   • IC Number exposed - Report to authorities

🟠 DO WITHIN 24 HOURS:
   • Call your bank (24/7 number provided)
   • Enable transaction alerts
   • Check recent login activity

🎯 MALAYSIAN HELP:
   Emergency: 999 (Police)
   Cybercrime: MICC www.micc.gov.my (24/7)
   Bank Helpline: [Your bank 24/7]
   Credit Check: MyDebtFreee.com.my
```

---

## 📁 Files Added

| File | Purpose |
|------|---------|
| `db_setup.py` | **UPDATED** - New mitigation tables |
| `mitigation_seed_data.sql` | **NEW** - 25+ mitigation plans |
| `mitigation_resources_malaysia.sql` | **NEW** - Malaysian contacts |
| `mitigation.py` | **NEW** - Python module for logic |
| `test_mitigation_data.py` | **NEW** - Verification script |

---

## ✅ Your Checklist

- [ ] Step 1: `python db_setup.py` ✓
- [ ] Step 2a: Insert SQL files ✓
- [ ] OR Step 2b: Run Python insert ✓
- [ ] Step 3: `python test_mitigation_data.py` ✓
- [ ] All 6 tests show ✓ PASS ✓

---

## 🚀 Status

**Ready to test!** 

Once tests pass:
- Integrate into search results
- Add to investigation details
- Show in recommendations widget
- Provide actionable guidance to users

---

## 📞 Contact Reference

```
EMERGENCY:             999 (Police)
Cybercrime Report:     www.micc.gov.my or +603-8000-8000
Bank Fraud (24/7):     Maybank 1-300-888-627 (or your bank)
Credit Check:          www.mydebtfreee.com.my
IC/MyKad Issues:       JPN 1-300-888-811
Government Complaint:  www.eaduan.gov.my
```

---

**Ready to run setup? Let me know results!** 🎯
