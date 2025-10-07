#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新しいSERP APIキーでメインアプリケーションをテストするスクリプト
"""

import os
import sys
import json
from dotenv import load_dotenv

# 新しいSERP APIキーを環境変数に設定
os.environ['SERP_API_KEY'] = "fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db"

def test_serp_search_system():
    """SERP検索システムのテスト"""
    print("🧪 SERP検索システムのテストを開始します...")
    
    try:
        from serp_search_system import get_serp_search_system
        
        serp_system = get_serp_search_system()
        print("✅ SERP検索システムの初期化成功")
        
        # テストクエリ
        test_queries = [
            "キャンピングカー バッテリー 交換",
            "トイレ ファン 故障",
            "エアコン 冷えない 修理",
            "雨漏り 修理 方法"
        ]
        
        for query in test_queries:
            print(f"\n🔍 テストクエリ: {query}")
            
            try:
                # 包括的検索のテスト
                results = serp_system.search(query, ['repair_info', 'parts_price', 'general_info'])
                
                if results and 'results' in results and results['results']:
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
                    
            except Exception as e:
                print(f"❌ 検索エラー: {str(e)}")
        
        print("\n✅ SERP検索システムのテスト完了")
        
    except ImportError as e:
        print(f"❌ インポートエラー: {str(e)}")
        print("SERP検索システムが正しくインストールされていない可能性があります。")
    except Exception as e:
        print(f"❌ テストエラー: {str(e)}")

def test_app_integration():
    """メインアプリケーションとの統合テスト"""
    print("\n🧪 メインアプリケーションとの統合テストを開始します...")
    
    try:
        # app.pyの検索機能をテスト
        from app import search, search_realtime_info, search_parts_price
        
        test_queries = [
            "キャンピングカー バッテリー 交換",
            "トイレ ファン 故障"
        ]
        
        for query in test_queries:
            print(f"\n🔍 アプリ統合テストクエリ: {query}")
            
            try:
                # メイン検索機能のテスト
                results = search(query)
                if results:
                    print(f"✅ メイン検索成功: {len(results)}件の結果")
                    for i, result in enumerate(results[:2]):
                        print(f"   {i+1}. {result[:100]}...")
                else:
                    print("⚠️ メイン検索結果なし")
                
                # リアルタイム情報検索のテスト
                realtime_results = search_realtime_info(query)
                if realtime_results:
                    print(f"✅ リアルタイム検索成功: {len(realtime_results)}件の結果")
                    for i, result in enumerate(realtime_results[:2]):
                        print(f"   {i+1}. {result[:100]}...")
                else:
                    print("⚠️ リアルタイム検索結果なし")
                
                # 価格検索のテスト
                price_results = search_parts_price(query)
                if price_results:
                    print(f"✅ 価格検索成功: {len(price_results)}件の結果")
                    for i, result in enumerate(price_results[:2]):
                        print(f"   {i+1}. {result[:100]}...")
                else:
                    print("⚠️ 価格検索結果なし")
                    
            except Exception as e:
                print(f"❌ アプリ統合テストエラー: {str(e)}")
        
        print("\n✅ メインアプリケーションとの統合テスト完了")
        
    except ImportError as e:
        print(f"❌ インポートエラー: {str(e)}")
        print("メインアプリケーションが正しくインストールされていない可能性があります。")
    except Exception as e:
        print(f"❌ 統合テストエラー: {str(e)}")

def test_flask_app():
    """Flaskアプリケーションのテスト"""
    print("\n🧪 Flaskアプリケーションのテストを開始します...")
    
    try:
        import requests
        
        # ローカルサーバーのテスト
        base_url = "http://localhost:5000"
        
        # ヘルスチェック
        try:
            response = requests.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print("✅ ヘルスチェック成功")
                print(f"   📊 機能状況:")
                for feature, status in health_data.get('features', {}).items():
                    status_icon = "✅" if status else "❌"
                    print(f"      {status_icon} {feature}: {status}")
            else:
                print(f"⚠️ ヘルスチェック失敗: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ サーバー接続エラー: {str(e)}")
            print("サーバーが起動していない可能性があります。")
            return
        
        # SERP検索APIのテスト
        test_query = "キャンピングカー バッテリー 価格"
        
        try:
            response = requests.post(
                f"{base_url}/api/serp-search",
                json={"query": test_query, "search_type": "comprehensive"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ SERP検索API成功: {len(data.get('results', []))}件の結果")
                else:
                    print(f"⚠️ SERP検索API失敗: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ SERP検索APIエラー: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ SERP検索API接続エラー: {str(e)}")
        
        print("\n✅ Flaskアプリケーションのテスト完了")
        
    except ImportError:
        print("❌ requestsライブラリがインストールされていません")
    except Exception as e:
        print(f"❌ Flaskアプリケーションテストエラー: {str(e)}")

if __name__ == "__main__":
    print("🚀 新しいSERP APIキーでメインアプリケーションのテストを開始します")
    print("=" * 60)
    
    # SERP検索システムのテスト
    test_serp_search_system()
    
    # メインアプリケーションとの統合テスト
    test_app_integration()
    
    # Flaskアプリケーションのテスト
    test_flask_app()
    
    print("\n" + "=" * 60)
    print("🎉 すべてのテストが完了しました")
    print("\n📋 次のステップ:")
    print("1. set_new_serp_api.batを実行してアプリケーションを起動してください")
    print("2. http://localhost:5000 でWebインターフェースを確認してください")
    print("3. 新しいSERP検索機能をテストしてください")
