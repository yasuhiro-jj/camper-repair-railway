#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雨漏りの修理手順と注意事項の抽出テスト
"""

from repair_category_manager import RepairCategoryManager

def test_water_leak_extraction():
    """雨漏りの抽出テスト"""
    print("🔍 雨漏りの修理手順と注意事項の抽出テストを開始...")
    
    try:
        # RepairCategoryManagerを初期化
        print("📚 RepairCategoryManagerを初期化中...")
        category_manager = RepairCategoryManager()
        print("✅ RepairCategoryManager初期化完了")
        
        # 雨漏りカテゴリーの存在確認
        if "雨漏り" not in category_manager.categories:
            print("❌ 雨漏りカテゴリーが見つかりません")
            return False
        
        print(f"✅ 雨漏りカテゴリーが見つかりました")
        
        # 雨漏りカテゴリーの詳細情報を表示
        water_leak_data = category_manager.categories["雨漏り"]
        print(f"\n📋 雨漏りカテゴリーの詳細:")
        print(f"  - ID: {water_leak_data.get('id', 'N/A')}")
        print(f"  - 名前: {water_leak_data.get('name', 'N/A')}")
        print(f"  - アイコン: {water_leak_data.get('icon', 'N/A')}")
        
        # キーワード情報
        keywords = water_leak_data.get("keywords", {})
        print(f"  - 主要キーワード: {keywords.get('primary', [])}")
        print(f"  - 詳細キーワード: {keywords.get('secondary', [])}")
        print(f"  - 文脈フレーズ: {keywords.get('context', [])}")
        
        # 修理費用目安の取得テスト
        print(f"\n💰 修理費用目安の取得テスト:")
        costs = category_manager.get_repair_costs("雨漏り")
        if costs:
            print(f"✅ 修理費用目安取得成功:")
            print(costs)
        else:
            print("❌ 修理費用目安の取得に失敗")
        
        # 修理手順の取得テスト（JSON形式）
        print(f"\n🔧 修理手順の取得テスト（JSON形式）:")
        steps = category_manager.get_repair_steps_from_json("雨漏り")
        if steps:
            print(f"✅ 修理手順取得成功:")
            print(steps)
        else:
            print("❌ 修理手順の取得に失敗")
        
        # 注意事項の取得テスト（JSON形式）
        print(f"\n⚠️ 注意事項の取得テスト（JSON形式）:")
        warnings = category_manager.get_warnings_from_json("雨漏り")
        if warnings:
            print(f"✅ 注意事項取得成功:")
            print(warnings)
        else:
            print("❌ 注意事項の取得に失敗")
        
        # ファイルパスの確認
        print(f"\n📁 ファイルパスの確認:")
        file_paths = category_manager.get_file_paths("雨漏り")
        print(f"  修理手順ファイル: {file_paths.get('repair_steps', 'N/A')}")
        print(f"  注意事項ファイル: {file_paths.get('warnings', 'N/A')}")
        print(f"  テキストコンテンツファイル: {file_paths.get('text_content', 'N/A')}")
        
        # ファイルからの内容取得テスト
        print(f"\n📄 ファイルからの内容取得テスト:")
        
        # 修理手順ファイルの内容取得
        repair_steps_content = category_manager.get_content_from_file("雨漏り", "repair_steps")
        if repair_steps_content:
            print(f"✅ 修理手順ファイルから内容取得成功 ({len(repair_steps_content)}文字)")
        else:
            print("❌ 修理手順ファイルからの内容取得に失敗")
        
        # 注意事項ファイルの内容取得
        warnings_content = category_manager.get_content_from_file("雨漏り", "warnings")
        if warnings_content:
            print(f"✅ 注意事項ファイルから内容取得成功 ({len(warnings_content)}文字)")
        else:
            print("❌ 注意事項ファイルからの内容取得に失敗")
        
        # テキストコンテンツファイルの内容取得
        text_content = category_manager.get_content_from_file("雨漏り", "text_content")
        if text_content:
            print(f"✅ テキストコンテンツファイルから内容取得成功 ({len(text_content)}文字)")
        else:
            print("❌ テキストコンテンツファイルからの内容取得に失敗")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_water_leak_extraction()
