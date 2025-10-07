#!/usr/bin/env python3
"""
修正されたアプリケーションのテストスクリプト
"""

import os
import sys

def test_imports():
    """必要なモジュールのインポートテスト"""
    print("=== インポートテスト ===")
    
    try:
        import streamlit as st
        print("✅ streamlit: OK")
    except ImportError as e:
        print(f"❌ streamlit: {e}")
        return False
    
    try:
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        print("✅ langchain_openai: OK")
    except ImportError as e:
        print(f"❌ langchain_openai: {e}")
        return False
    
    try:
        from langchain_core.messages import HumanMessage, AIMessage
        print("✅ langchain_core.messages: OK")
    except ImportError as e:
        print(f"❌ langchain_core.messages: {e}")
        return False
    
    try:
        from notion_client import Client
        print("✅ notion_client: OK")
    except ImportError as e:
        print(f"⚠️ notion_client: {e} (オプション)")
    
    # ChromaDBのインポートテスト（環境にインストールされていても問題なし）
    try:
        from langchain_chroma import Chroma
        print("⚠️ langchain_chroma: 環境にインストール済み（アプリでは無効化）")
    except ImportError:
        print("✅ langchain_chroma: インストールされていない")
    
    return True

def test_app_module():
    """アプリケーションモジュールのテスト"""
    print("\n=== アプリケーションモジュールテスト ===")
    
    try:
        import streamlit_app_with_blog_links
        print("✅ streamlit_app_with_blog_links: インポート成功")
        
        # 主要な関数が存在することを確認
        if hasattr(streamlit_app_with_blog_links, 'get_relevant_blog_links'):
            print("✅ get_relevant_blog_links: 関数存在")
        else:
            print("❌ get_relevant_blog_links: 関数が見つかりません")
            return False
        
        if hasattr(streamlit_app_with_blog_links, 'generate_ai_response_with_rag'):
            print("✅ generate_ai_response_with_rag: 関数存在")
        else:
            print("❌ generate_ai_response_with_rag: 関数が見つかりません")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ streamlit_app_with_blog_links: {e}")
        return False

def test_blog_links():
    """ブログリンク機能のテスト"""
    print("\n=== ブログリンク機能テスト ===")
    
    try:
        import streamlit_app_with_blog_links
        
        # テストクエリ
        test_queries = [
            "バッテリーが上がった",
            "水道ポンプが動かない",
            "ガスコンロに火がつかない"
        ]
        
        for query in test_queries:
            links = streamlit_app_with_blog_links.get_relevant_blog_links(query)
            print(f"✅ '{query}': {len(links)}件の関連ブログを取得")
            
            for link in links:
                print(f"   - {link['title']}: {link['url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ブログリンク機能: {e}")
        return False

def main():
    """メイン関数"""
    print("キャンピングカー修理アプリケーション - 修正テスト")
    print("=" * 50)
    
    # 環境変数の確認
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY: 設定済み")
    else:
        print("⚠️ OPENAI_API_KEY: 未設定（一部機能が制限されます）")
    
    notion_token = os.getenv("NOTION_TOKEN")
    if notion_token:
        print("✅ NOTION_TOKEN: 設定済み")
    else:
        print("⚠️ NOTION_TOKEN: 未設定（Notion機能が制限されます）")
    
    # テスト実行
    tests = [
        test_imports,
        test_app_module,
        test_blog_links
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 すべてのテストが成功しました！")
        print("アプリケーションは正常に動作するはずです。")
    else:
        print("❌ 一部のテストが失敗しました。")
        print("問題を修正してから再実行してください。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
