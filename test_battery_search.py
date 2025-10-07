
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
バッテリー検索機能のテストスクリプト
"""

import sys
import os

# 現在のディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_battery_search():
    """バッテリー検索機能をテスト"""
    print("🔍 バッテリー検索機能のテストを開始します...")
    
    try:
        # 知識ベースの読み込み
        from enhanced_knowledge_base_app import load_knowledge_base, extract_relevant_knowledge
        
        print("\n1. 知識ベースの読み込み...")
        knowledge_base = load_knowledge_base()
        print(f"✅ 知識ベース読み込み完了: {len(knowledge_base)}カテゴリ")
        
        # バッテリー関連のテストクエリ
        test_queries = [
            "バッテリーが充電されない",
            "サブバッテリーが空になる",
            "走行充電が効かない",
            "電圧が上がらない",
            "充電器が故障した",
            "バッテリーの交換時期",
            "リチウムバッテリーに変更したい"
        ]
        
        print("\n2. バッテリー関連クエリのテスト...")
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- テスト {i}: '{query}' ---")
            
            # 関連知識を抽出
            relevant_knowledge = extract_relevant_knowledge(query, knowledge_base)
            
            if relevant_knowledge:
                print(f"✅ 関連知識が見つかりました: {len(relevant_knowledge)}件")
                for j, knowledge in enumerate(relevant_knowledge[:2], 1):  # 最初の2件のみ表示
                    print(f"  {j}. {knowledge[:100]}...")
            else:
                print("❌ 関連知識が見つかりませんでした")
        
        # Notion統合のテスト
        print("\n3. Notion統合のテスト...")
        try:
            from optimized_notion_integration import search_camper_repair_info
            
            test_query = "バッテリーが充電されない"
            notion_results = search_camper_repair_info(test_query)
            
            print(f"✅ Notion検索完了:")
            print(f"  - 診断ノード: {len(notion_results['diagnostic_nodes'])}件")
            print(f"  - 修理ケース: {len(notion_results['repair_cases'])}件")
            print(f"  - 部品・工具: {len(notion_results['items'])}件")
            print(f"  - 総結果数: {notion_results['total_results']}件")
            
        except Exception as e:
            print(f"⚠️ Notion統合テストでエラー: {e}")
        
        print("\n🎉 バッテリー検索機能のテストが完了しました！")
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_battery_search()
