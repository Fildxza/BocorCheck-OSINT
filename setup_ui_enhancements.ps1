#!/usr/bin/env pwsh
# BocorCheck UI Enhancement - Quick Setup Script
# Run this script to automatically set up the decoy bank breaches table

param(
    [string]$MySQLUser = "fyp_user",
    [string]$MySQLPassword = "Admin123!",
    [string]$MySQLHost = "127.0.0.1",
    [string]$Database = "fyp_osint",
    [string]$Port = "3306"
)

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     BocorCheck UI Enhancement - Automated Setup Script         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if MySQL is available
Write-Host "[1/4] Checking MySQL availability..." -ForegroundColor Yellow
try {
    $mysqlCmd = "mysql"
    & $mysqlCmd --version | Out-Null
    Write-Host "✅ MySQL found" -ForegroundColor Green
} catch {
    Write-Host "❌ MySQL not found in PATH" -ForegroundColor Red
    Write-Host "   Please install MySQL or add it to your PATH environment variable" -ForegroundColor Gray
    exit 1
}

# Test database connection
Write-Host "[2/4] Testing database connection..." -ForegroundColor Yellow
try {
    $connectionTest = & mysql -h $MySQLHost -u $MySQLUser -p"$MySQLPassword" -e "SELECT 1;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database connection successful" -ForegroundColor Green
    } else {
        Write-Host "❌ Database connection failed" -ForegroundColor Red
        Write-Host "   User: $MySQLUser" -ForegroundColor Gray
        Write-Host "   Host: $MySQLHost" -ForegroundColor Gray
        Write-Host "   Database: $Database" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "❌ Error connecting to database: $_" -ForegroundColor Red
    exit 1
}

# Execute SQL script
Write-Host "[3/4] Creating decoy_bank_breaches table..." -ForegroundColor Yellow
try {
    $sqlFile = Join-Path $PSScriptRoot "decoy_bank_breaches.sql"
    if (-not (Test-Path $sqlFile)) {
        Write-Host "❌ SQL file not found at: $sqlFile" -ForegroundColor Red
        exit 1
    }
    
    & mysql -h $MySQLHost -u $MySQLUser -p"$MySQLPassword" $Database < $sqlFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SQL script executed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  SQL script execution had issues" -ForegroundColor Yellow
        Write-Host "   Please manually run: mysql -u $MySQLUser -p -h $MySQLHost $Database < $sqlFile" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error executing SQL script: $_" -ForegroundColor Red
    exit 1
}

# Verify table creation
Write-Host "[4/4] Verifying table creation..." -ForegroundColor Yellow
try {
    $verifyQuery = @"
SELECT COUNT(*) as total_records FROM decoy_bank_breaches WHERE is_active = TRUE;
SELECT severity_level, COUNT(*) as count FROM decoy_bank_breaches GROUP BY severity_level;
"@
    
    $verifyQuery | & mysql -h $MySQLHost -u $MySQLUser -p"$MySQLPassword" $Database
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Table verification successful" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Could not verify table (it may still have been created)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Verification check failed: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    Setup Complete! ✅                          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Start the Flask application:"
Write-Host "      .\.venv\Scripts\Activate.ps1"
Write-Host "      python app.py" -ForegroundColor White
Write-Host ""
Write-Host "   2. Test the new features:"
Write-Host "      • Login page:  http://localhost:5000/login"
Write-Host "      • Dashboard:   http://localhost:5000/" -ForegroundColor White
Write-Host "      • API:         http://localhost:5000/decoy-breaches" -ForegroundColor White
Write-Host ""
Write-Host "   3. Review the documentation:"
Write-Host "      • Integration Guide: UI_ENHANCEMENT_INTEGRATION_GUIDE.md"
Write-Host "      • Code Changes:      CODE_CHANGES_SUMMARY.md" -ForegroundColor White
Write-Host ""

Write-Host "📊 Database Information:" -ForegroundColor Cyan
Write-Host "   Table: decoy_bank_breaches" -ForegroundColor White
Write-Host "   Records: 15 fictional banking breaches" -ForegroundColor White
Write-Host "   Severity: 3 High, 7 Medium, 5 Low" -ForegroundColor White
Write-Host ""

Write-Host "🔒 Security Note:" -ForegroundColor Yellow
Write-Host "   All decoy data is 100% fictional for academic demonstration only." -ForegroundColor Gray
Write-Host ""

Write-Host "If you encounter any issues, see: UI_ENHANCEMENT_INTEGRATION_GUIDE.md" -ForegroundColor Magenta
