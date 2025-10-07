@echo off
echo ========================================
echo Anacondaプロンプトでバックアップ実行
echo ========================================

REM Anacondaプロンプトを起動してバックアップスクリプトを実行
call "C:\Users\user\anaconda3\Scripts\activate.bat"
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo.
echo 現在のディレクトリ: %CD%
echo.

REM バックアップスクリプトを実行
echo バックアップスクリプトを実行中...
call backup_today.bat

echo.
echo バックアップ完了！
echo.
pause
