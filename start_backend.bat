@echo off
echo バックエンドサーバーを起動しています...
echo.

cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo conda環境をアクティベート中...
call conda activate camper-repair-clean

echo.
echo 依存関係を確認中...
python -c "import flask, langchain, openai; print('依存関係OK')"

echo.
echo バックエンドサーバーを起動中...
echo アクセスURL: http://localhost:5002
echo.

python unified_backend_api.py

pause
