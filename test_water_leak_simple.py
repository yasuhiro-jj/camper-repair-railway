#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雨漏りの修理手順と注意事項の簡単なテスト
"""

import json
from repair_category_manager import RepairCategoryManager

def test_water_leak_simple():
    """雨漏りの簡単なテスト"""
    print("🔍 雨漏りの修理手順と注意事項の簡単なテストを開始...")
    
    try:
        # RepairCategoryManagerを初期化
        print("📚 RepairCategoryManagerを初期化中...")
        category_manager = RepairCategoryManager()
        print("✅ RepairCategoryManager初期化完了")
        
        # 雨漏りカテゴリーの存在確認
        if "雨漏り" not in category_manager.categories:
            print("❌ 雨漏りカテゴリーが見つかりません")
            return False
        
        print("✅ 雨漏りカテゴリーが見つかりました")
        
        # 雨漏りカテゴリーのデータを取得
        water_leak_data = category_manager.categories["雨漏り"]
        
        # fallback_stepsの確認
        fallback_steps = water_leak_data.get("fallback_steps", [])
        print(f"\n🔧 fallback_steps:")
        print(f"  - 長さ: {len(fallback_steps)}")
        for i, step in enumerate(fallback_steps, 1):
            print(f"  {i}. {step}")
        
        # fallback_warningsの確認
        fallback_warnings = water_leak_data.get("fallback_warnings", [])
        print(f"\n⚠️ fallback_warnings:")
        print(f"  - 長さ: {len(fallback_warnings)}")
        for i, warning in enumerate(fallback_warnings, 1):
            print(f"  {i}. {warning}")
        
        # get_repair_steps_from_jsonメソッドのテスト
        print(f"\n🔧 get_repair_steps_from_jsonメソッドのテスト:")
        steps_result = category_manager.get_repair_steps_from_json("雨漏り")
        if steps_result:
            print("✅ 修理手順の取得に成功:")
            print(steps_result)
        else:
            print("❌ 修理手順の取得に失敗")
        
        # get_warnings_from_jsonメソッドのテスト
        print(f"\n⚠️ get_warnings_from_jsonメソッドのテスト:")
        warnings_result = category_manager.get_warnings_from_json("雨漏り")
        if warnings_result:
            print("✅ 注意事項の取得に成功:")
            print(warnings_result)
        else:
            print("❌ 注意事項の取得に失敗")
        
        # 修理費用のテスト
        print(f"\n💰 修理費用のテスト:")
        costs_result = category_manager.get_repair_costs("雨漏り")
        if costs_result:
            print("✅ 修理費用の取得に成功:")
            print(costs_result)
        else:
            print("❌ 修理費用の取得に失敗")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_water_leak_simple()
