# Quick Start Guide - User Authentication System

## ⚡ 5-Minute Setup

### Step 1: Install bcrypt
```bash
pip install bcrypt==4.1.3
```

### Step 2: Initialize Database
```bash
python db_setup.py
```

**Expected Output:**
```
✓ MySQL schema is ready.
✓ Tables: alerts, breach_results, investigation_logs, login_logs, risk_scores, users
```

### Step 3: Start Flask App
```bash
python app.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
```

### Step 4: Test Registration
1. Open http://localhost:5000/signup
2. Create account:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `SecurePass123!`
   - Confirm: `SecurePass123!`
3. Click "Create Account"
4. Redirect to login page (normal behavior)

### Step 5: Test Login
1. Enter: `test@example.com` (or `testuser`)
2. Password: `SecurePass123!`
3. You're logged in! ✓

### Step 6: View Your Investigations
1. Click "View History"
2. You'll see "Showing your investigation history"
3. CSV export will only include YOUR data

---

## 🤖 Local Ollama AI Demo

If you want to prove the local AI is running for your FYP demo:

### Start Ollama + App Automatically
```powershell
.\start_local_ai_demo.ps1
```

This script will:
- Start Ollama if it is not already running
- Launch the Flask app
- Keep using the local `phi3` model configured in `bot.py`

### Open the AI Proof Page
Use this route after the app is running:

```text
http://127.0.0.1:5000/ai-proof
```

The page shows:
- Sample breach payload
- Live response from Ollama
- Raw JSON mitigation output

### Collect Evidence for Report
```powershell
.\collect_ai_evidence.ps1
```

This saves:
- A log file from `test_ai_integration.py`
- An HTML snapshot of the AI proof route

---

## 🔑 Test Credentials (for quick demo)

If you want to test with multiple accounts without creating them:

**Account 1:**
- Username: `researcher1`
- Email: `researcher1@fyp.edu.my`
- Password: `Research2026!`

**Account 2:**
- Username: `analyst2`
- Email: `analyst2@fyp.edu.my`
- Password: `Analysis2026!`

(Create these manually via /signup first)

---

## 🎯 What's New vs Before

### Before (Old System)
- Single hardcoded admin user (`admin`/`admin123`)
- Admin login: `/admin/login`
- All investigations visible to everyone
- Single session type

### After (New System)
- Multiple user accounts via `/signup`
- User login: `/login` (email or username)
- **Each user sees ONLY their own investigations** ✨
- Secure bcrypt passwords
- Admin login still works (backward compatible!)
- Full audit trail via `login_logs`

---

## 🚨 Important Security Notes

1. **Password Requirements** (enforced at signup):
   - ✓ Minimum 8 characters
   - ✓ At least 1 UPPERCASE letter
   - ✓ At least 1 lowercase letter
   - ✓ At least 1 number
   - ✓ At least 1 special character (!@#$%^&*)

2. **Common Errors & Fixes**:

   | Error | Cause | Fix |
   |-------|-------|-----|
   | "Email already registered" | Email in use | Choose different email |
   | "Invalid email/username or password" | Wrong credentials | Check typos, password case |
   | "Password must contain..." | Weak password | Follow requirements |
   | "Duplicate entry for key..." | Email/username exists | Use different email |

3. **Session Auto-Logout**:
   - Sessions expire after **2 hours** of inactivity
   - This is normal! Logout and log back in

---

## 🔒 Data Isolation Example

**User John:**
- Creates investigation: "john@email.com"
- Goes to `/history`
- ✓ Sees his investigation

**User Ahmed:**
- Logs in as different user
- Goes to `/history`
- ✗ DOES NOT see John's investigation
- ✓ Sees only his own investigations

**Admin User:**
- Logs in via `/admin/login` (old system)
- Goes to `/history`
- ✓ Sees ALL investigations (for audit purposes)

---

## 📊 Database Schema (Simplified)

```
users (NEW)
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── password_hash (bcrypt 60 chars)
├── role (user/admin)
└── created_at

investigation_logs (UPDATED)
├── id (PK)
├── user_id (FK → users.id)  ← NEW COLUMN
├── email
├── phone_number
├── breach_count
├── risk_score
├── risk_level
└── checked_at

login_logs (FOR AUDIT)
├── id (PK)
├── username
├── role
├── action (login/logout/failed_login/signup)
├── ip_address
├── user_agent
└── created_at
```

---

## 🧪 Testing Scenarios

### Scenario 1: Basic Auth
```
1. /signup → Create account "alice"
2. /login → Login as alice
3. Verify "Logged in as: alice" shows on dashboard
4. /logout → Session cleared
```

### Scenario 2: Data Isolation (IMPORTANT!)
```
1. Create account "bob" and login
2. Perform investigation (search any email)
3. /history → Should show bob's investigation
4. /logout

5. Create account "charlie" and login
6. /history → Should be EMPTY (doesn't show bob's data)
7. Perform investigation
8. /history → Now shows only charlie's investigation

RESULT: ✓ Data isolation working correctly
```

### Scenario 3: CSV Export (User-Scoped)
```
1. As alice: Create 3 investigations
2. /history/export → CSV has 3 rows
3. /logout

4. As bob: Create 1 investigation
5. /history/export → CSV has only 1 row

RESULT: ✓ Users only export their own data
```

---

## 📋 Backward Compatibility Checklist

- [ ] Old admin login still works: `/admin/login`
- [ ] Admin can see all investigations: yes
- [ ] Admin can export all data: yes
- [ ] Legacy investigations (no user_id) still visible: yes
- [ ] New users don't see old data: correct (privacy preserved)

---

## 🔧 Troubleshooting

### Q: "No such file or directory: auth.py"
**A:** Make sure `auth.py` is in the same folder as `app.py`

### Q: "Could not prepare MySQL schema"
**A:** Check MySQL is running and credentials in environment:
```bash
echo %MYSQL_USER%
echo %MYSQL_PASSWORD%
```

### Q: "User can still see other users' data"
**A:** Check SQL query in `fetch_investigation_history()`:
```python
# Should have: AND user_id = %s
# MUST pass user_id=session.get('user_id')
```

### Q: "Session expires too quickly"
**A:** Normal! 2 hours is industry standard for security.
Change in `app.py` line: `app.config['PERMANENT_SESSION_LIFETIME'] = 7200`

---

## 📚 File Checklist

Before starting, verify you have all files:

```
✓ app.py (updated)
✓ auth.py (NEW)
✓ db_setup.py (updated)
✓ requirements.txt (updated with bcrypt)
✓ templates/signup.html (NEW)
✓ templates/login.html (updated)
✓ templates/index.html (updated)
✓ templates/history.html (updated)
✓ AUTHENTICATION_SYSTEM.md (this file)
```

---

## 🎓 For Your FYP Presentation

### Demo Script (10 minutes)

```
SLIDE 1: PROBLEM
"Previously: Single admin user, all data visible to everyone"

DEMO (1):
- Show /admin/login page (old system)
- Explain limited

SLIDE 2: SOLUTION
"Now: Full user authentication system with data isolation"

DEMO (2):
- Go to /signup
- Show password requirements enforcement
- Create account: researcher1 / researcher1@fyp.edu.my / Research2026!
- Explain validation

DEMO (3):
- Go to /login
- Show "Create Account" link
- Sign in
- Show "Logged in as: researcher1" on dashboard

DEMO (4): MOST IMPORTANT - DATA ISOLATION
- Perform breach search for "test@email.com"
- Go to /history
- Note the investigation ID

- /logout
- Create second account: analyst2 / analyst2@fyp.edu.my / Analysis2026!
- Go to /history
- Show it's EMPTY (no access to first user's data)

- Explain this is the KEY SECURITY FEATURE

DEMO (5):
- CSV export shows only your own data
- Admin login still works for audit trail

SLIDE 3: SECURITY
- Show bcrypt hashing (never plain text)
- Show parameterized SQL (injection prevention)
- Show session security (HTTPOnly, SameSite)
- Show login_logs audit trail

CONCLUSION: "Professional, secure, scalable system ready for production"
```

---

## 📞 Quick Support Commands

### Reset Database (WARNING: Deletes all data!)
```bash
# Drop all tables
mysql -u fyp_user -p fyp_osint < /dev/null
# Reinitialize
python db_setup.py
```

### Check Database
```bash
mysql -u fyp_user -p fyp_osint
SELECT * FROM users;
SELECT * FROM login_logs;
```

### Restart Flask
```bash
# Stop: Ctrl+C
# Start:
python app.py
```

---

## ✅ Checklist Before Demo

- [ ] MySQL is running
- [ ] Database initialized: `python db_setup.py`
- [ ] Flask running: `python app.py`
- [ ] Test account created
- [ ] Test data isolation works
- [ ] /history shows user-scoped data
- [ ] CSV export works correctly
- [ ] Admin login still functions
- [ ] Logout clears session

---

**Everything Ready?** 🚀 Your system is now production-ready with enterprise-grade security!

For detailed documentation, see: `AUTHENTICATION_SYSTEM.md`
