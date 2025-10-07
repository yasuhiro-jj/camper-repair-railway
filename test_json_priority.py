#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSONファイル優先のテスト
"""

from repair_category_manager import RepairCategoryManager

def test_json_priority():
    """JSONファイル優先のテスト"""
    print("🧪 JSONファイル優先テスト開始")
    print("=" * 50)
    
    try:
        manager = RepairCategoryManager()
        
        # 雨漏りカテゴリーのテスト
        category = "雨漏り"
        print(f"📋 テストカテゴリー: {category}")
        
        # JSONファイルから修理手順を取得
        print(f"\n🛠 修理手順テスト:")
        json_steps = manager.get_repair_steps_from_json(category)
        if json_steps:
            print(f"✅ JSONから修理手順取得成功")
            print(f"📄 内容（最初の200文字）:")
            print(json_steps[:200])
            print("...")
            
            # 行数カウント
            lines = json_steps.split('\n')
            print(f"📊 行数: {len(lines)}行")
        else:
            print("❌ JSONから修理手順取得失敗")
        
        # JSONファイルから注意事項を取得
        print(f"\n⚠️ 注意事項テスト:")
        json_warnings = manager.get_warnings_from_json(category)
        if json_warnings:
            print(f"✅ JSONから注意事項取得成功")
            print(f"📄 内容（最初の200文字）:")
            print(json_warnings[:200])
            print("...")
            
            # 行数カウント
            lines = json_warnings.split('\n')
            print(f"📊 行数: {len(lines)}行")
        else:
            print("❌ JSONから注意事項取得失敗")
        
        # 修理費用目安のテスト
        print(f"\n💰 修理費用目安テスト:")
        costs = manager.get_repair_costs(category)
        if costs:
            print(f"✅ 修理費用目安取得成功")
            print(f"📄 内容:")
            print(costs)
        else:
            print("❌ 修理費用目安取得失敗")
        
        return True
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 JSONファイル優先テスト開始")
    print("=" * 60)
    
    success = test_json_priority()
    
    if success:
        print("\n🎉 テスト完了！")
        print("💡 これで雨漏り検索時にJSONファイルから修理手順・注意事項が表示されます")
    else:
        print("\n❌ テスト失敗。")
