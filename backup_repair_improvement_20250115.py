#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修理手順・注意事項抽出機能の改良版バックアップスクリプト
作成日: 2025年1月15日
"""

import os
import shutil
from datetime import datetime

def create_backup():
    """指定されたファイルをバックアップする"""
    
    # バックアップディレクトリの作成
    backup_dir = "backup_repair_improvement_20250115"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✅ バックアップディレクトリを作成しました: {backup_dir}")
    
    # バックアップ対象ファイル
    files_to_backup = [
        "app.py",
        "templates/repair_advice_center.html", 
        "エアコン.txt",
        "FFヒーター.txt"
    ]
    
    # バックアップ実行
    backup_count = 0
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            try:
                # ファイル名を取得
                filename = os.path.basename(file_path)
                
                # バックアップ先パス
                backup_path = os.path.join(backup_dir, filename)
                
                # ファイルをコピー
                shutil.copy2(file_path, backup_path)
                backup_count += 1
                print(f"✅ {file_path} → {backup_path}")
                
            except Exception as e:
                print(f"❌ {file_path} のバックアップに失敗: {e}")
        else:
            print(f"⚠️ ファイルが見つかりません: {file_path}")
    
    # バックアップ完了メッセージ
    print(f"\n🎉 バックアップ完了!")
    print(f"📁 バックアップディレクトリ: {backup_dir}")
    print(f"📄 バックアップファイル数: {backup_count}")
    print(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    create_backup()
