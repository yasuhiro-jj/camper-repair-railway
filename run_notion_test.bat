@echo off
echo Notion接続テストを実行します...
cd /d "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"
streamlit run test_notion_streamlit.py --server.port 8502
pause
