#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全な.envファイル作成スクリプト
"""

import os

def create_safe_env():
    print("=== 安全な.envファイル作成 ===")
    print()
    print("⚠️ 重要：実際のAPIキーをファイルに記載しないでください")
    print()
    
    # 安全な.envファイルの内容
    env_content = """# 環境変数設定（機密情報）
# このファイルはGitにコミットしないでください

# OpenAI API設定（必須）
OPENAI_API_KEY=your_openai_api_key_here

# SERP検索API設定（オプション）
SERP_API_KEY=your_serp_api_key_here

# LangSmith設定（オプション）
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=your_project_name
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# LangChain Tracing設定
LANGCHAIN_TRACING_V2=true

# Notion API設定（オプション）
NOTION_API_KEY=your_notion_api_key_here
NODE_DB_ID=your_node_database_id_here
CASE_DB_ID=your_case_database_id_here
ITEM_DB_ID=your_item_database_id_here
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ 安全な.envファイルが作成されました")
        print()
        print("次の手順：")
        print("1. .envファイルを開く")
        print("2. 'your_xxx_api_key_here'を実際のAPIキーに置き換える")
        print("3. ファイルを保存")
        print("4. アプリケーションを再起動")
        print()
        print("⚠️ 重要：.envファイルをGitにコミットしないでください")
        print("⚠️ 重要：実際のAPIキーをメモ帳やテキストファイルに保存しないでください")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    create_safe_env()