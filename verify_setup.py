#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定確認スクリプト
"""

import os
from config import OPENAI_API_KEY

def verify_setup():
    print("=== 設定確認 ===")
    print()
    
    # 環境変数の確認
    print("1. 環境変数の確認:")
    print(f"   OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', '設定されていません')}")
    print(f"   SERP_API_KEY: {os.getenv('SERP_API_KEY', '設定されていません')}")
    print()
    
    # config.pyからの読み込み確認
    print("2. config.pyからの読み込み:")
    print(f"   OPENAI_API_KEY: {OPENAI_API_KEY}")
    print()
    
    # APIキーの形式確認
    if OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-'):
        print("✅ APIキーの形式が正しいです")
        
        # 接続テスト
        print("\n3. API接続テスト:")
        try:
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model_name="gpt-4o-mini",
                temperature=0.1
            )
            
            response = llm.invoke("テスト")
            print(f"✅ API接続成功: {response.content}")
            
        except Exception as e:
            print(f"❌ API接続エラー: {e}")
            print("APIキーが正しいか確認してください")
    else:
        print("❌ APIキーが正しく設定されていません")
        print("sk-で始まる形式のAPIキーを設定してください")

if __name__ == "__main__":
    verify_setup()
