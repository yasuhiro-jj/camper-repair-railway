#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.envファイルのNOTION_API_KEYを確認し、実際に使用されているAPIキーをテストするスクリプト
"""

import os
import requests
from dotenv import load_dotenv

# .envファイルを明示的に読み込み
load_dotenv(override=True)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2022-06-28")

print("=" * 60)
print("🔍 .envファイルとAPIキーの確認")
print("=" * 60)

# .envファイルの内容を確認
env_file = ".env"
if os.path.exists(env_file):
    print(f"\n✅ .envファイルが見つかりました: {os.path.abspath(env_file)}")
    print("\n📋 .envファイルのNOTION_API_KEY設定:")
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if 'NOTION_API_KEY' in line and not line.strip().startswith('#'):
                    # マスクして表示
                    if '=' in line:
                        key, value = line.split('=', 1)
                        value = value.strip()
                        if value:
                            masked = value[:10] + "..." + value[-10:] if len(value) > 20 else value[:10] + "..."
                            print(f"   行{i}: {key}={masked}")
                            print(f"   実際の値（先頭）: {value[:15]}...")
                            print(f"   実際の値（末尾）: ...{value[-15:]}")
    except Exception as e:
        print(f"   ⚠️ 読み込みエラー: {e}")
else:
    print(f"\n❌ .envファイルが見つかりません")

print(f"\n📋 環境変数から読み込まれた値:")
if NOTION_API_KEY:
    print(f"   ✅ NOTION_API_KEYは設定されています")
    print(f"   先頭15文字: {NOTION_API_KEY[:15]}...")
    print(f"   末尾15文字: ...{NOTION_API_KEY[-15:]}")
    print(f"   長さ: {len(NOTION_API_KEY)}文字")
else:
    print(f"   ❌ NOTION_API_KEYが設定されていません")

# ユーザーが提供したAPIキーと比較
user_provided_key = "ntn_627215------QRquEZ9a8"
print(f"\n📋 ユーザーが提供したAPIキー:")
print(f"   先頭15文字: {user_provided_key[:15]}...")
print(f"   末尾15文字: ...{user_provided_key[-15:]}")
print(f"   長さ: {len(user_provided_key)}文字")

if NOTION_API_KEY:
    if NOTION_API_KEY.startswith(user_provided_key[:10]):
        print(f"\n✅ 環境変数のAPIキーは、提供されたキーと一致している可能性があります")
    else:
        print(f"\n⚠️ 環境変数のAPIキーが、提供されたキーと一致しません")
        print(f"   → .envファイルを確認して、正しいAPIキーが設定されているか確認してください")

# APIキーをテスト
print("\n" + "=" * 60)
print("🧪 APIキーのテスト")
print("=" * 60)

if NOTION_API_KEY:
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_API_VERSION,
    }
    
    try:
        print("\n📡 Notion APIに接続中...")
        resp = requests.get("https://api.notion.com/v1/users/me", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            user_data = resp.json()
            user_name = user_data.get('name', 'N/A')
            user_id = user_data.get('id', 'N/A')
            
            print(f"✅ APIキーは有効です")
            print(f"   ユーザー名: {user_name}")
            print(f"   ユーザーID: {user_id}")
            
            if "camper" in user_name.lower() or "repair" in user_name.lower() or "system" in user_name.lower():
                print(f"\n✅ これは「Camper Repair System」インテグレーションです！")
            elif "おおつき" in user_name or "チャットボット" in user_name:
                print(f"\n❌ これは「おおつきチャットボット３」インテグレーションです")
                print(f"   → .envファイルのNOTION_API_KEYを「Camper Repair System」のAPIキーに更新してください")
            else:
                print(f"\n⚠️ インテグレーション名を確認してください")
        else:
            print(f"❌ APIキーが無効です: {resp.status_code}")
            print(f"   レスポンス: {resp.text[:200]}")
    except Exception as e:
        print(f"❌ エラー: {e}")
else:
    print("\n⚠️ APIキーが設定されていないため、テストをスキップします")

print("\n" + "=" * 60)
print("💡 次のステップ")
print("=" * 60)

if NOTION_API_KEY and user_provided_key:
    if not NOTION_API_KEY.startswith(user_provided_key[:10]):
        print("""
1. .envファイルを開く
2. NOTION_API_KEYの行を見つける
3. 値を以下のように更新:
   NOTION_API_KEY=ntn_627215------QRquEZ9a8

4. ファイルを保存
5. サーバーを再起動（環境変数を読み込むため）
6. 再度 test_chat_logs_access.py を実行
""")

