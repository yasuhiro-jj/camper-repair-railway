#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ローカルNotion接続テストスクリプト
"""

import os
import streamlit as st
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

def test_notion_connection():
    """Notion接続をテスト"""
    print("🔍 Notion接続テストを開始...")
    
    # 環境変数の確認
    notion_api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    node_db_id = os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
    case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
    item_db_id = os.getenv("ITEM_DB_ID")
    
    print(f"📋 設定確認:")
    print(f"  - NOTION_API_KEY: {'✅ 設定済み' if notion_api_key else '❌ 未設定'}")
    print(f"  - NODE_DB_ID: {'✅ 設定済み' if node_db_id else '❌ 未設定'}")
    print(f"  - CASE_DB_ID: {'✅ 設定済み' if case_db_id else '❌ 未設定'}")
    print(f"  - ITEM_DB_ID: {'✅ 設定済み' if item_db_id else '❌ 未設定'}")
    
    if not notion_api_key:
        print("❌ Notion APIキーが設定されていません")
        return False
    
    try:
        # notion-clientのインポートテスト
        from notion_client import Client
        print("✅ notion-client: インポート成功")
        
        # クライアント初期化
        client = Client(auth=notion_api_key)
        print("✅ Notionクライアント: 初期化成功")
        
        # データベース接続テスト
        if node_db_id:
            try:
                response = client.databases.query(database_id=node_db_id)
                nodes_count = len(response.get("results", []))
                print(f"✅ 診断フローDB: 接続成功 ({nodes_count}件のノード)")
            except Exception as e:
                print(f"❌ 診断フローDB: 接続失敗 - {e}")
        
        if case_db_id:
            try:
                response = client.databases.query(database_id=case_db_id)
                cases_count = len(response.get("results", []))
                print(f"✅ 修理ケースDB: 接続成功 ({cases_count}件のケース)")
            except Exception as e:
                print(f"❌ 修理ケースDB: 接続失敗 - {e}")
        
        if item_db_id:
            try:
                response = client.databases.query(database_id=item_db_id)
                items_count = len(response.get("results", []))
                print(f"✅ 部品・工具DB: 接続成功 ({items_count}件のアイテム)")
            except Exception as e:
                print(f"❌ 部品・工具DB: 接続失敗 - {e}")
        
        print("🎉 Notion接続テスト完了")
        return True
        
    except ImportError as e:
        print(f"❌ notion-client: インポート失敗 - {e}")
        print("💡 解決方法: pip install notion-client==2.2.1")
        return False
    except Exception as e:
        print(f"❌ Notion接続エラー: {e}")
        return False

def test_streamlit_secrets():
    """Streamlit Secretsのテスト"""
    print("\n🔍 Streamlit Secretsテスト...")
    
    try:
        # Streamlit Secretsの読み込みテスト
        secrets = st.secrets
        print("✅ Streamlit Secrets: 読み込み成功")
        
        # 各設定の確認
        notion_api_key = secrets.get("NOTION_API_KEY")
        node_db_id = secrets.get("NODE_DB_ID")
        case_db_id = secrets.get("CASE_DB_ID")
        item_db_id = secrets.get("ITEM_DB_ID")
        
        print(f"📋 Streamlit Secrets設定:")
        print(f"  - NOTION_API_KEY: {'✅ 設定済み' if notion_api_key else '❌ 未設定'}")
        print(f"  - NODE_DB_ID: {'✅ 設定済み' if node_db_id else '❌ 未設定'}")
        print(f"  - CASE_DB_ID: {'✅ 設定済み' if case_db_id else '❌ 未設定'}")
        print(f"  - ITEM_DB_ID: {'✅ 設定済み' if item_db_id else '❌ 未設定'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit Secrets: 読み込み失敗 - {e}")
        return False

if __name__ == "__main__":
    print("🚀 ローカルNotion接続テスト開始")
    print("=" * 50)
    
    # 環境変数テスト
    test_notion_connection()
    
    # Streamlit Secretsテスト
    test_streamlit_secrets()
    
    print("\n" + "=" * 50)
    print("📝 次のステップ:")
    print("1. .streamlit/secrets.tomlに実際のAPIキーとDB IDを設定")
    print("2. streamlit run enhanced_knowledge_base_app.py でアプリを起動")
    print("3. 「🔧 システム情報」タブで接続状況を確認")
