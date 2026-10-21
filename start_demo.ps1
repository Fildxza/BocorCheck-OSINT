$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Python venv not found at .venv\\Scripts\\python.exe"
    Write-Host "Create it first with: py -3.11 -m venv .venv"
    exit 1
}

# Local runtime settings
$env:USE_MOCK_DATA = "true"
$env:ENABLE_DB_LOGGING = "true"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "fyp_user"
$env:MYSQL_PASSWORD = "Admin123!"
$env:MYSQL_DATABASE = "fyp_osint"
$env:FLASK_SECRET_KEY = "local-dev-secret"
$env:PHONE_DEFAULT_REGION = "MY"
# Set TELEGRAM_CHAT_ID (and TELEGRAM_BOT_TOKEN) in your .env or environment before running.
$env:ADMIN_USERNAME = "admin"
$env:ADMIN_PASSWORD = "admin123"

Write-Host "Preparing database schema..."
& $py db_setup.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Database setup failed. Check MySQL connection settings and try again."
    exit 1
}

Write-Host "Starting app at http://127.0.0.1:5000"
& $py app.py

python -c "
import mysql.connector
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='fyp_user',
    password='Admin123!',
    database='fyp_osint'
)
cursor = conn.cursor()
with open('DATABASE_UPDATES_3FEATURES.sql') as f:
    for statement in f.read().split(';'):
        if statement.strip():
            cursor.execute(statement)
conn.commit()
print('Database updated successfully!')
"
