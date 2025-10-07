#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最適化されたシステムのユニットテスト
"""

import os
import sys
import asyncio
import time
import tempfile
import shutil
from typing import Dict, Any

# テスト用の環境設定
os.environ["NOTION_API_KEY"] = "test_key"
os.environ["OPENAI_API_KEY"] = "test_key"

def test_cache_manager():
    """キャッシュマネージャーのテスト"""
    print("🧪 キャッシュマネージャーのテスト開始...")
    
    try:
        from data_access.cache_manager import CacheManager
        
        # 一時ディレクトリでテスト
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_db = os.path.join(temp_dir, "test_cache.db")
            cache = CacheManager(cache_db)
            
            # 基本的なキャッシュ操作
            test_data = {"test": "data", "number": 123}
            cache.set("test_key", test_data, ttl=60)
            
            retrieved = cache.get("test_key")
            assert retrieved == test_data, f"キャッシュ取得失敗: {retrieved} != {test_data}"
            
            # 統計情報
            stats = cache.get_stats()
            assert stats['valid_count'] >= 1, f"統計情報が正しくない: {stats}"
            
            print("✅ キャッシュマネージャーのテスト成功")
            return True
            
    except Exception as e:
        print(f"❌ キャッシュマネージャーのテスト失敗: {e}")
        return False

def test_delayed_imports():
    """遅延インポートのテスト"""
    print("🧪 遅延インポートのテスト開始...")
    
    try:
        # メインファイルの遅延インポート関数をテスト
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # 遅延インポート関数を直接テスト
        from enhanced_knowledge_base_app import get_data_access, get_streamlit, get_langchain
        
        # データアクセス層のテスト
        data_access = get_data_access()
        assert isinstance(data_access, dict), f"データアクセス層の形式が正しくない: {type(data_access)}"
        
        # Streamlitのテスト（インポートエラーは許容）
        st = get_streamlit()
        # stがNoneでもOK（テスト環境ではStreamlitが利用できない可能性）
        
        print("✅ 遅延インポートのテスト成功")
        return True
        
    except Exception as e:
        print(f"❌ 遅延インポートのテスト失敗: {e}")
        return False

def test_async_notion_client():
    """非同期Notionクライアントのテスト"""
    print("🧪 非同期Notionクライアントのテスト開始...")
    
    try:
        from data_access.notion_client import NotionClient
        
        client = NotionClient()
        
        # 非同期メソッドの存在確認
        assert hasattr(client, 'load_diagnostic_data_async'), "非同期メソッドが存在しない"
        assert hasattr(client, '_make_request'), "非同期リクエストメソッドが存在しない"
        assert hasattr(client, '_get_session'), "セッション管理メソッドが存在しない"
        
        print("✅ 非同期Notionクライアントのテスト成功")
        return True
        
    except Exception as e:
        print(f"❌ 非同期Notionクライアントのテスト失敗: {e}")
        return False

def test_knowledge_base_manager():
    """知識ベースマネージャーのテスト"""
    print("🧪 知識ベースマネージャーのテスト開始...")
    
    try:
        from data_access.knowledge_base import KnowledgeBaseManager
        
        kb_manager = KnowledgeBaseManager()
        
        # 基本的なメソッドの存在確認
        assert hasattr(kb_manager, 'extract_relevant_knowledge'), "知識抽出メソッドが存在しない"
        assert hasattr(kb_manager, 'get_category_specific_info'), "カテゴリ別情報取得メソッドが存在しない"
        assert hasattr(kb_manager, 'search_in_content'), "コンテンツ検索メソッドが存在しない"
        
        # 知識ベースの初期化確認
        assert hasattr(kb_manager, 'knowledge_base'), "知識ベースが初期化されていない"
        
        print("✅ 知識ベースマネージャーのテスト成功")
        return True
        
    except Exception as e:
        print(f"❌ 知識ベースマネージャーのテスト失敗: {e}")
        return False

def test_performance_improvements():
    """パフォーマンス改善のテスト"""
    print("🧪 パフォーマンス改善のテスト開始...")
    
    try:
        # 遅延インポートの速度テスト
        start_time = time.time()
        
        # データアクセス層の遅延インポート
        from enhanced_knowledge_base_app import ensure_data_access
        data_access = ensure_data_access()
        
        import_time = time.time() - start_time
        
        # インポート時間が1秒以内であることを確認
        assert import_time < 1.0, f"インポート時間が長すぎる: {import_time:.2f}秒"
        
        print(f"✅ パフォーマンス改善のテスト成功 (インポート時間: {import_time:.3f}秒)")
        return True
        
    except Exception as e:
        print(f"❌ パフォーマンス改善のテスト失敗: {e}")
        return False

def test_memory_usage():
    """メモリ使用量のテスト"""
    print("🧪 メモリ使用量のテスト開始...")
    
    try:
        import psutil
        import gc
        
        # ガベージコレクション実行
        gc.collect()
        
        # 初期メモリ使用量
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # データアクセス層の読み込み
        from enhanced_knowledge_base_app import ensure_data_access, ensure_streamlit, ensure_langchain
        
        data_access = ensure_data_access()
        st = ensure_streamlit()
        langchain = ensure_langchain()
        
        # メモリ使用量の確認
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # メモリ増加量が50MB以内であることを確認
        assert memory_increase < 50, f"メモリ使用量が多すぎる: {memory_increase:.1f}MB"
        
        print(f"✅ メモリ使用量のテスト成功 (増加量: {memory_increase:.1f}MB)")
        return True
        
    except ImportError:
        print("⚠️ psutilが利用できないため、メモリテストをスキップ")
        return True
    except Exception as e:
        print(f"❌ メモリ使用量のテスト失敗: {e}")
        return False

def run_all_tests():
    """全テストを実行"""
    print("🚀 最適化システムのテスト開始")
    print("=" * 50)
    
    tests = [
        test_cache_manager,
        test_delayed_imports,
        test_async_notion_client,
        test_knowledge_base_manager,
        test_performance_improvements,
        test_memory_usage
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
    
    print("=" * 50)
    print(f"📊 テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 全てのテストが成功しました！")
        return True
    else:
        print("⚠️ 一部のテストが失敗しました")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
