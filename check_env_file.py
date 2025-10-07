#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.envファイルの存在確認と作成
"""

import os

def check_and_create_env():
    print("=== .envファイル確認 ===")
    
    # .envファイルの存在確認
    if os.path.exists('.env'):
        print("✅ .envファイルが存在します")
        print("ファイルの場所:", os.path.abspath('.env'))
        
        # ファイルの内容を表示
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
            print("\nファイルの内容:")
            print(content)
        except Exception as e:
            print(f"ファイルの読み込みエラー: {e}")
    else:
        print("❌ .envファイルが見つかりません")
        print("create_env_file.pyを実行して作成してください")
        print()
        print("実行方法:")
        print("python create_env_file.py")

if __name__ == "__main__":
    check_and_create_env()
