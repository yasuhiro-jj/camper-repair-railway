#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIテストスクリプト
"""

import requests
import json

def test_door_search():
    """ドア検索のテスト"""
    url = "http://localhost:5000/api/search"
    data = {"query": "ドアの開け閉めの不具合"}
    
    try:
        response = requests.post(url, json=data)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"成功: {result.get('success', False)}")
            print(f"結果数: {result.get('count', 0)}")
            
            if result.get('results'):
                for i, res in enumerate(result['results']):
                    print(f"\n結果 {i+1}:")
                    print(f"  タイトル: {res.get('title', 'N/A')}")
                    print(f"  カテゴリ: {res.get('category', 'N/A')}")
                    print(f"  スコア: {res.get('score', 0)}")
                    print(f"  内容: {res.get('content', '')[:100]}...")
            else:
                print("結果なし")
                if result.get('general_advice'):
                    print(f"一般的なアドバイス: {result['general_advice']}")
        else:
            print(f"エラー: {response.text}")
            
    except Exception as e:
        print(f"リクエストエラー: {e}")

if __name__ == "__main__":
    test_door_search()
