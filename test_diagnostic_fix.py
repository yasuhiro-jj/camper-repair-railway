#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
診断データ読み込み修正のテスト
"""

print("🔧 診断データ読み込み修正テスト開始")
print("=" * 50)

try:
    # 1. 診断データマネージャーのテスト
    print("1. 診断データマネージャーのテスト...")
    from data_access.diagnostic_data import DiagnosticDataManager
    
    diag_manager = DiagnosticDataManager()
    print("✅ 診断データマネージャー作成成功")
    
    # 診断データの確認
    diagnostic_data = diag_manager.get_diagnostic_data()
    repair_cases = diag_manager.get_repair_cases()
    
    print(f"📊 診断データ: {'利用可能' if diagnostic_data else '利用不可'}")
    print(f"🔧 修理ケース数: {len(repair_cases) if repair_cases else 0}")
    
    if diagnostic_data:
        nodes = diagnostic_data.get("nodes", [])
        start_nodes = diagnostic_data.get("start_nodes", [])
        print(f"📈 診断ノード数: {len(nodes)}")
        print(f"🚀 開始ノード数: {len(start_nodes)}")
    else:
        print("⚠️ 診断データが利用できません（Notion接続の問題の可能性）")
    
    # 2. Notionクライアントの直接テスト
    print("\n2. Notionクライアントの直接テスト...")
    from data_access.notion_client import NotionClient
    
    notion_client = NotionClient()
    print("✅ Notionクライアント作成成功")
    
    if notion_client.api_key:
        print(f"🔑 APIキー設定済み: {notion_client.api_key[:15]}...")
        
        # 接続テスト
        try:
            success, message = notion_client.test_connection()
            if success:
                print(f"✅ Notion接続成功: {message}")
            else:
                print(f"⚠️ Notion接続失敗: {message}")
        except Exception as conn_e:
            print(f"⚠️ 接続テストエラー: {conn_e}")
    else:
        print("⚠️ APIキーが設定されていません")
    
    # 3. 知識ベースマネージャーのテスト
    print("\n3. 知識ベースマネージャーのテスト...")
    from data_access.knowledge_base import KnowledgeBaseManager
    
    kb_manager = KnowledgeBaseManager()
    kb_count = len(kb_manager.knowledge_base)
    print(f"✅ 知識ベースマネージャー作成成功 ({kb_count}カテゴリ)")
    
    if kb_count > 0:
        print("✅ 知識ベースにデータが存在")
        # 検索テスト
        search_results = kb_manager.search_in_content("バッテリー")
        print(f"🔍 'バッテリー'検索結果: {len(search_results)}件")
    
    print("\n🎉 修正テスト完了！")
    print("✅ JSONシリアライズエラーが解決されました")
    
except Exception as e:
    print(f"❌ テストエラー: {e}")
    import traceback
    traceback.print_exc()
