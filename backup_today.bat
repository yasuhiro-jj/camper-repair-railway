@echo off
echo ========================================
echo キャンピングカー修理システム 今日のバックアップ
echo 作成日: %date%
echo ========================================

REM 現在の日時を取得してバックアップフォルダ名を生成
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "BACKUP_DIR=backup_%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

echo バックアップフォルダ: %BACKUP_DIR%
mkdir "%BACKUP_DIR%"

echo.
echo バックアップを開始します...

REM 主要なPythonファイルのバックアップ
echo 主要なPythonファイルをバックアップ中...
if exist "app.py" (
    copy "app.py" "%BACKUP_DIR%\app.py" >nul 2>&1
    echo ✅ app.py をバックアップしました
)

if exist "streamlit_app.py" (
    copy "streamlit_app.py" "%BACKUP_DIR%\streamlit_app.py" >nul 2>&1
    echo ✅ streamlit_app.py をバックアップしました
)

if exist "unified_backend_api.py" (
    copy "unified_backend_api.py" "%BACKUP_DIR%\unified_backend_api.py" >nul 2>&1
    echo ✅ unified_backend_api.py をバックアップしました
)

if exist "unified_chatbot_app.py" (
    copy "unified_chatbot_app.py" "%BACKUP_DIR%\unified_chatbot_app.py" >nul 2>&1
    echo ✅ unified_chatbot_app.py をバックアップしました
)

if exist "config.py" (
    copy "config.py" "%BACKUP_DIR%\config.py" >nul 2>&1
    echo ✅ config.py をバックアップしました
)

REM テンプレートファイルのバックアップ
echo テンプレートファイルをバックアップ中...
if exist "templates\" (
    xcopy /E /I /H /Y /Q "templates" "%BACKUP_DIR%\templates\" >nul 2>&1
    echo ✅ templates フォルダをバックアップしました
)

REM 静的ファイルのバックアップ
echo 静的ファイルをバックアップ中...
if exist "static\" (
    xcopy /E /I /H /Y /Q "static" "%BACKUP_DIR%\static\" >nul 2>&1
    echo ✅ static フォルダをバックアップしました
)

REM データアクセス層のバックアップ
echo データアクセス層をバックアップ中...
if exist "data_access\" (
    xcopy /E /I /H /Y /Q "data_access" "%BACKUP_DIR%\data_access\" >nul 2>&1
    echo ✅ data_access フォルダをバックアップしました
)

REM フロントエンドのバックアップ
echo フロントエンドをバックアップ中...
if exist "frontend\" (
    xcopy /E /I /H /Y /Q "frontend" "%BACKUP_DIR%\frontend\" >nul 2>&1
    echo ✅ frontend フォルダをバックアップしました
)

if exist "new_frontend\" (
    xcopy /E /I /H /Y /Q "new_frontend" "%BACKUP_DIR%\new_frontend\" >nul 2>&1
    echo ✅ new_frontend フォルダをバックアップしました
)

REM 重要なテキストファイルのバックアップ
echo 重要なテキストファイルをバックアップ中...
for %%f in (エアコン.txt FFヒーター.txt バッテリー.txt サブバッテリー.txt タイヤ.txt トイレ.txt 雨漏り.txt) do (
    if exist "%%f" (
        copy "%%f" "%BACKUP_DIR%\%%f" >nul 2>&1
        echo ✅ %%f をバックアップしました
    )
)

REM 設定ファイルのバックアップ
echo 設定ファイルをバックアップ中...
if exist ".env" (
    copy ".env" "%BACKUP_DIR%\.env" >nul 2>&1
    echo ✅ .env ファイルをバックアップしました
)

if exist "env_example.txt" (
    copy "env_example.txt" "%BACKUP_DIR%\env_example.txt" >nul 2>&1
    echo ✅ env_example.txt をバックアップしました
)

if exist "requirements.txt" (
    copy "requirements.txt" "%BACKUP_DIR%\requirements.txt" >nul 2>&1
    echo ✅ requirements.txt をバックアップしました
)

REM ChromaDBのバックアップ
echo ChromaDBをバックアップ中...
if exist "chroma_db" (
    xcopy /E /I /H /Y /Q "chroma_db" "%BACKUP_DIR%\chroma_db\" >nul 2>&1
    echo ✅ ChromaDBをバックアップしました
) else (
    echo ⚠️ ChromaDBフォルダが見つかりません
)

REM バックアップ情報ファイルを作成
echo バックアップ情報を記録中...
(
echo バックアップ日時: %date% %time%
echo バックアップフォルダ: %BACKUP_DIR%
echo.
echo 含まれるファイル:
echo - 主要なPythonファイル (app.py, streamlit_app.py, etc.)
echo - テンプレートファイル (templates/)
echo - 静的ファイル (static/)
echo - データアクセス層 (data_access/)
echo - フロントエンド (frontend/, new_frontend/)
echo - 重要なテキストファイル
echo - 設定ファイル (.env, requirements.txt)
echo - ChromaDB (存在する場合)
echo.
echo 復元方法:
echo 1. プロジェクトフォルダに移動
echo 2. 必要なファイルを手動で復元
echo 3. 環境変数ファイルを復元
echo 4. ChromaDBを復元 (存在する場合)
echo.
echo 注意: 仮想環境は手動で再作成してください
echo conda activate your_env_name
echo pip install -r requirements.txt
) > "%BACKUP_DIR%\backup_info.txt"

REM バックアップサイズを計算
echo.
echo バックアップサイズを計算中...
for /f %%i in ('dir "%BACKUP_DIR%" /s /-c ^| find "個のファイル"') do set FILES=%%i
for /f %%i in ('dir "%BACKUP_DIR%" /s /-c ^| find "バイト"') do set SIZE=%%i

echo ========================================
echo バックアップ完了！
echo ========================================
echo バックアップフォルダ: %BACKUP_DIR%
echo ファイル数: %FILES%
echo サイズ: %SIZE%
echo.
echo バックアップ情報: %BACKUP_DIR%\backup_info.txt
echo.
echo 次のステップ:
echo 1. バックアップフォルダを安全な場所に移動
echo 2. クラウドストレージにアップロード（推奨）
echo 3. 定期的なバックアップスケジュールを設定
echo.
pause
