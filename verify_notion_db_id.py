#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotionデータベースIDを検証し、アクセス権限を確認するスクリプト
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_LOG_DB_ID = os.getenv("NOTION_LOG_DB_ID")
NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2022-06-28")

def extract_db_id_from_url(url: str) -> str:
    """URLからデータベースIDを抽出"""
    # URLからIDを抽出
    # 例: https://www.notion.so/workspace/029bdc77fc23411390d3de6595b07dfe?v=...
    parts = url.split('/')
    for part in parts:
        if len(part) == 32 and part.replace('-', '').isalnum():
            # ハイフンを削除
            db_id = part.replace('-', '')
            if len(db_id) == 32:
                return db_id
    
    # URLパラメータ内を確認
    if '?' in url:
        query_part = url.split('?')[0]
        parts = query_part.split('/')
        for part in parts:
            if len(part) == 32 and part.replace('-', '').isalnum():
                db_id = part.replace('-', '')
                if len(db_id) == 32:
                    return db_id
    
    return None

def verify_db_id(db_id: str) -> bool:
    """データベースIDの形式を検証"""
    if not db_id:
        return False
    
    # ハイフンを削除
    clean_id = db_id.replace('-', '')
    
    # 32文字の英数字か確認
    if len(clean_id) != 32:
        return False
    
    if not clean_id.isalnum():
        return False
    
    return True

def check_db_access(db_id: str):
    """データベースへのアクセスを確認"""
    if not NOTION_API_KEY:
        print("❌ NOTION_API_KEYが設定されていません")
        return False
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }
    
    try:
        url = f"https://api.notion.com/v1/databases/{db_id}"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            title = data.get('title', [{}])[0].get('plain_text', 'N/A')
            print(f"✅ データベースへのアクセス成功!")
            print(f"   データベース名: {title}")
            return True
        elif resp.status_code == 401:
            print("❌ 認証エラー (401): APIキーが無効です")
            return False
        elif resp.status_code == 403:
            print("❌ アクセス権限エラー (403)")
            print("   → インテグレーションにデータベースへのアクセス権限がありません")
            print("   → Notionデータベースの「Share」からインテグレーションを招待してください")
            return False
        elif resp.status_code == 404:
            print("❌ データベースが見つかりません (404)")
            print("   → データベースIDが間違っているか、存在しません")
            return False
        else:
            print(f"❌ エラー: {resp.status_code}")
            print(f"   レスポンス: {resp.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ リクエストエラー: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 NotionデータベースID検証ツール")
    print("=" * 60)
    
    # 現在の設定を確認
    print(f"\n📋 現在の設定:")
    print(f"   NOTION_API_KEY: {'設定済み' if NOTION_API_KEY else '❌ 未設定'}")
    print(f"   NOTION_LOG_DB_ID: {NOTION_LOG_DB_ID or '❌ 未設定'}")
    
    if not NOTION_LOG_DB_ID:
        print("\n❌ NOTION_LOG_DB_IDが設定されていません")
        print("\n💡 設定方法:")
        print("   1. Notionでデータベースを開く")
        print("   2. URLからIDを確認（32文字の英数字）")
        print("   3. .envファイルに NOTION_LOG_DB_ID=... を追加")
        return
    
    # IDの形式を検証
    print(f"\n🔍 データベースIDの形式を検証中...")
    if not verify_db_id(NOTION_LOG_DB_ID):
        print(f"❌ データベースIDの形式が正しくありません")
        print(f"   現在のID: {NOTION_LOG_DB_ID}")
        print(f"   期待される形式: 32文字の英数字（ハイフンなし）")
        
        # ハイフンが含まれているか確認
        if '-' in NOTION_LOG_DB_ID:
            clean_id = NOTION_LOG_DB_ID.replace('-', '')
            if len(clean_id) == 32:
                print(f"\n💡 ハイフンを削除したID: {clean_id}")
                print("   → .envファイルを更新して再度試してください")
        return
    
    print(f"✅ データベースIDの形式は正しいです")
    
    # アクセス確認
    print(f"\n🔍 データベースへのアクセスを確認中...")
    if check_db_access(NOTION_LOG_DB_ID):
        print("\n✅ 全ての確認が完了しました!")
        print("   → データベースIDは正しく、アクセス権限もあります")
    else:
        print("\n⚠️ 問題が見つかりました")
        print("   → 上記のエラーメッセージを確認してください")
    
    print("\n" + "=" * 60)
    print("💡 URLからIDを抽出する場合")
    print("=" * 60)
    print("NotionのURLを入力してください（Enterでスキップ）:")
    url = input("> ").strip()
    
    if url:
        extracted_id = extract_db_id_from_url(url)
        if extracted_id:
            print(f"\n✅ 抽出されたID: {extracted_id}")
            if verify_db_id(extracted_id):
                print("   → このIDを .envファイルの NOTION_LOG_DB_ID に設定してください")
                if check_db_access(extracted_id):
                    print("\n✅ このIDでアクセス可能です!")
        else:
            print("\n❌ URLからIDを抽出できませんでした")
            print("   → URLの形式を確認してください")

if __name__ == "__main__":
    main()

