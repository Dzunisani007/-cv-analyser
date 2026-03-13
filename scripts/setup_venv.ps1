Param(
  [string]$PythonExe = "python",
  [switch]$Install = $true
)

$ErrorActionPreference = "Stop"

Write-Host "== CV Analyser Service: setup venv ==" -ForegroundColor Cyan

# Ensure we're running from service/ (script location)
$ServiceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ServiceDir

if (-not (Get-Command $PythonExe -ErrorAction SilentlyContinue)) {
  throw "Python executable '$PythonExe' not found. Install Python 3.11+ and ensure it's on PATH."
}

& $PythonExe --version

if (-not (Test-Path ".venv")) {
  Write-Host "Creating .venv..." -ForegroundColor Yellow
  & $PythonExe -m venv .venv
}

Write-Host "Activating .venv..." -ForegroundColor Yellow
. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

if ($Install) {
  Write-Host "Installing requirements.txt..." -ForegroundColor Yellow
  pip install -r requirements.txt
}

Write-Host "Done. Virtual environment is ready." -ForegroundColor Green
Write-Host "Next:" -ForegroundColor Green
Write-Host "  .\\scripts\\run_local.ps1" -ForegroundColor Green
Write-Host "  python -m pytest -q" -ForegroundColor Green
