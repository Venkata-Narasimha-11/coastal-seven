# Helper script to start the local PostgreSQL daemon for CLI Task Manager
$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$DATA_DIR = Join-Path $SCRIPT_DIR "..\pgdata"
$PG_BIN = "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe"

if (-not (Test-Path $DATA_DIR)) {
    Write-Host "Initializing local PostgreSQL cluster at $DATA_DIR..." -ForegroundColor Cyan
    & "C:\Program Files\PostgreSQL\17\bin\initdb.exe" -D $DATA_DIR -U postgres -A trust
}

Write-Host "Starting PostgreSQL on port 5433..." -ForegroundColor Green
& $PG_BIN -D $DATA_DIR -o "-p 5433" -l (Join-Path $SCRIPT_DIR "logs\pg_ctl.log") start
