#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NotionDBに部品・工具データを作成するスクリプト
キャンピングカーの修理に必要な部品と工具の詳細情報を作成
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
item_db_id = os.getenv("ITEM_DB_ID")
if not item_db_id:
    print("❌ 部品・工具データベースIDが設定されていません")
    print("💡 .envファイルにITEM_DB_IDを設定してください")
    sys.exit(1)

# Notionクライアントの初期化
client = Client(auth=notion_api_key)

def create_item(name, category, price=None, supplier=None, description=None, related_cases=None, related_nodes=None):
    """部品・工具を作成"""
    try:
        properties = {
            "部品名": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            },
            "カテゴリ": {
                "rich_text": [
                    {
                        "text": {
                            "content": category
                        }
                    }
                ]
            },
            "価格": {
                "rich_text": [
                    {
                        "text": {
                            "content": str(price) if price else "要確認"
                        }
                    }
                ]
            },
            "購入先": {
                "rich_text": [
                    {
                        "text": {
                            "content": supplier if supplier else "要確認"
                        }
                    }
                ]
            },
            "型番/仕様": {
                "rich_text": [
                    {
                        "text": {
                            "content": "要確認"
                        }
                    }
                ]
            },
            "在庫状況": {
                "rich_text": [
                    {
                        "text": {
                            "content": "在庫あり"
                        }
                    }
                ]
            },
            "備考": {
                "rich_text": [
                    {
                        "text": {
                            "content": description if description else "キャンピングカー修理用"
                        }
                    }
                ]
            },
            "メモ": {
                "rich_text": [
                    {
                        "text": {
                            "content": "定期的な点検と交換が必要です。"
                        }
                    }
                ]
            }
        }
        
        # 関連修理ケースがある場合（relationは後で設定）
        # if related_cases:
        #     properties["修理ケースDB"] = {
        #         "relation": [
        #             {"id": case_id} for case_id in related_cases
        #         ]
        #     }
        
        # 関連診断ノードがある場合（relationは後で設定）
        # if related_nodes:
        #     properties["関連修理ノード"] = {
        #         "relation": [
        #             {"id": node_id} for node_id in related_nodes
        #         ]
        #     }
        
        response = client.pages.create(
            parent={"database_id": item_db_id},
            properties=properties
        )
        
        print(f"✅ 部品・工具作成成功: {name}")
        return response["id"]
        
    except Exception as e:
        print(f"❌ 部品・工具作成失敗: {name} - {str(e)}")
        return None

def main():
    """メイン処理"""
    print("🚐 キャンピングカー部品・工具データの作成を開始します...")
    print(f"📊 対象データベース: {item_db_id}")
    
    # 部品・工具の定義
    items = [
        # バッテリー関連
        {
            "name": "バッテリー端子",
            "category": "部品",
            "price": 1500,
            "supplier": "オートバックス",
            "description": "バッテリーの端子接続用。腐食防止加工済み。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "充電器",
            "category": "部品",
            "price": 15000,
            "supplier": "ヨドバシカメラ",
            "description": "12Vバッテリー用充電器。自動充電制御機能付き。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "端子清掃ブラシ",
            "category": "工具",
            "price": 800,
            "supplier": "ホームセンター",
            "description": "バッテリー端子の清掃用ブラシ。金属製で耐久性抜群。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "電圧計",
            "category": "工具",
            "price": 3000,
            "supplier": "ホームセンター",
            "description": "デジタル電圧計。12V/24V対応。",
            "related_cases": [],
            "related_nodes": []
        },
        
        # インバーター関連
        {
            "name": "ヒューズ",
            "category": "部品",
            "price": 200,
            "supplier": "ホームセンター",
            "description": "各種容量のヒューズ。5A/10A/15A/20A対応。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "電源スイッチ",
            "category": "部品",
            "price": 1200,
            "supplier": "ホームセンター",
            "description": "12V用電源スイッチ。LED表示付き。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "制御基板",
            "category": "部品",
            "price": 8000,
            "supplier": "専門業者",
            "description": "インバーター制御用基板。交換時は専門業者に依頼。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "マルチメーター",
            "category": "工具",
            "price": 5000,
            "supplier": "ホームセンター",
            "description": "デジタルマルチメーター。電圧・電流・抵抗測定対応。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "はんだごて",
            "category": "工具",
            "price": 2500,
            "supplier": "ホームセンター",
            "description": "30Wはんだごて。電子工作用。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "ヒューズプライヤー",
            "category": "工具",
            "price": 1500,
            "supplier": "ホームセンター",
            "description": "ヒューズの取り外し専用工具。",
            "related_cases": [],
            "related_nodes": []
        },
        
        # 水道関連
        {
            "name": "ポンプモーター",
            "category": "部品",
            "price": 12000,
            "supplier": "専門業者",
            "description": "12V水道ポンプ用モーター。交換時は専門業者に依頼。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "フィルター",
            "category": "部品",
            "price": 800,
            "supplier": "ホームセンター",
            "description": "水道用フィルター。定期的な交換が必要。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "配管",
            "category": "部品",
            "price": 500,
            "supplier": "ホームセンター",
            "description": "水道用配管。各種サイズ対応。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "配管クリーナー",
            "category": "工具",
            "price": 1200,
            "supplier": "ホームセンター",
            "description": "配管の詰まり除去用クリーナー。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "フィルター清掃ブラシ",
            "category": "工具",
            "price": 600,
            "supplier": "ホームセンター",
            "description": "フィルター清掃用ブラシ。細かい目詰まり除去。",
            "related_cases": [],
            "related_nodes": []
        },
        
        # トイレ関連
        {
            "name": "パッキン",
            "category": "部品",
            "price": 400,
            "supplier": "ホームセンター",
            "description": "トイレ用パッキン。各種サイズ対応。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "フラッパー",
            "category": "部品",
            "price": 1500,
            "supplier": "ホームセンター",
            "description": "トイレ用フラッパー。交換用パーツ。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "パッキン取り外し工具",
            "category": "工具",
            "price": 1800,
            "supplier": "ホームセンター",
            "description": "パッキンの取り外し専用工具。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "シーラント",
            "category": "部品",
            "price": 800,
            "supplier": "ホームセンター",
            "description": "防水用シーラント。トイレの水漏れ防止。",
            "related_cases": [],
            "related_nodes": []
        },
        
        # ルーフベント関連
        {
            "name": "モーター",
            "category": "部品",
            "price": 8000,
            "supplier": "専門業者",
            "description": "ルーフベント用モーター。交換時は専門業者に依頼。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "防水シール",
            "category": "部品",
            "price": 1200,
            "supplier": "ホームセンター",
            "description": "ルーフベント用防水シール。雨漏り防止。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "スイッチ",
            "category": "部品",
            "price": 1500,
            "supplier": "ホームセンター",
            "description": "ルーフベント用スイッチ。開閉制御用。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "ギア",
            "category": "部品",
            "price": 3000,
            "supplier": "専門業者",
            "description": "ルーフベント用ギア。開閉機構用。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "防水シーラント",
            "category": "部品",
            "price": 1000,
            "supplier": "ホームセンター",
            "description": "防水用シーラント。ルーフベントの雨漏り防止。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "スイッチテスター",
            "category": "工具",
            "price": 2000,
            "supplier": "ホームセンター",
            "description": "スイッチの動作確認用テスター。",
            "related_cases": [],
            "related_nodes": []
        },
        
        # 冷蔵庫関連
        {
            "name": "コンプレッサー",
            "category": "部品",
            "price": 25000,
            "supplier": "専門業者",
            "description": "冷蔵庫用コンプレッサー。交換時は専門業者に依頼。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "温度センサー",
            "category": "部品",
            "price": 3000,
            "supplier": "専門業者",
            "description": "冷蔵庫用温度センサー。温度制御用。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "冷媒",
            "category": "部品",
            "price": 5000,
            "supplier": "専門業者",
            "description": "冷蔵庫用冷媒。充填時は専門業者に依頼。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "温度計",
            "category": "工具",
            "price": 1500,
            "supplier": "ホームセンター",
            "description": "デジタル温度計。冷蔵庫内温度測定用。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "圧力計",
            "category": "工具",
            "price": 8000,
            "supplier": "専門業者",
            "description": "冷媒圧力測定用。専門業者向け。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "冷媒検知器",
            "category": "工具",
            "price": 15000,
            "supplier": "専門業者",
            "description": "冷媒漏れ検知用。専門業者向け。",
            "related_cases": [],
            "related_nodes": []
        },
        
        # ガス関連
        {
            "name": "点火装置",
            "category": "部品",
            "price": 12000,
            "supplier": "専門業者",
            "description": "ガスヒーター用点火装置。交換時は専門業者に依頼。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "ガス栓",
            "category": "部品",
            "price": 2000,
            "supplier": "専門業者",
            "description": "ガス供給用栓。ガス漏れ防止。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "フィルター",
            "category": "部品",
            "price": 800,
            "supplier": "ホームセンター",
            "description": "ガスヒーター用フィルター。空気清浄用。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "ガス漏れ検知器",
            "category": "工具",
            "price": 5000,
            "supplier": "ホームセンター",
            "description": "ガス漏れ検知用。安全確認必須。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "点火テスター",
            "category": "工具",
            "price": 3000,
            "supplier": "専門業者",
            "description": "点火装置テスト用。専門業者向け。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "フィルター清掃ブラシ",
            "category": "工具",
            "price": 600,
            "supplier": "ホームセンター",
            "description": "フィルター清掃用ブラシ。目詰まり除去。",
            "related_cases": [],
            "related_nodes": []
        },
        
        # 電装系関連
        {
            "name": "LEDユニット",
            "category": "部品",
            "price": 2000,
            "supplier": "ホームセンター",
            "description": "12V用LEDユニット。省電力・長寿命。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "配線",
            "category": "部品",
            "price": 500,
            "supplier": "ホームセンター",
            "description": "12V用配線。各種長さ対応。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "配線テスター",
            "category": "工具",
            "price": 2500,
            "supplier": "ホームセンター",
            "description": "配線の導通確認用テスター。",
            "related_cases": [],
            "related_nodes": []
        },
        
        # 防水関連
        {
            "name": "シーリング",
            "category": "部品",
            "price": 1200,
            "supplier": "ホームセンター",
            "description": "防水用シーリング。雨漏り防止。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "パッキン",
            "category": "部品",
            "price": 800,
            "supplier": "ホームセンター",
            "description": "防水用パッキン。各種サイズ対応。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "コーキング",
            "category": "部品",
            "price": 600,
            "supplier": "ホームセンター",
            "description": "防水用コーキング。隙間埋め用。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "シーリングガン",
            "category": "工具",
            "price": 3000,
            "supplier": "ホームセンター",
            "description": "シーリング施工用ガン。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "パッキン取り外し工具",
            "category": "工具",
            "price": 1800,
            "supplier": "ホームセンター",
            "description": "パッキンの取り外し専用工具。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "コーキングガン",
            "category": "工具",
            "price": 2500,
            "supplier": "ホームセンター",
            "description": "コーキング施工用ガン。",
            "related_cases": [],
            "related_nodes": []
        },
        
        # 配管関連
        {
            "name": "断熱材",
            "category": "部品",
            "price": 800,
            "supplier": "ホームセンター",
            "description": "配管用断熱材。凍結防止。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "配管継手",
            "category": "部品",
            "price": 300,
            "supplier": "ホームセンター",
            "description": "配管接続用継手。各種サイズ対応。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "配管カッター",
            "category": "工具",
            "price": 2000,
            "supplier": "ホームセンター",
            "description": "配管切断用カッター。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "配管継手工具",
            "category": "工具",
            "price": 3500,
            "supplier": "ホームセンター",
            "description": "配管継手取り付け用工具。",
            "related_cases": [],
            "related_nodes": []
        },
        {
            "name": "断熱テープ",
            "category": "部品",
            "price": 500,
            "supplier": "ホームセンター",
            "description": "配管用断熱テープ。簡単施工。",
            "related_cases": [],
            "related_nodes": []
        }
    ]
    
    print(f"📝 作成予定の部品・工具数: {len(items)}")
    
    # 部品・工具の作成
    created_items = []
    for i, item in enumerate(items, 1):
        print(f"\n[{i}/{len(items)}] {item['name']} を作成中...")
        
        item_id = create_item(
            name=item["name"],
            category=item["category"],
            price=item.get("price"),
            supplier=item.get("supplier"),
            description=item.get("description"),
            related_cases=item.get("related_cases"),
            related_nodes=item.get("related_nodes")
        )
        
        if item_id:
            created_items.append({
                "id": item_id,
                "name": item["name"],
                "category": item["category"]
            })
    
    # 結果の表示
    print(f"\n{'='*60}")
    print(f"✅ 部品・工具作成完了！")
    print(f"📊 作成結果: {len(created_items)}/{len(items)}件")
    print(f"{'='*60}")
    
    for item in created_items:
        print(f"• {item['category']}: {item['name']} (ID: {item['id']})")
    
    print(f"\n🎉 部品・工具データの作成が完了しました！")
    print(f"💡 これで診断システムの基盤が整いました。")

if __name__ == "__main__":
    main()
