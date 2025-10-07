@echo off
REM キャンピングカー修理システム 復元スクリプト
REM 使用方法: restore_script.bat [バックアップフォルダ名]

echo ========================================
echo キャンピングカー修理システム 復元開始
echo ========================================

REM バックアップフォルダの指定
if "%1"=="" (
    echo 利用可能なバックアップフォルダ:
    dir /B /AD backup_* 2>nul
    echo.
    set /p BACKUP_DIR="復元するバックアップフォルダ名を入力してください: "
) else (
    set BACKUP_DIR=%1
)

REM バックアップフォルダの存在確認
if not exist "%BACKUP_DIR%" (
    echo エラー: バックアップフォルダ '%BACKUP_DIR%' が見つかりません。
    echo 利用可能なバックアップフォルダ:
    dir /B /AD backup_* 2>nul
    pause
    exit /b 1
)

echo 復元元フォルダ: %BACKUP_DIR%
echo.

REM 復元前の確認
echo 警告: この操作は現在のファイルを上書きします。
set /p CONFIRM="続行しますか？ (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo 復元をキャンセルしました。
    pause
    exit /b 0
)

REM 現在のファイルを一時バックアップ
echo 現在のファイルを一時バックアップ中...
set TEMP_BACKUP=temp_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TEMP_BACKUP=%TEMP_BACKUP: =0%
mkdir "%TEMP_BACKUP%"
xcopy /E /I /H /Y /Q . "%TEMP_BACKUP%\" /EXCLUDE:backup_exclude.txt >nul 2>&1

REM プロジェクトファイルの復元
echo プロジェクトファイルを復元中...
xcopy /E /I /H /Y /Q "%BACKUP_DIR%\project_files\*" .\ /EXCLUDE:backup_exclude.txt

REM 環境変数ファイルの復元
echo 環境変数ファイルを復元中...
if exist "%BACKUP_DIR%\.env" (
    copy "%BACKUP_DIR%\.env" .\ >nul 2>&1
    echo .env ファイルを復元しました
)

if exist "%BACKUP_DIR%\env_example.txt" (
    copy "%BACKUP_DIR%\env_example.txt" .\ >nul 2>&1
    echo env_example.txt ファイルを復元しました
)

REM 設定ファイルの復元
echo 設定ファイルを復元中...
if exist "%BACKUP_DIR%\config.py" (
    copy "%BACKUP_DIR%\config.py" .\ >nul 2>&1
    echo config.py ファイルを復元しました
)

REM ChromaDBの復元
echo ChromaDBを復元中...
if exist "%BACKUP_DIR%\chroma_db" (
    if exist chroma_db (
        echo 既存のChromaDBを削除中...
        rmdir /S /Q chroma_db
    )
    xcopy /E /I /H /Y /Q "%BACKUP_DIR%\chroma_db" .\ >nul 2>&1
    echo ChromaDBを復元しました
) else (
    echo ChromaDBが見つかりません
)

REM 復元完了メッセージ
echo.
echo ========================================
echo 復元完了！
echo ========================================
echo 復元元: %BACKUP_DIR%
echo 一時バックアップ: %TEMP_BACKUP%
echo.
echo 次のステップ:
echo 1. 仮想環境を再作成: python -m venv venv
echo 2. 仮想環境をアクティベート: venv\Scripts\activate
echo 3. 依存関係をインストール: pip install -r requirements.txt
echo 4. 環境変数を設定: .env ファイルを確認
echo 5. システムをテスト: python repair_center_api.py
echo.
echo 一時バックアップは必要に応じて削除してください。
echo rmdir /S /Q "%TEMP_BACKUP%"
echo.
pause
