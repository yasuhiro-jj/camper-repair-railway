@echo off
chcp 65001 > nul
echo ========================================
echo キャンピングカー修理AI システム起動（新フロントエンド）
echo ========================================
echo.

echo 1. バックエンド（Flask）を起動中...
start "Backend" cmd /k "start_backend_local.bat"

echo バックエンドの起動を待機中（10秒）...
timeout /t 10 /nobreak > nul

echo.
echo 2. 新フロントエンド（Next.js）を起動中...
start "New Frontend" cmd /k "start_new_frontend_local.bat"

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
