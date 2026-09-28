# Helper script to stop the local PostgreSQL daemon for CLI Task Manager
$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$DATA_DIR = Join-Path $SCRIPT_DIR "..\pgdata"
$PG_BIN = "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe"

Write-Host "Stopping PostgreSQL on port 5433..." -ForegroundColor Yellow
& $PG_BIN -D $DATA_DIR stop -m fast
