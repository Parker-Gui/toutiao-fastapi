@echo off
chcp 65001 >nul
setlocal

set "REDIS_DIR=C:\Tools\Redis-8.10.2\Redis-8.10.2-Windows-x64-msys2"
set "BACKEND_DIR=D:\Project\Study\toutiao\toutiao_backend"
set "FRONTEND_DIR=D:\Project\Study\toutiao\toutiao-frontend"

echo ========================================
echo   Toutiao Project Launcher
echo ========================================
echo.

REM ---- 1. Redis ----
echo [1/3] Starting Redis...
if exist "%REDIS_DIR%\redis-cli.exe" (
    "%REDIS_DIR%\redis-cli.exe" ping >nul 2>&1
    if %errorlevel% equ 0 (
        echo   Redis already running (port 6379)
    ) else (
        start "" "%REDIS_DIR%\redis-server.exe"
        timeout /t 2 >nul
        "%REDIS_DIR%\redis-cli.exe" ping >nul 2>&1
        if %errorlevel% equ 0 (
            echo   Redis started (port 6379)
        ) else (
            echo   Redis failed to start
            pause
            exit /b 1
        )
    )
) else (
    echo   ERROR: Redis not found at %REDIS_DIR%
    pause
    exit /b 1
)

REM ---- 2. Backend ----
echo [2/3] Starting backend (FastAPI)...
start "Backend" cmd /c "cd /d %BACKEND_DIR% && uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3 >nul
echo   Backend  : http://127.0.0.1:8000

REM ---- 3. Frontend ----
echo [3/3] Starting frontend (Vite)...
start "Frontend" cmd /c "cd /d %FRONTEND_DIR% && npm run dev"
timeout /t 3 >nul
echo   Frontend : http://localhost:5173

echo.
echo ========================================
echo   All services running!
echo   Backend  : http://127.0.0.1:8000
echo   Frontend : http://localhost:5173
echo   Redis    : 127.0.0.1:6379
echo ========================================
echo.
echo Close the backend / frontend / Redis windows to stop each service.
echo.

pause
endlocal