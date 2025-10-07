#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雨漏りの抽出問題のデバッグスクリプト
"""

import json
from repair_category_manager import RepairCategoryManager

def debug_water_leak():
    """雨漏りの抽出問題をデバッグ"""
    print("🔍 雨漏りの抽出問題をデバッグ中...")
    
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
        
        # 雨漏りカテゴリーの生データを表示
        water_leak_data = category_manager.categories["雨漏り"]
        print(f"\n📋 雨漏りカテゴリーの生データ:")
        print(f"  - キー: {list(water_leak_data.keys())}")
        
        # fallback_stepsの確認
        fallback_steps = water_leak_data.get("fallback_steps", [])
        print(f"\n🔧 fallback_steps:")
        print(f"  - タイプ: {type(fallback_steps)}")
        print(f"  - 長さ: {len(fallback_steps)}")
        print(f"  - 内容: {fallback_steps}")
        
        # fallback_warningsの確認
        fallback_warnings = water_leak_data.get("fallback_warnings", [])
        print(f"\n⚠️ fallback_warnings:")
        print(f"  - タイプ: {type(fallback_warnings)}")
        print(f"  - 長さ: {len(fallback_warnings)}")
        print(f"  - 内容: {fallback_warnings}")
        
        # get_repair_steps_from_jsonメソッドのテスト
        print(f"\n🔧 get_repair_steps_from_jsonメソッドのテスト:")
        steps_result = category_manager.get_repair_steps_from_json("雨漏り")
        print(f"  - 結果: {steps_result}")
        print(f"  - 長さ: {len(steps_result)}")
        
        # get_warnings_from_jsonメソッドのテスト
        print(f"\n⚠️ get_warnings_from_jsonメソッドのテスト:")
        warnings_result = category_manager.get_warnings_from_json("雨漏り")
        print(f"  - 結果: {warnings_result}")
        print(f"  - 長さ: {len(warnings_result)}")
        
        # 修理費用のテスト
        print(f"\n💰 修理費用のテスト:")
        costs_result = category_manager.get_repair_costs("雨漏り")
        print(f"  - 結果: {costs_result}")
        print(f"  - 長さ: {len(costs_result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    debug_water_leak()
