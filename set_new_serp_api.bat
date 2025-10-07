@echo off
REM 新しいSERP APIキーを設定するバッチファイル
REM このファイルを実行してからアプリケーションを起動してください

echo 新しいSERP APIキーを設定しています...

REM 新しいSERP APIキーを設定
set SERP_API_KEY=fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db

echo ✅ SERP_API_KEYが設定されました
echo 新しいAPIキー: %SERP_API_KEY%

echo.
echo 🧪 SERP APIキーのテストを実行します...
python test_new_serp_api.py

echo.
echo 🚀 メインアプリケーションを起動しますか？
echo 1. Flaskアプリ (推奨) - http://localhost:5000
echo 2. Streamlitアプリ - http://localhost:8501
echo 3. テストのみ実行
echo 4. 終了
echo.

set /p choice="選択してください (1-4): "

if "%choice%"=="1" goto start_flask
if "%choice%"=="2" goto start_streamlit
if "%choice%"=="3" goto test_only
if "%choice%"=="4" goto end
goto invalid_choice

:start_flask
echo.
echo 🌐 Flaskアプリを起動中...
echo 📱 ブラウザで http://localhost:5000 にアクセスしてください
echo 🛑 停止するには Ctrl+C を押してください
echo.
python app.py
goto end

:start_streamlit
echo.
echo 📊 Streamlitアプリを起動中...
echo 📱 ブラウザで http://localhost:8501 にアクセスしてください
echo 🛑 停止するには Ctrl+C を押してください
echo.
streamlit run streamlit_app.py
goto end

:test_only
echo.
echo 🧪 SERP検索機能のテストを実行中...
python test_serp_integration.py
goto end

:invalid_choice
echo.
echo ❌ 無効な選択です
pause
goto end

:end
echo.
echo 👋 アプリケーションを終了しました
pause
