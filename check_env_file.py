#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.envファイルの内容を確認するスクリプト
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """.envファイルの内容を確認"""
    print("="*60)
    print("🔍 .envファイルの確認")
    print("="*60)
    print()
    
    # 現在のディレクトリを確認
    current_dir = Path.cwd()
    print(f"📁 現在のディレクトリ: {current_dir}")
    print()
    
    # .envファイルのパス
    env_file = current_dir / ".env"
    
    if not env_file.exists():
        print("❌ .envファイルが見つかりません")
        print(f"   パス: {env_file}")
        return
    
    print(f"✅ .envファイルが見つかりました: {env_file}")
    print()
    
    # .envファイルの内容を読み込む
    load_dotenv(env_file)
    
    # NOTION_API_KEYを取得
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_token = os.getenv("NOTION_TOKEN")
    
    print("📋 環境変数の確認:")
    print(f"   NOTION_API_KEY: {'設定済み' if notion_api_key else '未設定'}")
    print(f"   NOTION_TOKEN: {'設定済み' if notion_token else '未設定'}")
    print()
    
    # 実際に使用されるトークン
    actual_token = notion_api_key or notion_token
    
    if actual_token:
        # トークンの最初の20文字を表示
        token_preview = actual_token[:20] + "..." if len(actual_token) > 20 else actual_token
        print(f"📝 使用されるトークン（最初の20文字）: {token_preview}")
        print(f"   トークンの長さ: {len(actual_token)}文字")
        
        # トークンの形式を確認
        if actual_token.startswith("secret_"):
            print(f"   形式: Internal Integration Token (secret_)")
        elif actual_token.startswith("ntn_"):
            print(f"   形式: OAuth Access Token (ntn_)")
        else:
            print(f"   ⚠️  予期しない形式です")
        
        print()
        print("💡 このトークンでAPI接続をテストします...")
        print()
        
        # API接続テスト
        import requests
        headers = {
            "Authorization": f"Bearer {actual_token}",
            "Notion-Version": "2022-06-28"
        }
        
        try:
            response = requests.get("https://api.notion.com/v1/users/me", headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                user_name = user_data.get('name', 'N/A')
                print(f"✅ API接続成功")
                print(f"   ユーザー名: {user_name}")
                
                if "camper" in user_name.lower() or "repair" in user_name.lower() or "system" in user_name.lower():
                    print(f"\n✅ 正しいインテグレーション（Camper Repair System）が使用されています！")
                elif "おおつき" in user_name or "チャットボット" in user_name:
                    print(f"\n❌ まだ「おおつきチャットボット３」のトークンが使用されています")
                    print(f"\n🔧 解決方法:")
                    print(f"   1. .envファイルのNOTION_API_KEYを確認")
                    print(f"   2. 「Camper Repair System」のトークンに変更")
                    print(f"   3. ファイルを保存（Ctrl+S）")
                    print(f"   4. バックエンドサーバーを再起動（環境変数を読み込むため）")
                    print(f"   5. 再度このスクリプトを実行")
                else:
                    print(f"\n⚠️  インテグレーション名: {user_name}")
            else:
                print(f"❌ API接続エラー: {response.status_code}")
                print(f"   レスポンス: {response.text[:200]}")
        except Exception as e:
            print(f"❌ エラー: {e}")
    else:
        print("❌ NOTION_API_KEYまたはNOTION_TOKENが設定されていません")
        print()
        print("💡 解決方法:")
        print("   1. .envファイルにNOTION_API_KEYを設定してください")
        print("   2. 例: NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    print()
    print("="*60)
    print("📝 .envファイルの内容（NOTION_API_KEYの行のみ）:")
    print("="*60)
    
    # .envファイルの内容を読み込んで表示
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            found_lines = []
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if 'NOTION_API_KEY' in line_stripped or 'NOTION_TOKEN' in line_stripped:
                    found_lines.append((i, line_stripped))
            
            if found_lines:
                for line_num, line_content in found_lines:
                    # トークンの一部をマスク
                    if '=' in line_content:
                        key, value = line_content.split('=', 1)
                        value = value.strip()
                        if value:
                            # 最初の15文字と最後の5文字を表示
                            if len(value) > 20:
                                masked_value = value[:15] + "..." + value[-5:]
                            else:
                                masked_value = value
                            print(f"   行{line_num}: {key}={masked_value}")
                            print(f"       完全な値: {value}")
                        else:
                            print(f"   行{line_num}: {line_content} (値が空)")
                    else:
                        print(f"   行{line_num}: {line_content}")
            else:
                print("   ⚠️  NOTION_API_KEYまたはNOTION_TOKENの行が見つかりませんでした")
    except Exception as e:
        print(f"   ❌ ファイル読み込みエラー: {e}")
    
    print()
    print("="*60)
    print("🔍 比較:")
    print("="*60)
    print(f"   .envファイルから読み込まれたトークン: {actual_token[:20] if actual_token else 'なし'}...")
    print(f"   期待されるトークン（Camper Repair System）: ntn_627215497511qG27b0j4...")
    print()
    
    if actual_token and actual_token.startswith("ntn_627215497511qG27b0j4"):
        print("✅ 正しいトークン（Camper Repair System）が設定されています！")
        print("   しかし、まだ「おおつきチャットボット３」と表示される場合:")
        print("   1. バックエンドサーバーを再起動してください")
        print("   2. Pythonプロセスを再起動してください")
        print("   3. 環境変数のキャッシュをクリアしてください")
    elif actual_token and actual_token.startswith("ntn_62721549751923qI"):
        print("❌ まだ古いトークン（おおつきチャットボット３）が使用されています")
        print("   .envファイルを確認して、正しいトークンに更新してください")
    else:
        print("⚠️  トークンの形式を確認してください")

if __name__ == "__main__":
    check_env_file()
