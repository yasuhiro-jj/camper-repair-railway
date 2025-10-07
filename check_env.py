#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境変数の確認スクリプト
"""

import os

print("=== 現在の環境変数確認 ===")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', '設定されていません')}")
print(f"SERP_API_KEY: {os.getenv('SERP_API_KEY', '設定されていません')}")

print("\n=== すべての環境変数（API関連） ===")
for key, value in os.environ.items():
    if 'OPENAI' in key.upper() or 'API' in key.upper() or 'SERP' in key.upper():
        print(f"{key}: {value}")

print("\n=== 解決方法 ===")
print("1. set_env_vars.batを実行して環境変数を設定")
print("2. または、コマンドプロンプトで直接設定:")
print("   set OPENAI_API_KEY=sk-your-actual-api-key-here")
print("3. アプリケーションを再起動")
