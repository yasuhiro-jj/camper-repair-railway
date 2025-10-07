# full_data_migration.py
import json
import csv
from notion_client import Client
import os
import time

# 環境変数から設定を取得
API_KEY = os.getenv("NOTION_API_KEY")
NODE_DB = os.getenv("NODE_DB_ID")
CASE_DB = os.getenv("CASE_DB_ID")
ITEM_DB = os.getenv("ITEM_DB_ID")

client = Client(auth=API_KEY)

def migrate_all_diagnostic_nodes():
    """すべての診断フローデータを移行"""
    print(" 全診断フローデータの移行を開始...")
    
    # mock_diagnostic_nodes.jsonを読み込み
    with open('mock_diagnostic_nodes.json', 'r', encoding='utf-8') as f:
        diagnostic_data = json.load(f)
    
    created_pages = {}
    total_nodes = len(diagnostic_data[0])
    processed = 0
    
    # 各診断ノードをNotionに追加
    for node_id, node_data in diagnostic_data[0].items():
        processed += 1
        print(f"📝 [{processed}/{total_nodes}] {node_id} を追加中...")
        
        # Notionページを作成
        properties = {
            "ノードID": {"title": [{"text": {"content": node_id}}]},
            "質問内容": {"rich_text": [{"text": {"content": node_data.get("question", "")}}]},
            "診断結果": {"rich_text": [{"text": {"content": node_data.get("result", "")}}]},
            "カテゴリ": {"rich_text": [{"text": {"content": node_data.get("category", "")}}]},
            "開始フラグ": {"checkbox": node_data.get("is_start", False)},
            "終端フラグ": {"checkbox": node_data.get("is_end", False)},
            "次のノード": {"rich_text": [{"text": {"content": ", ".join(node_data.get("next_nodes", []))}}]},
            "難易度": {"rich_text": [{"text": {"content": "初級"}}]},
            "メモ": {"rich_text": [{"text": {"content": f"{node_data.get('category', '')}関連の診断ノード"}}]}
        }
        
        try:
            response = client.pages.create(
                parent={"database_id": NODE_DB},
                properties=properties
            )
            created_pages[node_id] = response["id"]
            print(f"✅ {node_id} を追加しました")
            
            # API制限を避けるため少し待機
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ {node_id} の追加に失敗: {e}")
    
    print(f"\n📊 診断フロー移行結果:")
    print(f"成功: {len(created_pages)}件")
    print(f"失敗: {total_nodes - len(created_pages)}件")
    
    return created_pages

def migrate_all_repair_cases():
    """すべての修理ケースデータを移行"""
    print("\n 全修理ケースデータの移行を開始...")
    
    # まず部品・工具のIDマッピングを作成
    parts_tools_mapping = {}
    
    # 部品・工具データベースから既存のアイテムを取得
    try:
        response = client.databases.query(database_id=ITEM_DB)
        for page in response["results"]:
            item_name = page["properties"]["部品名"]["title"][0]["text"]["content"]
            item_id = page["id"]
            parts_tools_mapping[item_name] = item_id
        print(f"📋 既存の部品・工具: {len(parts_tools_mapping)}件")
    except Exception as e:
        print(f"⚠️ 部品・工具マッピングの取得に失敗: {e}")
        parts_tools_mapping = {}
    
    # CSVファイルを読み込み
    with open('修理ケースDB 24d709bb38f18039a8b3e0bec10bb7eb.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cases = list(reader)
    
    # CSVファイルに含まれる部品・工具を収集
    required_items = set()
    for row in cases:
        # 必要な部品
        parts_text = row.get("必要な部品", "")
        if parts_text:
            for part in parts_text.split(", "):
                part = part.strip()
                if part:
                    required_items.add(part)
        
        # 必要な工具
        tools_text = row.get("必要な工具", "")
        if tools_text:
            for tool in tools_text.split(", "):
                tool = tool.strip()
                if tool:
                    required_items.add(tool)
    
    print(f"📋 CSVファイルで必要な部品・工具: {len(required_items)}件")
    
    # 不足している部品・工具を部品・工具データベースに追加
    missing_items = required_items - set(parts_tools_mapping.keys())
    if missing_items:
        print(f"📋 不足している部品・工具: {len(missing_items)}件")
        for item_name in missing_items:
            print(f"  {item_name} を追加中...")
            
            # カテゴリを推定
            if any(keyword in item_name for keyword in ["バッテリー", "端子", "ケーブル", "リレー", "配線", "コネクタ", "ベルト", "オルタネーター", "アース"]):
                category = "部品"
            elif any(keyword in item_name for keyword in ["テスター", "レンチ", "ブラシ", "ドライバー", "メーター", "クランプ"]):
                category = "工具"
            else:
                category = "その他"
            
            properties = {
                "部品名": {"title": [{"text": {"content": item_name}}]},
                "カテゴリ": {"rich_text": [{"text": {"content": category}}]},
                "価格": {"rich_text": [{"text": {"content": "要確認"}}]},
                "購入先": {"rich_text": [{"text": {"content": "要確認"}}]},
                "在庫状況": {"rich_text": [{"text": {"content": "要確認"}}]},
                "メモ": {"rich_text": [{"text": {"content": f"CSVファイルから自動追加された{item_name}"}}]}
            }
            
            try:
                response = client.pages.create(
                    parent={"database_id": ITEM_DB},
                    properties=properties
                )
                parts_tools_mapping[item_name] = response["id"]
                print(f"✅ {item_name} を追加しました")
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ {item_name} の追加に失敗: {e}")
    
    created_cases = {}
    total_cases = len(cases)
    processed = 0
    
    for row in cases:
        processed += 1
        case_name = row.get("対象名称", f"CASE-{processed}")
        print(f" [{processed}/{total_cases}] {case_name} を追加中...")
        
        # HTMLタグを除去（<br>を改行に変換）
        repair_steps = row.get("修理手順", "").replace("<br>", "\n")
        
        # 必要な部品と工具をリレーション型として設定
        required_parts = []
        required_tools = []
        
        # 必要な部品の処理
        parts_text = row.get("必要な部品", "")
        if parts_text:
            for part in parts_text.split(", "):
                part = part.strip()
                if part and part in parts_tools_mapping:
                    required_parts.append({"id": parts_tools_mapping[part]})
        
        # 必要な工具の処理
        tools_text = row.get("必要な工具", "")
        if tools_text:
            for tool in tools_text.split(", "):
                tool = tool.strip()
                if tool and tool in parts_tools_mapping:
                    required_tools.append({"id": parts_tools_mapping[tool]})
        
        properties = {
            "ケースID": {"title": [{"text": {"content": row.get("terminal_case_id", f"CASE-{processed}")}}]},
            "症状": {"rich_text": [{"text": {"content": row.get("症状", "")}}]},
            "修理手順": {"rich_text": [{"text": {"content": repair_steps}}]},
            "推定時間": {"rich_text": [{"text": {"content": f"{row.get('作業時間', '')}分"}}]},
            "難易度": {"rich_text": [{"text": {"content": row.get("難易度", "初級")}}]},
            "注意事項": {"rich_text": [{"text": {"content": row.get("注意事項", "")}}]}
        }
        
        # リレーション型のフィールドを追加（空でない場合のみ）
        if required_parts:
            properties["必要な部品"] = {"relation": required_parts}
        
        if required_tools:
            properties["必要な工具"] = {"relation": required_tools}
        
        try:
            response = client.pages.create(
                parent={"database_id": CASE_DB},
                properties=properties
            )
            created_cases[case_name] = response["id"]
            print(f"✅ {case_name} を追加しました")
            
            # API制限を避けるため少し待機
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ {case_name} の追加に失敗: {e}")
    
    print(f"\n📊 修理ケース移行結果:")
    print(f"成功: {len(created_cases)}件")
    print(f"失敗: {total_cases - len(created_cases)}件")
    
    return created_cases

def migrate_parts_and_tools():
    """部品・工具データを移行"""
    print("\n 部品・工具データの移行を開始...")
    
    # 部品・工具のマスターデータ
    parts_and_tools = [
        {"name": "バッテリー", "category": "バッテリー", "price": "8,000円", "supplier": "カー用品店", "stock": "在庫あり"},
        {"name": "ブースターケーブル", "category": "工具", "price": "3,000円", "supplier": "ホームセンター", "stock": "在庫あり"},
        {"name": "テスター", "category": "工具", "price": "5,000円", "supplier": "電気工具店", "stock": "在庫あり"},
        {"name": "レンチ", "category": "工具", "price": "2,000円", "supplier": "ホームセンター", "stock": "在庫あり"},
        {"name": "端子クリーナー", "category": "工具", "price": "1,500円", "supplier": "カー用品店", "stock": "在庫あり"},
        {"name": "バッテリーグリス", "category": "その他", "price": "800円", "supplier": "カー用品店", "stock": "在庫あり"},
        {"name": "ポータブルバッテリーチャージャー", "category": "工具", "price": "15,000円", "supplier": "カー用品店", "stock": "在庫あり"},
        {"name": "ワイヤーブラシ", "category": "工具", "price": "500円", "supplier": "ホームセンター", "stock": "在庫あり"},
        {"name": "ドライバー", "category": "工具", "price": "1,500円", "supplier": "ホームセンター", "stock": "在庫あり"},
        {"name": "保護手袋", "category": "その他", "price": "300円", "supplier": "ホームセンター", "stock": "在庫あり"}
    ]
    
    created_items = {}
    
    for item in parts_and_tools:
        print(f" {item['name']} を追加中...")
        
        properties = {
            "部品名": {"title": [{"text": {"content": item["name"]}}]},
            "カテゴリ": {"rich_text": [{"text": {"content": item["category"]}}]},
            "価格": {"rich_text": [{"text": {"content": item["price"]}}]},
            "購入先": {"rich_text": [{"text": {"content": item["supplier"]}}]},
            "在庫状況": {"rich_text": [{"text": {"content": item["stock"]}}]},
            "メモ": {"rich_text": [{"text": {"content": f"{item['category']}カテゴリの{item['name']}"}}]}
        }
        
        try:
            response = client.pages.create(
                parent={"database_id": ITEM_DB},
                properties=properties
            )
            created_items[item["name"]] = response["id"]
            print(f"✅ {item['name']} を追加しました")
            
            # API制限を避けるため少し待機
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ {item['name']} の追加に失敗: {e}")
    
    print(f"\n📊 部品・工具移行結果:")
    print(f"成功: {len(created_items)}件")
    print(f"失敗: {len(parts_and_tools) - len(created_items)}件")
    
    return created_items

def main():
    """メイン実行関数"""
    print("   全データ移行を開始します...")
    print(f"📋 使用するデータベース:")
    print(f"  診断フローDB: {NODE_DB}")
    print(f"  修理ケースDB: {CASE_DB}")
    print(f"  部品・工具DB: {ITEM_DB}")
    print()
    
    # 各データベースへの移行
    created_nodes = migrate_all_diagnostic_nodes()
    created_cases = migrate_all_repair_cases()
    created_items = migrate_parts_and_tools()
    
    # 総合結果
    print("\n" + "="*50)
    print("✅ 全データ移行完了！")
    print("="*50)
    print(f"📈 総合結果:")
    print(f"  診断ノード: {len(created_nodes)}件")
    print(f"  修理ケース: {len(created_cases)}件")
    print(f"  部品・工具: {len(created_items)}件")
    print(f"  合計: {len(created_nodes) + len(created_cases) + len(created_items)}件")
    print("="*50)

if __name__ == "__main__":
    main()