#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERP検索機能のテストスクリプト
"""

import os
import sys
import json
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

def test_serp_system():
    """SERP検索システムのテスト"""
    print("🧪 SERP検索システムのテストを開始します...")
    
    try:
        from serp_search_system import get_serp_search_system
        
        # SERP検索システムの初期化
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
                results = serp_system.search(query, ['comprehensive'])
                
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
                    
            except Exception as e:
                print(f"❌ 検索エラー: {str(e)}")
        
        print("\n✅ SERP検索システムのテスト完了")
        
    except ImportError as e:
        print(f"❌ インポートエラー: {str(e)}")
        print("SERP検索システムが正しくインストールされていない可能性があります。")
    except Exception as e:
        print(f"❌ テストエラー: {str(e)}")

def test_api_integration():
    """API統合のテスト"""
    print("\n🧪 API統合のテストを開始します...")
    
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
        
        # リアルタイム情報APIのテスト
        try:
            response = requests.post(
                f"{base_url}/api/realtime-info",
                json={"query": test_query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ リアルタイム情報API成功: {len(data.get('results', []))}件の結果")
                else:
                    print(f"⚠️ リアルタイム情報API失敗: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ リアルタイム情報APIエラー: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ リアルタイム情報API接続エラー: {str(e)}")
        
        # 価格検索APIのテスト
        try:
            response = requests.post(
                f"{base_url}/api/parts-price",
                json={"query": test_query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ 価格検索API成功: {len(data.get('results', []))}件の結果")
                else:
                    print(f"⚠️ 価格検索API失敗: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ 価格検索APIエラー: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 価格検索API接続エラー: {str(e)}")
        
        print("\n✅ API統合のテスト完了")
        
    except ImportError:
        print("❌ requestsライブラリがインストールされていません")
    except Exception as e:
        print(f"❌ API統合テストエラー: {str(e)}")

def check_environment():
    """環境変数の確認"""
    print("🔧 環境変数の確認...")
    
    # 必要な環境変数
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key',
        'GOOGLE_API_KEY': 'Google API Key (SERP検索用)',
        'GOOGLE_CSE_ID': 'Google Custom Search Engine ID (SERP検索用)',
        'SERP_API_KEY': 'SERP API Key (オプション)',
        'NOTION_API_KEY': 'Notion API Key (オプション)'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {description}: 設定済み")
        else:
            print(f"⚠️ {description}: 未設定")
    
    print()

if __name__ == "__main__":
    print("🚀 SERP検索機能の統合テストを開始します")
    print("=" * 50)
    
    # 環境変数の確認
    check_environment()
    
    # SERP検索システムのテスト
    test_serp_system()
    
    # API統合のテスト
    test_api_integration()
    
    print("\n" + "=" * 50)
    print("🎉 すべてのテストが完了しました")
    print("\n📋 次のステップ:")
    print("1. 環境変数を.envファイルに設定してください")
    print("2. repair_center_api.pyを起動してください")
    print("3. http://localhost:5000 でWebインターフェースを確認してください")
    print("4. 新しいSERP検索ボタンをテストしてください")
