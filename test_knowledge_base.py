#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知識ベースの動作テスト
"""

import os
import sys

# 環境変数設定
os.environ["NOTION_API_KEY"] = "test_key"
os.environ["OPENAI_API_KEY"] = "test_key"

def test_knowledge_base_loading():
    """知識ベースの読み込みテスト"""
    print("🧪 知識ベース読み込みテスト開始...")
    
    try:
        from data_access.knowledge_base import KnowledgeBaseManager
        
        kb_manager = KnowledgeBaseManager()
        
        print(f"📚 読み込まれたカテゴリ数: {len(kb_manager.knowledge_base)}")
        
        # カテゴリ一覧を表示
        categories = list(kb_manager.knowledge_base.keys())
        print(f"📂 カテゴリ一覧: {categories[:10]}...")  # 最初の10個を表示
        
        # 各カテゴリの内容長を確認
        for category in categories[:5]:  # 最初の5個をチェック
            content = kb_manager.knowledge_base[category]
            print(f"  - {category}: {len(content)}文字")
        
        return True
        
    except Exception as e:
        print(f"❌ 知識ベース読み込みテスト失敗: {e}")
        return False

def test_search_functionality():
    """検索機能のテスト"""
    print("\n🧪 検索機能テスト開始...")
    
    try:
        from data_access.knowledge_base import KnowledgeBaseManager
        
        kb_manager = KnowledgeBaseManager()
        
        # テストクエリ
        test_queries = [
            "バッテリー",
            "充電",
            "エアコン",
            "故障"
        ]
        
        for query in test_queries:
            print(f"\n🔍 検索クエリ: '{query}'")
            results = kb_manager.search_in_content(query)
            print(f"結果数: {len(results)}")
            
            if results:
                for category, content in results.items():
                    print(f"  - {category}: {len(content)}文字")
            else:
                print("  ❌ 結果なし")
        
        return True
        
    except Exception as e:
        print(f"❌ 検索機能テスト失敗: {e}")
        return False

def main():
    """メイン実行関数"""
    print("🚀 知識ベース動作テスト開始")
    print("=" * 50)
    
    # 読み込みテスト
    load_success = test_knowledge_base_loading()
    
    # 検索テスト
    search_success = test_search_functionality()
    
    print("\n" + "=" * 50)
    if load_success and search_success:
        print("✅ 全てのテストが成功しました！")
        return True
    else:
        print("❌ 一部のテストが失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
