@echo off
echo 🏗️ キャンピングカー修理AI - バックエンドテスト実行
echo ================================================

echo 📦 必要なライブラリをチェック中...
python -c "import sys; print(f'Python version: {sys.version}')"

echo.
echo 🧪 最適化テストを実行中...
python test_backend_local.py

echo.
echo 🚀 バックエンドアプリを起動中...
python backend_only_app.py

pause
