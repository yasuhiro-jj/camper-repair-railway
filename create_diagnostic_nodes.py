#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NotionDBに診断ノードを作成するスクリプト
キャンピングカーの修理診断に特化した専門的な診断フローを作成
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
node_db_id = os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
if not node_db_id:
    print("❌ 診断ノードデータベースIDが設定されていません")
    print("💡 .envファイルにNODE_DB_IDを設定してください")
    sys.exit(1)

# Notionクライアントの初期化
client = Client(auth=notion_api_key)

def create_diagnostic_node(title, category, symptoms, description, related_cases=None, related_items=None):
    """診断ノードを作成"""
    try:
        properties = {
            "ノードID": {
                "title": [
                    {
                        "text": {
                            "content": title
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
            "症状": {
                "rich_text": [
                    {
                        "text": {
                            "content": ", ".join(symptoms)
                        }
                    }
                ]
            },
            "質問内容": {
                "rich_text": [
                    {
                        "text": {
                            "content": f"{title}について詳しく教えてください。どのような症状がありますか？"
                        }
                    }
                ]
            },
            "診断結果": {
                "rich_text": [
                    {
                        "text": {
                            "content": description
                        }
                    }
                ]
            },
            "修理手順": {
                "rich_text": [
                    {
                        "text": {
                            "content": "詳細な診断が必要です。専門業者に相談することをお勧めします。"
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
            "開始フラグ": {
                "checkbox": category == "開始"
            },
            "終端フラグ": {
                "checkbox": category == "詳細"
            },
            "優先度": {
                "rich_text": [
                    {
                        "text": {
                            "content": "中"
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
                            "content": "30分〜2時間"
                        }
                    }
                ]
            }
        }
        
        # 関連修理ケースがある場合
        if related_cases:
            properties["関連診断ノード"] = {
                "relation": [
                    {"id": case_id} for case_id in related_cases
                ]
            }
        
        # 関連部品・工具がある場合
        if related_items:
            properties["必要部品（Rel）"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": ", ".join(related_items)
                        }
                    }
                ]
            }
        
        response = client.pages.create(
            parent={"database_id": node_db_id},
            properties=properties
        )
        
        print(f"✅ 診断ノード作成成功: {title}")
        return response["id"]
        
    except Exception as e:
        print(f"❌ 診断ノード作成失敗: {title} - {str(e)}")
        return None

def main():
    """メイン処理"""
    print("🚐 キャンピングカー診断ノードの作成を開始します...")
    print(f"📊 対象データベース: {node_db_id}")
    
    # 診断ノードの定義
    diagnostic_nodes = [
        {
            "title": "🔋 バッテリー電圧低下",
            "category": "開始",
            "symptoms": ["電圧が12V以下に低下", "充電されない", "急激な消耗", "エンジン始動時の異音"],
            "description": "バッテリーの電圧が低下している状態。充電システムやバッテリー本体の問題が考えられます。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "🔌 インバーター電源異常",
            "category": "開始",
            "symptoms": ["電源が入らない", "出力ゼロ", "LEDが点滅する", "エラーコードが表示"],
            "description": "インバーターの電源が入らない、または出力が異常な状態。電源回路や制御基板の問題が考えられます。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "💧 水道ポンプ動作不良",
            "category": "開始",
            "symptoms": ["ポンプが動作しない", "水が出ない", "水圧が弱い", "異音がする"],
            "description": "水道ポンプが正常に動作しない状態。モーター、配管、フィルターの問題が考えられます。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "🚽 トイレ水漏れ",
            "category": "開始",
            "symptoms": ["水漏れがする", "水が流れない", "タンクが満杯", "臭いがする"],
            "description": "トイレから水が漏れる、または水が流れない状態。パッキン、フラッパー、配管の問題が考えられます。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "🌪️ ルーフベント故障",
            "category": "開始",
            "symptoms": ["ファンが回らない", "雨漏りがする", "開閉が不良", "異音がする"],
            "description": "ルーフベントが正常に動作しない状態。モーター、スイッチ、防水シールの問題が考えられます。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "❄️ 冷蔵庫冷却不良",
            "category": "開始",
            "symptoms": ["冷えない", "冷凍室が凍らない", "コンプレッサーが動作しない", "霜が付く"],
            "description": "冷蔵庫が正常に冷却しない状態。コンプレッサー、冷媒、温度センサーの問題が考えられます。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "🔥 ガスヒーター点火不良",
            "category": "開始",
            "symptoms": ["火が付かない", "不完全燃焼", "異臭がする", "点火音がしない"],
            "description": "ガスヒーターが正常に点火しない状態。ガス供給、点火装置、安全装置の問題が考えられます。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "⚡ 電装系動作不良",
            "category": "開始",
            "symptoms": ["LEDが点灯しない", "配線がショート", "ヒューズが切れる", "電圧が不安定"],
            "description": "電装系が正常に動作しない状態。配線、ヒューズ、電源の問題が考えられます。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "🌧️ 雨漏り・防水不良",
            "category": "開始",
            "symptoms": ["屋根から雨漏り", "ウインドウ周りから漏れる", "ドアから水が入る", "シーリングが劣化"],
            "description": "車体から水が漏れる状態。シーリング、パッキン、コーキングの問題が考えられます。",
            "related_cases": [],
            "related_items": []
        },
        # 詳細診断ノード
        {
            "title": "バッテリー充電システム診断",
            "category": "詳細",
            "symptoms": ["充電器が動作しない", "充電されない", "バッテリー液の減少", "端子の腐食"],
            "description": "バッテリーの充電システムに問題がある状態。充電器、配線、端子の状態を詳しく確認します。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "インバーター出力異常診断",
            "category": "詳細",
            "symptoms": ["正弦波出力が不安定", "負荷時に停止", "電圧が不安定", "周波数がずれる"],
            "description": "インバーターの出力が不安定な状態。制御基板、出力回路、負荷の状態を詳しく確認します。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "水道ポンプ配管診断",
            "category": "詳細",
            "symptoms": ["配管から漏れる", "ポンプが過熱する", "タンクが空になる", "フィルターが詰まる"],
            "description": "水道ポンプの配管に問題がある状態。配管の接続、フィルター、タンクの状態を詳しく確認します。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "トイレ排水システム診断",
            "category": "詳細",
            "symptoms": ["排水ポンプが動作しない", "配管の詰まり", "タンクの亀裂", "パッキンが劣化"],
            "description": "トイレの排水システムに問題がある状態。排水ポンプ、配管、タンクの状態を詳しく確認します。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "ルーフベントモーター診断",
            "category": "詳細",
            "symptoms": ["モーターが過熱する", "スイッチが効かない", "風量が弱い", "振動が激しい"],
            "description": "ルーフベントのモーターに問題がある状態。モーター、スイッチ、ファンの状態を詳しく確認します。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "冷蔵庫コンプレッサー診断",
            "category": "詳細",
            "symptoms": ["コンプレッサーが動作しない", "過熱する", "ガス漏れの臭い", "電気代が高い"],
            "description": "冷蔵庫のコンプレッサーに問題がある状態。コンプレッサー、冷媒、断熱材の状態を詳しく確認します。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "ガスヒーター安全装置診断",
            "category": "詳細",
            "symptoms": ["安全装置が作動", "ガス漏れ", "炎が不安定", "ガス栓が固い"],
            "description": "ガスヒーターの安全装置に問題がある状態。ガス供給、安全装置、配管の状態を詳しく確認します。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "電装系配線診断",
            "category": "詳細",
            "symptoms": ["配線が熱い", "漏電する", "コンセントが使えない", "電装品が動作不良"],
            "description": "電装系の配線に問題がある状態。配線の接続、絶縁、ヒューズの状態を詳しく確認します。",
            "related_cases": [],
            "related_items": []
        },
        {
            "title": "防水シーリング診断",
            "category": "詳細",
            "symptoms": ["シーリングが劣化", "パッキンが硬化", "コーキングが剥がれる", "継ぎ目から漏れる"],
            "description": "防水シーリングに問題がある状態。シーリング、パッキン、コーキングの状態を詳しく確認します。",
            "related_cases": [],
            "related_items": []
        }
    ]
    
    print(f"📝 作成予定の診断ノード数: {len(diagnostic_nodes)}")
    
    # 診断ノードの作成
    created_nodes = []
    for i, node in enumerate(diagnostic_nodes, 1):
        print(f"\n[{i}/{len(diagnostic_nodes)}] {node['title']} を作成中...")
        
        node_id = create_diagnostic_node(
            title=node["title"],
            category=node["category"],
            symptoms=node["symptoms"],
            description=node["description"],
            related_cases=node.get("related_cases"),
            related_items=node.get("related_items")
        )
        
        if node_id:
            created_nodes.append({
                "id": node_id,
                "title": node["title"],
                "category": node["category"]
            })
    
    # 結果の表示
    print(f"\n{'='*60}")
    print(f"✅ 診断ノード作成完了！")
    print(f"📊 作成結果: {len(created_nodes)}/{len(diagnostic_nodes)}件")
    print(f"{'='*60}")
    
    for node in created_nodes:
        print(f"• {node['category']}: {node['title']} (ID: {node['id']})")
    
    print(f"\n🎉 診断ノードの作成が完了しました！")
    print(f"💡 次に修理ケースデータを作成することをお勧めします。")

if __name__ == "__main__":
    main()
