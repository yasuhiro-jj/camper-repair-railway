@echo off
chcp 65001 > nul
echo ========================================
echo キャンピングカー修理AI システム起動（Anaconda）
echo ========================================
echo.

echo 1. バックエンド（Flask + Anaconda）を起動中...
start "Backend (Anaconda)" cmd /k "start_backend_anaconda.bat"

echo バックエンドの起動を待機中（10秒）...
timeout /t 10 /nobreak > nul

echo.
echo 2. フロントエンド（Next.js）を起動中...
start "Frontend" cmd /k "start_frontend_local.bat"

echo.
echo ========================================
echo システム起動完了
echo ========================================
echo フロントエンド: http://localhost:3000
echo バックエンドAPI: http://localhost:5001
echo.
echo 両方のウィンドウを閉じるまでシステムは稼働します
echo ========================================

pause
