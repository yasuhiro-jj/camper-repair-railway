#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERP検索のデバッグスクリプト
"""

import os
import requests
import json
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

def debug_google_custom_search():
    """Google Custom Search APIのデバッグ"""
    print("🔍 Google Custom Search APIのデバッグを開始します...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if not api_key or not cse_id:
        print("❌ Google API KeyまたはCSE IDが設定されていません")
        return
    
    print(f"✅ API Key: {api_key[:10]}...")
    print(f"✅ CSE ID: {cse_id}")
    
    # テストクエリ
    test_queries = [
        "キャンピングカー バッテリー",
        "RV battery replacement",
        "camper van repair",
        "バッテリー 交換"
    ]
    
    for query in test_queries:
        print(f"\n🔍 テストクエリ: {query}")
        
        # 基本的な検索パラメータ
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': query,
            'num': 5,
            'lr': 'lang_ja',
            'safe': 'medium'
        }
        
        try:
            response = requests.get(
                'https://www.googleapis.com/customsearch/v1',
                params=params,
                timeout=10
            )
            
            print(f"📊 レスポンスステータス: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # 検索情報の表示
                search_info = data.get('searchInformation', {})
                print(f"📈 検索時間: {search_info.get('searchTime', 'N/A')}秒")
                print(f"📊 総結果数: {search_info.get('totalResults', 'N/A')}")
                
                # 結果の表示
                items = data.get('items', [])
                print(f"📄 取得結果数: {len(items)}")
                
                for i, item in enumerate(items[:3]):
                    print(f"   {i+1}. {item.get('title', 'N/A')[:60]}...")
                    print(f"      🔗 {item.get('link', 'N/A')}")
                    print(f"      📝 {item.get('snippet', 'N/A')[:100]}...")
                
                if len(items) == 0:
                    print("⚠️ 検索結果が0件です")
                    # エラー情報の確認
                    if 'error' in data:
                        print(f"❌ エラー: {data['error']}")
                    
            else:
                print(f"❌ エラー: {response.status_code}")
                print(f"レスポンス: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ 例外エラー: {str(e)}")

def debug_serp_api():
    """SERP APIのデバッグ"""
    print("\n🔍 SERP APIのデバッグを開始します...")
    
    api_key = os.getenv("SERP_API_KEY")
    
    if not api_key:
        print("❌ SERP API Keyが設定されていません")
        return
    
    print(f"✅ SERP API Key: {api_key[:10]}...")
    
    # テストクエリ
    test_query = "キャンピングカー バッテリー 交換"
    
    params = {
        'api_key': api_key,
        'q': test_query,
        'engine': 'google',
        'gl': 'jp',
        'hl': 'ja',
        'num': 5
    }
    
    try:
        response = requests.get(
            'https://serpapi.com/search',
            params=params,
            timeout=10
        )
        
        print(f"📊 レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 検索情報の表示
            search_info = data.get('search_information', {})
            print(f"📈 検索時間: {search_info.get('total_time_taken', 'N/A')}秒")
            
            # 結果の表示
            organic_results = data.get('organic_results', [])
            print(f"📄 取得結果数: {len(organic_results)}")
            
            for i, result in enumerate(organic_results[:3]):
                print(f"   {i+1}. {result.get('title', 'N/A')[:60]}...")
                print(f"      🔗 {result.get('link', 'N/A')}")
                print(f"      📝 {result.get('snippet', 'N/A')[:100]}...")
                
        else:
            print(f"❌ エラー: {response.status_code}")
            print(f"レスポンス: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 例外エラー: {str(e)}")

def test_simple_search():
    """シンプルな検索テスト"""
    print("\n🔍 シンプルな検索テストを開始します...")
    
    try:
        from serp_search_system import get_serp_search_system
        
        serp_system = get_serp_search_system()
        
        # シンプルなクエリでテスト
        simple_queries = [
            "バッテリー",
            "battery",
            "修理",
            "repair"
        ]
        
        for query in simple_queries:
            print(f"\n🔍 シンプルクエリ: {query}")
            
            # Google Custom Searchを直接テスト
            if serp_system.search_engines['google_custom']['enabled']:
                results = serp_system._search_google_custom(query, 'general_info')
                print(f"📄 Google Custom Search結果: {len(results)}件")
                
                for i, result in enumerate(results[:2]):
                    print(f"   {i+1}. {result.get('title', 'N/A')[:50]}...")
                    print(f"      🔗 {result.get('url', 'N/A')}")
            
    except Exception as e:
        print(f"❌ シンプル検索テストエラー: {str(e)}")

if __name__ == "__main__":
    print("🚀 SERP検索デバッグを開始します")
    print("=" * 50)
    
    # Google Custom Search APIのデバッグ
    debug_google_custom_search()
    
    # SERP APIのデバッグ
    debug_serp_api()
    
    # シンプルな検索テスト
    test_simple_search()
    
    print("\n" + "=" * 50)
    print("🎉 デバッグ完了")
