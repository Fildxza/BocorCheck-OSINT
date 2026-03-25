# 🔐 Admin Login Fix - Quick Setup

## Problem
Login failed with "Invalid email/username or password" when trying to use admin/admin.

## Root Cause
Admin user tidak ada dalam `users` table. System baru pakai auth.py dengan bcrypt hashing, bukan env variables.

---

## ✅ Solution (2 Steps)

### Step 1️⃣: Create Admin User

```powershell
python setup_admin.py
```

**Expected Output:**
```
✓ Admin user created successfully!

DEFAULT LOGIN CREDENTIALS:
==================================================
Username: admin
Password: Admin123!
Email: admin@bocorcheck.local
==================================================

⚠️  IMPORTANT SECURITY NOTES:
  1. Change the default password immediately after first login
  2. Use strong password (16+ chars, mix of upper/lower/numbers/special)
  3. Do NOT share admin credentials
  4. Admin account has access to all user data
```

---

### Step 2️⃣: Try Login Again

Go to: `http://localhost:5000/login`

**Use credentials:**
- **Username/Email:** `admin`
- **Password:** `Admin123!`

---

## 🔄 Change Admin Password (After First Login)

```powershell
python update_admin_password.py
```

**Steps:**
1. Enter current password: `Admin123!`
2. Enter new password (16+ chars recommended)
3. Confirm new password
4. ✓ Password updated

---

## 📊 Useful MySQL Queries

**All queries di:** `MYSQL_USEFUL_QUERIES.sql`

### Quick Checks:

**Check if admin user exists:**
```sql
SELECT * FROM users WHERE role = 'admin';
```

**List all users:**
```sql
SELECT id, username, email, role, created_at FROM users;
```

**Count investigations per user:**
```sql
SELECT u.username, COUNT(il.id) as investigations
FROM users u
LEFT JOIN investigation_logs il ON u.id = il.user_id
GROUP BY u.id;
```

**View login history:**
```sql
SELECT username, action, ip_address, created_at 
FROM login_logs 
ORDER BY created_at DESC LIMIT 20;
```

**Get HIGH risk investigations:**
```sql
SELECT email, breach_count, risk_score, risk_level, checked_at
FROM investigation_logs
WHERE risk_level = 'HIGH'
ORDER BY checked_at DESC;
```

---

## 📁 Files Added

| File | Purpose |
|------|---------|
| `setup_admin.py` | Create admin user in database |
| `update_admin_password.py` | Change admin password safely |
| `MYSQL_USEFUL_QUERIES.sql` | 30+ useful MySQL queries |

---

## 🎯 Admin Features

Once logged in, admin can:
- ✅ View ALL user investigations
- ✅ Access complete investigation history (not scoped)
- ✅ See user statistics  
- ✅ Access audit logs
- ✅ Manage system settings

---

## ⚠️ Security Reminders

1. **Change default password ASAP**
2. **Use strong passwords** (min 16 chars, uppercase + lowercase + numbers + special)
3. **Don't share admin credentials**
4. **Keep password file secure** (use password manager)
5. **Monitor login attempts** - check `login_logs` table regularly

---

## 🆘 Troubleshooting

### If setup_admin.py says "Admin user already exists"
Use `update_admin_password.py` to change password

### If you forget admin password
**Via MySQL directly:**
```powershell
# Login to MySQL and run:
# DELETE FROM users WHERE username = 'admin';
# Then run: python setup_admin.py
```

### If still can't login
1. Verify admin user exists:
   ```sql
   SELECT * FROM users WHERE username = 'admin';
   ```

2. Check password hash format (should be bcrypt starting with `$2b$`):
   ```sql
   SELECT username, password_hash FROM users WHERE username = 'admin';
   ```

3. Verify `auth.py` module loads:
   ```powershell
   python -c "from auth import login_user; print('✓ auth module OK')"
   ```

---

## 🚀 Next Steps

1. ✅ Run `python setup_admin.py`
2. ✅ Try login with admin/Admin123!
3. ✅ Change password with `python update_admin_password.py`
4. ✅ Explore MYSQL_USEFUL_QUERIES.sql for management

**Admin login should work now!** 🎉
