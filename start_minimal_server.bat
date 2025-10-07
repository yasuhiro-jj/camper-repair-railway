@echo off
chcp 65001 > nul
echo ========================================
echo 最小限サーバー起動（接続テスト用）
echo ========================================
echo.

REM Anaconda環境のアクティベート
echo Anaconda環境をアクティベート中...
call conda activate campingrepare
if %errorlevel% neq 0 (
    echo Anaconda環境のアクティベートに失敗しました
    pause
    exit /b 1
)

echo.
echo 最小限サーバーを起動中...
echo アクセスURL: http://localhost:5001
echo テストURL: http://localhost:5001/test
echo.
echo 注意: 接続できない場合は以下を確認してください:
echo 1. WindowsファイアウォールでPythonを許可
echo 2. 管理者権限でこのバッチファイルを実行
echo 3. ウイルス対策ソフトを一時的に無効化
echo.

python minimal_server.py

pause
