#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion統合機能のクイックテスト
FFヒーター、インバーター、サブバッテリーの動作確認
"""

import requests
import json
from typing import Dict, Any

def test_notion_integration():
    """Notion統合機能のテスト"""
    
    base_url = "http://localhost:5002"
    
    # テストケース
    test_cases = [
        {
            "name": "FFヒーター（ガス臭）",
            "message": "FFヒーターからガス臭がします。どうすれば？",
            "expected": {
                "notion_hit": True,
                "safety_warning": True,
                "keywords": ["ガス臭", "ガス漏れ", "プロパン臭"]
            }
        },
        {
            "name": "インバーター（過負荷）",
            "message": "ドライヤー起動でインバーターが落ちます",
            "expected": {
                "notion_hit": True,
                "safety_warning": False,
                "keywords": ["過負荷", "オーバーロード", "容量超過"]
            }
        },
        {
            "name": "サブバッテリー（劣化）",
            "message": "最近サブバッテリーがすぐ電圧下がる",
            "expected": {
                "notion_hit": True,
                "safety_warning": False,
                "keywords": ["電圧低下", "電圧降下", "劣化"]
            }
        }
    ]
    
    print("🧪 Notion統合機能のテスト開始\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 テスト {i}: {test_case['name']}")
        print(f"入力: {test_case['message']}")
        
        try:
            # 会話開始
            start_response = requests.post(f"{base_url}/start_conversation", 
                                         headers={"Content-Type": "application/json"})
            
            if start_response.status_code != 200:
                print(f"❌ 会話開始エラー: {start_response.status_code}")
                continue
            
            # 質問送信
            ask_payload = {
                "message": test_case["message"],
                "mode": "chat"
            }
            
            ask_response = requests.post(f"{base_url}/ask",
                                       headers={"Content-Type": "application/json"},
                                       json=ask_payload)
            
            if ask_response.status_code == 200:
                result = ask_response.json()
                
                print("✅ レスポンス受信")
                
                # Notion検索結果の確認
                notion_results = result.get("notion_results", {})
                if notion_results and not notion_results.get("error"):
                    repair_cases = notion_results.get("repair_cases", [])
                    diagnostic_nodes = notion_results.get("diagnostic_nodes", [])
                    
                    print(f"📊 Notion検索結果:")
                    print(f"  - 修理ケース: {len(repair_cases)}件")
                    print(f"  - 診断ノード: {len(diagnostic_nodes)}件")
                    
                    if repair_cases:
                        print("  - 修理ケース例:")
                        for case in repair_cases[:2]:
                            print(f"    • {case.get('title', 'N/A')} ({case.get('category', 'N/A')})")
                    
                    if diagnostic_nodes:
                        print("  - 診断ノード例:")
                        for node in diagnostic_nodes[:2]:
                            print(f"    • {node.get('title', 'N/A')} ({node.get('category', 'N/A')})")
                    
                    # セーフティ警告の確認
                    safety_warnings = notion_results.get("safety_warnings", [])
                    if safety_warnings:
                        print(f"🚨 セーフティ警告: {safety_warnings}")
                    else:
                        print("✅ セーフティ警告なし")
                    
                    # 拡張キーワードの確認
                    expanded_keywords = notion_results.get("expanded_keywords", [])
                    print(f"🔍 拡張キーワード: {expanded_keywords[:5]}...")
                    
                else:
                    print("⚠️ Notion検索結果なし")
                
                # 引用ログの確認
                citation_log = result.get("citation_log", {})
                if citation_log:
                    sources = citation_log.get("sources", {})
                    print(f"📝 引用ログ:")
                    print(f"  - Notion: {sources.get('notion', {}).get('items_cited', 0)}件")
                    print(f"  - RAG: {sources.get('rag', {}).get('items_cited', 0)}件")
                    print(f"  - SERP: {sources.get('serp', {}).get('items_cited', 0)}件")
                
                # 回答の先頭部分を表示
                response_text = result.get("response", "")
                if response_text:
                    lines = response_text.split('\n')[:10]
                    print("💬 回答（先頭部分）:")
                    for line in lines:
                        if line.strip():
                            print(f"  {line}")
                
            else:
                print(f"❌ 質問エラー: {ask_response.status_code}")
                print(f"エラー内容: {ask_response.text}")
        
        except requests.exceptions.ConnectionError:
            print("❌ サーバーに接続できません。バックエンドが起動しているか確認してください。")
        except Exception as e:
            print(f"❌ テストエラー: {e}")
        
        print("-" * 50)
    
    print("\n🎯 テスト完了")

if __name__ == "__main__":
    test_notion_integration()
