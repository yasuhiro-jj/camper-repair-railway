#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.envファイルの実際の内容を確認するスクリプト
"""

from pathlib import Path

def main():
    """メイン処理"""
    print("="*60)
    print("🔍 .envファイルの実際の内容を確認")
    print("="*60)
    print()
    
    # 現在のディレクトリを確認
    current_dir = Path.cwd()
    env_file = current_dir / ".env"
    
    print(f"📁 .envファイルのパス: {env_file}")
    print(f"   存在: {'✅' if env_file.exists() else '❌'}")
    print()
    
    if not env_file.exists():
        print("❌ .envファイルが見つかりません")
        return
    
    # .envファイルの内容を直接読み込む
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📝 .envファイルの総行数: {len(lines)}")
        print()
        print("="*60)
        print("📋 NOTION_API_KEYとNOTION_TOKENの行:")
        print("="*60)
        
        found_any = False
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            # コメント行をスキップ
            if line_stripped.startswith('#'):
                continue
            
            if 'NOTION_API_KEY' in line_stripped or 'NOTION_TOKEN' in line_stripped:
                found_any = True
                print(f"\n行{i}: {line_stripped}")
                
                if '=' in line_stripped:
                    key, value = line_stripped.split('=', 1)
                    value = value.strip()
                    
                    if value:
                        print(f"   キー: {key}")
                        print(f"   値の最初の25文字: {value[:25]}...")
                        print(f"   値の最後の10文字: ...{value[-10:]}")
                        print(f"   完全な値: {value}")
                        print(f"   値の長さ: {len(value)}文字")
                        
                        # 期待されるトークンと比較
                        expected_start = "ntn_627215497511qG27b0j4"
                        if value.startswith(expected_start):
                            print(f"   ✅ 正しいトークン（Camper Repair System）です！")
                        elif value.startswith("ntn_62721549751923qI"):
                            print(f"   ❌ 古いトークン（おおつきチャットボット３）です")
                            print(f"   → この行を削除またはコメントアウトしてください")
                        else:
                            print(f"   ⚠️  予期しないトークンです")
                    else:
                        print(f"   ⚠️  値が空です")
        
        if not found_any:
            print("   ⚠️  NOTION_API_KEYまたはNOTION_TOKENの行が見つかりませんでした")
        
        print()
        print("="*60)
        print("💡 推奨される設定:")
        print("="*60)
        print("   NOTION_API_KEY=ntn_627215497511qG27b0j4...（Camper Repair Systemのトークン）")
        print()
        print("   注意:")
        print("   - NOTION_API_KEYとNOTION_TOKENの両方が設定されている場合、NOTION_API_KEYが優先されます")
        print("   - 古いトークンの行は削除またはコメントアウトしてください")
        print("   - ファイルを保存した後、Pythonプロセスを再起動してください")
        
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")

if __name__ == "__main__":
    main()

