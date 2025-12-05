#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ビルダーマスタ管理モジュール（フェーズ1）
ビルダー（販売店）のCRUD操作とID自動採番を実装
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from data_access.notion_client import notion_client


class BuilderManager:
    """ビルダーマスタ管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.notion = notion_client.client
        self.builder_db_id = self._get_database_id()
        
        if not self.builder_db_id:
            raise ValueError("NOTION_BUILDER_DB_IDが設定されていません")
    
    def _get_database_id(self) -> Optional[str]:
        """データベースIDを取得"""
        db_id = (
            os.getenv("NOTION_BUILDER_DB_ID") or
            os.getenv("BUILDER_DB_ID")
        )
        if db_id:
            # ハイフンを削除して正規化
            return db_id.replace("-", "").lower()
        return None
    
    def _get_next_builder_id(self) -> str:
        """
        次のビルダーIDを生成（BUILDER-001形式）
        
        Returns:
            次のビルダーID（例: BUILDER-001）
        """
        try:
            # 既存のビルダーを取得して最大IDを探す
            response = self.notion.databases.query(
                database_id=self.builder_db_id,
                page_size=100
            )
            
            max_num = 0
            for page in response.get("results", []):
                props = page.get("properties", {})
                builder_id_prop = props.get("ビルダーID", {})
                
                if builder_id_prop.get("type") == "title":
                    title_array = builder_id_prop.get("title", [])
                    if title_array:
                        builder_id = title_array[0].get("plain_text", "")
                        # BUILDER-001形式から数値を抽出
                        if builder_id.startswith("BUILDER-"):
                            try:
                                num = int(builder_id.split("-")[1])
                                max_num = max(max_num, num)
                            except (ValueError, IndexError):
                                pass
            
            # 次のIDを生成
            next_num = max_num + 1
            return f"BUILDER-{next_num:03d}"
            
        except Exception as e:
            print(f"⚠️ ID自動採番エラー: {e}")
            # エラー時はタイムスタンプベースのIDを生成
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"BUILDER-{timestamp}"
    
    def list_builders(
        self,
        status: Optional[str] = None,
        prefecture: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        ビルダー一覧を取得
        
        Args:
            status: ステータスでフィルタ（アクティブ、休止中、退会）
            prefecture: 都道府県でフィルタ
            limit: 取得件数
        
        Returns:
            ビルダーリスト
        """
        try:
            filters = []
            
            # ステータスフィルタ
            if status:
                filters.append({
                    "property": "ステータス",
                    "select": {"equals": status}
                })
            
            # 都道府県フィルタ
            if prefecture:
                filters.append({
                    "property": "所在地（都道府県）",
                    "select": {"equals": prefecture}
                })
            
            query = {
                "database_id": self.builder_db_id,
                "page_size": limit,
                "sorts": [{
                    "property": "登録日",
                    "direction": "descending"
                }]
            }
            
            if filters:
                query["filter"] = {"and": filters} if len(filters) > 1 else filters[0]
            
            response = self.notion.databases.query(**query)
            
            builders = []
            for page in response.get("results", []):
                builders.append(self._parse_builder_page(page))
            
            return builders
            
        except Exception as e:
            print(f"❌ ビルダー一覧取得エラー: {e}")
            return []
    
    def get_builder(self, builder_id: str) -> Optional[Dict[str, Any]]:
        """
        ビルダー詳細を取得
        
        Args:
            builder_id: ビルダーID（BUILDER-001形式）またはNotion Page ID
        
        Returns:
            ビルダー情報（見つからない場合はNone）
        """
        try:
            # ビルダーIDで検索
            response = self.notion.databases.query(
                database_id=self.builder_db_id,
                filter={
                    "property": "ビルダーID",
                    "title": {"equals": builder_id}
                }
            )
            
            if response.get("results"):
                return self._parse_builder_page(response["results"][0])
            
            return None
            
        except Exception as e:
            print(f"❌ ビルダー取得エラー: {e}")
            return None
    
    def create_builder(
        self,
        name: str,
        prefecture: str,
        address: str,
        phone: str,
        email: str,
        contact_person: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        ビルダーを登録
        
        Args:
            name: ビルダー名
            prefecture: 都道府県
            address: 住所
            phone: 電話番号
            email: メールアドレス
            contact_person: 担当者名
            **kwargs: その他のフィールド（line_account, status, monthly_fee, contract_start_date, notes等）
        
        Returns:
            作成されたビルダー情報
        """
        try:
            # ID自動採番
            builder_id = self._get_next_builder_id()
            
            # プロパティを構築
            properties = {
                "ビルダーID": {
                    "title": [{"text": {"content": builder_id}}]
                },
                "ビルダー名": {
                    "rich_text": [{"text": {"content": name}}]
                },
                "所在地（都道府県）": {
                    "select": {"name": prefecture}
                },
                "住所": {
                    "rich_text": [{"text": {"content": address}}]
                },
                "電話番号": {
                    "phone_number": phone
                },
                "メールアドレス": {
                    "email": email
                },
                "担当者名": {
                    "rich_text": [{"text": {"content": contact_person}}]
                },
                "ステータス": {
                    "select": {"name": kwargs.get("status", "アクティブ")}
                },
                "登録日": {
                    "date": {"start": datetime.now().isoformat()}
                },
                "総紹介数": {
                    "number": kwargs.get("total_referrals", 0)
                },
                "成約数": {
                    "number": kwargs.get("total_deals", 0)
                },
                "月額利用料": {
                    "number": kwargs.get("monthly_fee", 0)
                }
            }
            
            # LINE公式アカウントがあれば追加
            if kwargs.get("line_account"):
                properties["LINE公式アカウント"] = {
                    "url": kwargs["line_account"]
                }
            
            # 契約開始日があれば追加
            if kwargs.get("contract_start_date"):
                properties["契約開始日"] = {
                    "date": {"start": kwargs["contract_start_date"]}
                }
            
            # 備考があれば追加
            if kwargs.get("notes"):
                properties["備考"] = {
                    "rich_text": [{"text": {"content": kwargs["notes"]}}]
                }
            
            # Notionにページ作成
            new_page = self.notion.pages.create(
                parent={"database_id": self.builder_db_id},
                properties=properties
            )
            
            return self._parse_builder_page(new_page)
            
        except Exception as e:
            print(f"❌ ビルダー登録エラー: {e}")
            raise
    
    def update_builder(
        self,
        builder_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        ビルダー情報を更新
        
        Args:
            builder_id: ビルダーID（BUILDER-001形式）またはNotion Page ID
            **kwargs: 更新するフィールド
        
        Returns:
            更新されたビルダー情報
        """
        try:
            # ビルダーを取得
            builder = self.get_builder(builder_id)
            if not builder:
                return None
            
            page_id = builder["page_id"]
            
            # 更新プロパティを構築
            properties = {}
            
            if "name" in kwargs:
                properties["ビルダー名"] = {
                    "rich_text": [{"text": {"content": kwargs["name"]}}]
                }
            if "prefecture" in kwargs:
                properties["所在地（都道府県）"] = {
                    "select": {"name": kwargs["prefecture"]}
                }
            if "address" in kwargs:
                properties["住所"] = {
                    "rich_text": [{"text": {"content": kwargs["address"]}}]
                }
            if "phone" in kwargs:
                properties["電話番号"] = {
                    "phone_number": kwargs["phone"]
                }
            if "email" in kwargs:
                properties["メールアドレス"] = {
                    "email": kwargs["email"]
                }
            if "contact_person" in kwargs:
                properties["担当者名"] = {
                    "rich_text": [{"text": {"content": kwargs["contact_person"]}}]
                }
            if "line_account" in kwargs:
                properties["LINE公式アカウント"] = {
                    "url": kwargs["line_account"]
                }
            if "status" in kwargs:
                properties["ステータス"] = {
                    "select": {"name": kwargs["status"]}
                }
            if "total_referrals" in kwargs:
                properties["総紹介数"] = {
                    "number": kwargs["total_referrals"]
                }
            if "total_deals" in kwargs:
                properties["成約数"] = {
                    "number": kwargs["total_deals"]
                }
            if "monthly_fee" in kwargs:
                properties["月額利用料"] = {
                    "number": kwargs["monthly_fee"]
                }
            if "contract_start_date" in kwargs:
                properties["契約開始日"] = {
                    "date": {"start": kwargs["contract_start_date"]}
                }
            if "notes" in kwargs:
                properties["備考"] = {
                    "rich_text": [{"text": {"content": kwargs["notes"]}}]
                }
            
            if not properties:
                return builder
            
            # Notionでページ更新
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            return self._parse_builder_page(updated_page)
            
        except Exception as e:
            print(f"❌ ビルダー更新エラー: {e}")
            raise
    
    def _parse_builder_page(self, page: Dict) -> Dict[str, Any]:
        """Notionページをビルダー情報にパース"""
        props = page.get("properties", {})
        
        return {
            "page_id": page["id"],
            "builder_id": self._get_property_title(props, "ビルダーID"),
            "name": self._get_property_text(props, "ビルダー名"),
            "prefecture": self._get_property_select(props, "所在地（都道府県）"),
            "address": self._get_property_text(props, "住所"),
            "phone": self._get_property_phone(props, "電話番号"),
            "email": self._get_property_email(props, "メールアドレス"),
            "contact_person": self._get_property_text(props, "担当者名"),
            "line_account": self._get_property_url(props, "LINE公式アカウント"),
            "status": self._get_property_select(props, "ステータス"),
            "registered_date": self._get_property_date(props, "登録日"),
            "total_referrals": self._get_property_number(props, "総紹介数"),
            "total_deals": self._get_property_number(props, "成約数"),
            "monthly_fee": self._get_property_number(props, "月額利用料"),
            "contract_start_date": self._get_property_date(props, "契約開始日"),
            "notes": self._get_property_text(props, "備考"),
            "created_time": page.get("created_time"),
            "last_edited_time": page.get("last_edited_time")
        }
    
    def _get_property_title(self, props: Dict, key: str) -> str:
        """Titleプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") == "title":
            title_array = prop.get("title", [])
            if title_array:
                return title_array[0].get("plain_text", "")
        return ""
    
    def _get_property_text(self, props: Dict, key: str) -> str:
        """Text/Rich Textプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") in ("rich_text", "text"):
            texts = prop.get("rich_text", [])
            if texts:
                return texts[0].get("plain_text", "")
        return ""
    
    def _get_property_select(self, props: Dict, key: str) -> Optional[str]:
        """Selectプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") == "select":
            select_obj = prop.get("select")
            if select_obj:
                return select_obj.get("name")
        return None
    
    def _get_property_phone(self, props: Dict, key: str) -> Optional[str]:
        """Phoneプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") == "phone_number":
            return prop.get("phone_number")
        return None
    
    def _get_property_email(self, props: Dict, key: str) -> Optional[str]:
        """Emailプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") == "email":
            return prop.get("email")
        return None
    
    def _get_property_url(self, props: Dict, key: str) -> Optional[str]:
        """URLプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") == "url":
            return prop.get("url")
        return None
    
    def _get_property_date(self, props: Dict, key: str) -> Optional[str]:
        """Dateプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") == "date":
            date_obj = prop.get("date")
            if date_obj:
                return date_obj.get("start")
        return None
    
    def _get_property_number(self, props: Dict, key: str) -> float:
        """Numberプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") == "number":
            return prop.get("number", 0)
        return 0

