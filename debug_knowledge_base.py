#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ナレッジベースの詳細デバッグ
"""

import os
import sys
from data_access.notion_client import NotionClient

def debug_knowledge_base():
    """ナレッジベースの詳細デバッグ"""
    print("🔍 ナレッジベースの詳細デバッグ")
    print("=" * 50)
    
    # 環境変数確認
    print("📋 環境変数確認:")
    print(f"NOTION_API_KEY: {'設定済み' if os.getenv('NOTION_API_KEY') else '未設定'}")
    print(f"KNOWLEDGE_BASE_DB_ID: {os.getenv('KNOWLEDGE_BASE_DB_ID', '未設定')}")
    print()
    
    try:
        # Notionクライアント初期化
        print("🔧 Notionクライアント初期化中...")
        notion_client = NotionClient()
        print("✅ Notionクライアント初期化成功")
        
        # ナレッジベースDB IDの確認
        kb_db_id = notion_client._get_database_id("KNOWLEDGE_BASE_DB_ID", "NOTION_KNOWLEDGE_BASE_DB_ID")
        print(f"📊 ナレッジベースDB ID: {kb_db_id}")
        
        if not kb_db_id:
            print("❌ ナレッジベースDB IDが取得できません")
            return
        
        # 直接データベースにアクセス
        print("\n🔍 ナレッジベースDBに直接アクセス中...")
        try:
            response = notion_client.client.databases.query(
                database_id=kb_db_id,
                page_size=10
            )
            
            pages = response.get("results", [])
            print(f"📊 取得したページ数: {len(pages)}")
            
            if not pages:
                print("⚠️ ナレッジベースDBにデータがありません")
                print("💡 Notionデータベースにナレッジを追加してください")
                return
            
            # 各ページの詳細を確認
            print("\n📝 ナレッジベースデータの詳細:")
            for i, page in enumerate(pages[:3]):  # 最初の3件を確認
                print(f"\n--- ページ {i+1} ---")
                properties = page.get("properties", {})
                print(f"プロパティ数: {len(properties)}")
                
                # プロパティ名を表示
                prop_names = list(properties.keys())
                print(f"プロパティ名: {prop_names}")
                
                # タイトルフィールドを探す
                title_found = False
                for prop_name, prop_data in properties.items():
                    if prop_data.get('type') == 'title':
                        title = prop_data.get('title', [{}])[0].get('plain_text', '')
                        if title:
                            print(f"タイトル: {title}")
                            title_found = True
                            break
                
                if not title_found:
                    print("タイトル: 見つかりません")
                
                # 各プロパティの詳細
                for prop_name, prop_data in properties.items():
                    prop_type = prop_data.get('type', 'unknown')
                    print(f"  {prop_name}: {prop_type}")
                    
                    if prop_type == 'rich_text':
                        texts = prop_data.get('rich_text', [])
                        if texts:
                            content = ''.join(t.get('plain_text', '') for t in texts)
                            print(f"    内容: {content[:100]}...")
                    elif prop_type == 'title':
                        title_data = prop_data.get('title', [])
                        if title_data:
                            title_text = title_data[0].get('plain_text', '')
                            print(f"    タイトル: {title_text}")
                    elif prop_type == 'select':
                        select_data = prop_data.get('select', {})
                        if select_data:
                            print(f"    選択値: {select_data.get('name', '')}")
                    elif prop_type == 'multi_select':
                        multi_data = prop_data.get('multi_select', [])
                        if multi_data:
                            values = [item.get('name', '') for item in multi_data]
                            print(f"    複数選択: {values}")
                    elif prop_type == 'url':
                        url_value = prop_data.get('url', '')
                        if url_value:
                            print(f"    URL: {url_value}")
            
            # load_knowledge_base関数をテスト
            print(f"\n🔍 load_knowledge_base関数をテスト中...")
            knowledge_items = notion_client.load_knowledge_base()
            
            if knowledge_items:
                print(f"✅ ナレッジベースデータ取得成功: {len(knowledge_items)}件")
                
                for i, item in enumerate(knowledge_items[:3]):
                    print(f"\n  アイテム {i+1}:")
                    print(f"    タイトル: {item.get('title', 'N/A')}")
                    print(f"    カテゴリ: {item.get('category', 'N/A')}")
                    print(f"    コンテンツ: {item.get('content', 'N/A')[:100]}...")
                    print(f"    キーワード: {item.get('keywords', [])}")
                    print(f"    タグ: {item.get('tags', [])}")
                    print(f"    URL: {item.get('url', 'N/A')}")
            else:
                print("❌ ナレッジベースデータ取得失敗")
                
        except Exception as e:
            print(f"❌ ナレッジベースDBアクセスエラー: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ デバッグエラー: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🔍 ナレッジベースデバッグ完了")

if __name__ == "__main__":
    debug_knowledge_base()