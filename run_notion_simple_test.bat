@echo off
echo Notion接続シンプルテストを実行します...
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo.
echo Python環境を確認中...
python --version
echo.

echo Notion接続テストを開始...
python test_notion_simple.py

echo.
echo テスト完了。何かキーを押すと終了します。
pause
