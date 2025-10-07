@echo off
echo 症状診断システムのスタンドアロンテストを実行します...
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo.
echo 症状診断フローをシミュレート中...
python test_diagnosis_standalone.py

echo.
echo テスト完了。何かキーを押すと終了します。
pause
