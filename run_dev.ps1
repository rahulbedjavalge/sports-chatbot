#!/usr/bin/env pwsh
# Dev helper: creates venv, installs deps, seeds DB, starts backend and serves frontend
param()

Set-Location -Path (Split-Path -Path $MyInvocation.MyCommand.Definition -Parent)

if (-not (Test-Path .\venv)) {
    python -m venv venv
}

Write-Output "Activating venv and installing requirements..."
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Output "Seeding DB..."
python backend\setup_db.py

Write-Output "Starting backend in new window..."
Start-Process powershell -ArgumentList "-NoExit","-Command",".\venv\\Scripts\\Activate.ps1; python backend\app.py"

Start-Sleep -Seconds 1
Write-Output "Serving frontend on http://127.0.0.1:8000 in new window..."
Start-Process powershell -ArgumentList "-NoExit","-Command","python -m http.server 8000 -d frontend"

Start-Sleep -Seconds 1
Write-Output "Opening browser to frontend..."
Start-Process "http://127.0.0.1:8000/index.html"

Write-Output "Done. Check the two new windows for backend and frontend logs."
