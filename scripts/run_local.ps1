Param(
  [switch]$WithDocker = $false
)

$ErrorActionPreference = "Stop"

Write-Host "== CV Analyser Service: run local ==" -ForegroundColor Cyan

$ServiceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ServiceDir

if (-not (Test-Path ".env")) {
  if (Test-Path ".env.example") {
    Copy-Item .env.example .env -Force
    Write-Host "Created .env from .env.example (please review/edit as needed)." -ForegroundColor Yellow
  } else {
    Write-Host "No .env or .env.example found. Continuing without env file." -ForegroundColor Yellow
  }
}

# Load .env into current PowerShell session
if (Test-Path ".env") {
  Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
    $name, $value = $_ -split '=', 2
    $env:$name = $value
  }
}

if ($WithDocker) {
  Write-Host "Starting docker-compose..." -ForegroundColor Yellow
  docker-compose up --build
  exit 0
}

if (-not (Test-Path ".venv")) {
  Write-Host "No .venv found. Run .\\scripts\\setup_venv.ps1 first." -ForegroundColor Red
  exit 1
}

Write-Host "Activating .venv..." -ForegroundColor Yellow
. .\.venv\Scripts\Activate.ps1

$host = $env:SERVICE_HOST
if (-not $host) { $host = "0.0.0.0" }
$port = $env:SERVICE_PORT
if (-not $port) { $port = "8000" }

Write-Host "Starting uvicorn on $host:$port ..." -ForegroundColor Green
uvicorn app.main:app --reload --host $host --port $port
