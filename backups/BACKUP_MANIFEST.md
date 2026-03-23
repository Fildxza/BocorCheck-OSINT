# FYP OSINT Breach Monitor - Backup Manifest

**Backup Date:** 2026-03-23 22:53:00  
**Pre-Upgrade Checkpoint:** Before feature/UI upgrade

---

## Files Backed Up

### 1. Database Backup
- **File:** `fyp_osint_backup_20260323_225341.sql`
- **Size:** 14,675 bytes
- **Database:** fyp_osint (all tables)
- **Includes:**
  - investigation_logs
  - breach_results
  - login_logs
- **Restore Command:**
  ```bash
  mysql -u fyp_user -p -h 127.0.0.1 fyp_osint < fyp_osint_backup_20260323_225341.sql
  ```

### 2. Source Code Backup
- **File:** `fyp_code_backup_20260323_225353.zip`
- **Size:** 28,054 bytes
- **Includes:**
  - app.py
  - bot.py
  - requirements.txt
  - templates/ (HTML files)
  - Other config files
- **Excludes:**
  - .venv/ (virtual environment)
  - .git/ (version control)
  - __pycache__/ (compiled files)
  - backups/ (this folder)

---

## Rollback Instructions

### If upgrade fails and you need to rollback:

**1. Restore Database:**
```powershell
mysql -u fyp_user -p -h 127.0.0.1 fyp_osint < backups\fyp_osint_backup_20260323_225341.sql
```

**2. Restore Code:**
```powershell
# Extract the backup ZIP
Expand-Archive -Path backups\fyp_code_backup_20260323_225353.zip -DestinationPath . -Force

# Reinstall dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Restart app
.\start_demo.ps1
```

---

## Next Steps

1. ✅ Backup complete — safe to proceed with upgrade
2. Create development branch (recommend: git branch `dev-ui-upgrade` before testing)
3. Test changes in isolated environment
4. Merge to main after validation

---

**Backup Storage Location:**  
`C:\Users\norha\fyp-osint-breach-monitor\backups\`

**Note:** Keep backups for at least 1-2 weeks, then archive to external drive if needed.
