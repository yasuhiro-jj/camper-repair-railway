#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notionクライアントの修正内容をテストするスクリプト
"""

import os
import sys
from data_access.notion_client import NotionClient

def test_notion_client():
    """Notionクライアントの基本機能をテスト"""
    print("=== Notionクライアント修正内容テスト ===")
    
    # クライアントの初期化
    client = NotionClient()
    
    # 1. 接続テスト
    print("\n1. 接続テスト...")
    success, message = client.test_connection()
    print(f"結果: {message}")
    
    if not success:
        print("⚠️ 接続に失敗しました。APIキーとデータベースIDを確認してください。")
        return False
    
    # 1.5. データベースクエリテスト
    print("\n1.5. データベースクエリテスト...")
    try:
        # 診断フローDBのクエリテスト
        node_db_id = client._get_database_id("NODE_DB_ID", "NOTION_DIAGNOSTIC_DB_ID")
        if node_db_id:
            response = client.client.databases.query(database_id=node_db_id)
            nodes_count = len(response.get("results", []))
            print(f"✅ 診断フローDB: {nodes_count}件のノード")
        
        # 修理ケースDBのクエリテスト
        case_db_id = client._get_database_id("CASE_DB_ID", "NOTION_REPAIR_CASE_DB_ID")
        if case_db_id:
            response = client.client.databases.query(database_id=case_db_id)
            cases_count = len(response.get("results", []))
            print(f"✅ 修理ケースDB: {cases_count}件のケース")
        
        # 部品・工具DBのクエリテスト
        item_db_id = client._get_database_id("ITEM_DB_ID")
        if item_db_id:
            response = client.client.databases.query(database_id=item_db_id)
            items_count = len(response.get("results", []))
            print(f"✅ 部品・工具DB: {items_count}件のアイテム")
            
    except Exception as e:
        print(f"❌ データベースクエリテストエラー: {e}")
        return False
    
    # 2. 診断データの読み込みテスト
    print("\n2. 診断データ読み込みテスト...")
    try:
        diagnostic_data = client.load_diagnostic_data()
        if diagnostic_data:
            nodes_count = len(diagnostic_data.get("nodes", []))
            start_nodes_count = len(diagnostic_data.get("start_nodes", []))
            print(f"✅ 診断ノード: {nodes_count}件")
            print(f"✅ 開始ノード: {start_nodes_count}件")
        else:
            print("⚠️ 診断データが取得できませんでした")
    except Exception as e:
        print(f"❌ 診断データ読み込みエラー: {e}")
    
    # 3. 修理ケースデータの読み込みテスト
    print("\n3. 修理ケースデータ読み込みテスト...")
    try:
        repair_cases = client.load_repair_cases()
        if repair_cases:
            print(f"✅ 修理ケース: {len(repair_cases)}件")
        else:
            print("⚠️ 修理ケースデータが取得できませんでした")
    except Exception as e:
        print(f"❌ 修理ケースデータ読み込みエラー: {e}")
    
    # 4. 検索機能テスト（text型フィールド対応）
    print("\n4. 検索機能テスト...")
    test_queries = ["バッテリー", "エアコン", "水漏れ"]
    
    for query in test_queries:
        try:
            results = client.search_database(query)
            print(f"検索クエリ '{query}': {len(results)}件の結果")
            for result in results[:3]:  # 最初の3件のみ表示
                print(f"  - {result.get('type', 'Unknown')}: {result.get('title', 'No title')}")
        except Exception as e:
            print(f"❌ 検索エラー ({query}): {e}")
    
    # 5. カテゴリ別検索テスト（text型フィールド対応）
    print("\n5. カテゴリ別検索テスト...")
    test_categories = ["インバーター", "FFヒーター", "バッテリー", "エアコン"]
    
    for category in test_categories:
        try:
            items = client.get_items_by_category(category)
            print(f"カテゴリ '{category}': {len(items)}件のアイテム")
            # 最初の2件の詳細を表示
            for item in items[:2]:
                print(f"  - {item.get('name', 'No name')} (価格: {item.get('price', 'N/A')})")
        except Exception as e:
            print(f"❌ カテゴリ検索エラー ({category}): {e}")
    
    print("\n=== テスト完了 ===")
    return True

if __name__ == "__main__":
    test_notion_client()

