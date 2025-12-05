#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.envファイルに設定されているトークンを確認し、API接続をテストするスクリプト
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests

def main():
    """メイン処理"""
    print("="*60)
    print("🔍 .envファイルのトークン確認とAPI接続テスト")
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
    
    # .envファイルを再読み込み（強制的に）
    load_dotenv(env_file, override=True)
    
    # トークンを取得
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_token = os.getenv("NOTION_TOKEN")
    actual_token = notion_api_key or notion_token
    
    print("📋 環境変数の確認:")
    print(f"   NOTION_API_KEY: {'設定済み' if notion_api_key else '未設定'}")
    print(f"   NOTION_TOKEN: {'設定済み' if notion_token else '未設定'}")
    print()
    
    if not actual_token:
        print("❌ トークンが見つかりません")
        return
    
    # トークンの最初と最後を表示
    token_preview = actual_token[:20] + "..." + actual_token[-10:] if len(actual_token) > 30 else actual_token
    print(f"📝 使用されるトークン:")
    print(f"   最初の20文字: {actual_token[:20]}...")
    print(f"   最後の10文字: ...{actual_token[-10:]}")
    print(f"   完全なトークン: {actual_token}")
    print()
    
    # トークンの形式を確認
    if actual_token.startswith("secret_"):
        print(f"   形式: Internal Integration Token (secret_)")
    elif actual_token.startswith("ntn_"):
        print(f"   形式: OAuth Access Token (ntn_)")
        print(f"   トークンの開始部分: {actual_token[:20]}")
    else:
        print(f"   ⚠️  予期しない形式です")
    
    print()
    print("="*60)
    print("📡 API接続テスト")
    print("="*60)
    print()
    
    # API接続テスト
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
            print()
            
            # トークンの比較（最初の20文字で比較）
            expected_token_start = "ntn_627215497511qG27"
            actual_token_start = actual_token[:20]  # 最初の20文字を比較
            
            print("="*60)
            print("🔍 トークンの比較")
            print("="*60)
            print(f"   .envファイルのトークン（最初の20文字）: {actual_token_start}")
            print(f"   期待されるトークン（Camper Repair System）: {expected_token_start}")
            print()
            
            # ユーザー名で判定（より確実）
            if "camper" in user_name.lower() or "repair" in user_name.lower() or "system" in user_name.lower():
                print("✅ 正しいインテグレーション（Camper Repair System）が使用されています！")
                print()
                print("🎯 次のステップ:")
                print("   1. python check_notion_db_access.py を実行")
                print("   2. データベースへのアクセスを確認")
            elif "おおつき" in user_name or "チャットボット" in user_name:
                print("❌ まだ「おおつきチャットボット３」のトークンが使用されています")
                print()
                print("💡 解決方法:")
                print("   1. .envファイルのNOTION_API_KEYを確認")
                print("   2. 「Camper Repair System」のトークンに変更")
                print("   3. ファイルを保存（Ctrl+S）")
                print("   4. Pythonプロセスを完全に終了")
                print("   5. 新しいターミナルで再度テスト")
            else:
                # トークンの開始部分で判定（補助的な確認）
                if actual_token_start.startswith(expected_token_start[:15]):
                    print("✅ トークンの開始部分が一致しています")
                    print("   ユーザー名で確認してください")
                else:
                    print("⚠️  トークンの開始部分が一致しません")
                    print("   ユーザー名で確認してください")
        else:
            print(f"❌ API接続エラー")
            print(f"   ステータスコード: {response.status_code}")
            error_data = response.json() if response.text else {}
            print(f"   エラーコード: {error_data.get('code', 'N/A')}")
            print(f"   エラーメッセージ: {error_data.get('message', response.text)}")
            
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()

