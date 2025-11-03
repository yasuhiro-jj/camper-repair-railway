#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notionデータベースを検索して見つけるスクリプト
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2022-06-28")

def search_databases():
    """利用可能なデータベースを検索"""
    if not NOTION_API_KEY:
        print("❌ NOTION_API_KEYが設定されていません")
        return
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }
    
    print("=" * 60)
    print("🔍 Notionデータベース検索")
    print("=" * 60)
    
    # 検索APIを使用してデータベースを検索
    try:
        search_url = "https://api.notion.com/v1/search"
        
        # データベースタイプのみを検索
        search_data = {
            "filter": {
                "value": "database",
                "property": "object"
            },
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time"
            }
        }
        
        print("\n📡 データベースを検索中...")
        resp = requests.post(search_url, headers=headers, json=search_data, timeout=10)
        
        print(f"   ステータスコード: {resp.status_code}")
        
        if resp.status_code == 200:
            results = resp.json()
            databases = results.get("results", [])
            
            print(f"\n✅ {len(databases)}個のデータベースが見つかりました")
            print("=" * 60)
            
            chat_logs_db = None
            
            for i, db in enumerate(databases, 1):
                title = "N/A"
                if db.get("title"):
                    title_parts = db["title"]
                    if isinstance(title_parts, list) and len(title_parts) > 0:
                        title = title_parts[0].get("plain_text", "N/A")
                    elif isinstance(title_parts, str):
                        title = title_parts
                
                db_id = db.get("id", "").replace("-", "")
                
                print(f"\n{i}. {title}")
                print(f"   ID: {db_id}")
                print(f"   作成日: {db.get('created_time', 'N/A')}")
                print(f"   更新日: {db.get('last_edited_time', 'N/A')}")
                
                # "Chat Logs"を含むデータベースを探す
                if "chat" in title.lower() or "log" in title.lower():
                    chat_logs_db = db
                    print(f"   ⭐ これがChat Logs DBかもしれません!")
            
            if chat_logs_db:
                db_id = chat_logs_db["id"].replace("-", "")
                title = "N/A"
                if chat_logs_db.get("title"):
                    title_parts = chat_logs_db["title"]
                    if isinstance(title_parts, list) and len(title_parts) > 0:
                        title = title_parts[0].get("plain_text", "N/A")
                
                print("\n" + "=" * 60)
                print("💡 見つかったChat Logs DB")
                print("=" * 60)
                print(f"   データベース名: {title}")
                print(f"   データベースID: {db_id}")
                print(f"\n   → .envファイルの NOTION_LOG_DB_ID を以下に更新してください:")
                print(f"   NOTION_LOG_DB_ID={db_id}")
                
                # 実際にアクセスできるか確認
                print(f"\n🔍 このIDでアクセスをテスト中...")
                test_url = f"https://api.notion.com/v1/databases/{db_id}"
                test_resp = requests.get(test_url, headers=headers, timeout=10)
                
                if test_resp.status_code == 200:
                    print(f"   ✅ アクセス成功!")
                    test_data = test_resp.json()
                    properties = test_data.get("properties", {})
                    print(f"   プロパティ数: {len(properties)}")
                    print(f"   プロパティ: {list(properties.keys())[:5]}...")
                elif test_resp.status_code == 403:
                    print(f"   ⚠️ アクセス権限エラー (403)")
                    print(f"   → インテグレーションに権限がありません")
                    print(f"   → データベースの「Share」からインテグレーションを招待してください")
                else:
                    print(f"   ❌ エラー: {test_resp.status_code}")
                    print(f"   レスポンス: {test_resp.text[:200]}")
            else:
                print("\n" + "=" * 60)
                print("⚠️ Chat Logs DBが見つかりませんでした")
                print("=" * 60)
                print("上記のリストから正しいデータベースを探してください")
                print("または、NotionでデータベースのURLを直接確認してください")
                
        elif resp.status_code == 401:
            print("\n❌ 認証エラー (401)")
            print("   → APIキーが無効です")
        elif resp.status_code == 403:
            print("\n❌ アクセス権限エラー (403)")
            print("   → APIキーに検索権限がありません")
        else:
            print(f"\n❌ エラー: {resp.status_code}")
            print(f"   レスポンス: {resp.text[:500]}")
            
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def check_user_info():
    """ユーザー情報を確認してAPIキーが有効か確認"""
    if not NOTION_API_KEY:
        print("❌ NOTION_API_KEYが設定されていません")
        return False
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_API_VERSION,
    }
    
    try:
        print("\n🔍 APIキーの有効性を確認中...")
        resp = requests.get("https://api.notion.com/v1/users/me", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            user_data = resp.json()
            print(f"   ✅ APIキーは有効です")
            print(f"   ユーザー: {user_data.get('name', 'N/A')}")
            return True
        else:
            print(f"   ❌ APIキーが無効です: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return False

if __name__ == "__main__":
    if check_user_info():
        search_databases()
    else:
        print("\n⚠️ APIキーが無効なため、検索をスキップします")

