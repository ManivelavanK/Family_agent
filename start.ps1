# KinNest — Clean Start Script
# Usage: Right-click -> "Run with PowerShell"  OR  run: .\start.ps1

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   KinNest Family OS — Starting Up" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill any processes holding ports 8000-8006
Write-Host "[1/3] Clearing ports 8000-8006..." -ForegroundColor Yellow
$ports = 8000,8001,8002,8003,8004,8005,8006
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conn) {
        $pids = $conn | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($pid in $pids) {
            if ($pid -ne 0) {
                taskkill /F /PID $pid 2>$null | Out-Null
                Write-Host "   Freed port $port (PID $pid)" -ForegroundColor DarkGray
            }
        }
    }
}
Write-Host "   Ports cleared." -ForegroundColor Green
Start-Sleep -Seconds 1

# Step 2: Start the Orchestrator (Backend) in a new window
Write-Host ""
Write-Host "[2/3] Starting Backend Orchestrator on port 8000..." -ForegroundColor Yellow
$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python orchestrator.py" -WindowStyle Normal
Write-Host "   Backend starting in new window..." -ForegroundColor Green
Start-Sleep -Seconds 4

# Step 3: Start the Frontend (Vite) in a new window
Write-Host ""
Write-Host "[3/3] Starting Frontend on port 5173..." -ForegroundColor Yellow
$frontendDir = Join-Path $backendDir "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; cmd /c npm run dev" -WindowStyle Normal
Write-Host "   Frontend starting in new window..." -ForegroundColor Green

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Both services starting!" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Backend  : http://localhost:8000" -ForegroundColor White
Write-Host "   Swagger  : http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Frontend : http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "   Login with:" -ForegroundColor White
Write-Host "     mother      / motherpass      (Parent)" -ForegroundColor DarkGray
Write-Host "     father      / fatherpass      (Parent)" -ForegroundColor DarkGray
Write-Host "     child       / childpass       (Child)" -ForegroundColor DarkGray
Write-Host "     grandparent / grandparentpass (Grandparent)" -ForegroundColor DarkGray
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Open the browser after a short delay
Start-Sleep -Seconds 5
$url = "http://localhost:5173"
Start-Process $url
