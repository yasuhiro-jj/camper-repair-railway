@echo off
chcp 65001 > nul
echo ========================================
echo 環境変数設定
echo ========================================
echo.

echo OpenAI APIキーを設定してください:
set /p OPENAI_API_KEY="OpenAI API Key: "

echo.
echo SERP APIキーを設定してください（デフォルト値を使用する場合はEnter）:
set /p SERP_API_KEY="SERP API Key (default: fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db): "

if "%SERP_API_KEY%"=="" set SERP_API_KEY=fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db

echo.
echo .envファイルを作成中...

echo # 環境変数設定 > .env
echo OPENAI_API_KEY=%OPENAI_API_KEY% >> .env
echo SERP_API_KEY=%SERP_API_KEY% >> .env
echo LANGSMITH_API_KEY= >> .env
echo LANGSMITH_PROJECT=default >> .env

echo.
echo 環境変数設定完了！
echo .envファイルが作成されました
echo.

pause
