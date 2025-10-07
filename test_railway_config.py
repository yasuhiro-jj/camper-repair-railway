#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Railwayデプロイ設定テストスクリプト
"""

import os
import sys
from pathlib import Path

def test_railway_config():
    """Railwayデプロイ設定をテスト"""
    print("🚀 Railwayデプロイ設定テスト開始")
    print("=" * 50)
    
    # 1. 必要なファイルの存在確認
    required_files = [
        "unified_backend_api.py",
        "requirements_railway.txt",
        "Procfile",
        "railway.json",
        "templates/unified_chatbot.html"
    ]
    
    print("📁 ファイル存在確認:")
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - 見つかりません")
            return False
    
    # 2. requirements.txtの内容確認
    print("\n📦 requirements.txt確認:")
    try:
        with open("requirements_railway.txt", "r") as f:
            requirements = f.read()
            if "Flask" in requirements and "gunicorn" in requirements:
                print("  ✅ 必要な依存関係が含まれています")
            else:
                print("  ❌ 必要な依存関係が不足しています")
                return False
    except Exception as e:
        print(f"  ❌ requirements.txt読み込みエラー: {e}")
        return False
    
    # 3. Procfileの内容確認
    print("\n🔧 Procfile確認:")
    try:
        with open("Procfile", "r") as f:
            procfile = f.read()
            if "gunicorn" in procfile and "unified_backend_api:app" in procfile:
                print("  ✅ Procfileが正しく設定されています")
            else:
                print("  ❌ Procfileの設定に問題があります")
                return False
    except Exception as e:
        print(f"  ❌ Procfile読み込みエラー: {e}")
        return False
    
    # 4. 環境変数の確認
    print("\n🔑 環境変数確認:")
    required_env_vars = [
        "OPENAI_API_KEY",
        "NOTION_API_KEY", 
        "NOTION_DATABASE_ID"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if os.getenv(var):
            print(f"  ✅ {var} - 設定済み")
        else:
            print(f"  ❌ {var} - 未設定")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ 未設定の環境変数: {', '.join(missing_vars)}")
        print("Railwayデプロイ時に設定してください")
    
    # 5. Flaskアプリのインポートテスト
    print("\n🐍 Flaskアプリテスト:")
    try:
        sys.path.append('.')
        import unified_backend_api
        print("  ✅ unified_backend_api.pyのインポート成功")
    except Exception as e:
        print(f"  ❌ unified_backend_api.pyのインポートエラー: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Railwayデプロイ設定テスト完了！")
    print("✅ 全ての設定が正しく構成されています")
    print("\n📋 次のステップ:")
    print("1. git add . && git commit -m 'Railway deployment ready'")
    print("2. git push origin main")
    print("3. Railway.appでデプロイ開始")
    
    return True

if __name__ == "__main__":
    success = test_railway_config()
    if not success:
        print("\n❌ 設定に問題があります。修正してから再実行してください。")
        sys.exit(1)
    else:
        print("\n🚀 Railwayデプロイの準備が完了しました！")
