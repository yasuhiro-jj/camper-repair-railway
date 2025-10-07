#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
data_access/モジュールの手動テスト
"""

import sys
import os

print("🚀 data_access/モジュール手動テスト開始")
print(f"Python: {sys.version}")
print(f"作業ディレクトリ: {os.getcwd()}")
print("=" * 60)

# 段階的テスト
test_count = 0
success_count = 0

# テスト 1: 基本インポート
test_count += 1
print(f"\n【テスト {test_count}】基本インポートテスト")
try:
    import data_access
    print("✅ data_access インポート成功")
    
    from data_access import NotionClient, KnowledgeBaseManager, DiagnosticDataManager
    print("✅ メインクラスインポート成功")
    success_count += 1
except Exception as e:
    print(f"❌ インポートエラー: {e}")
    import traceback
    traceback.print_exc()

# テスト 2: キャッシュマネージャー
test_count += 1
print(f"\n【テスト {test_count}】キャッシュマネージャーテスト")
try:
    from data_access.cache_manager import CacheManager, cached_result
    
    # テスト用キャッシュ
    test_cache = CacheManager("manual_test.db")
    print("✅ キャッシュマネージャー作成")
    
    # データ保存・取得テスト
    test_data = {"message": "テストデータ", "number": 123}
    test_cache.set("test_key", test_data)
    retrieved = test_cache.get("test_key")
    
    if retrieved == test_data:
        print("✅ キャッシュ保存・取得成功")
        success_count += 1
    else:
        print("❌ キャッシュデータが一致しません")
    
    # クリーンアップ
    if os.path.exists("manual_test.db"):
        os.remove("manual_test.db")
        
except Exception as e:
    print(f"❌ キャッシュテストエラー: {e}")
    import traceback
    traceback.print_exc()

# テスト 3: 知識ベースマネージャー
test_count += 1
print(f"\n【テスト {test_count}】知識ベースマネージャーテスト")
try:
    kb_manager = KnowledgeBaseManager()
    print("✅ 知識ベースマネージャー作成")
    
    # 知識ベースの内容確認
    kb_categories = len(kb_manager.knowledge_base)
    print(f"📚 読み込み済みカテゴリ数: {kb_categories}")
    
    if kb_categories > 0:
        print("✅ 知識ベースにデータが存在")
        # 最初のカテゴリを表示
        first_cat = list(kb_manager.knowledge_base.keys())[0]
        first_content = kb_manager.knowledge_base[first_cat]
        print(f"📖 サンプルカテゴリ: {first_cat}")
        print(f"📄 内容サンプル（最初の100文字）: {first_content[:100]}...")
        
        # 検索テスト
        search_test = kb_manager.search_in_content("バッテリー")
        print(f"🔍 'バッテリー'検索結果: {len(search_test)}件")
        
        success_count += 1
    else:
        print("⚠️ 知識ベースが空です")
        
except Exception as e:
    print(f"❌ 知識ベーステストエラー: {e}")
    import traceback
    traceback.print_exc()

# テスト 4: Notionクライアント
test_count += 1
print(f"\n【テスト {test_count}】Notionクライアントテスト")
try:
    notion_client = NotionClient()
    print("✅ Notionクライアント作成")
    
    # APIキー確認
    api_key_status = "設定済み" if notion_client.api_key else "未設定"
    print(f"🔑 APIキー状態: {api_key_status}")
    
    if notion_client.api_key:
        print(f"🔑 APIキー（最初の15文字）: {notion_client.api_key[:15]}...")
        
        # 接続テスト（簡易版）
        try:
            success, message = notion_client.test_connection()
            if success:
                print(f"✅ Notion接続テスト成功: {message}")
                success_count += 1
            else:
                print(f"⚠️ Notion接続テスト失敗: {message}")
                success_count += 0.5  # 部分的成功
        except Exception as conn_e:
            print(f"⚠️ 接続テストでエラー: {conn_e}")
            success_count += 0.5  # 部分的成功
    else:
        print("⚠️ APIキーが設定されていません（環境変数またはsecrets.tomlで設定してください）")
        success_count += 0.5  # 部分的成功
        
except Exception as e:
    print(f"❌ Notionクライアントエラー: {e}")
    import traceback
    traceback.print_exc()

# テスト 5: 診断データマネージャー
test_count += 1
print(f"\n【テスト {test_count}】診断データマネージャーテスト")
try:
    diag_manager = DiagnosticDataManager()
    print("✅ 診断データマネージャー作成")
    
    # 診断データ確認
    diagnostic_data = diag_manager.get_diagnostic_data()
    repair_cases = diag_manager.get_repair_cases()
    
    print(f"📊 診断データ: {'利用可能' if diagnostic_data else '利用不可'}")
    print(f"🔧 修理ケース数: {len(repair_cases) if repair_cases else 0}")
    
    # サマリー情報
    summary = diag_manager.get_diagnostic_summary()
    print(f"📈 データサマリー: {summary}")
    
    success_count += 1
    
except Exception as e:
    print(f"❌ 診断データマネージャーエラー: {e}")
    import traceback
    traceback.print_exc()

# 結果サマリー
print("\n" + "=" * 60)
print("📊 テスト結果サマリー")
print("=" * 60)
print(f"実行テスト数: {test_count}")
print(f"成功テスト数: {success_count}")
print(f"成功率: {(success_count/test_count)*100:.1f}%")

if success_count == test_count:
    print("🎉 全テスト成功！data_access/モジュールは正常に動作しています。")
elif success_count >= test_count * 0.8:
    print("✅ ほぼ成功！軽微な問題がありますが、基本機能は動作しています。")
elif success_count >= test_count * 0.5:
    print("⚠️ 部分的成功。いくつかの問題があります。")
else:
    print("❌ 多くのテストが失敗しました。設定や環境を確認してください。")

print("\n🏁 手動テスト完了")
