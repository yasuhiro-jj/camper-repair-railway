#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RepairCategoryManagerの直接テスト
"""

from repair_category_manager import RepairCategoryManager

def test_category_manager_direct():
    """RepairCategoryManagerの直接テスト"""
    print("🔍 RepairCategoryManagerの直接テストを開始...")
    
    try:
        # RepairCategoryManagerを初期化
        print("📚 RepairCategoryManagerを初期化中...")
        category_manager = RepairCategoryManager()
        print("✅ RepairCategoryManager初期化完了")
        
        # 雨漏りカテゴリーのテスト
        print("\n🌧️ 雨漏りカテゴリーのテスト:")
        
        # カテゴリー特定テスト
        test_queries = ["雨漏り", "水漏れ", "シーリング", "屋根", "天井"]
        for query in test_queries:
            category = category_manager.identify_category(query)
            print(f"  '{query}' -> {category}")
        
        # 雨漏りカテゴリーの詳細情報を取得
        if "雨漏り" in category_manager.categories:
            print("\n📋 雨漏りカテゴリーの詳細情報:")
            
            # 修理費用の取得
            costs = category_manager.get_repair_costs("雨漏り")
            print(f"\n💰 修理費用:")
            if costs:
                print("✅ 修理費用取得成功:")
                print(costs)
            else:
                print("❌ 修理費用の取得に失敗")
            
            # 修理手順の取得（JSON形式）
            steps = category_manager.get_repair_steps_from_json("雨漏り")
            print(f"\n🔧 修理手順（JSON形式）:")
            if steps:
                print("✅ 修理手順取得成功:")
                print(steps)
            else:
                print("❌ 修理手順の取得に失敗")
            
            # 注意事項の取得（JSON形式）
            warnings = category_manager.get_warnings_from_json("雨漏り")
            print(f"\n⚠️ 注意事項（JSON形式）:")
            if warnings:
                print("✅ 注意事項取得成功:")
                print(warnings)
            else:
                print("❌ 注意事項の取得に失敗")
            
            # ファイルからの内容取得テスト
            print(f"\n📄 ファイルからの内容取得テスト:")
            
            # 修理手順ファイル
            repair_steps_content = category_manager.get_content_from_file("雨漏り", "repair_steps")
            if repair_steps_content:
                print(f"✅ 修理手順ファイル取得成功 ({len(repair_steps_content)}文字)")
            else:
                print("❌ 修理手順ファイルの取得に失敗")
            
            # 注意事項ファイル
            warnings_content = category_manager.get_content_from_file("雨漏り", "warnings")
            if warnings_content:
                print(f"✅ 注意事項ファイル取得成功 ({len(warnings_content)}文字)")
            else:
                print("❌ 注意事項ファイルの取得に失敗")
            
            # テキストコンテンツファイル
            text_content = category_manager.get_content_from_file("雨漏り", "text_content")
            if text_content:
                print(f"✅ テキストコンテンツファイル取得成功 ({len(text_content)}文字)")
            else:
                print("❌ テキストコンテンツファイルの取得に失敗")
        
        else:
            print("❌ 雨漏りカテゴリーが見つかりません")
            print(f"利用可能なカテゴリー: {list(category_manager.categories.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_category_manager_direct()
