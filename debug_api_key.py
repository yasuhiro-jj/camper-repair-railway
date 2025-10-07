#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIキーの詳細デバッグ
"""

import os
from config import OPENAI_API_KEY, SERP_API_KEY

print("=== APIキーデバッグ情報 ===")
print(f"config.py から読み込まれた OPENAI_API_KEY: {OPENAI_API_KEY}")
print(f"config.py から読み込まれた SERP_API_KEY: {SERP_API_KEY}")

print("\n=== 環境変数から直接確認 ===")
print(f"os.getenv('OPENAI_API_KEY'): {os.getenv('OPENAI_API_KEY')}")
print(f"os.getenv('SERP_API_KEY'): {os.getenv('SERP_API_KEY')}")

print("\n=== 環境変数一覧（OPENAI関連） ===")
for key, value in os.environ.items():
    if 'OPENAI' in key.upper() or 'API' in key.upper():
        print(f"{key}: {value[:20]}..." if len(value) > 20 else f"{key}: {value}")

print("\n=== プレースホルダーチェック ===")
if OPENAI_API_KEY and "your_" in OPENAI_API_KEY:
    print("❌ プレースホルダーが検出されました！")
    print("実際のAPIキーに置き換える必要があります。")
else:
    print("✅ プレースホルダーは検出されませんでした。")

# 実際のAPIキーを使用してテスト
if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
    print("\n=== OpenAI API接続テスト ===")
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model_name="gpt-4o-mini",
            temperature=0.1
        )
        
        response = llm.invoke("テスト")
        print(f"✅ API接続成功: {response.content[:50]}...")
        
    except Exception as e:
        print(f"❌ API接続エラー: {e}")
        print(f"エラーの詳細: {str(e)}")
else:
    print("❌ 有効なAPIキーが設定されていません")
