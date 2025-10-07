#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セクション抽出のデバッグ用テストスクリプト
"""

from repair_category_manager import RepairCategoryManager
import re

def test_section_extraction():
    """セクション抽出のテスト"""
    print("🧪 セクション抽出テスト開始")
    print("=" * 50)
    
    try:
        manager = RepairCategoryManager()
        
        # 雨漏りカテゴリーの確認
        if "雨漏り" in manager.categories:
            print("✅ 雨漏りカテゴリーが存在します")
            
            # 修理手順ファイルの読み込み
            repair_steps_content = manager.get_content_from_file("雨漏り", "repair_steps")
            if repair_steps_content:
                print(f"✅ 修理手順ファイル読み込み成功 ({len(repair_steps_content)}文字)")
                print(f"📄 ファイル内容（最初の200文字）:")
                print(repair_steps_content[:200])
                print("...")
                
                # セクション抽出テスト
                print(f"\n🔧 修理手順セクション抽出テスト:")
                extracted_steps = manager.extract_section_from_content(repair_steps_content, "repair_steps_section")
                if extracted_steps:
                    print("✅ 修理手順セクション抽出成功")
                    print(f"📄 抽出内容（最初の200文字）:")
                    print(extracted_steps[:200])
                    print("...")
                else:
                    print("❌ 修理手順セクション抽出失敗")
                    
                    # 手動で正規表現テスト
                    print(f"\n🔍 手動正規表現テスト:")
                    patterns = manager.general_settings.get("extraction_patterns", {}).get("repair_steps_section", [])
                    for i, pattern in enumerate(patterns):
                        print(f"  パターン {i+1}: {pattern}")
                        match = re.search(pattern, repair_steps_content, re.DOTALL)
                        if match:
                            print(f"    ✅ マッチ成功")
                            print(f"    抽出内容: {match.group(1)[:100]}...")
                        else:
                            print(f"    ❌ マッチ失敗")
            else:
                print("❌ 修理手順ファイル読み込み失敗")
            
            # 注意事項ファイルの読み込み
            warnings_content = manager.get_content_from_file("雨漏り", "warnings")
            if warnings_content:
                print(f"\n✅ 注意事項ファイル読み込み成功 ({len(warnings_content)}文字)")
                print(f"📄 ファイル内容（最初の200文字）:")
                print(warnings_content[:200])
                print("...")
                
                # セクション抽出テスト
                print(f"\n⚠️ 注意事項セクション抽出テスト:")
                extracted_warnings = manager.extract_section_from_content(warnings_content, "warnings_section")
                if extracted_warnings:
                    print("✅ 注意事項セクション抽出成功")
                    print(f"📄 抽出内容（最初の200文字）:")
                    print(extracted_warnings[:200])
                    print("...")
                else:
                    print("❌ 注意事項セクション抽出失敗")
                    
                    # 手動で正規表現テスト
                    print(f"\n🔍 手動正規表現テスト:")
                    patterns = manager.general_settings.get("extraction_patterns", {}).get("warnings_section", [])
                    for i, pattern in enumerate(patterns):
                        print(f"  パターン {i+1}: {pattern}")
                        match = re.search(pattern, warnings_content, re.DOTALL)
                        if match:
                            print(f"    ✅ マッチ成功")
                            print(f"    抽出内容: {match.group(1)[:100]}...")
                        else:
                            print(f"    ❌ マッチ失敗")
            else:
                print("❌ 注意事項ファイル読み込み失敗")
                
        else:
            print("❌ 雨漏りカテゴリーが見つかりません")
            
        return True
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_content():
    """フォールバック内容のテスト"""
    print("\n🧪 フォールバック内容テスト")
    print("=" * 50)
    
    try:
        manager = RepairCategoryManager()
        
        # フォールバック修理手順の取得
        fallback_steps = manager.get_fallback_steps("雨漏り")
        print(f"🛠 フォールバック修理手順:")
        if fallback_steps:
            print(f"✅ 取得成功 ({len(fallback_steps)}件)")
            for i, step in enumerate(fallback_steps, 1):
                print(f"  {i}. {step}")
        else:
            print("❌ 取得失敗")
        
        # フォールバック注意事項の取得
        fallback_warnings = manager.get_fallback_warnings("雨漏り")
        print(f"\n⚠️ フォールバック注意事項:")
        if fallback_warnings:
            print(f"✅ 取得成功 ({len(fallback_warnings)}件)")
            for warning in fallback_warnings:
                print(f"  {warning}")
        else:
            print("❌ 取得失敗")
            
        return True
        
    except Exception as e:
        print(f"❌ フォールバックテスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 セクション抽出デバッグテスト開始")
    print("=" * 60)
    
    success1 = test_section_extraction()
    success2 = test_fallback_content()
    
    if success1 and success2:
        print("\n🎉 すべてのテストが完了しました！")
    else:
        print("\n❌ テストに失敗しました。")
