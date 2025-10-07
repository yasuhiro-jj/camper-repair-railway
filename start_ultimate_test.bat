@echo off
chcp 65001 > nul
echo ========================================
echo 🚨 究極テストサーバー起動
echo ========================================
echo.

echo 📋 現在の状況:
echo 作業ディレクトリ: %CD%
echo Python バージョン:
python --version
echo.

echo 🔍 ポート使用状況を確認中...
netstat -an | findstr :5001
netstat -an | findstr :5002
netstat -an | findstr :8000
echo.

echo 🚀 究極テストサーバーを起動中...
echo このサーバーは最もシンプルなHTTPサーバーです
echo Flask やその他のライブラリは不要です
echo.

REM Anaconda環境のアクティベート（エラーを無視）
call conda activate campingrepare 2>nul

echo サーバー起動中...
echo ⚠️ 接続できない場合の対処法:
echo 1. 管理者権限でこのバッチファイルを実行
echo 2. WindowsファイアウォールでPythonを許可
echo 3. ウイルス対策ソフトを一時的に無効化
echo 4. 別のブラウザで試す
echo.

python ultimate_test_server.py

echo.
echo ⚠️ サーバーが停止しました
echo 接続に成功した場合は、修理アドバイスセンターの
echo 統合バックエンドを起動できます
pause
