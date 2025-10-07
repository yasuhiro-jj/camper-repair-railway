@echo off
chcp 65001 > nul
echo ========================================
echo キャンピングカー修理AI フロントエンド起動
echo ========================================
echo.

REM フロントエンドディレクトリに移動
cd frontend

echo 依存関係をインストール中...
call npm install
if %errorlevel% neq 0 (
    echo 依存関係のインストールに失敗しました
    pause
    exit /b 1
)

echo.
echo Next.js 開発サーバーを起動中...
echo フロントエンドURL: http://localhost:3000
echo バックエンドAPI: http://localhost:5001
echo.

call npm run dev

pause
