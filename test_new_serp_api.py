#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新しいSERP APIキーのテストスクリプト
"""

import os
import requests
import json

def test_new_serp_api():
    """新しいSERP APIキーのテスト"""
    print("🧪 新しいSERP APIキーのテストを開始します...")
    
    # 新しいSERP APIキーを設定
    new_api_key = "fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db"
    
    print(f"🔑 新しいAPIキー: {new_api_key[:10]}...")
    
    # テストクエリ
    test_queries = [
        "キャンピングカー バッテリー 交換",
        "RV battery replacement",
        "camper van repair"
    ]
    
    for query in test_queries:
        print(f"\n🔍 テストクエリ: {query}")
        
        # SERP APIのテスト
        params = {
            'api_key': new_api_key,
            'q': query,
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
                
                # ショッピング結果の表示
                shopping_results = data.get('shopping_results', [])
                if shopping_results:
                    print(f"🛒 ショッピング結果: {len(shopping_results)}件")
                    for i, result in enumerate(shopping_results[:2]):
                        print(f"   {i+1}. {result.get('title', 'N/A')[:60]}...")
                        print(f"      💰 価格: {result.get('price', 'N/A')}")
                        print(f"      🔗 {result.get('link', 'N/A')}")
                
            elif response.status_code == 401:
                print("❌ 認証エラー: APIキーが無効です")
                print(f"レスポンス: {response.text[:200]}...")
            else:
                print(f"❌ エラー: {response.status_code}")
                print(f"レスポンス: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ 例外エラー: {str(e)}")

def test_serp_search_system():
    """SERP検索システムのテスト"""
    print("\n🧪 SERP検索システムのテストを開始します...")
    
    # 環境変数を設定
    os.environ['SERP_API_KEY'] = "fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db"
    
    try:
        from serp_search_system import get_serp_search_system
        
        serp_system = get_serp_search_system()
        print("✅ SERP検索システムの初期化成功")
        
        # テストクエリ
        test_query = "キャンピングカー バッテリー 交換"
        print(f"\n🔍 テストクエリ: {test_query}")
        
        # 包括的検索のテスト
        results = serp_system.search(test_query, ['repair_info', 'parts_price'])
        
        if results and 'results' in results:
            print(f"✅ 検索成功: {len(results['results'])}件の結果")
            
            # 意図分析の表示
            if 'intent_analysis' in results:
                intent = results['intent_analysis']
                print(f"   📊 意図分析: {intent['type']} (信頼度: {intent['confidence']:.2f})")
                print(f"   🔍 検索タイプ: {intent['search_type']}")
            
            # 使用された検索エンジンの表示
            if 'search_engines_used' in results:
                print(f"   🌐 使用検索エンジン: {', '.join(results['search_engines_used'])}")
            
            # 結果の詳細表示（最初の3件）
            for i, result in enumerate(results['results'][:3]):
                print(f"   📄 結果{i+1}: {result.get('title', 'N/A')[:50]}...")
                print(f"      🔗 URL: {result.get('url', 'N/A')}")
                print(f"      📊 関連度: {result.get('relevance_score', 0):.2f}")
                if result.get('price_info'):
                    print(f"      💰 価格情報: {result['price_info']}")
        else:
            print("⚠️ 検索結果なし")
            
    except ImportError as e:
        print(f"❌ インポートエラー: {str(e)}")
        print("SERP検索システムが正しくインストールされていない可能性があります。")
    except Exception as e:
        print(f"❌ テストエラー: {str(e)}")

if __name__ == "__main__":
    print("🚀 新しいSERP APIキーのテストを開始します")
    print("=" * 50)
    
    # 新しいSERP APIキーのテスト
    test_new_serp_api()
    
    # SERP検索システムのテスト
    test_serp_search_system()
    
    print("\n" + "=" * 50)
    print("🎉 テスト完了")
