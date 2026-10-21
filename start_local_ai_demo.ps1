$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host 'Python venv not found at .venv\Scripts\python.exe'
    Write-Host 'Create it first with: py -3.11 -m venv .venv'
    exit 1
}

function Test-OllamaEndpoint {
    try {
        Invoke-WebRequest -Uri 'http://127.0.0.1:11434' -TimeoutSec 3 -UseBasicParsing | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

$ollamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCommand) {
    Write-Host 'Ollama command not found on PATH. Install Ollama first.'
    exit 1
}

if (-not (Test-OllamaEndpoint)) {
    Write-Host 'Starting Ollama server...'
    Start-Process -FilePath $ollamaCommand.Source -ArgumentList 'serve' -WindowStyle Hidden

    $ollamaReady = $false
    foreach ($attempt in 1..30) {
        if (Test-OllamaEndpoint) {
            $ollamaReady = $true
            break
        }
        [System.Threading.Thread]::Sleep(1000)
    }

    if (-not $ollamaReady) {
        Write-Host 'Ollama server did not become ready on http://127.0.0.1:11434'
        exit 1
    }
}
else {
    Write-Host 'Ollama server is already running.'
}

$env:USE_MOCK_DATA = 'true'
$env:ENABLE_DB_LOGGING = 'true'
$env:MYSQL_HOST = '127.0.0.1'
$env:MYSQL_PORT = '3306'
$env:MYSQL_USER = 'fyp_user'
$env:MYSQL_PASSWORD = 'Admin123!'
$env:MYSQL_DATABASE = 'fyp_osint'
$env:FLASK_SECRET_KEY = 'local-dev-secret'
$env:PHONE_DEFAULT_REGION = 'MY'
# Set TELEGRAM_CHAT_ID (and TELEGRAM_BOT_TOKEN) in your .env or environment before running.
$env:ADMIN_USERNAME = 'admin'
$env:ADMIN_PASSWORD = 'admin123'

Write-Host 'Launching Flask app at http://127.0.0.1:5000'
& $python app.py
