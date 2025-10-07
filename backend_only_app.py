#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
バックエンドのみのキャンピングカー修理AIアプリ
フロントエンドを使わずにコマンドラインで動作
"""

import os
import sys
import asyncio
import time
from typing import Dict, Any, List

# 環境変数設定
os.environ["NOTION_API_KEY"] = "test_key"
os.environ["OPENAI_API_KEY"] = "test_key"

def print_banner():
    """バナーを表示"""
    print("=" * 60)
    print("🏗️ キャンピングカー修理AI - バックエンド版")
    print("最適化されたシステムでコマンドライン動作")
    print("=" * 60)

def print_menu():
    """メニューを表示"""
    print("\n📋 利用可能な機能:")
    print("1. 🔍 知識ベース検索")
    print("2. 🧪 診断データ取得")
    print("3. 📊 システム統計")
    print("4. ⚡ パフォーマンステスト")
    print("5. 🗂️ キャッシュ管理")
    print("0. 🚪 終了")

def test_knowledge_base_search():
    """知識ベース検索のテスト"""
    print("\n🔍 知識ベース検索テスト")
    print("-" * 30)
    
    try:
        from enhanced_knowledge_base_app import ensure_data_access
        
        data_access = ensure_data_access()
        if not data_access['available']:
            print("❌ データアクセス層が利用できません")
            return False
        
        kb_manager = data_access['knowledge_base_manager']
        
        # 利用可能なカテゴリを表示
        categories = kb_manager.get_all_categories()
        print(f"📚 利用可能カテゴリ: {len(categories)}件")
        print(f"   例: {categories[:5]}")
        
        # 検索テスト
        test_queries = [
            "バッテリー 充電",
            "エアコン 故障",
            "雨漏り 修理"
        ]
        
        for query in test_queries:
            print(f"\n🔍 検索クエリ: '{query}'")
            results = kb_manager.search_in_content(query)
            print(f"   結果数: {len(results)}件")
            
            if results:
                for category, content in list(results.items())[:2]:  # 最初の2件を表示
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"   📄 {category}: {preview}")
        
        print("✅ 知識ベース検索テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 知識ベース検索テスト失敗: {e}")
        return False

def test_diagnostic_data():
    """診断データ取得のテスト"""
    print("\n🧪 診断データ取得テスト")
    print("-" * 30)
    
    try:
        from enhanced_knowledge_base_app import ensure_data_access
        
        data_access = ensure_data_access()
        if not data_access['available']:
            print("❌ データアクセス層が利用できません")
            return False
        
        diagnostic_manager = data_access['diagnostic_data_manager']
        
        # 診断データの概要を取得
        summary = diagnostic_manager.get_diagnostic_summary()
        print(f"📊 診断データ統計:")
        print(f"   診断ノード: {summary['diagnostic_nodes']}件")
        print(f"   開始ノード: {summary['start_nodes']}件")
        print(f"   修理ケース: {summary['repair_cases']}件")
        print(f"   カテゴリ: {len(summary['categories'])}件")
        print(f"   症状: {len(summary['symptoms'])}件")
        
        # 症状の例を表示
        if summary['symptoms']:
            print(f"   症状例: {summary['symptoms'][:5]}")
        
        print("✅ 診断データ取得テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 診断データ取得テスト失敗: {e}")
        return False

def show_system_stats():
    """システム統計を表示"""
    print("\n📊 システム統計")
    print("-" * 30)
    
    try:
        from data_access.cache_manager import cache_manager
        
        # キャッシュ統計
        stats = cache_manager.get_stats()
        print(f"🗄️ キャッシュ統計:")
        print(f"   総キャッシュ数: {stats['total_count']}件")
        print(f"   有効キャッシュ: {stats['valid_count']}件")
        print(f"   期限切れ: {stats['expired_count']}件")
        
        if stats['type_stats']:
            print(f"   タイプ別統計:")
            for cache_type, count in stats['type_stats'].items():
                print(f"     {cache_type}: {count}件")
        
        # メモリ使用量
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"💾 メモリ使用量: {memory_mb:.1f}MB")
        except ImportError:
            print("💾 メモリ使用量: psutilが利用できません")
        
        print("✅ システム統計表示完了")
        return True
        
    except Exception as e:
        print(f"❌ システム統計表示失敗: {e}")
        return False

def test_performance():
    """パフォーマンステスト"""
    print("\n⚡ パフォーマンステスト")
    print("-" * 30)
    
    try:
        # 遅延インポートの速度テスト
        print("⏱️ 遅延インポート速度テスト...")
        start_time = time.time()
        
        from enhanced_knowledge_base_app import ensure_data_access, ensure_streamlit, ensure_langchain
        
        data_access = ensure_data_access()
        st = ensure_streamlit()
        langchain = ensure_langchain()
        
        total_time = time.time() - start_time
        print(f"   総インポート時間: {total_time:.3f}秒")
        
        # パフォーマンス評価
        if total_time < 1.0:
            print("   🚀 優秀: 1秒以内")
        elif total_time < 2.0:
            print("   ✅ 良好: 2秒以内")
        else:
            print("   ⚠️ 要改善: 2秒超過")
        
        # キャッシュ効果のテスト
        print("\n🗄️ キャッシュ効果テスト...")
        cache_start = time.time()
        
        # 2回目のアクセス（キャッシュヒット）
        data_access2 = ensure_data_access()
        
        cache_time = time.time() - cache_start
        print(f"   キャッシュアクセス時間: {cache_time:.3f}秒")
        
        if cache_time < 0.1:
            print("   🚀 キャッシュ効果: 優秀")
        elif cache_time < 0.5:
            print("   ✅ キャッシュ効果: 良好")
        else:
            print("   ⚠️ キャッシュ効果: 要改善")
        
        print("✅ パフォーマンステスト完了")
        return True
        
    except Exception as e:
        print(f"❌ パフォーマンステスト失敗: {e}")
        return False

def manage_cache():
    """キャッシュ管理"""
    print("\n🗂️ キャッシュ管理")
    print("-" * 30)
    
    try:
        from data_access.cache_manager import cache_manager
        
        # 現在のキャッシュ統計
        stats = cache_manager.get_stats()
        print(f"📊 現在のキャッシュ状況:")
        print(f"   総数: {stats['total_count']}件")
        print(f"   有効: {stats['valid_count']}件")
        print(f"   期限切れ: {stats['expired_count']}件")
        
        # クリーンアップ実行
        print("\n🧹 キャッシュクリーンアップ実行中...")
        cleanup_result = cache_manager.cleanup()
        
        print(f"   期限切れ削除: {cleanup_result['expired_deleted']}件")
        print(f"   古いキャッシュ削除: {cleanup_result['old_deleted']}件")
        
        # クリーンアップ後の統計
        new_stats = cache_manager.get_stats()
        print(f"\n📊 クリーンアップ後:")
        print(f"   総数: {new_stats['total_count']}件")
        print(f"   有効: {new_stats['valid_count']}件")
        
        print("✅ キャッシュ管理完了")
        return True
        
    except Exception as e:
        print(f"❌ キャッシュ管理失敗: {e}")
        return False

async def test_async_operations():
    """非同期処理のテスト"""
    print("\n🔄 非同期処理テスト")
    print("-" * 30)
    
    try:
        from data_access.notion_client import NotionClient
        
        client = NotionClient()
        
        # 非同期セッション管理のテスト
        print("🌐 非同期セッション作成...")
        session = await client._get_session()
        print(f"   セッション作成: {'成功' if session else '失敗'}")
        
        # セッションクローズ
        await client._close_session()
        print("   セッションクローズ: 完了")
        
        print("✅ 非同期処理テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 非同期処理テスト失敗: {e}")
        return False

def main():
    """メイン実行関数"""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("\n🔢 選択してください (0-5): ").strip()
            
            if choice == "0":
                print("\n👋 アプリケーションを終了します")
                break
            elif choice == "1":
                test_knowledge_base_search()
            elif choice == "2":
                test_diagnostic_data()
            elif choice == "3":
                show_system_stats()
            elif choice == "4":
                test_performance()
            elif choice == "5":
                manage_cache()
            else:
                print("❌ 無効な選択です。0-5の数字を入力してください。")
            
            input("\n⏸️ 続行するにはEnterキーを押してください...")
            
        except KeyboardInterrupt:
            print("\n\n👋 アプリケーションを終了します")
            break
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            input("⏸️ 続行するにはEnterキーを押してください...")

if __name__ == "__main__":
    main()
