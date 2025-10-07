@echo off
chcp 65001 > nul
echo ========================================
echo 🔧 接続トラブルシューティングツール
echo ========================================
echo.

echo 📋 システム情報を確認中...
echo OS: Windows
echo 現在時刻: %DATE% %TIME%
echo 作業ディレクトリ: %CD%
echo.

echo 🔍 Python 環境を確認中...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python が見つかりません
    echo 解決法: Anaconda Prompt を使用してください
    pause
    exit /b 1
)

echo 🔍 Conda 環境を確認中...
conda info --envs
if %errorlevel% neq 0 (
    echo ❌ Conda が見つかりません
    echo 解決法: Anaconda Prompt を使用してください
    pause
    exit /b 1
)

echo.
echo 🔍 ポート使用状況を確認中...
echo ポート 5001:
netstat -an | findstr :5001
echo ポート 5002:
netstat -an | findstr :5002
echo ポート 8000:
netstat -an | findstr :8000
echo.

echo 🔍 Python プロセスを確認中...
tasklist | findstr python
echo.

echo 🔍 Flask のインストール状況を確認中...
python -c "import flask; print('✅ Flask バージョン:', flask.__version__)" 2>nul || (
    echo ❌ Flask がインストールされていません
    echo インストール中...
    pip install flask
)

echo.
echo 🔍 ネットワーク設定を確認中...
echo ローカルIP:
ipconfig | findstr "IPv4"
echo.

echo 📋 ファイアウォール設定の確認方法:
echo 1. Windows の設定を開く
echo 2. 更新とセキュリティ → Windows セキュリティ
echo 3. ファイアウォールとネットワーク保護
echo 4. アプリをファイアウォール経由で許可
echo 5. Python.exe を探して許可にチェック
echo.

echo 🚀 推奨される解決手順:
echo 1. このウィンドウを閉じる
echo 2. Anaconda Prompt を右クリック → 管理者として実行
echo 3. cd "C:\Users\user\Desktop\udemy-langchain\camper-repair-clean"
echo 4. conda activate campingrepare
echo 5. start_emergency_server.bat
echo.

pause
