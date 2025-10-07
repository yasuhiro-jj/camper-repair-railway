#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全な.envファイル作成スクリプト
"""

import os

def create_env_file():
    print("=== 安全な.envファイル作成 ===")
    print()
    print("このスクリプトは、APIキーを安全に設定するための.envファイルを作成します。")
    print()
    
    # .envファイルの内容
    env_content = """# 環境変数設定（機密情報）
# このファイルはGitにコミットしないでください

# OpenAI API設定（必須）
OPENAI_API_KEY=your_openai_api_key_here

# SERP検索API設定（オプション）
SERP_API_KEY=your_serp_api_key_here

# Notion API設定（オプション）
NOTION_API_KEY=your_notion_api_key_here

# LangSmith設定（オプション）
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=your_project_name
"""
    
    # .envファイルを作成
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .envファイルが作成されました")
        print()
        print("次の手順：")
        print("1. .envファイルを開く")
        print("2. 'your_openai_api_key_here'を実際のAPIキーに置き換える")
        print("3. ファイルを保存")
        print("4. アプリケーションを再起動")
        print()
        print("⚠️ 重要：.envファイルをGitにコミットしないでください")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    create_env_file()
