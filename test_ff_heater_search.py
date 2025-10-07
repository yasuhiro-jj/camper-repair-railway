#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFヒーター検索機能のテストスクリプト
"""

import sys
import os

# 現在のディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repair_category_manager import RepairCategoryManager

def test_ff_heater_search():
    """FFヒーター検索機能をテスト"""
    print("🔥 FFヒーター検索機能テスト開始")
    print("=" * 50)
    
    # RepairCategoryManagerを初期化
    manager = RepairCategoryManager()
    
    # テストクエリ
    test_queries = [
        "FFヒーターの交換を考えている",
        "FFヒーターが故障した",
        "ヒーターの修理費用を知りたい",
        "暖房が効かない",
        "FFヒーターのメンテナンス方法",
        "ディーゼルヒーターの異音",
        "車載ヒーターの設置工事",
        "FFヒーターの部品交換",
        "燃焼式ヒーターのトラブル",
        "強制送風ヒーターの故障"
    ]
    
    print(f"📝 テストクエリ数: {len(test_queries)}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 テスト {i}: '{query}'")
        print("-" * 30)
        
        # カテゴリー特定
        category = manager.identify_category(query)
        
        if category:
            print(f"✅ 特定されたカテゴリー: {category}")
            
            # 修理費用情報を取得
            costs = manager.get_repair_costs(category)
            if costs:
                print(f"💰 修理費用目安:")
                print(costs[:200] + "..." if len(costs) > 200 else costs)
            
            # 修理手順を取得
            steps = manager.get_repair_steps_from_json(category)
            if steps:
                print(f"🔧 修理手順:")
                print(steps[:200] + "..." if len(steps) > 200 else steps)
            
            # 注意事項を取得
            warnings = manager.get_warnings_from_json(category)
            if warnings:
                print(f"⚠️ 注意事項:")
                print(warnings[:200] + "..." if len(warnings) > 200 else warnings)
        else:
            print("❌ カテゴリーが特定されませんでした")
        
        print()
        print("=" * 50)
        print()

if __name__ == "__main__":
    test_ff_heater_search()
