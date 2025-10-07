#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
デバッグ用テストスクリプト
"""

import os
import sys

# 環境変数設定
os.environ["NOTION_API_KEY"] = "test_key"
os.environ["OPENAI_API_KEY"] = "test_key"

def main():
    """メイン実行関数"""
    print("🚀 デバッグテスト開始")
    print("=" * 50)
    
    # 現在のディレクトリを確認
    print(f"📂 現在のディレクトリ: {os.getcwd()}")
    
    # JSONファイルの存在確認
    json_file = "category_definitions.json"
    if os.path.exists(json_file):
        print(f"✅ JSONファイル存在: {json_file}")
        print(f"📄 ファイルサイズ: {os.path.getsize(json_file)} bytes")
    else:
        print(f"❌ JSONファイルが見つかりません: {json_file}")
    
    # 知識ベースマネージャーのテスト
    try:
        print("\n📦 知識ベースマネージャーのテスト...")
        from data_access.knowledge_base import KnowledgeBaseManager
        
        print("🔄 知識ベースマネージャーを初期化中...")
        kb_manager = KnowledgeBaseManager()
        
        print(f"📚 知識ベースカテゴリ数: {len(kb_manager.knowledge_base)}")
        
        if len(kb_manager.knowledge_base) > 0:
            categories = list(kb_manager.knowledge_base.keys())
            print(f"📂 カテゴリ一覧: {categories[:5]}...")
            
            # バッテリーカテゴリの内容を確認
            if 'バッテリー' in kb_manager.knowledge_base:
                battery_content = kb_manager.knowledge_base['バッテリー']
                print(f"🔋 バッテリーカテゴリの内容:")
                print(f"  - 文字数: {len(battery_content)}")
                print(f"  - 最初の200文字: {battery_content[:200]}...")
                print(f"  - '充電' を含むか: {'充電' in battery_content}")
                print(f"  - 'バッテリー' を含むか: {'バッテリー' in battery_content}")
                
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
            else:
                print("❌ バッテリーカテゴリが見つかりません")
        else:
            print("❌ 知識ベースが空です")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*50}")
    if success:
        print("✅ デバッグテスト完了")
    else:
        print("❌ デバッグテスト失敗")
    sys.exit(0 if success else 1)
