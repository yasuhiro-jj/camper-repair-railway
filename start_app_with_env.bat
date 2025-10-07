@echo off
chcp 65001 >nul
echo 🔧 キャンピングカー修理アドバイスセンター起動スクリプト
echo ================================================

REM 環境変数を設定
set OPENAI_API_KEY=sk-proj-E_CJTfOabFVt新しいキー
set SERP_API_KEY=fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db
set LANGSMITH_API_KEY=your_langsmith_api_key_here
set LANGSMITH_PROJECT=camper-repair-center

echo ✅ 環境変数を設定しました

REM 現在のディレクトリを確認
echo 📁 現在のディレクトリ: %CD%

REM Pythonがインストールされているかチェック
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pythonがインストールされていません
    echo Python 3.8以上をインストールしてください
    pause
    exit /b 1
)

echo ✅ Pythonがインストールされています

REM 依存関係のインストール
echo 📦 依存関係をチェック中...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ❌ 依存関係のインストールに失敗しました
    echo 手動でインストールしてください: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ 依存関係がインストールされています

echo.
echo 🚀 Flaskアプリを起動中...
echo 📱 ブラウザで http://localhost:5000 にアクセスしてください
echo 🛑 停止するには Ctrl+C を押してください
echo.

REM Flaskアプリを起動
python app.py

echo.
echo 🛑 アプリが停止されました
pause
