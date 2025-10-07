@echo off
echo Notionデータベースのカテゴリ設定を確認します...
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo.
echo カテゴリ設定の詳細を確認中...
python check_notion_categories.py

echo.
echo 確認完了。何かキーを押すと終了します。
pause
