@echo off
chcp 65001 > nul
echo ========================================
echo サーバー接続診断ツール
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
echo 接続診断を実行中...
python test_server_connection.py

echo.
echo ========================================
echo 診断完了
echo ========================================
pause
