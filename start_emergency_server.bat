@echo off
chcp 65001 > nul
echo ========================================
echo 🚨 緊急サーバー起動（接続テスト用）
echo ========================================
echo.

echo 🔍 現在の状況を確認中...
echo 作業ディレクトリ: %CD%
echo Python パス: 
where python
echo.

echo 📋 環境変数を確認中...
echo CONDA_DEFAULT_ENV: %CONDA_DEFAULT_ENV%
echo PATH: %PATH%
echo.

echo 🚀 緊急サーバーを起動中...
echo 注意: このサーバーは自動で利用可能なポートを検索します
echo.

REM Anaconda環境のアクティベート（エラーを無視）
call conda activate campingrepare 2>nul

REM Flask のインストール確認とインストール
echo 📦 Flask の状態を確認中...
python -c "import flask; print('✅ Flask は既にインストール済み')" 2>nul || (
    echo ❌ Flask が見つかりません。インストール中...
    pip install flask
)

echo.
echo 🚀 緊急サーバーを起動します...
echo 接続できない場合は以下を確認してください:
echo 1. 管理者権限でこのバッチファイルを実行
echo 2. WindowsファイアウォールでPythonを許可
echo 3. ウイルス対策ソフトを一時的に無効化
echo.

python emergency_server.py

echo.
echo ⚠️ サーバーが停止しました
pause
