#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正規表現パターンのテスト
"""

import re

def test_repair_steps_patterns():
    """修理手順パターンのテスト"""
    print("🧪 修理手順正規表現パターンテスト")
    print("=" * 50)
    
    # テスト用の修理手順内容
    repair_steps_content = """## 修理手順

### 1. 問題箇所の特定
- 水の流れを追跡して浸入経路を特定
- 外側からの浸入経路確認（屋根、窓枠、ドア周辺）
- 内側からの水漏れ確認（配管、エアコンダクト）
- 配管の水漏れ確認（給水・排水配管）

### 2. 安全確認と準備
- 高所作業時の安全確保（安全帯の使用）
- 電気系統への水の侵入防止
- 作業工具の準備（シーリング材、パテ、ブラシ等）
- 保護具の着用（手袋、マスク、安全帽）"""
    
    # 修正されたパターン
    patterns = [
        "## 修理手順\\s*\\n(.*?)(?=\\n##|\\n⚠️|\\n\\*\\*|$)",
        "## 詳細修理手順\\s*\\n(.*?)(?=\\n##|\\n⚠️|\\n\\*\\*|$)",
        "## 手順\\s*\\n(.*?)(?=\\n##|\\n⚠️|\\n\\*\\*|$)",
        "## 修理手順(.*?)(?=\\n##|\\n⚠️|\\n\\*\\*|$)",
        "## 詳細修理手順(.*?)(?=\\n##|\\n⚠️|\\n\\*\\*|$)",
        "## 手順(.*?)(?=\\n##|\\n⚠️|\\n\\*\\*|$)"
    ]
    
    print(f"📄 テスト内容（最初の200文字）:")
    print(repair_steps_content[:200])
    print("...")
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\n🔍 パターン {i}: {pattern}")
        match = re.search(pattern, repair_steps_content, re.DOTALL)
        if match:
            print(f"  ✅ マッチ成功")
            extracted = match.group(1).strip()
            print(f"  📄 抽出内容（最初の100文字）: {extracted[:100]}...")
        else:
            print(f"  ❌ マッチ失敗")

def test_warnings_patterns():
    """注意事項パターンのテスト"""
    print("\n🧪 注意事項正規表現パターンテスト")
    print("=" * 50)
    
    # テスト用の注意事項内容
    warnings_content = """## 注意事項

⚠️ 安全第一で作業を行ってください

- 高所作業時は必ず安全帯を使用
- 電気系統への水の侵入に注意
- 応急処置後は必ず専門業者による点検を受ける
- シーリング材は適切な種類を選択する
- 作業前には必ず電源をOFFにする"""
    
    # 修正されたパターン
    patterns = [
        "## 注意事項\\s*\\n(.*?)(?=\\n##|\\n\\*\\*|$)",
        "## 安全上の注意事項\\s*\\n(.*?)(?=\\n##|\\n\\*\\*|$)",
        "## 注意\\s*\\n(.*?)(?=\\n##|\\n\\*\\*|$)",
        "⚠️ 注意事項\\s*\\n(.*?)(?=\\n##|\\n\\*\\*|$)"
    ]
    
    print(f"📄 テスト内容（最初の200文字）:")
    print(warnings_content[:200])
    print("...")
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\n🔍 パターン {i}: {pattern}")
        match = re.search(pattern, warnings_content, re.DOTALL)
        if match:
            print(f"  ✅ マッチ成功")
            extracted = match.group(1).strip()
            print(f"  📄 抽出内容（最初の100文字）: {extracted[:100]}...")
        else:
            print(f"  ❌ マッチ失敗")

if __name__ == "__main__":
    print("🚀 正規表現パターンテスト開始")
    print("=" * 60)
    
    test_repair_steps_patterns()
    test_warnings_patterns()
    
    print("\n🎉 テスト完了！")
