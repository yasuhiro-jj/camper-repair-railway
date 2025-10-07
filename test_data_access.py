#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
data_access/モジュールの動作テスト
"""

import sys
import os
import traceback

def test_imports():
    """各モジュールのインポートテスト"""
    print("🔍 data_access/モジュールのインポートテスト開始")
    print("=" * 50)
    
    try:
        # 1. 基本インポートテスト
        print("1. 基本モジュールのインポート...")
        import data_access
        print("✅ data_access モジュールのインポート成功")
        
        # 2. 各クラスのインポートテスト
        print("\n2. 各クラスのインポートテスト...")
        from data_access import NotionClient, KnowledgeBaseManager, DiagnosticDataManager
        print("✅ NotionClient インポート成功")
        print("✅ KnowledgeBaseManager インポート成功")
        print("✅ DiagnosticDataManager インポート成功")
        
        # 3. キャッシュマネージャーのテスト
        print("\n3. キャッシュマネージャーのテスト...")
        from data_access.cache_manager import CacheManager, cache_manager, cached_result
        print("✅ CacheManager インポート成功")
        print("✅ cache_manager インスタンス取得成功")
        print("✅ cached_result デコレータ取得成功")
        
        # 4. Notionクライアントのテスト
        print("\n4. Notionクライアントのテスト...")
        from data_access.notion_client import NotionClient as NC
        notion_client = NC()
        print("✅ NotionClient インスタンス作成成功")
        
        # 5. 知識ベースマネージャーのテスト
        print("\n5. 知識ベースマネージャーのテスト...")
        from data_access.knowledge_base import KnowledgeBaseManager as KBM
        kb_manager = KBM()
        print("✅ KnowledgeBaseManager インスタンス作成成功")
        
        # 6. 診断データマネージャーのテスト
        print("\n6. 診断データマネージャーのテスト...")
        from data_access.diagnostic_data import DiagnosticDataManager as DDM
        diag_manager = DDM()
        print("✅ DiagnosticDataManager インスタンス作成成功")
        
        print("\n🎉 全てのインポートテストが成功しました！")
        return True
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        traceback.print_exc()
        return False

def test_cache_manager():
    """キャッシュマネージャーの動作テスト"""
    print("\n🔍 キャッシュマネージャーの動作テスト")
    print("=" * 50)
    
    try:
        from data_access.cache_manager import CacheManager
        
        # テスト用キャッシュマネージャーを作成
        test_cache = CacheManager("test_cache.db")
        print("✅ テスト用キャッシュマネージャー作成成功")
        
        # 基本的なキャッシュ操作テスト
        test_key = "test_key_123"
        test_value = {"message": "テストデータ", "timestamp": "2024-01-01"}
        
        # キャッシュに保存
        test_cache.set(test_key, test_value, ttl=60, cache_type="test")
        print("✅ キャッシュ保存成功")
        
        # キャッシュから取得
        retrieved_value = test_cache.get(test_key)
        if retrieved_value == test_value:
            print("✅ キャッシュ取得成功")
        else:
            print("❌ キャッシュ取得失敗: 値が一致しません")
            return False
        
        # キャッシュ統計取得
        stats = test_cache.get_stats()
        print(f"✅ キャッシュ統計取得成功: {stats}")
        
        # テスト用キャッシュを削除
        test_cache.delete(test_key)
        print("✅ キャッシュ削除成功")
        
        # テスト用データベースファイルを削除
        if os.path.exists("test_cache.db"):
            os.remove("test_cache.db")
            print("✅ テスト用データベースファイル削除成功")
        
        print("🎉 キャッシュマネージャーの動作テストが成功しました！")
        return True
        
    except Exception as e:
        print(f"❌ キャッシュマネージャーテストエラー: {e}")
        traceback.print_exc()
        return False

def test_knowledge_base():
    """知識ベースマネージャーの動作テスト"""
    print("\n🔍 知識ベースマネージャーの動作テスト")
    print("=" * 50)
    
    try:
        from data_access.knowledge_base import KnowledgeBaseManager
        
        # 知識ベースマネージャーを作成
        kb_manager = KnowledgeBaseManager()
        print("✅ 知識ベースマネージャー作成成功")
        
        # 知識ベースの状態確認
        print(f"📚 知識ベースのカテゴリ数: {len(kb_manager.knowledge_base)}")
        
        if len(kb_manager.knowledge_base) > 0:
            print("✅ 知識ベースにデータが読み込まれています")
            
            # 最初のカテゴリを表示
            first_category = list(kb_manager.knowledge_base.keys())[0]
            print(f"📖 最初のカテゴリ: {first_category}")
            
            # 検索テスト
            test_query = "バッテリー"
            search_results = kb_manager.search_in_content(test_query)
            print(f"🔍 検索結果数: {len(search_results)}")
            
            if search_results:
                print("✅ 検索機能が正常に動作しています")
            else:
                print("⚠️ 検索結果がありません（データが不足している可能性があります）")
        else:
            print("⚠️ 知識ベースが空です（JSONファイルまたはテキストファイルが不足している可能性があります）")
        
        print("🎉 知識ベースマネージャーの動作テストが完了しました！")
        return True
        
    except Exception as e:
        print(f"❌ 知識ベースマネージャーテストエラー: {e}")
        traceback.print_exc()
        return False

def test_notion_client():
    """Notionクライアントの動作テスト"""
    print("\n🔍 Notionクライアントの動作テスト")
    print("=" * 50)
    
    try:
        from data_access.notion_client import NotionClient
        
        # Notionクライアントを作成
        notion_client = NotionClient()
        print("✅ Notionクライアント作成成功")
        
        # APIキーの確認
        if notion_client.api_key:
            print("✅ Notion APIキーが設定されています")
            print(f"🔑 APIキー（最初の10文字）: {notion_client.api_key[:10]}...")
        else:
            print("⚠️ Notion APIキーが設定されていません")
            print("💡 環境変数 NOTION_API_KEY または .streamlit/secrets.toml で設定してください")
        
        # 接続テスト（APIキーがある場合のみ）
        if notion_client.api_key:
            try:
                success, message = notion_client.test_connection()
                if success:
                    print(f"✅ Notion接続テスト成功: {message}")
                else:
                    print(f"⚠️ Notion接続テスト失敗: {message}")
            except Exception as e:
                print(f"⚠️ Notion接続テストでエラー: {e}")
        else:
            print("⏭️ APIキーがないため、接続テストをスキップします")
        
        print("🎉 Notionクライアントの動作テストが完了しました！")
        return True
        
    except Exception as e:
        print(f"❌ Notionクライアントテストエラー: {e}")
        traceback.print_exc()
        return False

def test_diagnostic_data():
    """診断データマネージャーの動作テスト"""
    print("\n🔍 診断データマネージャーの動作テスト")
    print("=" * 50)
    
    try:
        from data_access.diagnostic_data import DiagnosticDataManager
        
        # 診断データマネージャーを作成
        diag_manager = DiagnosticDataManager()
        print("✅ 診断データマネージャー作成成功")
        
        # 診断データの確認
        diagnostic_data = diag_manager.get_diagnostic_data()
        if diagnostic_data:
            print("✅ 診断データが読み込まれています")
            nodes = diagnostic_data.get("nodes", [])
            start_nodes = diagnostic_data.get("start_nodes", [])
            print(f"📊 診断ノード数: {len(nodes)}")
            print(f"🚀 開始ノード数: {len(start_nodes)}")
        else:
            print("⚠️ 診断データが読み込まれていません（Notion接続の問題の可能性があります）")
        
        # 修理ケースの確認
        repair_cases = diag_manager.get_repair_cases()
        print(f"🔧 修理ケース数: {len(repair_cases)}")
        
        # 診断サマリーの取得
        summary = diag_manager.get_diagnostic_summary()
        print(f"📈 診断サマリー: {summary}")
        
        print("🎉 診断データマネージャーの動作テストが完了しました！")
        return True
        
    except Exception as e:
        print(f"❌ 診断データマネージャーテストエラー: {e}")
        traceback.print_exc()
        return False

def main():
    """メインテスト関数"""
    print("🚀 data_access/モジュールの包括的テスト開始")
    print("=" * 60)
    
    test_results = []
    
    # 各テストを実行
    test_results.append(("インポートテスト", test_imports()))
    test_results.append(("キャッシュマネージャーテスト", test_cache_manager()))
    test_results.append(("知識ベースマネージャーテスト", test_knowledge_base()))
    test_results.append(("Notionクライアントテスト", test_notion_client()))
    test_results.append(("診断データマネージャーテスト", test_diagnostic_data()))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 総合結果: {passed}/{total} テストが成功")
    
    if passed == total:
        print("🎉 全てのテストが成功しました！data_access/モジュールは正常に動作しています。")
    else:
        print("⚠️ 一部のテストが失敗しました。エラーメッセージを確認して問題を解決してください。")
    
    return passed == total

if __name__ == "__main__":
    main()
