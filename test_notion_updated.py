#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
Notionデータベース構造確認スクリプト（更新版） 
 
import os 
from dotenv import load_dotenv 
 
# .envファイルの読み込み 
load_dotenv() 
 
def check_notion_databases(): 
    """Notionデータベースの構造とIDを確認""" 
    print("?? Notionデータベース構造確認を開始...") 
 
    # 環境変数の確認 
    notion_api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN") 
    if not notion_api_key: 
        print("? Notion APIキーが設定されていません") 
        return 
 
    try: 
        from notion_client import Client 
        client = Client(auth=notion_api_key) 
 
        # ユーザー情報を取得 
        user = client.users.me() 
        print(f"? Notion接続成功: {user.get('name', 'Unknown User')}") 
 
        # 環境変数からデータベースIDを取得 
        node_db_id = os.getenv("NODE_DB_ID") 
        case_db_id = os.getenv("CASE_DB_ID") 
        item_db_id = os.getenv("ITEM_DB_ID") 
 
        print("?? 環境変数から取得したデータベースIDのテスト:") 
 
        # 診断フローDB 
        if node_db_id: 
            try: 
                response = client.databases.retrieve(database_id=node_db_id) 
                title = "タイトルなし" 
                title_prop = response.get("title", []) 
                if title_prop: 
                    title = title_prop[0].get("plain_text", "タイトルなし") 
                print(f"? 診断フローDB ({node_db_id}): {title}") 
            except Exception as e: 
                print(f"? 診断フローDB ({node_db_id}): アクセス不可 - {e}") 
 
        # 修理ケースDB 
        if case_db_id: 
            try: 
                response = client.databases.retrieve(database_id=case_db_id) 
                title = "タイトルなし" 
                title_prop = response.get("title", []) 
                if title_prop: 
                    title = title_prop[0].get("plain_text", "タイトルなし") 
                print(f"? 修理ケースDB ({case_db_id}): {title}") 
            except Exception as e: 
                print(f"? 修理ケースDB ({case_db_id}): アクセス不可 - {e}") 
 
        # 部品・工具DB 
        if item_db_id: 
            try: 
                response = client.databases.retrieve(database_id=item_db_id) 
                title = "タイトルなし" 
                title_prop = response.get("title", []) 
                if title_prop: 
                    title = title_prop[0].get("plain_text", "タイトルなし") 
                print(f"? 部品・工具DB ({item_db_id}): {title}") 
            except Exception as e: 
                print(f"? 部品・工具DB ({item_db_id}): アクセス不可 - {e}") 
 
    except ImportError as e: 
        print(f"? notion-clientライブラリがインストールされていません: {e}") 
        print("?? 解決方法: pip install notion-client==2.2.1") 
    except Exception as e: 
        print(f"? Notion接続エラー: {e}") 
 
if __name__ == "__main__": 
    check_notion_databases() 
