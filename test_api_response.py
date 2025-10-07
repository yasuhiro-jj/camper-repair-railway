#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIレスポンスのテストスクリプト
"""

import requests
import json

def test_api_response():
    """APIレスポンスのテスト"""
    print("🔍 APIレスポンスのテストを開始...")
    
    # テストクエリ
    test_queries = ["雨漏り", "水漏れ", "シーリング"]
    
    for query in test_queries:
        print(f"\n📝 テストクエリ: '{query}'")
        
        try:
            # APIリクエスト
            url = "http://localhost:5001/api/search"
            data = {"query": query}
            
            print(f"🌐 APIリクエスト送信中...")
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ APIレスポンス取得成功")
                
                # レスポンスの詳細を表示
                print(f"📊 レスポンス詳細:")
                print(f"  - success: {result.get('success', 'N/A')}")
                print(f"  - results数: {len(result.get('results', []))}")
                
                # 各結果の詳細を表示
                for i, item in enumerate(result.get('results', [])):
                    print(f"\n  📋 結果 {i+1}:")
                    print(f"    - title: {item.get('title', 'N/A')}")
                    print(f"    - category: {item.get('category', 'N/A')}")
                    print(f"    - source: {item.get('source', 'N/A')}")
                    print(f"    - repair_steps存在: {bool(item.get('repair_steps'))}")
                    print(f"    - warnings存在: {bool(item.get('warnings'))}")
                    
                    # 修理手順の詳細
                    if item.get('repair_steps'):
                        print(f"    - 修理手順数: {len(item['repair_steps'])}")
                        for j, step in enumerate(item['repair_steps'][:3]):  # 最初の3つだけ表示
                            print(f"      {j+1}. {step[:50]}...")
                    
                    # 注意事項の詳細
                    if item.get('warnings'):
                        print(f"    - 注意事項数: {len(item['warnings'])}")
                        for j, warning in enumerate(item['warnings'][:3]):  # 最初の3つだけ表示
                            print(f"      {j+1}. {warning[:50]}...")
                
            else:
                print(f"❌ APIレスポンス失敗: {response.status_code}")
                print(f"   エラー: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ サーバーに接続できません。アプリケーションが起動しているか確認してください。")
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
    
    return True

if __name__ == "__main__":
    test_api_response()
