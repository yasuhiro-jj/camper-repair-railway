#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API接続テスト
"""

import os
from config import OPENAI_API_KEY

print("=== API接続テスト ===")
print(f"設定されたAPIキー: {OPENAI_API_KEY[:20]}..." if OPENAI_API_KEY and len(OPENAI_API_KEY) > 20 else f"設定されたAPIキー: {OPENAI_API_KEY}")

if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_ACTUAL_API_KEY_HERE":
    print("❌ APIキーが設定されていません")
    print("set_env_vars.batを実行するか、環境変数を手動で設定してください")
else:
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model_name="gpt-4o-mini",
            temperature=0.1
        )
        
        response = llm.invoke("こんにちは")
        print(f"✅ API接続成功: {response.content}")
        
    except Exception as e:
        print(f"❌ API接続エラー: {e}")
        print("APIキーが正しく設定されているか確認してください")
