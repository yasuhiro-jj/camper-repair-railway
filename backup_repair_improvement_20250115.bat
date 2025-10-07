@echo off
echo ========================================
echo 修理手順・注意事項抽出機能の改良版バックアップ
echo 作成日: 2025年1月15日
echo ========================================

REM バックアップディレクトリの作成
if not exist "backup_repair_improvement_20250115" mkdir "backup_repair_improvement_20250115"

echo.
echo バックアップを開始します...

REM app.pyのバックアップ
if exist "app.py" (
    copy "app.py" "backup_repair_improvement_20250115\app.py"
    echo ✅ app.py をバックアップしました
) else (
    echo ❌ app.py が見つかりません
)

REM templates/repair_advice_center.htmlのバックアップ
if exist "templates\repair_advice_center.html" (
    copy "templates\repair_advice_center.html" "backup_repair_improvement_20250115\repair_advice_center.html"
    echo ✅ templates/repair_advice_center.html をバックアップしました
) else (
    echo ❌ templates/repair_advice_center.html が見つかりません
)

REM エアコン.txtのバックアップ
if exist "エアコン.txt" (
    copy "エアコン.txt" "backup_repair_improvement_20250115\エアコン.txt"
    echo ✅ エアコン.txt をバックアップしました
) else (
    echo ❌ エアコン.txt が見つかりません
)

REM FFヒーター.txtのバックアップ
if exist "FFヒーター.txt" (
    copy "FFヒーター.txt" "backup_repair_improvement_20250115\FFヒーター.txt"
    echo ✅ FFヒーター.txt をバックアップしました
) else (
    echo ❌ FFヒーター.txt が見つかりません
)

echo.
echo ========================================
echo バックアップ完了!
echo バックアップディレクトリ: backup_repair_improvement_20250115
echo ========================================
pause
