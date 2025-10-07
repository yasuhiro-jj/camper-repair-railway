@echo off
REM キャンピングカー修理システム 完全バックアップスクリプト
REM 作成日: %date%

echo ========================================
echo キャンピングカー修理システム バックアップ開始
echo ========================================

REM 現在の日時を取得してバックアップフォルダ名を生成
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "BACKUP_DIR=backup_%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

echo バックアップフォルダ: %BACKUP_DIR%
mkdir "%BACKUP_DIR%"

REM プロジェクトファイル全体をバックアップ
echo プロジェクトファイルをバックアップ中...
xcopy /E /I /H /Y /Q . "%BACKUP_DIR%\project_files\" /EXCLUDE:backup_exclude.txt

REM 環境変数ファイルのバックアップ
echo 環境変数ファイルをバックアップ中...
if exist .env (
    copy .env "%BACKUP_DIR%\" >nul 2>&1
    echo .env ファイルをバックアップしました
) else (
    echo .env ファイルが見つかりません
)

if exist env_example.txt (
    copy env_example.txt "%BACKUP_DIR%\" >nul 2>&1
    echo env_example.txt ファイルをバックアップしました
)

REM 設定ファイルのバックアップ
echo 設定ファイルをバックアップ中...
if exist config.py (
    copy config.py "%BACKUP_DIR%\" >nul 2>&1
    echo config.py ファイルをバックアップしました
)

REM ChromaDBのバックアップ
echo ChromaDBをバックアップ中...
if exist chroma_db (
    xcopy /E /I /H /Y /Q chroma_db "%BACKUP_DIR%\chroma_db\" >nul 2>&1
    echo ChromaDBをバックアップしました
) else (
    echo ChromaDBフォルダが見つかりません
)

REM 仮想環境のバックアップ（存在する場合）
echo 仮想環境をバックアップ中...
if exist venv (
    echo 仮想環境をスキップしています（サイズが大きいため）
    echo venv フォルダは手動で再作成してください
) else (
    echo 仮想環境が見つかりません
)

REM バックアップ情報ファイルを作成
echo バックアップ情報を記録中...
(
echo バックアップ日時: %date% %time%
echo バックアップフォルダ: %BACKUP_DIR%
echo.
echo 含まれるファイル:
echo - プロジェクトファイル全体
echo - 環境変数ファイル (.env, env_example.txt)
echo - 設定ファイル (config.py)
echo - ChromaDB (存在する場合)
echo.
echo 復元方法:
echo 1. プロジェクトフォルダに移動
echo 2. xcopy /E /I /H /Y "%BACKUP_DIR%\project_files\*" .\
echo 3. 環境変数ファイルを復元
echo 4. ChromaDBを復元 (存在する場合)
echo.
echo 注意: 仮想環境は手動で再作成してください
echo python -m venv venv
echo venv\Scripts\activate
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
