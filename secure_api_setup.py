#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セキュアなAPIキー設定スクリプト
"""

import os
import getpass

def secure_api_setup():
    print("=== セキュアなAPIキー設定 ===")
    print()
    print("このスクリプトは、APIキーを安全に設定します。")
    print("入力されたAPIキーは画面に表示されません。")
    print()
    
    # OpenAI APIキーの入力
    print("OpenAI APIキーを入力してください（sk-で始まる）:")
    openai_key = getpass.getpass("APIキー: ")
    
    if not openai_key.startswith('sk-'):
        print("❌ 無効なAPIキー形式です。sk-で始まる必要があります。")
        return
    
    # 環境変数として設定
    os.environ['OPENAI_API_KEY'] = openai_key
    
    # SERP APIキーの入力（オプション）
    print("\nSERP APIキーを入力してください（オプション、Enterでスキップ）:")
    serp_key = getpass.getpass("SERP APIキー: ")
    
    if serp_key:
        os.environ['SERP_API_KEY'] = serp_key
    
    print("\n✅ 環境変数が設定されました")
    print("⚠️ 注意：この設定は現在のセッションでのみ有効です")
    print("永続的に設定するには、システム環境変数として設定してください")
    
    # 接続テスト
    print("\n=== API接続テスト ===")
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            api_key=openai_key,
            model_name="gpt-4o-mini",
            temperature=0.1
        )
        
        response = llm.invoke("テスト")
        print(f"✅ API接続成功: {response.content}")
        
    except Exception as e:
        print(f"❌ API接続エラー: {e}")

if __name__ == "__main__":
    secure_api_setup()
