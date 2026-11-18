# Toutiao launcher — run with:  . .\start.ps1
# (dot-space-script, executes in current scope, inherits your env)

$backendDir  = "D:\Project\Study\toutiao\toutiao_backend"
$frontendDir = "D:\Project\Study\toutiao\toutiao-frontend"
$redisDir    = "C:\Tools\Redis-8.10.2\Redis-8.10.2-Windows-x64-msys2"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Toutiao Project Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ---- 1. Redis ----
Write-Host "[1/3] Starting Redis..." -ForegroundColor Yellow
$redisCheck = & "$redisDir\redis-cli.exe" ping 2>$null
if ($redisCheck -eq "PONG") {
    Write-Host "  Redis already running" -ForegroundColor Green
} else {
    $redisProc = Start-Process "$redisDir\redis-server.exe" -NoNewWindow -PassThru
    Start-Sleep 2
    if ((& "$redisDir\redis-cli.exe" ping 2>$null) -eq "PONG") {
        Write-Host "  Redis started (6379)" -ForegroundColor Green
    } else {
        Write-Host "  Redis FAILED" -ForegroundColor Red
    }
}

# ---- 2. Backend ----
Write-Host "[2/3] Starting backend..." -ForegroundColor Yellow
$backendProc = Start-Process uv -ArgumentList "run","uvicorn","main:app","--reload","--host","127.0.0.1","--port","8000" `
    -WorkingDirectory $backendDir -NoNewWindow -PassThru
Start-Sleep 3
Write-Host "  Backend : http://127.0.0.1:8000" -ForegroundColor Green

# ---- 3. Frontend ----
Write-Host "[3/3] Starting frontend..." -ForegroundColor Yellow
$frontendProc = Start-Process cmd -ArgumentList "/c","npm run dev" `
    -WorkingDirectory $frontendDir -NoNewWindow -PassThru
Start-Sleep 3
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backend : http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ctrl+C to stop" -ForegroundColor Gray

try { while ($true) { Start-Sleep 3 } } finally {
    Write-Host "`nStopping..." -ForegroundColor Yellow
    $redisProc, $backendProc, $frontendProc | ForEach-Object {
        if ($_ -and !$_.HasExited) { Stop-Process $_.Id -Force -ErrorAction SilentlyContinue }
    }
    Write-Host "All stopped." -ForegroundColor Green
}