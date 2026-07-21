$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host 'Python venv not found at .venv\Scripts\python.exe'
    exit 1
}

$artifactsDir = Join-Path $PSScriptRoot 'artifacts'
New-Item -ItemType Directory -Force -Path $artifactsDir | Out-Null

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$logFile = Join-Path $artifactsDir "ai_integration_$stamp.log"
$htmlFile = Join-Path $artifactsDir "ai_proof_$stamp.html"

Write-Host 'Running Ollama integration test and saving log...'
& $python test_ai_integration.py | Tee-Object -FilePath $logFile

function Test-AppEndpoint {
    try {
        Invoke-WebRequest -Uri 'http://127.0.0.1:5000/ai-proof' 
    }
    catch {
        return $false
    }
}

if (-not (Test-AppEndpoint)) {
    Write-Host 'Flask app is not reachable at http://127.0.0.1:5000/ai-proof'
    Write-Host 'Start the app first with: .\start_local_ai_demo.ps1'
    exit 1
}

Write-Host 'Saving AI proof HTML...'
Invoke-WebRequest -Uri 'http://127.0.0.1:5000/ai-proof' -OutFile $htmlFile

Write-Host ''
Write-Host 'Evidence files created:'
Write-Host "  Log:  $logFile"
Write-Host "  HTML: $htmlFile"
