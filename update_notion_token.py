#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notionトークン更新支援スクリプト
新規インテグレーション作成後のトークン更新を支援します
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

def find_env_file():
    """環境変数ファイルを探す"""
    possible_files = [
        ".env",
        "env.template",
        ".env.local",
        ".env.example"
    ]
    
    for filename in possible_files:
        if os.path.exists(filename):
            return filename
    return None

def backup_env_file(env_file: str):
    """環境変数ファイルをバックアップ"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{env_file}.backup_{timestamp}"
    shutil.copy2(env_file, backup_file)
    print(f"✅ バックアップ作成: {backup_file}")
    return backup_file

def update_token_in_file(filepath: str, new_token: str):
    """環境変数ファイル内のNOTION_TOKENを更新"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        updated = False
        new_lines = []
        
        for line in lines:
            stripped = line.strip()
            # NOTION_TOKENまたはNOTION_API_KEYの行を更新
            if stripped.startswith('NOTION_TOKEN=') or stripped.startswith('NOTION_API_KEY='):
                # コメント行でない場合
                if not stripped.startswith('#'):
                    # 既存の値を新しいトークンに置き換え
                    if '=' in stripped:
                        key = stripped.split('=')[0]
                        new_lines.append(f"{key}={new_token}\n")
                        updated = True
                        print(f"✅ {key}を更新しました")
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # トークンが見つからない場合は追加
        if not updated:
            new_lines.append(f"\n# Notion API Token (更新日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            new_lines.append(f"NOTION_TOKEN={new_token}\n")
            print("✅ NOTION_TOKENを追加しました")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return True
        
    except Exception as e:
        print(f"❌ ファイル更新エラー: {e}")
        return False

def main():
    print("=" * 80)
    print("Notionトークン更新支援ツール")
    print("=" * 80)
    print()
    
    # 環境変数ファイルを探す
    env_file = find_env_file()
    if not env_file:
        print("⚠️ 環境変数ファイル（.env）が見つかりません")
        print()
        print("手動で更新してください:")
        print("  1. .envファイルを開く")
        print("  2. NOTION_TOKEN=新しいトークン を設定")
        print("  3. ファイルを保存")
        return
    
    print(f"📄 環境変数ファイル: {env_file}")
    print()
    
    # 新しいトークンの入力
    print("新しいNotionトークンを入力してください（secret_...で始まる文字列）")
    print("（Ctrl+Cでキャンセル）")
    print()
    new_token = input("新しいトークン: ").strip()
    
    if not new_token:
        print("❌ トークンが入力されませんでした")
        return
    
    if not (new_token.startswith("secret_") or new_token.startswith("ntn_")):
        print("⚠️ 警告: トークンの形式が正しくない可能性があります")
        print("   通常は 'secret_' または 'ntn_' で始まります")
        response = input("続行しますか？ (y/N): ").strip().lower()
        if response != 'y':
            print("キャンセルしました")
            return
    
    print()
    print("=" * 80)
    print("更新前の確認")
    print("=" * 80)
    
    # バックアップ作成
    backup_file = backup_env_file(env_file)
    
    # トークン更新
    print()
    print("トークンを更新中...")
    success = update_token_in_file(env_file, new_token)
    
    if success:
        print()
        print("=" * 80)
        print("✅ 更新完了")
        print("=" * 80)
        print()
        print("次のステップ:")
        print("  1. 診断スクリプトを実行して接続を確認:")
        print("     python diagnose_notion_db_sharing_issue.py")
        print()
        print("  2. アプリケーションを再起動してください")
        print()
        print(f"  3. 問題があればバックアップから復元:")
        print(f"     copy {backup_file} {env_file}")
    else:
        print()
        print("❌ 更新に失敗しました")
        print(f"   バックアップから復元してください: copy {backup_file} {env_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nキャンセルされました")
        sys.exit(0)

