@echo off
chcp 65001 > nul
echo Repair Center API Starting...
echo.

REM Install required libraries
echo Checking required libraries...
pip install flask flask-cors requests > nul 2>&1

REM Check if port 5000 is in use
echo Checking port 5000 status...
netstat -an | findstr :5000 > nul
if %errorlevel% == 0 (
    echo Port 5000 is already in use
    echo Terminating existing processes...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
        taskkill /f /pid %%a > nul 2>&1
    )
    timeout /t 2 > nul
)

REM Start API server
echo Starting API server...
echo.
echo Access URL: http://localhost:5000
echo API Endpoint: http://localhost:5000/api/search
echo Health Check: http://localhost:5000/api/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Open browser automatically
start http://localhost:5000

python repair_center_api.py

pause
