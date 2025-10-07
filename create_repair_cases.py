#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NotionDBに修理ケースデータを作成するスクリプト
キャンピングカーの実際の修理事例に基づいた専門的なケースを作成
"""

import os
import sys
from notion_client import Client
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# Notion APIキーの設定
notion_api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
if not notion_api_key:
    print("❌ Notion APIキーが設定されていません")
    print("💡 .envファイルにNOTION_API_KEYを設定してください")
    sys.exit(1)

# データベースIDの設定
case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
if not case_db_id:
    print("❌ 修理ケースデータベースIDが設定されていません")
    print("💡 .envファイルにCASE_DB_IDを設定してください")
    sys.exit(1)

# Notionクライアントの初期化
client = Client(auth=notion_api_key)

def create_repair_case(case_id, title, category, symptoms, solution, parts=None, tools=None, related_nodes=None, related_items=None):
    """修理ケースを作成"""
    try:
        properties = {
            "ケースID": {
                "title": [
                    {
                        "text": {
                            "content": case_id
                        }
                    }
                ]
            },
            "症状": {
                "rich_text": [
                    {
                        "text": {
                            "content": ", ".join(symptoms)
                        }
                    }
                ]
            },
            "修理手順": {
                "rich_text": [
                    {
                        "text": {
                            "content": solution
                        }
                    }
                ]
            },
            "注意事項": {
                "rich_text": [
                    {
                        "text": {
                            "content": "安全第一で作業を行ってください。不明な点がある場合は専門業者に相談してください。"
                        }
                    }
                ]
            },
            "難易度": {
                "rich_text": [
                    {
                        "text": {
                            "content": "中級"
                        }
                    }
                ]
            },
            "推定時間": {
                "rich_text": [
                    {
                        "text": {
                            "content": "1時間〜4時間"
                        }
                    }
                ]
            },
            "画像・動画": {
                "rich_text": [
                    {
                        "text": {
                            "content": "作業前後の写真を撮影して記録を残してください。"
                        }
                    }
                ]
            }
        }
        
        # 必要な部品がある場合（番号付きプロパティに分散保存）
        if parts:
            for i, part in enumerate(parts, 1):
                if i <= 11:  # 最大11個まで対応
                    prop_name = f"必要部品（Rel） {i}"
                    properties[prop_name] = {
                        "rich_text": [
                            {
                                "text": {
                                    "content": part
                                }
                            }
                        ]
                    }
        
        # 必要な工具がある場合
        if tools:
            properties["必要工具（Rel）"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": ", ".join(tools)
                        }
                    }
                ]
            }
        
        response = client.pages.create(
            parent={"database_id": case_db_id},
            properties=properties
        )
        
        print(f"✅ 修理ケース作成成功: {title}")
        return response["id"]
        
    except Exception as e:
        print(f"❌ 修理ケース作成失敗: {title} - {str(e)}")
        return None

def main():
    """メイン処理"""
    print("🚐 キャンピングカー修理ケースの作成を開始します...")
    print(f"📊 対象データベース: {case_db_id}")
    
    # 修理ケースの定義
    repair_cases = [
        {
            "case_id": "CASE-001",
            "title": "バッテリー電圧低下の修理",
            "category": "バッテリー",
            "symptoms": ["電圧が12V以下に低下", "充電されない", "急激な消耗"],
            "solution": "バッテリーの端子を清掃し、充電器の動作を確認。端子の腐食が激しい場合は新しい端子に交換。充電器が正常に動作しない場合は充電器の修理または交換が必要。",
            "parts": ["バッテリー端子", "充電器"],
            "tools": ["端子清掃ブラシ", "電圧計", "充電器"],
            "related_nodes": [],
            "related_items": []
        },
        {
            "case_id": "CASE-002",
            "title": "インバーター電源異常の修理",
            "category": "インバーター",
            "symptoms": ["電源が入らない", "出力ゼロ", "LEDが点滅する"],
            "solution": "電源スイッチとヒューズを確認。ヒューズが切れている場合は交換。電源が入らない場合は電源回路の修理が必要。制御基板に問題がある場合は専門業者に依頼。",
            "parts": ["ヒューズ", "電源スイッチ", "制御基板"],
            "tools": ["マルチメーター", "はんだごて", "ヒューズプライヤー"],
            "related_nodes": [],
            "related_items": []
        },
        {
            "case_id": "CASE-003",
            "title": "水道ポンプ動作不良の修理",
            "category": "水道",
            "symptoms": ["ポンプが動作しない", "水が出ない", "水圧が弱い"],
            "solution": "ポンプの電源を確認し、モーターの動作をテスト。モーターが動作しない場合はモーターの交換が必要。水が出ない場合は配管の詰まりを確認し、必要に応じてフィルターを清掃または交換。",
            "parts": ["ポンプモーター", "フィルター", "配管"],
            "tools": ["電圧計", "配管クリーナー", "フィルター清掃ブラシ"],
            "related_nodes": [],
            "related_items": []
        },
        {
            "case_id": "CASE-004",
            "title": "トイレ水漏れの修理",
            "category": "トイレ",
            "symptoms": ["水漏れがする", "水が流れない", "タンクが満杯"],
            "solution": "パッキンの劣化を確認し、必要に応じて交換。フラッパーが故障している場合は新しいフラッパーに交換。配管の詰まりがある場合は配管クリーナーで清掃。",
            "parts": ["パッキン", "フラッパー", "配管"],
            "tools": ["パッキン取り外し工具", "配管クリーナー", "シーラント"],
            "related_nodes": [],
            "related_items": []
        },
        {
            "case_id": "CASE-005",
            "title": "ルーフベント故障の修理",
            "category": "ルーフベント",
            "symptoms": ["ファンが回らない", "雨漏りがする", "開閉が不良"],
            "solution": "モーターの動作を確認し、必要に応じて交換。雨漏りがある場合は防水シールを交換。開閉が不良の場合はスイッチとギアの状態を確認し、修理または交換。",
            "parts": ["モーター", "防水シール", "スイッチ", "ギア"],
            "tools": ["電圧計", "防水シーラント", "スイッチテスター"],
            "related_nodes": [],
            "related_items": []
        },
        {
            "case_id": "CASE-006",
            "title": "冷蔵庫冷却不良の修理",
            "category": "冷蔵庫",
            "symptoms": ["冷えない", "冷凍室が凍らない", "コンプレッサーが動作しない"],
            "solution": "コンプレッサーの動作を確認し、必要に応じて交換。冷媒の漏れがある場合は専門業者に依頼。温度センサーの動作を確認し、故障している場合は交換。",
            "parts": ["コンプレッサー", "温度センサー", "冷媒"],
            "tools": ["温度計", "圧力計", "冷媒検知器"],
            "related_nodes": [],
            "related_items": []
        },
        {
            "case_id": "CASE-007",
            "title": "ガスヒーター点火不良の修理",
            "category": "ガスヒーター",
            "symptoms": ["火が付かない", "不完全燃焼", "異臭がする"],
            "solution": "ガス供給を確認し、ガス栓の状態をチェック。点火装置の動作を確認し、必要に応じて修理または交換。不完全燃焼がある場合は空気の流れを確認し、フィルターを清掃。",
            "parts": ["点火装置", "ガス栓", "フィルター"],
            "tools": ["ガス漏れ検知器", "点火テスター", "フィルター清掃ブラシ"],
            "related_nodes": [],
            "related_items": []
        },
        {
            "case_id": "CASE-008",
            "title": "電装系動作不良の修理",
            "category": "電装系",
            "symptoms": ["LEDが点灯しない", "配線がショート", "ヒューズが切れる"],
            "solution": "配線の接続を確認し、ショートしている箇所を特定して修理。ヒューズが切れている場合は交換。LEDが点灯しない場合はLEDユニットの交換が必要。",
            "parts": ["LEDユニット", "ヒューズ", "配線"],
            "tools": ["マルチメーター", "配線テスター", "はんだごて"],
            "related_nodes": [],
            "related_items": []
        },
        {
            "case_id": "CASE-009",
            "title": "雨漏り・防水不良の修理",
            "category": "防水",
            "symptoms": ["屋根から雨漏り", "ウインドウ周りから漏れる", "シーリングが劣化"],
            "solution": "劣化したシーリングを除去し、新しいシーリングを施工。パッキンが硬化している場合は交換。コーキングが剥がれている場合は除去して新しいコーキングを施工。",
            "parts": ["シーリング", "パッキン", "コーキング"],
            "tools": ["シーリングガン", "パッキン取り外し工具", "コーキングガン"],
            "related_nodes": [],
            "related_items": []
        },
        {
            "case_id": "CASE-010",
            "title": "配管凍結の修理",
            "category": "配管",
            "symptoms": ["配管が凍結", "水が出ない", "配管から漏れる"],
            "solution": "凍結した配管を温めて解凍。配管に亀裂がある場合は新しい配管に交換。凍結を防ぐために断熱材を巻く。冬期は配管を空にして凍結を防ぐ。",
            "parts": ["配管", "断熱材", "配管継手"],
            "tools": ["配管カッター", "配管継手工具", "断熱テープ"],
            "related_nodes": [],
            "related_items": []
        }
    ]
    
    print(f"📝 作成予定の修理ケース数: {len(repair_cases)}")
    
    # 修理ケースの作成
    created_cases = []
    for i, case in enumerate(repair_cases, 1):
        print(f"\n[{i}/{len(repair_cases)}] {case['title']} を作成中...")
        
        case_id = create_repair_case(
            case_id=case["case_id"],
            title=case["title"],
            category=case["category"],
            symptoms=case["symptoms"],
            solution=case["solution"],
            parts=case.get("parts"),
            tools=case.get("tools"),
            related_nodes=case.get("related_nodes"),
            related_items=case.get("related_items")
        )
        
        if case_id:
            created_cases.append({
                "id": case_id,
                "case_id": case["case_id"],
                "title": case["title"],
                "category": case["category"]
            })
    
    # 結果の表示
    print(f"\n{'='*60}")
    print(f"✅ 修理ケース作成完了！")
    print(f"📊 作成結果: {len(created_cases)}/{len(repair_cases)}件")
    print(f"{'='*60}")
    
    for case in created_cases:
        print(f"• {case['category']}: {case['title']} (ID: {case['id']})")
    
    print(f"\n🎉 修理ケースの作成が完了しました！")
    print(f"💡 次に部品・工具データを作成することをお勧めします。")

if __name__ == "__main__":
    main()
