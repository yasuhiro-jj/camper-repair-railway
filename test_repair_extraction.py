#!/usr/bin/env python3
"""
修理手順・注意事項抽出のテストスクリプト
"""

import os
import sys

# 現在のディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_repair_extraction():
    """修理手順・注意事項抽出のテスト"""
    
    # テスト用のテキストファイルを読み込み
    test_files = ['エアコン.txt', 'FFヒーター.txt']
    
    for filename in test_files:
        if os.path.exists(filename):
            print(f"\n🔍 {filename} のテスト開始")
            print("=" * 50)
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修理手順の抽出テスト
            print("\n🔧 修理手順抽出テスト:")
            repair_steps = extract_repair_steps_test(content)
            if repair_steps:
                print("✅ 修理手順抽出成功:")
                print(repair_steps[:200] + "..." if len(repair_steps) > 200 else repair_steps)
            else:
                print("❌ 修理手順抽出失敗")
            
            # 注意事項の抽出テスト
            print("\n⚠️ 注意事項抽出テスト:")
            warnings = extract_warnings_test(content)
            if warnings:
                print("✅ 注意事項抽出成功:")
                print(warnings[:200] + "..." if len(warnings) > 200 else warnings)
            else:
                print("❌ 注意事項抽出失敗")
            
            # 費用目安の抽出テスト
            print("\n💰 費用目安抽出テスト:")
            costs = extract_cost_information_test(content)
            if costs:
                print("✅ 費用目安抽出成功:")
                print(costs[:200] + "..." if len(costs) > 200 else costs)
            else:
                print("❌ 費用目安抽出失敗")
        else:
            print(f"❌ {filename} が見つかりません")

def extract_repair_steps_test(content):
    """テキストから修理手順を抽出（テスト版）"""
    import re
    
    # 修理手順セクションを検索
    patterns = [
        r'## 修理手順\s*\n(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'修理手順\s*\n(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'## 修理手順(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'修理手順(.*?)(?=\n##|\n⚠️|\n\*\*|$)'
    ]
    
    for pattern in patterns:
        steps_match = re.search(pattern, content, re.DOTALL)
        if steps_match:
            steps_section = steps_match.group(1).strip()
            
            # 手順情報を整理
            steps_lines = []
            for line in steps_section.split('\n'):
                line = line.strip()
                if line and not line.startswith('---'):
                    # 番号付きリスト（1. 2. 3. など）
                    if re.match(r'^\d+\.', line):
                        steps_lines.append(line)
                    # 箇条書き（• - * など）
                    elif re.match(r'^[•\-\*]\s', line):
                        steps_lines.append(line)
                    # 手順の見出し（**問題箇所の特定**など）
                    elif re.match(r'^\*\*.*\*\*', line):
                        steps_lines.append(line)
                    # 手順の詳細（- で始まる行）
                    elif line.startswith('- '):
                        steps_lines.append(line)
                    # 空行でない行
                    elif line:
                        steps_lines.append(line)
            
            if steps_lines:
                return '\n'.join(steps_lines)
    
    return None

def extract_warnings_test(content):
    """テキストから注意事項を抽出（テスト版）"""
    import re
    
    # 注意事項セクションを検索
    patterns = [
        r'## 注意事項\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'⚠️ 注意事項\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'注意事項\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'⚠️\s*(.*?)(?=\n##|\n\*\*|$)'
    ]
    
    for pattern in patterns:
        warnings_match = re.search(pattern, content, re.DOTALL)
        if warnings_match:
            warnings_section = warnings_match.group(1).strip()
            
            # 注意事項情報を整理
            warnings_lines = []
            for line in warnings_section.split('\n'):
                line = line.strip()
                if line and not line.startswith('---'):
                    # ⚠️ マークを含む行
                    if '⚠️' in line:
                        warnings_lines.append(line)
                    # 箇条書き（• - * など）
                    elif re.match(r'^[•\-\*]\s', line):
                        warnings_lines.append(line)
                    # 注意事項の見出し（**安全第一**など）
                    elif re.match(r'^\*\*.*\*\*', line):
                        warnings_lines.append(line)
                    # 注意事項の詳細（- で始まる行）
                    elif line.startswith('- '):
                        warnings_lines.append(line)
                    # 空行でない行
                    elif line:
                        warnings_lines.append(line)
            
            if warnings_lines:
                return '\n'.join(warnings_lines)
    
    return None

def extract_cost_information_test(content):
    """テキストから修理費用を抽出（テスト版）"""
    import re
    
    # 費用目安セクションを検索
    patterns = [
        r'## 修理費用目安\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'修理費用目安\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'## 修理費用目安(.*?)(?=\n##|\n\*\*|$)',
        r'修理費用目安(.*?)(?=\n##|\n\*\*|$)'
    ]
    
    for pattern in patterns:
        cost_match = re.search(pattern, content, re.DOTALL)
        if cost_match:
            cost_section = cost_match.group(1).strip()
            
            # 費用情報を整理
            cost_lines = [line.strip() for line in cost_section.split('\n') if line.strip() and '円' in line]
            
            if cost_lines:
                return '\n'.join(cost_lines)
    
    return None

if __name__ == "__main__":
    print("🚀 修理手順・注意事項抽出テスト開始")
    test_repair_extraction()
    print("\n✅ テスト完了")
