#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def test_get_repair_steps_from_file(category):
    """専用ファイルから修理手順を取得（テスト用）"""
    
    # カテゴリーに応じてファイル名を決定
    file_mapping = {
        'トイレ': 'トイレ_修理手順.txt',
        'バッテリー': 'バッテリー_修理手順.txt',
        'エアコン': 'エアコン_修理手順.txt',
        '雨漏り': '雨漏り_修理手順.txt',
        'サブバッテリー': 'サブバッテリー_修理手順.txt'
    }
    
    filename = file_mapping.get(category)
    if not filename:
        print(f"  ❌ {category}の修理手順ファイルが見つかりません")
        return None
    
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  ✅ {filename}から修理手順を取得しました ({len(content)}文字)")
                print(f"  ファイル内容の最初の500文字:")
                print(content[:500])
                print("=" * 50)
                
                # 修理手順セクションを抽出
                steps_match = re.search(r'## 修理手順\s*\n(.*?)(?=\n##|$)', content, re.DOTALL)
                if steps_match:
                    steps_content = steps_match.group(1).strip()
                    print(f"  ✅ 修理手順セクションを抽出しました ({len(steps_content)}文字)")
                    print(f"  抽出された内容:")
                    print(steps_content)
                    print("=" * 50)
                    
                    # 手順を配列に変換
                    steps_lines = [line.strip() for line in steps_content.split('\n') if line.strip() and not line.startswith('---')]
                    print(f"  ✅ {len(steps_lines)}件の修理手順を抽出")
                    result = '\n'.join(steps_lines)
                    print(f"  最終結果:")
                    print(result)
                    return result
                else:
                    print(f"  ❌ {filename}に修理手順セクションが見つかりません")
                    print(f"  正規表現パターン: r'## 修理手順\\s*\\n(.*?)(?=\\n##|$)'")
                    print(f"  ファイルに含まれる見出し:")
                    headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
                    for header in headers:
                        print(f"    - {header}")
                    return None
        else:
            print(f"  ❌ {filename}が存在しません")
            return None
    except Exception as e:
        print(f"  ❌ {filename}の読み込みエラー: {e}")
        return None

def test_get_warnings_from_file(category):
    """専用ファイルから注意事項を取得（テスト用）"""
    
    # カテゴリーに応じてファイル名を決定
    file_mapping = {
        'トイレ': 'トイレ_注意事項.txt',
        'バッテリー': 'バッテリー_注意事項.txt',
        'エアコン': 'エアコン_注意事項.txt',
        '雨漏り': '雨漏り_注意事項.txt',
        'サブバッテリー': 'サブバッテリー_注意事項.txt'
    }
    
    filename = file_mapping.get(category)
    if not filename:
        print(f"  ❌ {category}の注意事項ファイルが見つかりません")
        return None
    
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  ✅ {filename}から注意事項を取得しました ({len(content)}文字)")
                print(f"  ファイル内容:")
                print(content)
                print("=" * 50)
                
                # 注意事項セクションを抽出
                warnings_match = re.search(r'## 注意事項\s*\n(.*?)(?=\n##|$)', content, re.DOTALL)
                if warnings_match:
                    warnings_content = warnings_match.group(1).strip()
                    print(f"  ✅ 注意事項セクションを抽出しました ({len(warnings_content)}文字)")
                    print(f"  抽出された内容:")
                    print(warnings_content)
                    print("=" * 50)
                    
                    # 注意事項を配列に変換
                    warnings_lines = [line.strip() for line in warnings_content.split('\n') if line.strip() and not line.startswith('---')]
                    print(f"  ✅ {len(warnings_lines)}件の注意事項を抽出")
                    result = '\n'.join(warnings_lines)
                    print(f"  最終結果:")
                    print(result)
                    return result
                else:
                    print(f"  ❌ {filename}に注意事項セクションが見つかりません")
                    print(f"  正規表現パターン: r'## 注意事項\\s*\\n(.*?)(?=\\n##|$)'")
                    print(f"  ファイルに含まれる見出し:")
                    headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
                    for header in headers:
                        print(f"    - {header}")
                    return None
        else:
            print(f"  ❌ {filename}が存在しません")
            return None
    except Exception as e:
        print(f"  ❌ {filename}の読み込みエラー: {e}")
        return None

if __name__ == "__main__":
    print("=== トイレ修理手順テスト ===")
    test_get_repair_steps_from_file('トイレ')
    
    print("\n=== トイレ注意事項テスト ===")
    test_get_warnings_from_file('トイレ')
    
    print("\n=== バッテリー修理手順テスト ===")
    test_get_repair_steps_from_file('バッテリー')
    
    print("\n=== バッテリー注意事項テスト ===")
    test_get_warnings_from_file('バッテリー')
