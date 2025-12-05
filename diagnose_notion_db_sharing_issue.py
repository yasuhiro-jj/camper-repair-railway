#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NotionインテグレーションDB共有問題の診断と解決スクリプト
"""

import os
import sys
import requests
from notion_client import Client
from typing import Dict, Optional, Tuple

# 対象DB情報
TARGET_DB_ID = "1afb2b6e3a5f4d2b94d0edeca5a57824"
PARENT_PAGE_ID = "256e9a7ee5b780078a6ce7c26eab963c"
NOTION_API_VERSION = "2022-06-28"

def get_notion_token() -> Optional[str]:
    """環境変数からNotionトークンを取得"""
    token = (
        os.getenv("NOTION_API_KEY") or 
        os.getenv("NOTION_TOKEN")
    )
    return token

def test_user_info(client: Client) -> Tuple[bool, Dict]:
    """ユーザー情報を取得してワークスペースを確認"""
    try:
        user = client.users.me()
        return True, user
    except Exception as e:
        return False, {"error": str(e)}

def test_database_access(client: Client, db_id: str) -> Tuple[bool, Dict]:
    """データベースへのアクセスをテスト"""
    try:
        # データベース情報を取得
        db_info = client.databases.retrieve(database_id=db_id)
        return True, db_info
    except Exception as e:
        error_str = str(e)
        if "403" in error_str or "object_not_found" in error_str.lower():
            return False, {
                "error": "403 Forbidden",
                "message": "データベースへのアクセス権限がありません",
                "reason": "インテグレーションがこのDBに共有されていません"
            }
        elif "404" in error_str:
            return False, {
                "error": "404 Not Found",
                "message": "データベースが見つかりません",
                "reason": "DB IDが間違っているか、存在しません"
            }
        else:
            return False, {"error": error_str}

def test_database_query(client: Client, db_id: str) -> Tuple[bool, Dict]:
    """データベースのクエリをテスト"""
    try:
        response = client.databases.query(database_id=db_id, page_size=1)
        return True, {
            "total_results": len(response.get("results", [])),
            "has_more": response.get("has_more", False)
        }
    except Exception as e:
        return False, {"error": str(e)}

def check_parent_page_access(client: Client, page_id: str) -> Tuple[bool, Dict]:
    """親ページへのアクセスを確認"""
    try:
        page = client.pages.retrieve(page_id=page_id)
        return True, page
    except Exception as e:
        return False, {"error": str(e)}

def format_db_id(db_id: str) -> str:
    """DB IDをフォーマット（ハイフン削除）"""
    return db_id.replace("-", "")

def main():
    print("=" * 80)
    print("NotionインテグレーションDB共有問題の診断")
    print("=" * 80)
    print()
    
    # トークン取得
    token = get_notion_token()
    if not token:
        print("❌ エラー: NOTION_TOKENまたはNOTION_API_KEYが設定されていません")
        print()
        print("💡 解決方法:")
        print("   環境変数にNOTION_TOKENを設定してください")
        print("   export NOTION_TOKEN=secret_...")
        print("   または")
        print("   set NOTION_TOKEN=secret_...  (Windows)")
        return
    
    print(f"✅ トークン取得成功: {token[:15]}...")
    print()
    
    # クライアント初期化
    try:
        client = Client(auth=token)
    except Exception as e:
        print(f"❌ クライアント初期化エラー: {e}")
        return
    
    # 1. ユーザー情報とワークスペース確認
    print("【ステップ1】ユーザー情報とワークスペース確認")
    print("-" * 80)
    success, user_info = test_user_info(client)
    if success:
        user_name = user_info.get("name", "Unknown")
        user_type = user_info.get("type", "Unknown")
        print(f"✅ 接続成功")
        print(f"   ユーザー名: {user_name}")
        print(f"   タイプ: {user_type}")
        if "bot" in user_info:
            bot_info = user_info.get("bot", {})
            print(f"   ボット名: {bot_info.get('name', 'N/A')}")
    else:
        print(f"❌ 接続失敗: {user_info.get('error', 'Unknown error')}")
        return
    print()
    
    # 2. データベースアクセステスト
    print("【ステップ2】データベースアクセステスト")
    print("-" * 80)
    formatted_db_id = format_db_id(TARGET_DB_ID)
    print(f"対象DB ID: {formatted_db_id}")
    
    success, db_info = test_database_access(client, formatted_db_id)
    if success:
        print("✅ データベースへのアクセス成功")
        title = db_info.get("title", [])
        if title:
            db_title = title[0].get("plain_text", "N/A") if isinstance(title, list) else str(title)
            print(f"   データベース名: {db_title}")
        
        # クエリテスト
        print()
        print("   クエリテスト実行中...")
        query_success, query_result = test_database_query(client, formatted_db_id)
        if query_success:
            print(f"   ✅ クエリ成功: {query_result.get('total_results', 0)}件のレコード")
        else:
            print(f"   ⚠️ クエリエラー: {query_result.get('error', 'Unknown')}")
    else:
        error_type = db_info.get("error", "Unknown")
        error_message = db_info.get("message", "")
        error_reason = db_info.get("reason", "")
        
        print(f"❌ データベースアクセス失敗")
        print(f"   エラー: {error_type}")
        if error_message:
            print(f"   メッセージ: {error_message}")
        if error_reason:
            print(f"   原因: {error_reason}")
        print()
        print("🔧 解決方法:")
        print("   1. Notionでデータベースを開く")
        print("   2. 右上の「共有」ボタンをクリック")
        print("   3. 「Camper Repair System」インテグレーションを検索")
        print("   4. 見つからない場合は:")
        print("      a) 設定 → コネクト → Camper Repair System → 「ページに追加」")
        print("      b) 作業マニュアルDBを指定")
        print("      c) DBをリロード後、共有で「編集」権限を付与")
    print()
    
    # 3. 親ページアクセステスト
    print("【ステップ3】親ページアクセステスト")
    print("-" * 80)
    formatted_parent_id = format_db_id(PARENT_PAGE_ID)
    print(f"親ページID: {formatted_parent_id}")
    
    success, page_info = check_parent_page_access(client, formatted_parent_id)
    if success:
        print("✅ 親ページへのアクセス成功")
        title = page_info.get("properties", {}).get("title", {})
        if title:
            page_title = title.get("title", [{}])[0].get("plain_text", "N/A") if isinstance(title.get("title"), list) else "N/A"
            print(f"   ページ名: {page_title}")
    else:
        print(f"⚠️ 親ページへのアクセス失敗: {page_info.get('error', 'Unknown')}")
        print("   （親ページへのアクセスは必須ではありません）")
    print()
    
    # 4. 推奨アクション
    print("=" * 80)
    print("【推奨アクション】")
    print("=" * 80)
    
    # DBアクセスが成功しているか確認
    success, _ = test_database_access(client, formatted_db_id)
    if success:
        print("✅ データベースへのアクセスは正常です！")
        print("   問題は解決済みです。")
    else:
        print("❌ データベースへのアクセスができていません")
        print()
        print("【解決手順】")
        print()
        print("方法A: 設定画面から直接追加（推奨）")
        print("  1. Notionで「設定とメンバー」→「コネクト」を開く")
        print("  2. 「Camper Repair System」を探す")
        print("  3. 「…」メニュー → 「ページに追加」")
        print("  4. 作業マニュアルDBを選択")
        print("  5. DBをリロード後、「共有」から「編集」権限を付与")
        print()
        print("方法B: 新規インテグレーション作成（確実）")
        print("  1. Notionで新しいInternal Integrationを作成")
        print("  2. 新トークンを発行")
        print("  3. 設定 → コネクト → 新インテグレーション → 「ページに追加」")
        print("  4. 作業マニュアルDBを指定")
        print("  5. .envのNOTION_TOKENを新トークンに更新")
        print()
        print("方法C: 親ページ経由で共有")
        print("  1. 親ページ（キャンピングカーのチャットボット要素）を開く")
        print("  2. 「共有」から「Camper Repair System」を追加")
        print("  3. 子DBに権限が継承されるか確認")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

