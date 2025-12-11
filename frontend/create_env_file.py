#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.env.localファイルを作成するスクリプト
"""

import os
from pathlib import Path

def create_env_file():
    """環境変数ファイルを作成"""
    # 現在のディレクトリを取得
    current_dir = Path(__file__).parent
    
    # .env.localファイルのパス
    env_file = current_dir / '.env.local'
    
    # ファイルの内容
    content = """# API URL設定
NEXT_PUBLIC_API_URL=https://web-development-8c2f.up.railway.app
"""
    
    # ファイルが既に存在するか確認
    if env_file.exists():
        print(f"⚠️  {env_file} は既に存在します")
        response = input("上書きしますか？ (y/N): ").strip().lower()
        if response != 'y':
            print("キャンセルしました")
            return
    
    # ファイルを作成
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {env_file} を作成しました")
        print("\nファイルの内容:")
        print(content)
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    create_env_file()

