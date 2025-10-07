#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カテゴリー特定のテストスクリプト
"""

from repair_category_manager import RepairCategoryManager

def test_category_identification():
    """カテゴリー特定をテストする"""
    print("🔍 カテゴリー特定テストを開始...")
    
    try:
        # RepairCategoryManagerを初期化
        print("📚 RepairCategoryManagerを初期化中...")
        category_manager = RepairCategoryManager()
        print("✅ RepairCategoryManager初期化完了")
        
        # テストクエリ
        test_queries = [
            "雨漏り",
            "水漏れ",
            "シーリング",
            "防水",
            "屋根",
            "天井",
            "バッテリー",
            "エアコン",
            "トイレ"
        ]
        
        print(f"\n📊 読み込み済みカテゴリー数: {len(category_manager.categories)}")
        print("📋 利用可能なカテゴリー:")
        for category_name in category_manager.categories.keys():
            print(f"  - {category_name}")
        
        print("\n🔍 カテゴリー特定テスト:")
        for query in test_queries:
            print(f"\n--- クエリ: '{query}' ---")
            category = category_manager.identify_category(query)
            print(f"結果: {category or '特定されませんでした'}")
            
            if category:
                # 修理費用目安の取得テスト
                costs = category_manager.get_repair_costs(category)
                print(f"修理費用目安: {costs[:100] if costs else '取得失敗'}...")
                
                # 修理手順の取得テスト
                steps = category_manager.get_repair_steps_from_json(category)
                print(f"修理手順: {steps[:100] if steps else '取得失敗'}...")
                
                # 注意事項の取得テスト
                warnings = category_manager.get_warnings_from_json(category)
                print(f"注意事項: {warnings[:100] if warnings else '取得失敗'}...")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_category_identification()
