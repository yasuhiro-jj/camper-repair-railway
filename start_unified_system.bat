@echo off
chcp 65001 > nul
echo ========================================
echo 最強キャンピングカー修理チャットボット起動
echo ========================================
echo.

REM 環境変数の設定
echo Setting environment variables...
REM OpenAI APIキーを環境変数から取得
if "%OPENAI_API_KEY%"=="" (
    echo エラー: OPENAI_API_KEYが設定されていません
    echo 以下のコマンドでAPIキーを設定してください:
    echo setx OPENAI_API_KEY "実際のAPIキー"
    pause
    exit /b 1
)
echo OpenAI APIキーが設定されています: %OPENAI_API_KEY:~0,10%...
set SERP_API_KEY=fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db
set LANGSMITH_API_KEY=
set LANGSMITH_PROJECT=default
set LANGCHAIN_TRACING_V2=true
set LANGCHAIN_PROJECT=default

echo.
echo 依存関係をインストール中...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依存関係のインストールに失敗しました
    pause
    exit /b 1
)

echo.
echo 統合システムを起動中...
echo.

REM バックグラウンドで統合バックエンドAPIを起動
echo 1. 統合バックエンドAPIを起動中...
start "統合バックエンドAPI" cmd /k "python unified_backend_api.py"

REM 少し待機
timeout /t 5 /nobreak > nul

REM バックグラウンドでFlaskアプリを起動
echo 2. Flaskアプリを起動中...
start "Flaskアプリ" cmd /k "python app.py"

REM 少し待機
timeout /t 3 /nobreak > nul

REM バックグラウンドでStreamlitアプリを起動
echo 3. Streamlitアプリを起動中...
start "Streamlitアプリ" cmd /k "streamlit run streamlit_app.py --server.port 8501"

REM 少し待機
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo 🎉 最強チャットボットシステム起動完了！
echo ========================================
echo.
echo 📱 アクセスURL:
echo   - 統合フロントエンド: http://localhost:5001/unified_chatbot.html
echo   - Streamlitアプリ: http://localhost:8501
echo   - 修理アドバイスセンター: http://localhost:5001/repair_advice_center.html
echo   - 統合バックエンドAPI: http://localhost:5002
echo.
echo 🔧 機能:
echo   - AI診断 + RAG検索 + リアルタイム情報
echo   - 画像認識 + 音声処理 + 予測分析
echo   - 学習機能 + マルチモーダル対応
echo.
echo 🧪 テスト実行:
echo   python test_unified_system.py
echo.
echo 🛑 停止するには各ウィンドウでCtrl+Cを押してください
echo.

REM システムテストの実行
echo システムテストを実行しますか？ (y/n)
set /p test_choice=
if /i "%test_choice%"=="y" (
    echo.
    echo 🧪 統合システムテストを実行中...
    python test_unified_system.py
    echo.
    echo テスト完了。Enterキーを押して終了してください。
    pause > nul
)

echo.
echo システム起動完了。ブラウザでアクセスしてください。
pause
