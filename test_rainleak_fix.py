#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雨漏りの修理手順と注意事項の抽出問題の直接テスト
"""

import json
import os
from repair_category_manager import RepairCategoryManager

def test_rainleak_extraction():
    """雨漏りの修理手順と注意事項の抽出テスト"""
    print("🔍 雨漏りの修理手順と注意事項の抽出テストを開始...")
    
    # 1. まずJSONファイルを直接読み込んでテスト
    print("\n1️⃣ JSONファイルの直接読み込みテスト:")
    try:
        with open("category_definitions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if "雨漏り" in data.get("categories", {}):
            print("✅ JSONファイルに雨漏りカテゴリーが存在")
            water_leak = data["categories"]["雨漏り"]
            
            fallback_steps = water_leak.get("fallback_steps", [])
            fallback_warnings = water_leak.get("fallback_warnings", [])
            
            print(f"  - fallback_steps数: {len(fallback_steps)}")
            print(f"  - fallback_warnings数: {len(fallback_warnings)}")
            
            if fallback_steps:
                print("✅ fallback_stepsが存在:")
                for i, step in enumerate(fallback_steps, 1):
                    print(f"    {i}. {step}")
            else:
                print("❌ fallback_stepsが見つからない")
                
            if fallback_warnings:
                print("✅ fallback_warningsが存在:")
                for i, warning in enumerate(fallback_warnings, 1):
                    print(f"    {i}. {warning}")
            else:
                print("❌ fallback_warningsが見つからない")
        else:
            print("❌ JSONファイルに雨漏りカテゴリーが見つからない")
    except Exception as e:
        print(f"❌ JSONファイル読み込みエラー: {e}")
    
    # 2. RepairCategoryManagerを使ったテスト
    print("\n2️⃣ RepairCategoryManagerを使ったテスト:")
    try:
        category_manager = RepairCategoryManager()
        print("✅ RepairCategoryManager初期化完了")
        
        if "雨漏り" in category_manager.categories:
            print("✅ RepairCategoryManagerに雨漏りカテゴリーが存在")
            
            # 修理手順の取得テスト
            steps = category_manager.get_repair_steps_from_json("雨漏り")
            print(f"\n🔧 修理手順の取得結果:")
            if steps:
                print("✅ 修理手順の取得成功:")
                print(steps)
            else:
                print("❌ 修理手順の取得失敗")
            
            # 注意事項の取得テスト
            warnings = category_manager.get_warnings_from_json("雨漏り")
            print(f"\n⚠️ 注意事項の取得結果:")
            if warnings:
                print("✅ 注意事項の取得成功:")
                print(warnings)
            else:
                print("❌ 注意事項の取得失敗")
                
            # 修理費用の取得テスト
            costs = category_manager.get_repair_costs("雨漏り")
            print(f"\n💰 修理費用の取得結果:")
            if costs:
                print("✅ 修理費用の取得成功:")
                print(costs)
            else:
                print("❌ 修理費用の取得失敗")
                
        else:
            print("❌ RepairCategoryManagerに雨漏りカテゴリーが見つからない")
            print(f"利用可能なカテゴリー: {list(category_manager.categories.keys())}")
            
    except Exception as e:
        print(f"❌ RepairCategoryManagerテストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. カテゴリー特定テスト
    print("\n3️⃣ カテゴリー特定テスト:")
    try:
        test_queries = ["雨漏り", "水漏れ", "シーリング", "屋根", "天井"]
        for query in test_queries:
            category = category_manager.identify_category(query)
            print(f"  '{query}' -> {category}")
    except Exception as e:
        print(f"❌ カテゴリー特定テストエラー: {e}")
    
    return True

if __name__ == "__main__":
    test_rainleak_extraction()
