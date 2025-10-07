#!/usr/bin/env python3
"""
開発者認証テストスクリプト
"""

import os
import streamlit as st
from dotenv import load_dotenv

def test_developer_auth():
    """開発者認証のテスト"""
    print("🔍 開発者認証テスト開始")
    
    # .envファイルを読み込み
    try:
        load_dotenv()
        print("✅ .envファイルを読み込みました")
    except Exception as e:
        print(f"❌ .envファイルの読み込みに失敗: {e}")
    
    # 環境変数からパスワードを取得
    dev_password_env = os.getenv("DEVELOPER_PASSWORD", "")
    print(f"環境変数パスワード: '{dev_password_env}' (長さ: {len(dev_password_env)})")
    
    # Streamlitシークレットからパスワードを取得（モック）
    try:
        # 実際のStreamlitシークレットをシミュレート
        dev_password_secret = "nre03851"  # .streamlit/secrets.tomlの値
        print(f"シークレットパスワード: '{dev_password_secret}' (長さ: {len(dev_password_secret)})")
    except Exception as e:
        print(f"❌ シークレットの読み込みに失敗: {e}")
        dev_password_secret = ""
    
    # 最終パスワードを決定
    dev_password = dev_password_env or dev_password_secret
    print(f"最終パスワード: '{dev_password}' (長さ: {len(dev_password)})")
    
    # テストパスワード
    test_passwords = [
        "nre03851",
        "nre03851 ",
        " nre03851",
        " nre03851 ",
        "NRE03851",
        "nre03852",
        "",
        None
    ]
    
    print("\n🔑 パスワード認証テスト:")
    for i, test_pwd in enumerate(test_passwords, 1):
        if test_pwd is None:
            test_pwd = ""
        
        # パスワードの前処理
        test_pwd_clean = test_pwd.strip() if test_pwd else ""
        dev_password_clean = dev_password.strip() if dev_password else ""
        
        # 複数の比較方法
        exact_match = test_pwd == dev_password
        clean_match = test_pwd_clean == dev_password_clean
        mixed_match = test_pwd_clean == dev_password or test_pwd == dev_password_clean
        
        result = "✅ 成功" if (exact_match or clean_match or mixed_match) else "❌ 失敗"
        
        print(f"{i}. テストパスワード: '{test_pwd}' -> {result}")
        print(f"   完全一致: {exact_match}")
        print(f"   クリーン一致: {clean_match}")
        print(f"   混合一致: {mixed_match}")
        print()
    
    # 文字コードの比較
    if dev_password:
        print("🔍 設定パスワードの文字コード:")
        for i, char in enumerate(dev_password):
            print(f"  文字{i+1}: '{char}' -> {ord(char)}")
    
    print("\n✅ テスト完了")

if __name__ == "__main__":
    test_developer_auth()
