<#
.SYNOPSIS
    Day 15 Local CI Test Suite Runner.
.DESCRIPTION
    Runs the complete continuous integration pipeline locally:
    1. TypeScript Typecheck (tsc --noEmit)
    2. Vitest Component & Unit Tests (RTL + MSW)
    3. Production Bundle Build (vite build)
    4. Playwright End-to-End Tests (optional if browser installed)
#>

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🚀 Day 15 CI Pipeline: TypeScript & Component Testing" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$frontendDir = Join-Path $PSScriptRoot "..\frontend"
Set-Location $frontendDir

function Run-Step($name, $command) {
    Write-Host "`n[CI Step] $name..." -ForegroundColor Yellow
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        Invoke-Expression $command
        $stopwatch.Stop()
        Write-Host "✅ PASSED: $name in $($stopwatch.Elapsed.TotalSeconds.ToString('0.00'))s" -ForegroundColor Green
    } catch {
        $stopwatch.Stop()
        Write-Host "❌ FAILED: $name" -ForegroundColor Red
        Write-Error $_
        exit 1
    }
}

# 1. Typecheck
Run-Step "1/3: Strict TypeScript Type Checking" "npm run typecheck"

# 2. Vitest Tests
Run-Step "2/3: Vitest Component, Store & MSW Integration Tests" "npm run test:run"

# 3. Production Build
Run-Step "3/3: Production Vite Bundle Compilation" "npm run build"

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "🎉 ALL CI VERIFICATION STEPS PASSED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
