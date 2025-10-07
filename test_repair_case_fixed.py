# test_repair_case_fixed.py
from notion_client import Client
import os

# 環境変数から設定を取得
API_KEY = os.getenv("NOTION_API_KEY")
CASE_DB = os.getenv("CASE_DB_ID")

client = Client(auth=API_KEY)

def test_repair_case_migration_fixed():
    """サブバッテリー関連の修理ケースをテスト移行（メモプロパティ削除版）"""
    print(" サブバッテリー関連修理ケースのテスト移行（修正版）...")
    
    # サブバッテリー関連の修理ケース
    subbattery_cases = [
        {
            "name": "サブバッテリー完全放電",
            "case_id": "CASE-SUB-001",
            "症状": "サブバッテリーが完全放電・使用不可",
            "原因": "過放電、経年劣化",
            "修理手順": "1. ブースターケーブルで応急措置\n2. ポータブルバッテリーチャージャーで充電\n3. 新品交換（3-5年使用の場合）",
            "必要な部品": "ブースターケーブル, ポータブルバッテリーチャージャー, サブバッテリー",
            "必要な工具": "テスター, レンチ",
            "推定時間": "30分",
            "難易度": "初級",
            "注意事項": "火気厳禁。作業時はマイナス端子から外す。スパーク・感電に注意。"
        },
        {
            "name": "サブバッテリー端子接続不良",
            "case_id": "CASE-SUB-002", 
            "症状": "サブバッテリー端子/配線の接続不良",
            "原因": "端子の汚れ・腐食、配線の緩み",
            "修理手順": "1. 端子の清掃（ワイヤーブラシ使用）\n2. 端子・配線の締め直し\n3. 必要に応じて端子交換",
            "必要な部品": "端子クリーナー, バッテリー端子, バッテリーグリス",
            "必要な工具": "ワイヤーブラシ, レンチ, ドライバー",
            "推定時間": "20分",
            "難易度": "初級",
            "注意事項": "端子の清掃時は保護手袋を着用。腐食した端子は交換を推奨。"
        }
    ]
    
    created_cases = {}
    
    for case in subbattery_cases:
        print(f" {case['name']} を追加中...")
        
        # メモプロパティを削除して修正
        properties = {
            "ケースID": {"title": [{"text": {"content": case["case_id"]}}]},
            "症状": {"rich_text": [{"text": {"content": case["症状"]}}]},
            "修理手順": {"rich_text": [{"text": {"content": case["修理手順"]}}]},
            "必要な部品": {"rich_text": [{"text": {"content": case["必要な部品"]}}]},
            "必要な工具": {"rich_text": [{"text": {"content": case["必要な工具"]}}]},
            "推定時間": {"rich_text": [{"text": {"content": case["推定時間"]}}]},
            "難易度": {"rich_text": [{"text": {"content": case["難易度"]}}]},
            "注意事項": {"rich_text": [{"text": {"content": case["注意事項"]}}]}
        }
        
        try:
            response = client.pages.create(
                parent={"database_id": CASE_DB},
                properties=properties
            )
            created_cases[case["case_id"]] = response["id"]
            print(f"✅ {case['name']} を追加しました (ID: {response['id']})")
        except Exception as e:
            print(f"❌ {case['name']} の追加に失敗: {e}")
    
    print(f"\n📊 修理ケース移行結果:")
    print(f"成功: {len(created_cases)}件")
    print(f"失敗: {len(subbattery_cases) - len(created_cases)}件")
    
    return created_cases

if __name__ == "__main__":
    print(" 修理ケースのテスト移行を開始します...")
    created_cases = test_repair_case_migration_fixed()
    print(f"\n✅ 修理ケース移行完了！")
    print(f"   結果: {len(created_cases)}件成功")