#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFヒーター検索機能の簡単テスト
"""

from repair_category_manager import RepairCategoryManager

def test_simple():
    """簡単なテスト"""
    print("🔥 FFヒーター検索テスト")
    
    manager = RepairCategoryManager()
    
    # テストクエリ
    query = "FFヒーターの交換を考えている"
    print(f"クエリ: {query}")
    
    # カテゴリー特定
    category = manager.identify_category(query)
    print(f"特定されたカテゴリー: {category}")
    
    if category:
        print("✅ カテゴリー特定成功！")
        
        # 修理費用を取得
        costs = manager.get_repair_costs(category)
        print(f"修理費用目安: {costs[:100]}...")
        
        # 修理手順を取得
        steps = manager.get_repair_steps_from_json(category)
        print(f"修理手順: {steps[:100]}...")
    else:
        print("❌ カテゴリー特定失敗")

if __name__ == "__main__":
    test_simple()
