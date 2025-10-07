@echo off
chcp 65001 >nul
echo.
echo ========================================
echo Anaconda環境変数設定スクリプト
echo キャンピングカー修理AIチャットアプリ
echo ========================================
echo.

REM プロジェクトディレクトリに移動
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo 📁 現在のディレクトリ: %CD%
echo.

echo 🔧 環境変数の設定方法を選択してください:
echo.
echo 1. .envファイルを作成（推奨）
echo 2. 環境変数を直接設定
echo 3. Streamlitシークレットファイルを作成
echo 4. 現在の設定を確認
echo 5. 終了
echo.

set /p choice="選択してください (1-5): "

if "%choice%"=="1" goto create_env_file
if "%choice%"=="2" goto set_env_vars
if "%choice%"=="3" goto create_secrets
if "%choice%"=="4" goto check_settings
if "%choice%"=="5" goto end
goto invalid_choice

:create_env_file
echo.
echo 📝 .envファイルを作成中...
if exist ".env" (
    echo ⚠️  .envファイルが既に存在します
    set /p overwrite="上書きしますか？ (y/n): "
    if /i not "%overwrite%"=="y" goto end
)

echo # OpenAI API設定（必須） > .env
echo OPENAI_API_KEY=your_openai_api_key_here >> .env
echo. >> .env
echo # Notion API設定（オプション） >> .env
echo NOTION_API_KEY=your_notion_integration_token_here >> .env
echo NOTION_TOKEN=your_notion_integration_token_here >> .env
echo NOTION_DIAGNOSTIC_DB_ID=your_notion_diagnostic_database_id_here >> .env
echo. >> .env
echo # NotionデータベースID >> .env
echo NODE_DB_ID=your_notion_diagnostic_database_id_here >> .env
echo CASE_DB_ID=your_notion_repair_case_database_id_here >> .env
echo. >> .env
echo # LangSmith設定（オプション） >> .env
echo LANGSMITH_API_KEY=your_langsmith_api_key_here >> .env
echo LANGSMITH_PROJECT=camper-repair-ai >> .env
echo LANGSMITH_ENDPOINT=https://api.smith.langchain.com >> .env

echo ✅ .envファイルが作成されました
echo.
echo ⚠️  重要: .envファイルを編集して実際のAPIキーを設定してください
echo 📝 メモ帳で開く場合は: notepad .env
echo.
goto end

:set_env_vars
echo.
echo 🔧 環境変数を直接設定します
echo.
echo 現在の設定:
echo OPENAI_API_KEY: %OPENAI_API_KEY%
echo.
set /p api_key="OpenAI APIキーを入力してください: "
if not "%api_key%"=="" (
    set OPENAI_API_KEY=%api_key%
    echo ✅ OpenAI APIキーが設定されました
) else (
    echo ❌ APIキーが入力されませんでした
)
echo.
echo 現在の設定:
echo OPENAI_API_KEY: %OPENAI_API_KEY%
echo.
echo ⚠️  注意: この設定は現在のセッションのみ有効です
echo 📝 永続的に設定するには、Anacondaプロンプトの設定ファイルを編集してください
echo.
goto end

:create_secrets
echo.
echo 🔐 Streamlitシークレットファイルを作成中...
if not exist ".streamlit" mkdir .streamlit

if exist ".streamlit\secrets.toml" (
    echo ⚠️  secrets.tomlファイルが既に存在します
    set /p overwrite="上書きしますか？ (y/n): "
    if /i not "%overwrite%"=="y" goto end
)

echo # OpenAI API設定（必須） > .streamlit\secrets.toml
echo OPENAI_API_KEY = "your_openai_api_key_here" >> .streamlit\secrets.toml
echo. >> .streamlit\secrets.toml
echo # Notion API設定（オプション） >> .streamlit\secrets.toml
echo NOTION_API_KEY = "your_notion_integration_token_here" >> .streamlit\secrets.toml
echo NOTION_TOKEN = "your_notion_integration_token_here" >> .streamlit\secrets.toml
echo NOTION_DIAGNOSTIC_DB_ID = "your_notion_diagnostic_database_id_here" >> .streamlit\secrets.toml
echo. >> .streamlit\secrets.toml
echo # NotionデータベースID >> .streamlit\secrets.toml
echo NODE_DB_ID = "your_notion_diagnostic_database_id_here" >> .streamlit\secrets.toml
echo CASE_DB_ID = "your_notion_repair_case_database_id_here" >> .streamlit\secrets.toml
echo. >> .streamlit\secrets.toml
echo # LangSmith設定（オプション） >> .streamlit\secrets.toml
echo LANGSMITH_API_KEY = "your_langsmith_api_key_here" >> .streamlit\secrets.toml
echo LANGSMITH_PROJECT = "camper-repair-ai" >> .streamlit\secrets.toml
echo LANGSMITH_ENDPOINT = "https://api.smith.langchain.com" >> .streamlit\secrets.toml

echo ✅ Streamlitシークレットファイルが作成されました
echo.
echo ⚠️  重要: secrets.tomlファイルを編集して実際のAPIキーを設定してください
echo 📝 メモ帳で開く場合は: notepad .streamlit\secrets.toml
echo.
goto end

:check_settings
echo.
echo 🔍 現在の設定を確認中...
echo.
echo 📁 ファイルの存在確認:
if exist ".env" (
    echo ✅ .envファイル: 存在
) else (
    echo ❌ .envファイル: 存在しません
)

if exist ".streamlit\secrets.toml" (
    echo ✅ secrets.tomlファイル: 存在
) else (
    echo ❌ secrets.tomlファイル: 存在しません
)

echo.
echo 🔧 環境変数の確認:
echo OPENAI_API_KEY: %OPENAI_API_KEY%
if "%OPENAI_API_KEY%"=="" (
    echo ❌ OpenAI APIキーが設定されていません
) else (
    echo ✅ OpenAI APIキーが設定されています
)

echo.
echo 📝 設定方法:
echo 1. .envファイルを作成: 選択肢1を実行
echo 2. 環境変数を設定: 選択肢2を実行
echo 3. Streamlitシークレットを作成: 選択肢3を実行
echo.
goto end

:invalid_choice
echo.
echo ❌ 無効な選択です
pause
goto end

:end
echo.
echo 👋 設定が完了しました
echo.
echo 🚀 アプリケーションを起動するには:
echo streamlit run enhanced_knowledge_base_app.py --server.port 8508
echo.
pause
