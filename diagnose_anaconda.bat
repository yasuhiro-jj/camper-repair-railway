@echo off
chcp 65001 >nul
title Anaconda環境診断ツール
echo.
echo ========================================
echo Anaconda環境診断ツール
echo ========================================
echo.

echo 📁 現在のディレクトリ: %CD%
echo.

echo 🔍 Python環境の確認...
python --version
if errorlevel 1 (
    echo ❌ Pythonが見つかりません
) else (
    echo ✅ Pythonが正常に動作しています
)

echo.
echo 🔍 Conda環境の確認...
conda --version
if errorlevel 1 (
    echo ❌ Condaが見つかりません
) else (
    echo ✅ Condaが正常に動作しています
)

echo.
echo 🔍 環境変数の確認...
echo PATH: %PATH%
echo.

echo 🔍 現在のconda環境...
conda info --envs

echo.
echo 🔍 アクティブな環境...
conda info

echo.
echo 診断が完了しました
pause

