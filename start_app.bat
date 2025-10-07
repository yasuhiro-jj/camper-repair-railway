@echo off
echo 🔧 キャンピングカー修理チャットボットを起動しています...

REM 仮想環境をアクティベート
call venv\Scripts\activate

REM 依存関係をインストール
pip install -r requirements.txt

REM Streamlitアプリを起動
streamlit run streamlit_app.py

pause