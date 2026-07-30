@echo off
title KinNest Startup

echo.
echo ================================================
echo    KinNest Family OS -- Starting Up
echo ================================================
echo.

echo [1/3] Clearing ports 8000-8006...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000 \|:8001 \|:8002 \|:8003 \|:8004 \|:8005 \|:8006 "') do (
    if not "%%a"=="0" (
        taskkill /F /PID %%a >nul 2>&1
    )
)
echo    Ports cleared.
timeout /t 1 /nobreak >nul

echo.
echo [2/3] Starting Backend Orchestrator on port 8000...
start "KinNest Backend" cmd /k "cd /d %~dp0 && python orchestrator.py"
timeout /t 4 /nobreak >nul

echo.
echo [3/3] Starting Frontend on port 5173...
start "KinNest Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ================================================
echo    Both services are starting!
echo.
echo    Backend  : http://localhost:8000
echo    Swagger  : http://localhost:8000/docs
echo    Frontend : http://localhost:5173
echo.
echo    Default Login Credentials:
echo      mother      / motherpass      (Parent)
echo      father      / fatherpass      (Parent)
echo      child       / childpass       (Child)
echo      grandparent / grandparentpass (Grandparent)
echo ================================================
echo.

timeout /t 5 /nobreak >nul
start http://localhost:5173
