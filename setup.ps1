# Skylark Intelligence Engine - Hero Setup Script
# Usage: .\setup.ps1

$ErrorActionPreference = 'Stop'

Write-Host '--------------------------------------------------' -ForegroundColor Cyan
Write-Host '   SKYLARK INTELLIGENCE ENGINE: INSTALL & BOOT' -ForegroundColor Cyan
Write-Host '--------------------------------------------------' -ForegroundColor Cyan

# 1. Environment Initialization
if (-not (Test-Path '.env')) {
    Write-Host '[*] Initializing environment from template...' -ForegroundColor Yellow
    Copy-Item '.env.example' '.env'
    Write-Host '[!] Created .env. PLEASE ADD YOUR GROQ_API_KEY BEFORE CONTINUING.' -ForegroundColor Red
    return
}

# 2. Database Infrastructure
Write-Host '[*] Orchestrating Database Container...' -ForegroundColor Cyan
docker compose up -d db

# 3. Backend Provisioning
Write-Host '[*] Setting up Backend Virtual Environment...' -ForegroundColor Cyan
Set-Location backend
if (-not (Test-Path 'venv')) {
    python -m venv venv
}
& .\venv\Scripts\pip install -r requirements.txt
Set-Location ..

# 4. Frontend Provisioning
Write-Host '[*] Installing Frontend Dependencies (NPM)...' -ForegroundColor Cyan
Set-Location frontend
if (-not (Test-Path 'node_modules')) {
    npm install
}
Set-Location ..

# 5. Forensic Seeding
Write-Host '[*] Generating Initial Forensic Scenarios...' -ForegroundColor Cyan
& .\backend\venv\Scripts\python backend/scratch/refresh_data.py

# 6. Parallel Execution
Write-Host ''
Write-Host '🚀 ALL SYSTEMS READY' -ForegroundColor Green
Write-Host '--------------------------------------------------'
Write-Host 'Starting Maya API and Dashboard in parallel windows...' -ForegroundColor White
Write-Host ''

# Launch Backend in a separate window
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd backend; venv\Scripts\activate; uvicorn app.main:app --reload'

# Launch Frontend in a separate window
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd frontend; npm run dev'

Write-Host 'Investigation Terminals are now active.' -ForegroundColor Green
Write-Host 'UI: http://localhost:3000' -ForegroundColor Cyan
Write-Host '--------------------------------------------------'
Write-Host '[*] Setup complete. Your forensic environment is fully synchronized.'
