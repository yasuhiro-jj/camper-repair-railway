#!/usr/bin/env python3
"""
キャンピングカー修理AI 統合テストスクリプト
フロントエンドとバックエンドの連携をテストします
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# テスト設定
BACKEND_URL = "http://localhost:5001"
FRONTEND_URL = "http://localhost:3000"
TEST_TIMEOUT = 10

def test_backend_health():
    """バックエンドのヘルスチェック"""
    print("🔧 バックエンドヘルスチェック...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ バックエンド正常: {data}")
            return True
        else:
            print(f"❌ バックエンド異常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ バックエンド接続エラー: {e}")
        return False

def test_backend_chat():
    """バックエンドチャット機能テスト"""
    print("💬 バックエンドチャット機能テスト...")
    try:
        test_question = "バッテリーが充電されない"
        response = requests.post(
            f"{BACKEND_URL}/ask",
            data={"question": test_question},
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if "answer" in data and data["answer"]:
                print(f"✅ チャット機能正常: {len(data['answer'])}文字の回答")
                return True
            else:
                print(f"❌ チャット機能異常: 回答が空")
                return False
        else:
            print(f"❌ チャット機能異常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ チャット機能エラー: {e}")
        return False

def test_backend_search():
    """バックエンド検索機能テスト"""
    print("🔍 バックエンド検索機能テスト...")
    try:
        test_query = "バッテリー修理"
        response = requests.post(
            f"{BACKEND_URL}/api/search",
            json={"query": test_query},
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("results"):
                print(f"✅ 検索機能正常: {len(data['results'])}件の結果")
                return True
            else:
                print(f"❌ 検索機能異常: 結果が空")
                return False
        else:
            print(f"❌ 検索機能異常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 検索機能エラー: {e}")
        return False

def test_backend_categories():
    """バックエンドカテゴリ機能テスト"""
    print("📋 バックエンドカテゴリ機能テスト...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/categories", timeout=TEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("categories"):
                print(f"✅ カテゴリ機能正常: {len(data['categories'])}件のカテゴリ")
                return True
            else:
                print(f"❌ カテゴリ機能異常: カテゴリが空")
                return False
        else:
            print(f"❌ カテゴリ機能異常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ カテゴリ機能エラー: {e}")
        return False

def test_frontend_connection():
    """フロントエンド接続テスト"""
    print("🌐 フロントエンド接続テスト...")
    try:
        response = requests.get(FRONTEND_URL, timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            print("✅ フロントエンド接続正常")
            return True
        else:
            print(f"❌ フロントエンド接続異常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ フロントエンド接続エラー: {e}")
        return False

def test_api_proxy():
    """APIプロキシテスト（フロントエンド経由でバックエンドAPIにアクセス）"""
    print("🔄 APIプロキシテスト...")
    try:
        # フロントエンド経由でバックエンドAPIにアクセス
        response = requests.get(f"{FRONTEND_URL}/api/health", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ APIプロキシ正常: {data}")
            return True
        else:
            print(f"❌ APIプロキシ異常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ APIプロキシエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 キャンピングカー修理AI 統合テスト開始")
    print("=" * 50)
    
    test_results = []
    
    # バックエンドテスト
    print("\n📡 バックエンドテスト")
    print("-" * 30)
    test_results.append(("バックエンドヘルスチェック", test_backend_health()))
    test_results.append(("バックエンドチャット機能", test_backend_chat()))
    test_results.append(("バックエンド検索機能", test_backend_search()))
    test_results.append(("バックエンドカテゴリ機能", test_backend_categories()))
    
    # フロントエンドテスト
    print("\n🌐 フロントエンドテスト")
    print("-" * 30)
    test_results.append(("フロントエンド接続", test_frontend_connection()))
    test_results.append(("APIプロキシ", test_api_proxy()))
    
    # 結果サマリー
    print("\n📊 テスト結果サマリー")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 総合結果: {passed}/{total} テスト通過")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！システムは正常に動作しています。")
        return 0
    else:
        print("⚠️ 一部のテストが失敗しました。ログを確認してください。")
        return 1

if __name__ == "__main__":
    print("キャンピングカー修理AI 統合テスト")
    print("バックエンドURL:", BACKEND_URL)
    print("フロントエンドURL:", FRONTEND_URL)
    print()
    
    # サーバー起動待機
    print("⏳ サーバー起動を待機中...")
    time.sleep(3)
    
    exit_code = main()
    sys.exit(exit_code)
