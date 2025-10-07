@echo off
chcp 65001 >nul
echo ========================================
echo Anacondaプロンプトでバックアップ実行（修正版）
echo ========================================

REM Anacondaプロンプトを起動してバックアップスクリプトを実行
call "C:\Users\user\anaconda3\Scripts\activate.bat"
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo.
echo 現在のディレクトリ: %CD%
echo.

REM 修正版バックアップスクリプトを実行
echo 修正版バックアップスクリプトを実行中...
call backup_today_fixed.bat

echo.
echo バックアップ完了！
echo.
pause
