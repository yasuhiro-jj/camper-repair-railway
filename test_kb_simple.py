#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知識ベースの簡単なテスト
"""

import os
import sys

# 環境変数設定
os.environ["NOTION_API_KEY"] = "test_key"
os.environ["OPENAI_API_KEY"] = "test_key"

def test_knowledge_base_simple():
    """知識ベースの簡単なテスト"""
    print("🧪 知識ベース簡単テスト開始...")
    
    try:
        # 知識ベースマネージャーを直接インポート
        from data_access.knowledge_base import KnowledgeBaseManager
        
        print("📦 知識ベースマネージャーをインポート中...")
        kb_manager = KnowledgeBaseManager()
        
        print(f"📚 読み込まれたカテゴリ数: {len(kb_manager.knowledge_base)}")
        
        if len(kb_manager.knowledge_base) == 0:
            print("❌ 知識ベースが空です！")
            return False
        
        # カテゴリ一覧を表示
        categories = list(kb_manager.knowledge_base.keys())
        print(f"📂 カテゴリ一覧: {categories[:10]}...")
        
        # バッテリーカテゴリの内容を確認
        if 'バッテリー' in kb_manager.knowledge_base:
            battery_content = kb_manager.knowledge_base['バッテリー']
            print(f"\n🔋 バッテリーカテゴリの内容:")
            print(f"  - 文字数: {len(battery_content)}")
            print(f"  - 最初の300文字:")
            print(f"    {battery_content[:300]}")
            print(f"  - '充電' を含むか: {'充電' in battery_content}")
            print(f"  - 'バッテリー' を含むか: {'バッテリー' in battery_content}")
        else:
            print("❌ バッテリーカテゴリが見つかりません")
        
        # 検索テスト
        print(f"\n🔍 検索テスト:")
        test_query = "バッテリー"
        print(f"検索クエリ: '{test_query}'")
        results = kb_manager.search_in_content(test_query)
        print(f"検索結果数: {len(results)}")
        
        if results:
            for category, content in results.items():
                print(f"  - {category}: {len(content)}文字")
        else:
            print("  ❌ 検索結果なし")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行関数"""
    print("🚀 知識ベース簡単テスト開始")
    print("=" * 50)
    
    success = test_knowledge_base_simple()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ テスト完了")
    else:
        print("❌ テスト失敗")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
