#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
検索機能のデバッグスクリプト
"""

import requests
import json

def test_search_api():
    """検索APIをテストする"""
    print("🔍 検索APIテストを開始...")
    
    base_url = "http://localhost:5000"
    
    # ヘルスチェック
    try:
        print("🏥 ヘルスチェック中...")
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ サーバー状態: {health_data}")
        else:
            print(f"❌ ヘルスチェック失敗: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ サーバーに接続できません: {e}")
        print("💡 app.pyが起動しているか確認してください")
        return False
    
    # 雨漏り検索テスト
    try:
        print("\n🔍 雨漏り検索テスト中...")
        search_data = {"query": "雨漏り"}
        search_response = requests.post(
            f"{base_url}/api/search",
            json=search_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 検索レスポンス: {search_response.status_code}")
        
        if search_response.status_code == 200:
            result = search_response.json()
            print("✅ 検索成功:")
            print(f"  - success: {result.get('success', 'N/A')}")
            print(f"  - results: {len(result.get('results', []))}件")
            print(f"  - query: {result.get('query', 'N/A')}")
            
            if result.get('results'):
                print("📋 検索結果の詳細:")
                for i, res in enumerate(result['results'][:3]):
                    print(f"  {i+1}. {res.get('title', 'N/A')[:50]}...")
        else:
            print(f"❌ 検索失敗: {search_response.status_code}")
            print(f"エラー内容: {search_response.text}")
            
    except Exception as e:
        print(f"❌ 検索APIエラー: {e}")
    
    # テキストファイル検索テスト
    try:
        print("\n📄 テキストファイル検索テスト中...")
        text_search_data = {"query": "雨漏り"}
        text_response = requests.post(
            f"{base_url}/api/search_text_files",
            json=text_search_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 テキスト検索レスポンス: {text_response.status_code}")
        
        if text_response.status_code == 200:
            result = text_response.json()
            print("✅ テキスト検索成功:")
            print(f"  - success: {result.get('success', 'N/A')}")
            print(f"  - results: {len(result.get('results', []))}件")
        else:
            print(f"❌ テキスト検索失敗: {text_response.status_code}")
            print(f"エラー内容: {text_response.text}")
            
    except Exception as e:
        print(f"❌ テキスト検索APIエラー: {e}")
    
    return True

if __name__ == "__main__":
    test_search_api()
