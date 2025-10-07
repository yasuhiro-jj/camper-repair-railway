@echo off
echo Notion接続直接テストを実行します...
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo.
echo Python環境を確認中...
python --version
echo.

echo 必要なライブラリを確認中...
python -c "import notion_client; print('✅ notion-client: OK')" 2>nul || echo "❌ notion-client: インストールが必要"
python -c "import dotenv; print('✅ python-dotenv: OK')" 2>nul || echo "❌ python-dotenv: インストールが必要"
echo.

echo Notion接続テストを開始...
python test_notion_direct.py

echo.
echo テスト完了。
pause
