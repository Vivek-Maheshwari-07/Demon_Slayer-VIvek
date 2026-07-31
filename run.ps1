# EPISTEME One-Click PowerShell Launcher

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 Launching EPISTEME Backend & Frontend..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Creating template .env file..." -ForegroundColor Yellow
    "OPENROUTER_API_KEY=" | Out-File -Encoding utf8 .env
}

# Launch Python run.py cross-platform process runner
python run.py
