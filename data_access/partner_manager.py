#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パートナー修理店管理モジュール
Notionデータベースからパートナー修理店情報を取得・管理
"""

import os
from typing import List, Dict, Optional, Any
from data_access.notion_client import notion_client

# 環境変数からパートナーDB IDを取得
PARTNER_DB_ID = os.getenv("NOTION_PARTNER_DB_ID", "")

class PartnerManager:
    """パートナー修理店管理クラス"""
    
    def __init__(self):
        self.db_id = PARTNER_DB_ID
        if not self.db_id:
            print("⚠️ NOTION_PARTNER_DB_ID が設定されていません")
    
    def list_shops(self, status: Optional[str] = None, prefecture: Optional[str] = None, specialty: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        パートナー修理店一覧を取得（APIエンドポイント用）
        
        Args:
            status: ステータスフィルタ（オプション、デフォルト: アクティブ）
            prefecture: 都道府県フィルタ（オプション）
            specialty: 専門分野フィルタ（オプション）
        
        Returns:
            パートナー修理店のリスト
        """
        import sys
        sys.stderr.write(f"[AgentLog] list_shops called with status={status}, prefecture={prefecture}, specialty={specialty}\n")
        sys.stderr.flush()
        
        if not self.db_id:
            sys.stderr.write(f"[AgentLog] ERROR: db_id is not set. NOTION_PARTNER_DB_ID={PARTNER_DB_ID}\n")
            sys.stderr.flush()
            return []
        
        try:
            # フィルタ条件を構築
            filters = []
            
            # ステータスフィルタ（デフォルトは「アクティブ」）
            if status:
                filters.append({
                    "property": "status",
                    "select": {
                        "equals": status
                    }
                })
            else:
                # デフォルトでアクティブのみ
                filters.append({
                    "property": "status",
                    "select": {
                        "equals": "アクティブ"
                    }
                })
            
            # 都道府県フィルタ
            if prefecture:
                filters.append({
                    "property": "prefecture",
                    "select": {
                        "equals": prefecture
                    }
                })
            
            # 専門分野フィルタ
            if specialty:
                filters.append({
                    "property": "specialties",
                    "multi_select": {
                        "contains": specialty
                    }
                })
            
            # フィルタをAND条件で結合
            filter_condition = {}
            if len(filters) > 0:
                if len(filters) == 1:
                    filter_condition = filters[0]
                else:
                    filter_condition = {
                        "and": filters
                    }
            
            sys.stderr.write(f"[AgentLog] Querying Notion database with filter: {filter_condition}\n")
            sys.stderr.flush()
            
            # Notionからデータ取得
            response = notion_client.databases.query(
                database_id=self.db_id,
                filter=filter_condition if filter_condition else None,
                sorts=[
                    {
                        "property": "name",
                        "direction": "ascending"
                    }
                ]
            )
            
            sys.stderr.write(f"[AgentLog] Notion response received: {len(response.get('results', []))} results\n")
            sys.stderr.flush()
            
            partners = []
            for page in response.get("results", []):
                partner = self._parse_partner_page(page)
                if partner:
                    partners.append(partner)
            
            sys.stderr.write(f"[AgentLog] ✅ パートナー修理店を{len(partners)}件取得しました\n")
            sys.stderr.flush()
            print(f"✅ パートナー修理店を{len(partners)}件取得しました")
            return partners
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            sys.stderr.write(f"[AgentLog] ❌ パートナー修理店取得エラー: {e}\n")
            sys.stderr.write(f"[AgentLog] Traceback: {error_trace}\n")
            sys.stderr.flush()
            print(f"❌ パートナー修理店取得エラー: {e}")
            print(error_trace)
            return []
    
    def get_all_partners(self, prefecture: Optional[str] = None, specialty: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        パートナー修理店一覧を取得
        
        Args:
            prefecture: 都道府県フィルタ（オプション）
            specialty: 専門分野フィルタ（オプション）
        
        Returns:
            パートナー修理店のリスト
        """
        # list_shopsに委譲
        return self.list_shops(status="アクティブ", prefecture=prefecture, specialty=specialty)
    
    def get_partner_by_id(self, shop_id: str) -> Optional[Dict[str, Any]]:
        """
        指定されたIDのパートナー修理店を取得
        
        Args:
            shop_id: 修理店ID
        
        Returns:
            パートナー修理店情報 or None
        """
        if not self.db_id:
            return None
        
        try:
            response = notion_client.databases.query(
                database_id=self.db_id,
                filter={
                    "property": "shop_id",
                    "rich_text": {
                        "equals": shop_id
                    }
                }
            )
            
            results = response.get("results", [])
            if results:
                return self._parse_partner_page(results[0])
            
            return None
            
        except Exception as e:
            print(f"❌ パートナー修理店取得エラー (ID: {shop_id}): {e}")
            return None
    
    def _parse_partner_page(self, page: Dict) -> Optional[Dict[str, Any]]:
        """
        NotionページをPartnerShop形式にパース
        
        Args:
            page: Notionページオブジェクト
        
        Returns:
            パートナー修理店情報の辞書
        """
        try:
            properties = page.get("properties", {})
            
            # 基本情報
            shop_id = self._get_text_property(properties, "shop_id")
            name = self._get_title_property(properties, "name")
            phone = self._get_phone_property(properties, "phone")
            email = self._get_email_property(properties, "email")
            prefecture = self._get_select_property(properties, "prefecture")
            address = self._get_text_property(properties, "address")
            specialties = self._get_multi_select_property(properties, "specialties")
            business_hours = self._get_text_property(properties, "business_hours")
            status = self._get_select_property(properties, "status")
            
            # 数値情報
            initial_diagnosis_fee = self._get_number_property(properties, "initial_diagnosis_fee", 0)
            avg_rating = self._get_number_property(properties, "avg_rating", 0.0)
            review_count = self._get_number_property(properties, "review_count", 0)
            repair_count = self._get_number_property(properties, "repair_count", 0)
            
            # 必須フィールドのチェック
            if not shop_id or not name:
                print(f"⚠️ 必須フィールドが不足しています: shop_id={shop_id}, name={name}")
                return None
            
            return {
                "shop_id": shop_id,
                "name": name,
                "phone": phone or "",
                "email": email or "",
                "prefecture": prefecture or "",
                "address": address or "",
                "specialties": specialties,
                "business_hours": business_hours or "要問合せ",
                "initial_diagnosis_fee": initial_diagnosis_fee,
                "status": status or "アクティブ",
                "avg_rating": avg_rating,
                "review_count": review_count,
                "repair_count": repair_count,
                "page_id": page["id"],
                # フロントエンド互換用
                "success_rate": 0,  # 今後実装
                "total_referrals": 0,  # 今後実装
                "total_deals": 0,  # 今後実装
                "line_notification": False,  # 今後実装
            }
            
        except Exception as e:
            print(f"❌ パートナーページのパースエラー: {e}")
            return None
    
    # プロパティ取得ヘルパーメソッド
    def _get_title_property(self, properties: Dict, key: str) -> str:
        """タイトルプロパティを取得"""
        try:
            title_list = properties.get(key, {}).get("title", [])
            if title_list:
                return title_list[0].get("text", {}).get("content", "")
        except:
            pass
        return ""
    
    def _get_text_property(self, properties: Dict, key: str) -> str:
        """テキストプロパティを取得"""
        try:
            text_list = properties.get(key, {}).get("rich_text", [])
            if text_list:
                return text_list[0].get("text", {}).get("content", "")
        except:
            pass
        return ""
    
    def _get_select_property(self, properties: Dict, key: str) -> str:
        """セレクトプロパティを取得"""
        try:
            select = properties.get(key, {}).get("select", {})
            if select:
                return select.get("name", "")
        except:
            pass
        return ""
    
    def _get_multi_select_property(self, properties: Dict, key: str) -> List[str]:
        """マルチセレクトプロパティを取得"""
        try:
            multi_select = properties.get(key, {}).get("multi_select", [])
            return [item.get("name", "") for item in multi_select]
        except:
            pass
        return []
    
    def _get_number_property(self, properties: Dict, key: str, default: float = 0) -> float:
        """数値プロパティを取得"""
        try:
            number = properties.get(key, {}).get("number")
            if number is not None:
                return number
        except:
            pass
        return default
    
    def _get_phone_property(self, properties: Dict, key: str) -> str:
        """電話番号プロパティを取得"""
        try:
            phone = properties.get(key, {}).get("phone_number")
            if phone:
                return phone
        except:
            pass
        return ""
    
    def _get_email_property(self, properties: Dict, key: str) -> str:
        """メールプロパティを取得"""
        try:
            email = properties.get(key, {}).get("email")
            if email:
                return email
        except:
            pass
        return ""

# シングルトンインスタンス
partner_manager = PartnerManager()



