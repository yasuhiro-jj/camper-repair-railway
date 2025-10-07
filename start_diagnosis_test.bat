@echo off
echo 症状診断システムをテストします...
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"

echo.
echo Streamlitアプリを起動中...
streamlit run streamlit_app.py --server.port 8501

echo.
echo アプリケーションが起動しました。
echo ブラウザで http://localhost:8501 にアクセスしてください。
pause
