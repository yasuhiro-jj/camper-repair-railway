#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notionデータベースに費用情報を含むサンプルデータを作成
"""

import os
import sys
from data_access.notion_client import NotionClient

def create_sample_cost_data():
    """費用情報を含むサンプルデータを作成"""
    print("🔧 費用情報を含むサンプルデータを作成中...")
    
    try:
        notion_client = NotionClient()
        print("✅ Notionクライアント初期化成功")
        
        # 修理ケースDB IDを取得
        case_db_id = notion_client._get_database_id("CASE_DB_ID", "NOTION_REPAIR_CASE_DB_ID")
        if not case_db_id:
            print("❌ 修理ケースDB IDが取得できません")
            return
        
        print(f"📊 修理ケースDB ID: {case_db_id}")
        
        # サンプルデータを作成
        sample_cases = [
            {
                "ケースID": "ルーフベント故障_001",
                "カテゴリ": "ルーフベント",
                "症状": "ルーフベントが開かない、閉まらない、異音がする",
                "解決方法": "1. モーターの確認\n2. ギアの清掃・潤滑\n3. 必要に応じてモーター交換",
                "費用目安": "診断料: 3,000円\nモーター交換: 15,000円〜25,000円\nギア修理: 5,000円〜8,000円"
            },
            {
                "ケースID": "バッテリー故障_001", 
                "カテゴリ": "バッテリー",
                "症状": "エンジンがかからない、電圧が低い、充電できない",
                "解決方法": "1. バッテリー電圧測定\n2. 端子の清掃\n3. バッテリー交換",
                "費用目安": "診断料: 2,000円\nバッテリー交換: 15,000円〜35,000円\n端子清掃: 3,000円"
            },
            {
                "ケースID": "エアコン故障_001",
                "カテゴリ": "エアコン", 
                "症状": "冷房が効かない、暖房が効かない、異音がする",
                "解決方法": "1. フィルター清掃\n2. 冷媒ガス確認\n3. コンプレッサー点検",
                "費用目安": "診断料: 5,000円\n冷媒ガス補充: 8,000円〜12,000円\nコンプレッサー交換: 50,000円〜80,000円"
            }
        ]
        
        print(f"📝 {len(sample_cases)}件のサンプルデータを作成中...")
        
        for i, case_data in enumerate(sample_cases):
            try:
                # Notionページを作成
                page_data = {
                    "parent": {"database_id": case_db_id},
                    "properties": {
                        "ケースID": {
                            "title": [
                                {
                                    "text": {
                                        "content": case_data["ケースID"]
                                    }
                                }
                            ]
                        },
                        "カテゴリ": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": case_data["カテゴリ"]
                                    }
                                }
                            ]
                        },
                        "症状": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": case_data["症状"]
                                    }
                                }
                            ]
                        },
                        "解決方法": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": case_data["解決方法"]
                                    }
                                }
                            ]
                        },
                        "費用目安": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": case_data["費用目安"]
                                    }
                                }
                            ]
                        }
                    }
                }
                
                # ページを作成
                response = notion_client.client.pages.create(**page_data)
                print(f"✅ ケース {i+1} 作成成功: {case_data['ケースID']}")
                
            except Exception as e:
                print(f"❌ ケース {i+1} 作成失敗: {e}")
                # 既存のページが存在する場合はスキップ
                if "already exists" in str(e).lower():
                    print(f"  → 既存のページのためスキップ")
                else:
                    import traceback
                    traceback.print_exc()
        
        print("\n✅ サンプルデータ作成完了")
        print("🔍 作成されたデータを確認するには: python check_notion_cost_data.py")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_sample_cost_data()
