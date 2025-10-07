@echo off
chcp 65001 > nul
echo ========================================
echo 修理アドバイスセンター バックエンド起動（統合版）
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

REM 環境変数の設定
echo 環境変数を設定中...
set OPENAI_API_KEY=sk-proj-E_CJTfOabFVt新しいキー
set SERP_API_KEY=fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db
set LANGSMITH_API_KEY=
set LANGSMITH_PROJECT=default

echo.
echo 統合バックエンドAPIを起動中...
echo バックエンドURL: http://localhost:5002
echo 修理アドバイスセンター: http://localhost:5002/repair_advice_center.html
echo ヘルスチェック: http://localhost:5002/api/unified/health
echo.

python unified_backend_api.py

pause
