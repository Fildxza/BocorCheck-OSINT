@echo off
REM BocorCheck UI Enhancement - Quick Setup Script (Batch Version)
REM Run this script to automatically set up the decoy bank breaches table

setlocal enabledelayedexpansion

set MYSQL_USER=fyp_user
set MYSQL_PASSWORD=Admin123!
set MYSQL_HOST=127.0.0.1
set MYSQL_PORT=3306
set DATABASE=fyp_osint

echo.
echo ════════════════════════════════════════════════════════════════
echo      BocorCheck UI Enhancement - Automated Setup Script
echo ════════════════════════════════════════════════════════════════
echo.

REM Check if MySQL is available
echo [1/4] Checking MySQL availability...
where mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] MySQL not found in PATH
    echo Please install MySQL or add it to your PATH environment variable
    pause
    exit /b 1
)
echo [OK] MySQL found
echo.

REM Test database connection
echo [2/4] Testing database connection...
mysql -h %MYSQL_HOST% -u %MYSQL_USER% -p%MYSQL_PASSWORD% -e "SELECT 1;" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Database connection failed
    echo User: %MYSQL_USER%
    echo Host: %MYSQL_HOST%
    echo Database: %DATABASE%
    pause
    exit /b 1
)
echo [OK] Database connection successful
echo.

REM Execute SQL script
echo [3/4] Creating decoy_bank_breaches table...
if not exist "decoy_bank_breaches.sql" (
    echo [ERROR] SQL file not found: decoy_bank_breaches.sql
    pause
    exit /b 1
)

mysql -h %MYSQL_HOST% -u %MYSQL_USER% -p%MYSQL_PASSWORD% %DATABASE% < decoy_bank_breaches.sql
if %errorlevel% neq 0 (
    echo [WARNING] SQL script execution had issues
    echo Please manually run: mysql -u %MYSQL_USER% -p -h %MYSQL_HOST% %DATABASE% ^< decoy_bank_breaches.sql
) else (
    echo [OK] SQL script executed successfully
)
echo.

REM Verify table creation
echo [4/4] Verifying table creation...
mysql -h %MYSQL_HOST% -u %MYSQL_USER% -p%MYSQL_PASSWORD% %DATABASE% -e "SELECT COUNT(*) as total_records FROM decoy_bank_breaches WHERE is_active = TRUE;"
if %errorlevel% neq 0 (
    echo [WARNING] Could not verify table (it may still have been created)
) else (
    echo [OK] Table verification successful
)
echo.

echo ════════════════════════════════════════════════════════════════
echo                     Setup Complete!
echo ════════════════════════════════════════════════════════════════
echo.

echo Next Steps:
echo.
echo 1. Start the Flask application:
echo    .\.venv\Scripts\activate.bat
echo    python app.py
echo.
echo 2. Test the new features:
echo    * Login page:  http://localhost:5000/login
echo    * Dashboard:   http://localhost:5000/
echo    * API:         http://localhost:5000/decoy-breaches
echo.
echo 3. Review the documentation:
echo    * Integration Guide: UI_ENHANCEMENT_INTEGRATION_GUIDE.md
echo    * Code Changes:      CODE_CHANGES_SUMMARY.md
echo.

echo Database Information:
echo    Table: decoy_bank_breaches
echo    Records: 15 fictional banking breaches
echo    Severity: 3 High, 7 Medium, 5 Low
echo.

echo SECURITY NOTE:
echo    All decoy data is 100%% fictional for academic demonstration only.
echo.

pause
