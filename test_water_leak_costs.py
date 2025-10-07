#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雨漏り検索の修理費用目安テスト
"""

from repair_category_manager import RepairCategoryManager

def test_water_leak_costs():
    """雨漏りの修理費用目安テスト"""
    print("�� 雨漏り修理費用目安テスト開始")
    print("=" * 50)
    
    try:
        # カテゴリーマネージャーを初期化
        manager = RepairCategoryManager()
        print(f"✅ カテゴリーマネージャー初期化成功")
        
        # 雨漏りカテゴリーの確認
        if "雨漏り" in manager.categories:
            print("✅ 雨漏りカテゴリーが存在します")
            
            # 修理費用目安の取得
            costs = manager.get_repair_costs("雨漏り")
            print(f"\n�� 修理費用目安取得結果:")
            if costs:
                print("✅ 修理費用目安取得成功")
                print("📄 内容:")
                print(costs)
            else:
                print("❌ 修理費用目安取得失敗")
            
            # カテゴリーデータの詳細確認
            water_leak_data = manager.categories["雨漏り"]
            repair_costs_data = water_leak_data.get("repair_costs", [])
            print(f"\n📊 修理費用データ詳細:")
            print(f"  データ件数: {len(repair_costs_data)}件")
            for i, cost_item in enumerate(repair_costs_data, 1):
                item = cost_item.get("item", "")
                price_range = cost_item.get("price_range", "")
                print(f"  {i}. {item}: {price_range}")
                
        else:
            print("❌ 雨漏りカテゴリーが見つかりません")
            
        return True
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_category_identification():
    """雨漏りカテゴリー特定テスト"""
    print("\n🔍 雨漏りカテゴリー特定テスト")
    print("=" * 50)
    
    manager = RepairCategoryManager()
    
    test_queries = [
        "雨漏り",
        "雨漏りがしている",
        "水漏れ",
        "屋根の水漏れ",
        "天井から水が落ちる"
    ]
    
    for query in test_queries:
        print(f"\n📝 クエリ: '{query}'")
        category = manager.identify_category(query)
        if category:
            print(f"✅ カテゴリー特定成功: {category}")
            
            # 修理費用目安の取得
            costs = manager.get_repair_costs(category)
            if costs:
                print(f"💰 修理費用目安: 取得成功")
                print(f"   内容: {costs[:100]}...")
            else:
                print(f"❌ 修理費用目安: 取得失敗")
        else:
            print(f"❌ カテゴリー特定失敗")

if __name__ == "__main__":
    print("🚀 雨漏り修理費用目安テスト開始")
    print("=" * 60)
    
    success1 = test_water_leak_costs()
    success2 = test_category_identification()
    
    if success1 and success2:
        print("\n🎉 すべてのテストが完了しました！")
    else:
        print("\n❌ テストに失敗しました。")
