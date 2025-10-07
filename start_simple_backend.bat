@echo off
chcp 65001 > nul
echo ========================================
echo 簡易バックエンドサーバー起動（テスト用）
echo ========================================
echo.

REM Anaconda環境のアクティベート
echo Anaconda環境をアクティベート中...
call conda activate campingrepare
if %errorlevel% neq 0 (
    echo Anaconda環境のアクティベートに失敗しました
    pause
    exit /b 1
)

echo.
echo 簡易バックエンドサーバーを起動中...
echo アクセスURL: http://localhost:5001
echo.

python simple_backend_server.py

pause
