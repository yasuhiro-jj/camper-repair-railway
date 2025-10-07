#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIキーの設定確認テスト
"""

import os
from config import OPENAI_API_KEY, SERP_API_KEY

print("=== APIキー設定確認 ===")
print(f"OPENAI_API_KEY: {OPENAI_API_KEY[:10]}..." if OPENAI_API_KEY else "OPENAI_API_KEY: 未設定")
print(f"SERP_API_KEY: {SERP_API_KEY[:10]}..." if SERP_API_KEY else "SERP_API_KEY: 未設定")

# 環境変数から直接確認
print("\n=== 環境変数から直接確認 ===")
env_openai = os.getenv("OPENAI_API_KEY")
print(f"環境変数 OPENAI_API_KEY: {env_openai[:10]}..." if env_openai else "環境変数 OPENAI_API_KEY: 未設定")

# OpenAI API接続テスト
if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
    print("\n=== OpenAI API接続テスト ===")
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model_name="gpt-4o-mini",
            temperature=0.1
        )
        
        response = llm.invoke("こんにちは")
        print(f"✅ OpenAI API接続成功: {response.content[:50]}...")
        
    except Exception as e:
        print(f"❌ OpenAI API接続エラー: {e}")
else:
    print("❌ OpenAI APIキーが正しく設定されていません")
