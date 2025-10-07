#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カテゴリー特定の詳細テストスクリプト
"""

from repair_category_manager import RepairCategoryManager

def test_category_identification_detailed():
    """カテゴリー特定の詳細テスト"""
    print("🔍 カテゴリー特定の詳細テストを開始...")
    
    # 設定ファイルの存在確認
    import os
    config_file = "category_definitions.json"
    if os.path.exists(config_file):
        print(f"✅ 設定ファイル {config_file} が見つかりました")
    else:
        print(f"❌ 設定ファイル {config_file} が見つかりません")
        print("💡 現在のディレクトリ:", os.getcwd())
        print("💡 利用可能なファイル:")
        for file in os.listdir("."):
            if file.endswith(".json"):
                print(f"  - {file}")
        return False
    
    try:
        # RepairCategoryManagerを初期化
        print("📚 RepairCategoryManagerを初期化中...")
        category_manager = RepairCategoryManager()
        print("✅ RepairCategoryManager初期化完了")
        
        # カテゴリーの存在確認
        if hasattr(category_manager, 'categories') and category_manager.categories:
            print(f"\n📋 利用可能なカテゴリー数: {len(category_manager.categories)}")
            for category_name, category_data in category_manager.categories.items():
                keywords = category_data.get("keywords", {})
                primary = keywords.get("primary", [])
                secondary = keywords.get("secondary", [])
                print(f"  - {category_name}: 主要={primary}, 詳細={secondary}")
        else:
            print("❌ カテゴリーが読み込まれていません")
            print("💡 category_definitions.jsonファイルの存在を確認してください")
            return False
        
        # テストクエリ（問題のあるカテゴリー）
        test_queries = [
            "雨漏り",
            "水漏れ", 
            "シーリング",
            "バッテリー",
            "充電",
            "トイレ",
            "便器",
            "エアコン",
            "冷房",
            "ドア",
            "窓",
            "冷蔵庫",
            "ガスコンロ"
        ]
        
        print("\n🔍 カテゴリー特定テスト:")
        for query in test_queries:
            print(f"\n--- クエリ: '{query}' ---")
            
            # カテゴリー特定
            category = category_manager.identify_category(query)
            print(f"特定されたカテゴリー: {category or 'なし'}")
            
            if category:
                # カテゴリーデータの詳細表示
                category_data = category_manager.categories.get(category, {})
                keywords = category_data.get("keywords", {})
                primary = keywords.get("primary", [])
                secondary = keywords.get("secondary", [])
                context = keywords.get("context", [])
                exclusion = category_data.get("exclusion_keywords", [])
                
                print(f"  主要キーワード: {primary}")
                print(f"  詳細キーワード: {secondary}")
                print(f"  文脈フレーズ: {context}")
                print(f"  除外キーワード: {exclusion}")
                
                # 修理費用目安の取得テスト
                costs = category_manager.get_repair_costs(category)
                print(f"  修理費用目安: {costs[:100] if costs else '取得失敗'}...")
                
                # 修理手順の取得テスト
                steps = category_manager.get_repair_steps_from_json(category)
                print(f"  修理手順: {steps[:100] if steps else '取得失敗'}...")
                
                # 注意事項の取得テスト
                warnings = category_manager.get_warnings_from_json(category)
                print(f"  注意事項: {warnings[:100] if warnings else '取得失敗'}...")
            else:
                print("  ❌ カテゴリーが特定されませんでした")
                
                # デバッグ: 各カテゴリーとの関連性をチェック
                print("  🔍 デバッグ情報:")
                for cat_name, cat_data in category_manager.categories.items():
                    is_related = category_manager._is_category_related(query.lower(), cat_data)
                    print(f"    - {cat_name}: {is_related}")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_category_identification_detailed()