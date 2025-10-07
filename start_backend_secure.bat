@echo off
echo Starting Camper Repair AI Backend (Secure Mode)...
echo.

REM 環境変数が設定されているかチェック
if "%OPENAI_API_KEY%"=="" (
    echo ERROR: OPENAI_API_KEY is not set!
    echo Please run 'set_api_keys.bat' first to set your API key.
    echo.
    pause
    exit /b 1
)

echo Environment variables are set.
echo Starting Flask application on http://localhost:5001
echo.

python app.py

pause
