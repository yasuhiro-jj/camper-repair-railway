@echo off
title Fix PowerShell and Start Anaconda
echo PowerShellの実行ポリシーを修正中...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
echo.
echo Anacondaプロンプトを起動中...
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"
call "C:\Users\user\anaconda3\Scripts\activate.bat"
echo.
echo ✅ Anaconda環境が起動しました
echo 📁 現在のディレクトリ: %CD%
echo.
cmd /k
