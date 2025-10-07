@echo off
chcp 65001 > nul
echo ========================================
echo キャンピングカー修理AI バックエンド起動
echo ========================================
echo.

REM 環境変数の設定
echo 環境変数を設定中...
set OPENAI_API_KEY=sk-proj-E_CJTfOabFVt新しいキー
set SERP_API_KEY=fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db
set LANGSMITH_API_KEY=
set LANGSMITH_PROJECT=default
set LANGCHAIN_TRACING_V2=true
set LANGCHAIN_PROJECT=default

echo.
echo 依存関係をインストール中...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依存関係のインストールに失敗しました
    pause
    exit /b 1
)

echo.
echo Flask アプリケーションを起動中...
echo バックエンドURL: http://localhost:5001
echo フロントエンドからアクセス可能
echo.

python app.py

pause
