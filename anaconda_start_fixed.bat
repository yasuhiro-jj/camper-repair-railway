@echo off
chcp 65001 >nul
title キャンピングカー修理AI - Anaconda環境
echo.
echo ========================================
echo キャンピングカー修理AIチャットアプリ
echo Anaconda環境用起動スクリプト
echo ========================================
echo.

REM プロジェクトディレクトリに移動
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo 📁 現在のディレクトリ: %CD%
echo.

REM conda環境の確認
echo 🔍 conda環境を確認中...
conda info --envs

echo.
echo 以下のオプションから選択してください:
echo.
echo 1. 新しいconda環境を作成して起動
echo 2. 既存の環境を使用して起動
echo 3. 環境変数のみ設定
echo 4. 終了
echo.

set /p choice="選択してください (1-4): "

if "%choice%"=="1" goto create_env
if "%choice%"=="2" goto use_existing
if "%choice%"=="3" goto setup_env
if "%choice%"=="4" goto end
goto invalid_choice

:create_env
echo.
echo 🐍 新しいconda環境を作成中...
conda create -n camper-repair python=3.9 -y
if errorlevel 1 (
    echo ❌ 環境の作成に失敗しました
    echo エラーの詳細を確認してください
    pause
    exit /b 1
)

echo ✅ 環境が作成されました
goto activate_env

:use_existing
echo.
echo 既存の環境名を入力してください:
set /p env_name="環境名: "
conda activate %env_name%
if errorlevel 1 (
    echo ❌ 環境のアクティベートに失敗しました
    echo 環境名を確認してください
    pause
    exit /b 1
)
echo ✅ 環境 %env_name% がアクティベートされました
goto install_deps

:activate_env
echo.
echo 🔄 環境をアクティベート中...
conda activate camper-repair
if errorlevel 1 (
    echo ❌ 環境のアクティベートに失敗しました
    echo condaの設定を確認してください
    pause
    exit /b 1
)
echo ✅ 環境 camper-repair がアクティベートされました

:install_deps
echo.
echo 📦 依存関係をインストール中...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依存関係のインストールに失敗しました
    echo 手動でインストールしてください: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ 依存関係のインストールが完了しました

:setup_env
echo.
echo ⚙️ 環境変数の設定...
if not exist ".env" (
    echo 📝 .envファイルを作成中...
    echo OPENAI_API_KEY=your_openai_api_key_here > .env
    echo NOTION_API_KEY=your_notion_api_key_here >> .env
    echo NODE_DB_ID=your_notion_node_db_id >> .env
    echo CASE_DB_ID=your_notion_case_db_id >> .env
    echo ITEM_DB_ID=your_notion_item_db_id >> .env
    echo ✅ .envファイルが作成されました
    echo ⚠️  .envファイルを編集してAPIキーを設定してください
) else (
    echo ✅ .envファイルが既に存在します
)

echo.
echo 🚀 アプリケーションを起動しますか？
echo.
echo 1. Flaskアプリ (推奨) - http://localhost:5000
echo 2. Streamlitアプリ - http://localhost:8501
echo 3. 起動スクリプトを使用
echo 4. 終了
echo.

set /p app_choice="選択してください (1-4): "

if "%app_choice%"=="1" goto start_flask
if "%app_choice%"=="2" goto start_streamlit
if "%app_choice%"=="3" goto start_script
if "%app_choice%"=="4" goto end
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

:start_script
echo.
echo 🔧 起動スクリプトを実行中...
python run_app.py
goto end

:invalid_choice
echo.
echo ❌ 無効な選択です
echo 1-4の数字を入力してください
pause
goto end

:end
echo.
echo 👋 アプリケーションを終了しました
echo 何かキーを押すとウィンドウが閉じます...
pause >nul

