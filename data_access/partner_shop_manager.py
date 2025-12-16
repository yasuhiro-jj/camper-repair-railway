#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パートナー修理店管理モジュール（フェーズ4-2）
パートナー修理店のCRUD操作とID自動採番を実装
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from data_access.notion_client import notion_client
import requests


class PartnerShopManager:
    """パートナー修理店管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.notion = notion_client.client
        self.partner_db_id = self._get_database_id()
        
        if not self.partner_db_id:
            raise ValueError("NOTION_PARTNER_DB_IDが設定されていません")
    
    def _get_database_id(self) -> Optional[str]:
        """データベースIDを取得"""
        # #region agent log
        try:
            import sys as _sys
            _sys.stderr.write(
                "[AgentLog] PartnerShopManager._get_database_id env presence "
                f"NOTION_PARTNER_DB_ID={bool(os.getenv('NOTION_PARTNER_DB_ID'))}, "
                f"PARTNER_SHOP_DB_ID={bool(os.getenv('PARTNER_SHOP_DB_ID'))}, "
                f"PARTNER_DB_ID={bool(os.getenv('PARTNER_DB_ID'))}\n"
            )
            _sys.stderr.flush()
        except Exception:
            pass
        # #endregion

        db_id = (
            os.getenv("NOTION_PARTNER_DB_ID")
            or os.getenv("PARTNER_SHOP_DB_ID")
            or os.getenv("PARTNER_DB_ID")
        )
        if db_id:
            # ハイフンを削除して正規化
            return db_id.replace("-", "").lower()
        return None
    
    def _get_next_shop_id(self) -> str:
        """
        次の店舗IDを生成（SHOP-001形式）
        
        Returns:
            次の店舗ID（例: SHOP-001）
        """
        try:
            # 既存の店舗を取得して最大IDを探す
            response = self.notion.databases.query(
                database_id=self.partner_db_id,
                page_size=100
            )
            
            max_num = 0
            for page in response.get("results", []):
                props = page.get("properties", {})
                shop_id_prop = props.get("店舗ID", {})
                
                if shop_id_prop.get("type") == "title":
                    title_array = shop_id_prop.get("title", [])
                    if title_array:
                        shop_id = title_array[0].get("plain_text", "")
                        # SHOP-001形式から数値を抽出
                        if shop_id.startswith("SHOP-"):
                            try:
                                num = int(shop_id.split("-")[1])
                                max_num = max(max_num, num)
                            except (ValueError, IndexError):
                                pass
            
            # 次のIDを生成
            next_num = max_num + 1
            return f"SHOP-{next_num:03d}"
            
        except Exception as e:
            print(f"⚠️ ID自動採番エラー: {e}")
            # エラー時はタイムスタンプベースのIDを生成
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"SHOP-{timestamp}"
    
    def list_shops(
        self,
        status: Optional[str] = None,
        prefecture: Optional[str] = None,
        specialty: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        パートナー修理店一覧を取得
        
        Args:
            status: ステータスでフィルタ（アクティブ、休止中、退会）
            prefecture: 都道府県でフィルタ
            specialty: 専門分野でフィルタ
            limit: 取得件数
        
        Returns:
            パートナー修理店リスト
        """
        try:
            # #region agent log
            try:
                import sys as _sys
                _sys.stderr.write(
                    "[AgentLog] PartnerShopManager.list_shops called "
                    f"db_id={self.partner_db_id}, status={status}, prefecture={prefecture}, specialty={specialty}, limit={limit}\n"
                )
                _sys.stderr.flush()
            except Exception:
                pass
            # #endregion

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
                "database_id": self.partner_db_id,
                "page_size": limit,
                "sorts": [
                    {
                        "property": "修理回数",
                        "direction": "descending"
                    },
                    {
                        "property": "修理金額の合計",
                        "direction": "descending"
                    },
                    {
                        "property": "平均星評価",
                        "direction": "descending"
                    },
                    {
                        "property": "評価件数",
                        "direction": "descending"
                    }
                ]
            }
            
            if filters:
                query["filter"] = {"and": filters} if len(filters) > 1 else filters[0]

            # #region agent log
            try:
                import sys as _sys, json as _json
                _sys.stderr.write(f"[AgentLog] PartnerShopManager.query payload: {_json.dumps(query, ensure_ascii=False)}\n")
                _sys.stderr.flush()
            except Exception:
                pass
            # #endregion

            def _post_database_query(payload: Dict[str, Any]) -> Dict[str, Any]:
                url = f"https://api.notion.com/v1/databases/{self.partner_db_id}/query"
                headers = {
                    "Authorization": f"Bearer {notion_client.api_key}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json",
                }
                # Notion APIの /databases/{id}/query は body に database_id を含めない
                body = dict(payload or {})
                body.pop("database_id", None)
                # direction の正規化（desc/asc などを API 仕様に合わせる）
                sorts = body.get("sorts")
                if isinstance(sorts, list):
                    for s in sorts:
                        if isinstance(s, dict) and "direction" in s:
                            d = str(s.get("direction", "")).lower()
                            if d in ("desc", "descending"):
                                s["direction"] = "descending"
                            elif d in ("asc", "ascending"):
                                s["direction"] = "ascending"
                resp = requests.post(url, headers=headers, json=body, timeout=20)
                try:
                    resp.raise_for_status()
                except Exception as e:
                    # #region agent log
                    try:
                        import sys as _sys
                        _sys.stderr.write(f"[AgentLog] PartnerShopManager.http_error status={resp.status_code}\n")
                        _sys.stderr.write(f"[AgentLog] PartnerShopManager.http_error body={resp.text[:500]}\n")
                        _sys.stderr.flush()
                    except Exception:
                        pass
                    # #endregion
                    raise e
                return resp.json()

            # #region agent log
            # まずフィルタ無しで1件取れるか確認（DBアクセス/権限/IDの切り分け）
            try:
                import sys as _sys
                probe = _post_database_query({"page_size": 1})
                _sys.stderr.write(
                    f"[AgentLog] PartnerShopManager.probe(no-filter) results_count={len(probe.get('results', []))}\n"
                )
                _sys.stderr.flush()
            except Exception as e:
                import sys as _sys, traceback as _tb
                _sys.stderr.write(f"[AgentLog] PartnerShopManager.probe(no-filter) ERROR: {type(e).__name__}: {e}\n")
                _sys.stderr.write(f"[AgentLog] PartnerShopManager.probe(no-filter) Traceback: {_tb.format_exc()}\n")
                _sys.stderr.flush()
            # #endregion

            response = _post_database_query(query)

            # #region agent log
            try:
                import sys as _sys
                _sys.stderr.write(f"[AgentLog] PartnerShopManager.query results_count={len(response.get('results', []))}\n")
                _sys.stderr.flush()
            except Exception:
                pass
            # #endregion
            
            shops = []
            for page in response.get("results", []):
                shops.append(self._parse_shop_page(page))
            
            return shops
            
        except Exception as e:
            # #region agent log
            try:
                import sys as _sys, traceback as _tb
                _sys.stderr.write(f"[AgentLog] PartnerShopManager.list_shops ERROR: {type(e).__name__}: {e}\n")
                _sys.stderr.write(f"[AgentLog] PartnerShopManager.list_shops Traceback: {_tb.format_exc()}\n")
                _sys.stderr.flush()
            except Exception:
                pass
            # #endregion
            print(f"❌ パートナー修理店一覧取得エラー: {e}")
            return []
    
    def get_shop(self, shop_id: str) -> Optional[Dict[str, Any]]:
        """
        パートナー修理店詳細を取得
        
        Args:
            shop_id: 店舗ID（SHOP-001形式）またはNotion Page ID
        
        Returns:
            パートナー修理店情報（見つからない場合はNone）
        """
        try:
            # まずpage_idで直接取得を試みる
            if len(shop_id) == 32:  # Notion Page IDは32文字
                try:
                    page = self.notion.pages.retrieve(shop_id)
                    if page.get("parent", {}).get("database_id") == self.partner_db_id:
                        return self._parse_shop_page(page)
                except Exception:
                    pass
            
            # 店舗IDで検索
            response = self.notion.databases.query(
                database_id=self.partner_db_id,
                filter={
                    "property": "店舗ID",
                    "title": {"equals": shop_id}
                }
            )
            
            if response.get("results"):
                return self._parse_shop_page(response["results"][0])
            
            return None
            
        except Exception as e:
            print(f"❌ パートナー修理店取得エラー: {e}")
            return None
    
    def get_shop_by_page_id(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Page IDでパートナー修理店詳細を取得
        
        Args:
            page_id: Notion Page ID
        
        Returns:
            パートナー修理店情報（見つからない場合はNone）
        """
        try:
            page = self.notion.pages.retrieve(page_id)
            return self._parse_shop_page(page)
        except Exception as e:
            print(f"❌ パートナー修理店取得エラー（Page ID: {page_id}）: {e}")
            return None
    
    def create_shop(
        self,
        name: str,
        phone: str,
        email: str,
        prefecture: str,
        address: str,
        specialties: List[str],
        business_hours: str,
        initial_diagnosis_fee: float = 3000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        パートナー修理店を登録
        
        Args:
            name: 店舗名
            phone: 電話番号
            email: メールアドレス
            prefecture: 都道府県
            address: 住所
            specialties: 専門分野リスト
            business_hours: 営業時間
            initial_diagnosis_fee: 初診断料
            **kwargs: その他のフィールド
        
        Returns:
            作成されたパートナー修理店情報
        """
        try:
            # ID自動採番
            shop_id = self._get_next_shop_id()
            
            # プロパティを構築
            properties = {
                "店舗ID": {
                    "title": [{"text": {"content": shop_id}}]
                },
                "店舗名": {
                    "rich_text": [{"text": {"content": name}}]
                },
                "電話番号": {
                    "phone_number": phone
                },
                "メールアドレス": {
                    "email": email
                },
                "所在地（都道府県）": {
                    "select": {"name": prefecture}
                },
                "住所": {
                    "rich_text": [{"text": {"content": address}}]
                },
                "専門分野": {
                    "multi_select": [{"name": s} for s in specialties]
                },
                "営業時間": {
                    "rich_text": [{"text": {"content": business_hours}}]
                },
                "初診断料": {
                    "number": initial_diagnosis_fee
                },
                "成約率": {
                    "number": kwargs.get("success_rate", 0)
                },
                "総紹介数": {
                    "number": kwargs.get("total_referrals", 0)
                },
                "成約数": {
                    "number": kwargs.get("total_deals", 0)
                },
                "ステータス": {
                    "select": {"name": kwargs.get("status", "アクティブ")}
                },
                "LINE通知": {
                    "checkbox": kwargs.get("line_notification", False)
                },
                "登録日": {
                    "date": {"start": datetime.now().isoformat()}
                }
            }
            
            # LINE Webhook URLがあれば追加
            if kwargs.get("line_webhook_url"):
                properties["LINE Webhook URL"] = {
                    "url": kwargs["line_webhook_url"]
                }
            
            # 備考があれば追加
            if kwargs.get("notes"):
                properties["備考"] = {
                    "rich_text": [{"text": {"content": kwargs["notes"]}}]
                }
            
            # Notionにページ作成
            new_page = self.notion.pages.create(
                parent={"database_id": self.partner_db_id},
                properties=properties
            )
            
            return self._parse_shop_page(new_page)
            
        except Exception as e:
            print(f"❌ パートナー修理店登録エラー: {e}")
            raise
    
    def update_shop(
        self,
        shop_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        パートナー修理店情報を更新
        
        Args:
            shop_id: 店舗ID（SHOP-001形式）またはNotion Page ID
            **kwargs: 更新するフィールド
        
        Returns:
            更新されたパートナー修理店情報
        """
        try:
            # 店舗を取得
            shop = self.get_shop(shop_id)
            if not shop:
                return None
            
            page_id = shop["page_id"]
            
            # 更新プロパティを構築
            properties = {}
            
            if "name" in kwargs:
                properties["店舗名"] = {
                    "rich_text": [{"text": {"content": kwargs["name"]}}]
                }
            if "phone" in kwargs:
                properties["電話番号"] = {
                    "phone_number": kwargs["phone"]
                }
            if "email" in kwargs:
                properties["メールアドレス"] = {
                    "email": kwargs["email"]
                }
            if "prefecture" in kwargs:
                properties["所在地（都道府県）"] = {
                    "select": {"name": kwargs["prefecture"]}
                }
            if "address" in kwargs:
                properties["住所"] = {
                    "rich_text": [{"text": {"content": kwargs["address"]}}]
                }
            if "specialties" in kwargs:
                properties["専門分野"] = {
                    "multi_select": [{"name": s} for s in kwargs["specialties"]]
                }
            if "business_hours" in kwargs:
                properties["営業時間"] = {
                    "rich_text": [{"text": {"content": kwargs["business_hours"]}}]
                }
            if "initial_diagnosis_fee" in kwargs:
                properties["初診断料"] = {
                    "number": kwargs["initial_diagnosis_fee"]
                }
            if "success_rate" in kwargs:
                properties["成約率"] = {
                    "number": kwargs["success_rate"]
                }
            if "total_referrals" in kwargs:
                properties["総紹介数"] = {
                    "number": kwargs["total_referrals"]
                }
            if "total_deals" in kwargs:
                properties["成約数"] = {
                    "number": kwargs["total_deals"]
                }
            if "status" in kwargs:
                properties["ステータス"] = {
                    "select": {"name": kwargs["status"]}
                }
            if "line_notification" in kwargs:
                properties["LINE通知"] = {
                    "checkbox": kwargs["line_notification"]
                }
            if "line_webhook_url" in kwargs:
                properties["LINE Webhook URL"] = {
                    "url": kwargs["line_webhook_url"]
                }
            if "notes" in kwargs:
                properties["備考"] = {
                    "rich_text": [{"text": {"content": kwargs["notes"]}}]
                }
            
            if not properties:
                return shop
            
            # Notionでページ更新
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            return self._parse_shop_page(updated_page)
            
        except Exception as e:
            print(f"❌ パートナー修理店更新エラー: {e}")
            raise
    
    def _parse_shop_page(self, page: Dict) -> Dict[str, Any]:
        """Notionページをパートナー修理店情報にパース"""
        props = page.get("properties", {})
        
        return {
            "page_id": page["id"],
            "shop_id": self._get_property_title(props, "店舗ID"),
            "name": self._get_property_text(props, "店舗名"),
            "phone": self._get_property_phone(props, "電話番号"),
            "email": self._get_property_email(props, "メールアドレス"),
            "prefecture": self._get_property_select(props, "所在地（都道府県）"),
            "address": self._get_property_text(props, "住所"),
            "specialties": self._get_property_multi_select(props, "専門分野"),
            "business_hours": self._get_property_text(props, "営業時間"),
            "initial_diagnosis_fee": self._get_property_number(props, "初診断料"),
            "success_rate": self._get_property_number(props, "成約率"),
            "total_referrals": self._get_property_number(props, "総紹介数"),
            "total_deals": self._get_property_number(props, "成約数"),
            "status": self._get_property_select(props, "ステータス"),
            "line_notification": self._get_property_checkbox(props, "LINE通知"),
            "line_webhook_url": self._get_property_url(props, "LINE Webhook URL"),
            "line_bot_id": self._get_property_text(props, "LINE Bot ID"),
            "line_user_id": self._get_property_text(props, "LINEユーザーID"),
            "registered_date": self._get_property_date(props, "登録日"),
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
    
    def _get_property_checkbox(self, props: Dict, key: str) -> bool:
        """Checkboxプロパティを取得"""
        prop = props.get(key, {})
        if prop.get("type") == "checkbox":
            return prop.get("checkbox", False)
        return False
    
    def update_shop_ratings(
        self,
        page_id: str,
        avg_rating: float,
        review_count: int,
        latest_review_date: Optional[str] = None
    ) -> bool:
        """
        パートナー工場の評価情報を更新
        
        Args:
            page_id: パートナー工場のNotion Page ID
            avg_rating: 平均星評価（1.0〜5.0）
            review_count: 評価件数
            latest_review_date: 最新の評価日時（ISO形式）
        
        Returns:
            更新成功かどうか
        """
        try:
            properties = {
                "平均星評価": {
                    "number": round(avg_rating, 1)
                },
                "評価件数": {
                    "number": review_count
                }
            }
            
            if latest_review_date:
                properties["最新の評価日時"] = {
                    "date": {"start": latest_review_date}
                }
            
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            return True
        
        except Exception as e:
            print(f"❌ パートナー工場評価情報更新エラー: {e}")
            return False
    
    def update_shop_statistics(
        self,
        page_id: str
    ) -> bool:
        """
        パートナー工場の統計情報を更新（修理回数、修理金額の合計）
        
        Args:
            page_id: パートナー工場のNotion Page ID
        
        Returns:
            更新成功かどうか
        """
        try:
            from data_access.deal_manager import DealManager
            
            deal_manager = DealManager()
            
            # この工場に関連する完了した商談を取得
            completed_deals = deal_manager.get_deals_by_partner(
                partner_page_id=page_id,
                status="completed"
            )
            
            # 修理回数（完了した商談数）
            repair_count = len(completed_deals)
            
            # 修理金額の合計
            total_amount = sum(
                deal.get("deal_amount", 0) or 0
                for deal in completed_deals
            )
            
            # プロパティを更新
            properties = {
                "修理回数": {
                    "number": repair_count
                },
                "修理金額の合計": {
                    "number": total_amount
                }
            }
            
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            print(f"✅ パートナー工場統計情報を更新しました: {page_id} (修理回数: {repair_count}, 合計金額: {total_amount:,}円)")
            return True
        
        except Exception as e:
            print(f"❌ パートナー工場統計情報更新エラー: {e}")
            import traceback
            traceback.print_exc()
            return False

