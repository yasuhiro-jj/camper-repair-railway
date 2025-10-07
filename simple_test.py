#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
data_access/モジュールのシンプルテスト
"""

print("🔍 data_access/モジュールのシンプルテスト開始")

# 1. 基本インポートテスト
try:
    import data_access
    print("✅ data_access モジュールインポート成功")
    
    from data_access import NotionClient, KnowledgeBaseManager, DiagnosticDataManager
    print("✅ メインクラスインポート成功")
    
except Exception as e:
    print(f"❌ インポートエラー: {e}")
    exit(1)

# 2. キャッシュマネージャーテスト
try:
    from data_access.cache_manager import CacheManager
    cache_test = CacheManager("test_simple.db")
    
    # 簡単なキャッシュテスト
    cache_test.set("test_key", {"data": "test"}, ttl=60)
    result = cache_test.get("test_key")
    
    if result and result.get("data") == "test":
        print("✅ キャッシュマネージャー動作成功")
    else:
        print("❌ キャッシュマネージャー動作失敗")
    
    # クリーンアップ
    import os
    if os.path.exists("test_simple.db"):
        os.remove("test_simple.db")
        
except Exception as e:
    print(f"❌ キャッシュテストエラー: {e}")

# 3. 知識ベースマネージャーテスト
try:
    kb_manager = KnowledgeBaseManager()
    kb_count = len(kb_manager.knowledge_base)
    print(f"✅ 知識ベースマネージャー作成成功 ({kb_count}カテゴリ)")
    
    if kb_count > 0:
        print("✅ 知識ベースにデータが存在します")
        first_category = list(kb_manager.knowledge_base.keys())[0]
        print(f"📖 最初のカテゴリ: {first_category}")
    else:
        print("⚠️ 知識ベースが空です")
    
except Exception as e:
    print(f"❌ 知識ベーステストエラー: {e}")

# 4. Notionクライアントテスト
try:
    notion_client = NotionClient()
    print("✅ Notionクライアント作成成功")
    
    if notion_client.api_key:
        print(f"✅ Notion APIキー設定済み (最初の10文字: {notion_client.api_key[:10]}...)")
    else:
        print("⚠️ Notion APIキーが設定されていません")
    
except Exception as e:
    print(f"❌ Notionクライアントテストエラー: {e}")

# 5. 診断データマネージャーテスト
try:
    diag_manager = DiagnosticDataManager()
    print("✅ 診断データマネージャー作成成功")
    
    # 基本情報を取得
    diagnostic_data = diag_manager.get_diagnostic_data()
    repair_cases = diag_manager.get_repair_cases()
    
    print(f"📊 診断データ: {'あり' if diagnostic_data else 'なし'}")
    print(f"🔧 修理ケース数: {len(repair_cases)}")
    
except Exception as e:
    print(f"❌ 診断データマネージャーテストエラー: {e}")

print("\n🎉 テスト完了！")
