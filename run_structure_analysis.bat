@echo off
echo Notionデータベースの構造を詳しく分析します...
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo.
echo データベース構造を分析中...
python analyze_notion_structure.py

echo.
echo 分析完了。何かキーを押すと終了します。
pause
