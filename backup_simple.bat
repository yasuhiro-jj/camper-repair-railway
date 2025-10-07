@echo off
echo ========================================
echo キャンピングカー修理システム シンプルバックアップ
echo 作成日: %date%
echo ========================================

REM シンプルな日時取得（PowerShellを使用）
for /f "tokens=1-3 delims=/" %%a in ("%date%") do (
    set "MM=%%a"
    set "DD=%%b" 
    set "YYYY=%%c"
)

for /f "tokens=1-3 delims=:" %%a in ("%time%") do (
    set "HH=%%a"
    set "Min=%%b"
    set "Sec=%%c"
)

REM 前ゼロを追加
if %MM% LSS 10 set "MM=0%MM%"
if %DD% LSS 10 set "DD=0%DD%"
if %HH% LSS 10 set "HH=0%HH%"
if %Min% LSS 10 set "Min=0%Min%"
if %Sec% LSS 10 set "Sec=0%Sec%"

set "BACKUP_DIR=backup_%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

echo バックアップフォルダ: %BACKUP_DIR%
mkdir "%BACKUP_DIR%" 2>nul

echo.
echo バックアップを開始します...

REM 主要なPythonファイルのバックアップ
echo [1/8] 主要なPythonファイルをバックアップ中...
if exist "app.py" copy "app.py" "%BACKUP_DIR%\app.py" >nul 2>&1 && echo   - app.py
if exist "streamlit_app.py" copy "streamlit_app.py" "%BACKUP_DIR%\streamlit_app.py" >nul 2>&1 && echo   - streamlit_app.py
if exist "unified_backend_api.py" copy "unified_backend_api.py" "%BACKUP_DIR%\unified_backend_api.py" >nul 2>&1 && echo   - unified_backend_api.py
if exist "unified_chatbot_app.py" copy "unified_chatbot_app.py" "%BACKUP_DIR%\unified_chatbot_app.py" >nul 2>&1 && echo   - unified_chatbot_app.py
if exist "config.py" copy "config.py" "%BACKUP_DIR%\config.py" >nul 2>&1 && echo   - config.py

REM テンプレートファイルのバックアップ
echo [2/8] テンプレートファイルをバックアップ中...
if exist "templates\" (
    xcopy /E /I /H /Y /Q "templates" "%BACKUP_DIR%\templates\" >nul 2>&1
    echo   - templates フォルダ
)

REM 静的ファイルのバックアップ
echo [3/8] 静的ファイルをバックアップ中...
if exist "static\" (
    xcopy /E /I /H /Y /Q "static" "%BACKUP_DIR%\static\" >nul 2>&1
    echo   - static フォルダ
)

REM データアクセス層のバックアップ
echo [4/8] データアクセス層をバックアップ中...
if exist "data_access\" (
    xcopy /E /I /H /Y /Q "data_access" "%BACKUP_DIR%\data_access\" >nul 2>&1
    echo   - data_access フォルダ
)

REM フロントエンドのバックアップ
echo [5/8] フロントエンドをバックアップ中...
if exist "frontend\" (
    xcopy /E /I /H /Y /Q "frontend" "%BACKUP_DIR%\frontend\" >nul 2>&1
    echo   - frontend フォルダ
)
if exist "new_frontend\" (
    xcopy /E /I /H /Y /Q "new_frontend" "%BACKUP_DIR%\new_frontend\" >nul 2>&1
    echo   - new_frontend フォルダ
)

REM 重要なテキストファイルのバックアップ
echo [6/8] 重要なテキストファイルをバックアップ中...
for %%f in (エアコン.txt FFヒーター.txt バッテリー.txt サブバッテリー.txt タイヤ.txt トイレ.txt 雨漏り.txt) do (
    if exist "%%f" (
        copy "%%f" "%BACKUP_DIR%\%%f" >nul 2>&1
        echo   - %%f
    )
)

REM 設定ファイルのバックアップ
echo [7/8] 設定ファイルをバックアップ中...
if exist ".env" copy ".env" "%BACKUP_DIR%\.env" >nul 2>&1 && echo   - .env
if exist "env_example.txt" copy "env_example.txt" "%BACKUP_DIR%\env_example.txt" >nul 2>&1 && echo   - env_example.txt
if exist "requirements.txt" copy "requirements.txt" "%BACKUP_DIR%\requirements.txt" >nul 2>&1 && echo   - requirements.txt

REM ChromaDBのバックアップ
echo [8/8] ChromaDBをバックアップ中...
if exist "chroma_db" (
    xcopy /E /I /H /Y /Q "chroma_db" "%BACKUP_DIR%\chroma_db\" >nul 2>&1
    echo   - ChromaDB フォルダ
) else (
    echo   - ChromaDB フォルダが見つかりません
)

REM バックアップ情報ファイルを作成
echo.
echo バックアップ情報を記録中...
(
echo バックアップ日時: %date% %time%
echo バックアップフォルダ: %BACKUP_DIR%
echo.
echo 含まれるファイル:
echo - 主要なPythonファイル
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
) > "%BACKUP_DIR%\backup_info.txt"

echo.
echo ========================================
echo バックアップ完了！
echo ========================================
echo バックアップフォルダ: %BACKUP_DIR%
echo バックアップ情報: %BACKUP_DIR%\backup_info.txt
echo.
echo 次のステップ:
echo 1. バックアップフォルダを安全な場所に移動
echo 2. クラウドストレージにアップロード（推奨）
echo 3. 定期的なバックアップスケジュールを設定
echo.
pause
