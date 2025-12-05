#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工場マスタ管理モジュール（フェーズ1）
工場のCRUD操作とID自動採番を実装
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from data_access.notion_client import notion_client


class FactoryManager:
    """工場マスタ管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.notion = notion_client.client
        self.factory_db_id = self._get_database_id()
        
        if not self.factory_db_id:
            raise ValueError("NOTION_FACTORY_DB_IDが設定されていません")
    
    def _get_database_id(self) -> Optional[str]:
        """データベースIDを取得"""
        db_id = (
            os.getenv("NOTION_FACTORY_DB_ID") or
            os.getenv("FACTORY_DB_ID")
        )
        if db_id:
            # ハイフンを削除して正規化
            return db_id.replace("-", "").lower()
        return None
    
    def _get_next_factory_id(self) -> str:
        """
        次の工場IDを生成（FACTORY-001形式）
        
        Returns:
            次の工場ID（例: FACTORY-001）
        """
        try:
            # 既存の工場を取得して最大IDを探す
            response = self.notion.databases.query(
                database_id=self.factory_db_id,
                page_size=100
            )
            
            max_num = 0
            for page in response.get("results", []):
                props = page.get("properties", {})
                factory_id_prop = props.get("工場ID", {})
                
                if factory_id_prop.get("type") == "title":
                    title_array = factory_id_prop.get("title", [])
                    if title_array:
                        factory_id = title_array[0].get("plain_text", "")
                        # FACTORY-001形式から数値を抽出
                        if factory_id.startswith("FACTORY-"):
                            try:
                                num = int(factory_id.split("-")[1])
                                max_num = max(max_num, num)
                            except (ValueError, IndexError):
                                pass
            
            # 次のIDを生成
            next_num = max_num + 1
            return f"FACTORY-{next_num:03d}"
            
        except Exception as e:
            print(f"⚠️ ID自動採番エラー: {e}")
            # エラー時はタイムスタンプベースのIDを生成
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"FACTORY-{timestamp}"
    
    def list_factories(
        self,
        status: Optional[str] = None,
        prefecture: Optional[str] = None,
        specialty: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        工場一覧を取得
        
        Args:
            status: ステータスでフィルタ（アクティブ、休止中、退会）
            prefecture: 都道府県でフィルタ
            specialty: 専門分野でフィルタ
            limit: 取得件数
        
        Returns:
            工場リスト
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
            
            # 専門分野フィルタ
            if specialty:
                filters.append({
                    "property": "専門分野",
                    "multi_select": {"contains": specialty}
                })
            
            query = {
                "database_id": self.factory_db_id,
                "page_size": limit,
                "sorts": [{
                    "property": "登録日",
                    "direction": "descending"
                }]
            }
            
            if filters:
                query["filter"] = {"and": filters} if len(filters) > 1 else filters[0]
            
            response = self.notion.databases.query(**query)
            
            factories = []
            for page in response.get("results", []):
                factories.append(self._parse_factory_page(page))
            
            return factories
            
        except Exception as e:
            print(f"❌ 工場一覧取得エラー: {e}")
            return []
    
    def get_factory(self, factory_id: str) -> Optional[Dict[str, Any]]:
        """
        工場詳細を取得
        
        Args:
            factory_id: 工場ID（FACTORY-001形式）またはNotion Page ID
        
        Returns:
            工場情報（見つからない場合はNone）
        """
        try:
            # 工場IDで検索
            response = self.notion.databases.query(
                database_id=self.factory_db_id,
                filter={
                    "property": "工場ID",
                    "title": {"equals": factory_id}
                }
            )
            
            if response.get("results"):
                return self._parse_factory_page(response["results"][0])
            
            return None
            
        except Exception as e:
            print(f"❌ 工場取得エラー: {e}")
            return None
    
    def create_factory(
        self,
        name: str,
        prefecture: str,
        address: str,
        phone: str,
        email: str,
        specialties: List[str],
        business_hours: str,
        service_areas: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        工場を登録
        
        Args:
            name: 工場名
            prefecture: 都道府県
            address: 住所
            phone: 電話番号
            email: メールアドレス
            specialties: 専門分野リスト
            business_hours: 営業時間
            service_areas: 対応可能エリアリスト
            **kwargs: その他のフィールド
        
        Returns:
            作成された工場情報
        """
        try:
            # ID自動採番
            factory_id = self._get_next_factory_id()
            
            # プロパティを構築
            properties = {
                "工場ID": {
                    "title": [{"text": {"content": factory_id}}]
                },
                "工場名": {
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
                "専門分野": {
                    "multi_select": [{"name": s} for s in specialties]
                },
                "営業時間": {
                    "rich_text": [{"text": {"content": business_hours}}]
                },
                "対応可能エリア": {
                    "multi_select": [{"name": area} for area in service_areas]
                },
                "ステータス": {
                    "select": {"name": kwargs.get("status", "アクティブ")}
                },
                "登録日": {
                    "date": {"start": datetime.now().isoformat()}
                },
                "総案件数": {
                    "number": kwargs.get("total_cases", 0)
                },
                "完了案件数": {
                    "number": kwargs.get("completed_cases", 0)
                },
                "平均対応時間": {
                    "number": kwargs.get("avg_response_time", 0)
                },
                "評価スコア": {
                    "number": kwargs.get("rating", 0)
                }
            }
            
            # 備考があれば追加
            if kwargs.get("notes"):
                properties["備考"] = {
                    "rich_text": [{"text": {"content": kwargs["notes"]}}]
                }
            
            # Notionにページ作成
            new_page = self.notion.pages.create(
                parent={"database_id": self.factory_db_id},
                properties=properties
            )
            
            return self._parse_factory_page(new_page)
            
        except Exception as e:
            print(f"❌ 工場登録エラー: {e}")
            raise
    
    def update_factory(
        self,
        factory_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        工場情報を更新
        
        Args:
            factory_id: 工場ID（FACTORY-001形式）またはNotion Page ID
            **kwargs: 更新するフィールド
        
        Returns:
            更新された工場情報
        """
        try:
            # 工場を取得
            factory = self.get_factory(factory_id)
            if not factory:
                return None
            
            page_id = factory["page_id"]
            
            # 更新プロパティを構築
            properties = {}
            
            if "name" in kwargs:
                properties["工場名"] = {
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
            if "specialties" in kwargs:
                properties["専門分野"] = {
                    "multi_select": [{"name": s} for s in kwargs["specialties"]]
                }
            if "business_hours" in kwargs:
                properties["営業時間"] = {
                    "rich_text": [{"text": {"content": kwargs["business_hours"]}}]
                }
            if "service_areas" in kwargs:
                properties["対応可能エリア"] = {
                    "multi_select": [{"name": area} for area in kwargs["service_areas"]]
                }
            if "status" in kwargs:
                properties["ステータス"] = {
                    "select": {"name": kwargs["status"]}
                }
            if "total_cases" in kwargs:
                properties["総案件数"] = {
                    "number": kwargs["total_cases"]
                }
            if "completed_cases" in kwargs:
                properties["完了案件数"] = {
                    "number": kwargs["completed_cases"]
                }
            if "avg_response_time" in kwargs:
                properties["平均対応時間"] = {
                    "number": kwargs["avg_response_time"]
                }
            if "rating" in kwargs:
                properties["評価スコア"] = {
                    "number": kwargs["rating"]
                }
            if "notes" in kwargs:
                properties["備考"] = {
                    "rich_text": [{"text": {"content": kwargs["notes"]}}]
                }
            
            if not properties:
                return factory
            
            # Notionでページ更新
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            return self._parse_factory_page(updated_page)
            
        except Exception as e:
            print(f"❌ 工場更新エラー: {e}")
            raise
    
    def get_factory_cases(
        self,
        factory_id: str,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        工場の案件一覧を取得
        
        Args:
            factory_id: 工場ID（FACTORY-001形式）またはNotion Page ID
            status: ステータスでフィルタ
            limit: 取得件数
        
        Returns:
            案件リスト
        """
        try:
            # 工場を取得
            factory = self.get_factory(factory_id)
            if not factory:
                return []
            
            # 修理ケースDBから工場でフィルタ
            case_db_id = os.getenv("NOTION_CASE_DB_ID") or os.getenv("CASE_DB_ID")
            if not case_db_id:
                print("⚠️ 修理ケースDB IDが設定されていません")
                return []
            
            case_db_id = case_db_id.replace("-", "").lower()
            
            filters = [{
                "property": "工場",
                "relation": {"contains": factory["page_id"]}
            }]
            
            if status:
                filters.append({
                    "property": "ステータス",
                    "select": {"equals": status}
                })
            
            query = {
                "database_id": case_db_id,
                "page_size": limit,
                "filter": {"and": filters} if len(filters) > 1 else filters[0],
                "sorts": [{
                    "property": "登録日",
                    "direction": "descending"
                }]
            }
            
            response = self.notion.databases.query(**query)
            
            cases = []
            for page in response.get("results", []):
                # 案件情報をパース（簡易版）
                cases.append({
                    "page_id": page["id"],
                    "case_id": self._get_property_text(page, "ケースID"),
                    "category": self._get_property_text(page, "カテゴリ"),
                    "status": self._get_property_select(page, "ステータス"),
                    "created_time": page.get("created_time")
                })
            
            return cases
            
        except Exception as e:
            print(f"❌ 工場案件取得エラー: {e}")
            return []
    
    def _parse_factory_page(self, page: Dict) -> Dict[str, Any]:
        """Notionページを工場情報にパース"""
        props = page.get("properties", {})
        
        return {
            "page_id": page["id"],
            "factory_id": self._get_property_title(props, "工場ID"),
            "name": self._get_property_text(props, "工場名"),
            "prefecture": self._get_property_select(props, "所在地（都道府県）"),
            "address": self._get_property_text(props, "住所"),
            "phone": self._get_property_phone(props, "電話番号"),
            "email": self._get_property_email(props, "メールアドレス"),
            "specialties": self._get_property_multi_select(props, "専門分野"),
            "business_hours": self._get_property_text(props, "営業時間"),
            "service_areas": self._get_property_multi_select(props, "対応可能エリア"),
            "status": self._get_property_select(props, "ステータス"),
            "registered_date": self._get_property_date(props, "登録日"),
            "total_cases": self._get_property_number(props, "総案件数"),
            "completed_cases": self._get_property_number(props, "完了案件数"),
            "avg_response_time": self._get_property_number(props, "平均対応時間"),
            "rating": self._get_property_number(props, "評価スコア"),
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
    
    def _get_property_text(self, props_or_page: Dict, key: str) -> str:
        """Text/Rich Textプロパティを取得"""
        # pageオブジェクトが渡された場合はpropertiesを取得
        if "properties" in props_or_page:
            props = props_or_page.get("properties", {})
        else:
            props = props_or_page
        
        prop = props.get(key, {})
        if prop.get("type") in ("rich_text", "text"):
            texts = prop.get("rich_text", [])
            if texts:
                return texts[0].get("plain_text", "")
        return ""
    
    def _get_property_select(self, props_or_page: Dict, key: str) -> Optional[str]:
        """Selectプロパティを取得"""
        # pageオブジェクトが渡された場合はpropertiesを取得
        if "properties" in props_or_page:
            props = props_or_page.get("properties", {})
        else:
            props = props_or_page
        
        prop = props.get(key, {})
        if prop.get("type") == "select":
            select_obj = prop.get("select")
            if select_obj:
                return select_obj.get("name")
        return None
    
    def _get_property_multi_select(self, props: Dict, key: str) -> List[str]:
        """Multi-selectプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") == "multi_select":
            multi_select_array = prop.get("multi_select", [])
            return [item.get("name", "") for item in multi_select_array]
        return []
    
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

