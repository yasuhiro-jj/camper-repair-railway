#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ローカルでのデプロイ前テストスクリプト
"""

import os
import sys
import subprocess
import importlib.util

def test_imports():
    """必要なモジュールのインポートテスト"""
    print("🔍 必要なモジュールのインポートテスト...")
    
    required_modules = [
        'streamlit',
        'langchain',
        'langchain_openai', 
        'dotenv',
        'notion_client',
        'aiohttp'
    ]
    
    failed_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n💥 失敗したモジュール: {failed_modules}")
        print("💡 以下のコマンドでインストールしてください:")
        print("pip install -r requirements_deploy.txt")
        return False
    
    print("✅ すべてのモジュールが正常にインポートできました")
    return True

def test_main_app():
    """メインアプリのインポートテスト"""
    print("\n🔍 メインアプリのインポートテスト...")
    
    try:
        # streamlit_app_advanced.pyをインポート
        spec = importlib.util.spec_from_file_location("streamlit_app_advanced", "streamlit_app_advanced.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        print("✅ streamlit_app_advanced.py のインポート成功")
        return True
        
    except Exception as e:
        print(f"❌ streamlit_app_advanced.py のインポート失敗: {e}")
        return False

def test_conversation_memory():
    """会話メモリ機能のテスト"""
    print("\n🔍 会話メモリ機能のテスト...")
    
    try:
        from conversation_memory import NaturalConversationManager
        print("✅ conversation_memory.py のインポート成功")
        
        # OpenAI APIキーの確認
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("✅ OpenAI APIキーが設定されています")
        else:
            print("⚠️ OpenAI APIキーが設定されていません（.envファイルを確認してください）")
        
        return True
        
    except Exception as e:
        print(f"❌ conversation_memory.py のインポート失敗: {e}")
        return False

def test_data_access():
    """データアクセス層のテスト"""
    print("\n🔍 データアクセス層のテスト...")
    
    try:
        from data_access.notion_client import NotionClient
        print("✅ NotionClient のインポート成功")
        
        # Notion APIキーの確認
        notion_key = os.getenv("NOTION_API_KEY")
        if notion_key:
            print("✅ Notion APIキーが設定されています")
        else:
            print("⚠️ Notion APIキーが設定されていません（オプション機能）")
        
        return True
        
    except Exception as e:
        print(f"❌ データアクセス層のインポート失敗: {e}")
        return False

def test_streamlit_config():
    """Streamlit設定のテスト"""
    print("\n🔍 Streamlit設定のテスト...")
    
    config_file = ".streamlit/config.toml"
    if os.path.exists(config_file):
        print("✅ .streamlit/config.toml が存在します")
        return True
    else:
        print("❌ .streamlit/config.toml が見つかりません")
        return False

def test_requirements():
    """requirements.txtのテスト"""
    print("\n🔍 requirements.txtのテスト...")
    
    req_file = "requirements_deploy.txt"
    if os.path.exists(req_file):
        print("✅ requirements_deploy.txt が存在します")
        
        # ファイル内容の確認
        with open(req_file, 'r') as f:
            content = f.read()
            print("📋 依存関係:")
            for line in content.strip().split('\n'):
                if line.strip():
                    print(f"   • {line.strip()}")
        
        return True
    else:
        print("❌ requirements_deploy.txt が見つかりません")
        return False

def main():
    """メインテスト関数"""
    print("🚀 Streamlit Cloud デプロイ前テストを開始...\n")
    
    tests = [
        test_imports,
        test_main_app,
        test_conversation_memory,
        test_data_access,
        test_streamlit_config,
        test_requirements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"💥 テスト実行エラー: {e}")
    
    print(f"\n📊 テスト結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 すべてのテストが通過しました！デプロイ準備完了です。")
        print("\n🚀 次のステップ:")
        print("1. GitHubにリポジトリを作成")
        print("2. プロジェクトをアップロード")
        print("3. Streamlit Cloudでデプロイ")
        print("4. シークレット（環境変数）を設定")
        return True
    else:
        print("💥 一部のテストが失敗しました。デプロイ前に修正してください。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
