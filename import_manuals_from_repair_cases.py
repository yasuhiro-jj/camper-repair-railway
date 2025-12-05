#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion修理ケースDBからマニュアルを抽出して、マニュアルDBに追加するスクリプト
フェーズ2-3: 工場教育AIモード用
"""

import os
import sys
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_MANUAL_DB_ID = os.getenv("NOTION_MANUAL_DB_ID")
# 複数の環境変数名に対応
NOTION_CASE_DB_ID = (
    os.getenv("CASE_DB_ID") or 
    os.getenv("NOTION_CASE_DB_ID") or 
    os.getenv("NOTION_REPAIR_CASE_DB_ID") or
    os.getenv("NOTION_CASE_DB_ID")
)
NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2022-06-28")

NOTION_PAGES_URL = "https://api.notion.com/v1/pages"
NOTION_DATABASE_URL = "https://api.notion.com/v1/databases"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": NOTION_API_VERSION,
    "Content-Type": "application/json",
}


def format_database_id(db_id: str) -> str:
    """
    NotionデータベースIDを正しい形式にフォーマット
    32文字のIDを8-4-4-4-12の形式に変換
    """
    if not db_id:
        return ""
    
    # ハイフンを除去
    db_id = db_id.replace("-", "")
    
    # 32文字でない場合はそのまま返す
    if len(db_id) != 32:
        return db_id
    
    # 8-4-4-4-12の形式にフォーマット
    return f"{db_id[:8]}-{db_id[8:12]}-{db_id[12:16]}-{db_id[16:20]}-{db_id[20:]}"


def get_repair_cases(limit: int = 100) -> List[Dict[str, Any]]:
    """修理ケースDBからデータを取得"""
    if not NOTION_CASE_DB_ID:
        print("❌ CASE_DB_IDが設定されていません")
        return []
    
    # データベースIDを正しい形式にフォーマット
    db_id = format_database_id(NOTION_CASE_DB_ID)
    print(f"   📋 データベースID: {db_id[:8]}...{db_id[-8:]}")
    
    try:
        url = f"{NOTION_DATABASE_URL}/{db_id}/query"
        print(f"   🔗 リクエストURL: {url[:80]}...")
        
        response = requests.post(
            url,
            headers=headers,
            json={"page_size": limit},
            timeout=15
        )
        
        if not response.ok:
            print(f"❌ 修理ケース取得エラー: {response.status_code}")
            print(f"   レスポンス: {response.text[:500]}")
            
            if response.status_code == 404:
                print("\n   💡 考えられる原因:")
                print("   1. データベースIDが間違っている")
                print("   2. データベースがインテグレーションと共有されていない")
                print("   3. データベースIDにハイフンが含まれている（除去が必要）")
                print(f"\n   確認: データベースID = {db_id}")
            
            return []
        
        results = response.json().get("results", [])
        print(f"   ✅ 取得成功: {len(results)}件")
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
        return []
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_property_text(prop: Dict) -> str:
    """Rich Textプロパティからテキストを抽出"""
    if not prop or prop.get("type") != "rich_text":
        return ""
    
    rich_text = prop.get("rich_text", [])
    if not rich_text:
        return ""
    
    return "".join(item.get("plain_text", "") for item in rich_text)


def extract_property_select(prop: Dict) -> str:
    """Selectプロパティから値を抽出"""
    if not prop or prop.get("type") != "select":
        return ""
    
    select = prop.get("select")
    if not select:
        return ""
    
    return select.get("name", "")


def extract_property_multi_select(prop: Dict) -> List[str]:
    """Multi-selectプロパティから値を抽出"""
    if not prop or prop.get("type") != "multi_select":
        return []
    
    multi_select = prop.get("multi_select", [])
    return [item.get("name", "") for item in multi_select]


def extract_property_number(prop: Dict) -> Optional[int]:
    """Numberプロパティから値を抽出"""
    if not prop or prop.get("type") != "number":
        return None
    
    return prop.get("number")


def convert_repair_case_to_manual(case: Dict, manual_id: str) -> Optional[Dict[str, Any]]:
    """修理ケースをマニュアル形式に変換"""
    try:
        props = case.get("properties", {})
        
        # タイトルを取得
        title = ""
        for prop_name, prop_data in props.items():
            if prop_data.get("type") == "title":
                title_list = prop_data.get("title", [])
                if title_list:
                    title = title_list[0].get("text", {}).get("content", "")
                break
        
        if not title:
            return None
        
        # 各種プロパティを取得
        category = extract_property_select(props.get("カテゴリ", {}))
        solution = extract_property_text(props.get("解決方法", {}))
        repair_steps = extract_property_text(props.get("修理手順", {}))
        tools = extract_property_multi_select(props.get("必要な工具", {}))
        difficulty = extract_property_select(props.get("難易度", {}))
        estimated_time = extract_property_number(props.get("推定時間", {}))
        
        # 作業手順を統合（解決方法 + 修理手順）
        steps = solution
        if repair_steps:
            if steps:
                steps += "\n\n" + repair_steps
            else:
                steps = repair_steps
        
        if not steps:
            steps = "修理ケースから抽出された情報です。詳細は元のケースを参照してください。"
        
        # 難易度のデフォルト値
        if not difficulty:
            difficulty = "中級"
        
        # 推定時間のデフォルト値
        if not estimated_time:
            estimated_time = 60
        
        # マニュアルデータを構築
        manual_properties = {
            "マニュアルID": {
                "title": [{"text": {"content": manual_id}}]
            },
            "タイトル": {
                "rich_text": [{"text": {"content": f"{title}（修理ケースから抽出）"}}]
            },
            "カテゴリ": {
                "select": {"name": category} if category else None
            },
            "作業手順": {
                "rich_text": [{"text": {"content": steps[:2000]}}]  # Notionの制限に合わせて切り詰め
            },
            "必要な工具": {
                "multi_select": [{"name": tool} for tool in tools] if tools else []
            },
            "難易度": {
                "select": {"name": difficulty}
            },
            "推定時間": {
                "number": estimated_time
            },
            "安全注意事項": {
                "rich_text": [{"text": {"content": "修理ケースから抽出された情報です。実際の作業時は安全に注意してください。"}}]
            },
            "タグ": {
                "multi_select": [{"name": "修理"}, {"name": "ケース"}]
            }
        }
        
        # Noneのプロパティを削除
        manual_properties = {k: v for k, v in manual_properties.items() if v is not None}
        
        return manual_properties
    
    except Exception as e:
        print(f"⚠️ 変換エラー: {e}")
        return None


def create_manual(manual_properties: Dict[str, Any]) -> bool:
    """マニュアルをNotionに作成"""
    if not NOTION_MANUAL_DB_ID:
        print("❌ NOTION_MANUAL_DB_IDが設定されていません")
        return False
    
    # データベースIDを正しい形式にフォーマット
    db_id = format_database_id(NOTION_MANUAL_DB_ID)
    
    try:
        response = requests.post(
            NOTION_PAGES_URL,
            headers=headers,
            json={
                "parent": {"database_id": db_id},
                "properties": manual_properties
            },
            timeout=15
        )
        
        if response.ok:
            return True
        else:
            print(f"❌ マニュアル作成エラー: {response.status_code}")
            print(f"   レスポンス: {response.text[:200]}")
            if response.status_code == 404:
                print(f"   データベースID: {db_id}")
                print(f"   データベースがインテグレーションと共有されているか確認してください")
            return False
    
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


def get_existing_manual_ids() -> List[str]:
    """既存のマニュアルIDを取得"""
    if not NOTION_MANUAL_DB_ID:
        return []
    
    # データベースIDを正しい形式にフォーマット
    db_id = format_database_id(NOTION_MANUAL_DB_ID)
    
    try:
        response = requests.post(
            f"{NOTION_DATABASE_URL}/{db_id}/query",
            headers=headers,
            json={"page_size": 100},
            timeout=15
        )
        
        if not response.ok:
            if response.status_code == 404:
                print(f"   ⚠️ マニュアルDBが見つかりません（404）")
                print(f"   データベースID: {db_id}")
                print(f"   データベースがインテグレーションと共有されているか確認してください")
            return []
        
        results = response.json().get("results", [])
        existing_ids = []
        
        for page in results:
            props = page.get("properties", {})
            for prop_name, prop_data in props.items():
                if prop_data.get("type") == "title":
                    title_list = prop_data.get("title", [])
                    if title_list:
                        manual_id = title_list[0].get("text", {}).get("content", "")
                        if manual_id.startswith("MANUAL-"):
                            existing_ids.append(manual_id)
                    break
        
        return existing_ids
    
    except Exception as e:
        print(f"⚠️ 既存ID取得エラー: {e}")
        return []


def get_next_manual_id(existing_ids: List[str]) -> str:
    """次のマニュアルIDを生成"""
    if not existing_ids:
        return "MANUAL-101"
    
    # 数値部分を抽出して最大値を取得
    numbers = []
    for manual_id in existing_ids:
        try:
            num = int(manual_id.replace("MANUAL-", ""))
            numbers.append(num)
        except:
            pass
    
    if not numbers:
        return "MANUAL-101"
    
    next_num = max(numbers) + 1
    return f"MANUAL-{next_num:03d}"


def main():
    """メイン処理"""
    print("=" * 60)
    print("修理ケースDBからマニュアルを抽出・追加")
    print("=" * 60)
    
    # 環境変数チェック
    print("\n🔍 環境変数の確認...")
    print(f"   NOTION_API_KEY: {'設定済み' if NOTION_API_KEY else '❌ 未設定'}")
    print(f"   NOTION_MANUAL_DB_ID: {NOTION_MANUAL_DB_ID if NOTION_MANUAL_DB_ID else '❌ 未設定'}")
    print(f"   NOTION_CASE_DB_ID: {NOTION_CASE_DB_ID if NOTION_CASE_DB_ID else '❌ 未設定'}")
    
    if not NOTION_API_KEY:
        print("\n❌ NOTION_API_KEYが設定されていません")
        return
    
    if not NOTION_MANUAL_DB_ID:
        print("\n❌ NOTION_MANUAL_DB_IDが設定されていません")
        print("   .envファイルに以下を追加してください:")
        print("   NOTION_MANUAL_DB_ID=1afb2b6e3a5f4d2b94d0edeca5a57824")
        return
    
    if not NOTION_CASE_DB_ID:
        print("\n❌ CASE_DB_IDが設定されていません")
        print("   .envファイルに以下を確認してください:")
        print("   CASE_DB_ID=256e9a7ee5b78021924cd65854d8880f")
        print("   または")
        print("   NOTION_CASE_DB_ID=256e9a7ee5b78021924cd65854d8880f")
        return
    
    # 既存のマニュアルIDを取得
    print("\n📋 既存のマニュアルIDを確認中...")
    existing_ids = get_existing_manual_ids()
    print(f"   既存マニュアル数: {len(existing_ids)}件")
    
    # 修理ケースを取得
    print("\n📋 修理ケースを取得中...")
    repair_cases = get_repair_cases(limit=50)
    print(f"   取得件数: {len(repair_cases)}件")
    
    if not repair_cases:
        print("⚠️ 修理ケースが見つかりませんでした")
        return
    
    # マニュアルに変換して追加
    print("\n📝 マニュアルに変換して追加中...")
    success_count = 0
    skip_count = 0
    
    for case in repair_cases:
        manual_id = get_next_manual_id(existing_ids)
        manual_properties = convert_repair_case_to_manual(case, manual_id)
        
        if not manual_properties:
            skip_count += 1
            continue
        
        if create_manual(manual_properties):
            print(f"   ✅ {manual_id}: {manual_properties.get('タイトル', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '')[:50]}")
            existing_ids.append(manual_id)
            success_count += 1
        else:
            skip_count += 1
    
    print("\n" + "=" * 60)
    print("処理完了")
    print("=" * 60)
    print(f"✅ 追加成功: {success_count}件")
    print(f"⚠️ スキップ: {skip_count}件")
    print(f"📊 合計マニュアル数: {len(existing_ids)}件")


if __name__ == "__main__":
    main()

