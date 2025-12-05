#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
評価管理モジュール
お客様からの評価（星評価・コメント）を管理
"""

import os
import requests
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_REVIEW_DB_ID = os.getenv("NOTION_REVIEW_DB_ID")
NOTION_DEAL_DB_ID = os.getenv("NOTION_DEAL_DB_ID") or os.getenv("DEAL_DB_ID")
NOTION_PARTNER_DB_ID = os.getenv("NOTION_PARTNER_DB_ID") or os.getenv("PARTNER_SHOP_DB_ID")
NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2022-06-28")

# データベースIDをサニタイズ
def _sanitize_db_id(db_id: str | None) -> str | None:
    if not db_id:
        return None
    try:
        import re
        cleaned = re.sub(r"[^0-9a-fA-F]", "", db_id).lower()
        return cleaned
    except Exception:
        return db_id.replace("-", "") if db_id else None

NOTION_REVIEW_DB_ID = _sanitize_db_id(NOTION_REVIEW_DB_ID)
NOTION_DEAL_DB_ID = _sanitize_db_id(NOTION_DEAL_DB_ID)
NOTION_PARTNER_DB_ID = _sanitize_db_id(NOTION_PARTNER_DB_ID)

NOTION_PAGES_URL = "https://api.notion.com/v1/pages"
NOTION_DATABASE_URL = "https://api.notion.com/v1/databases"


class ReviewManager:
    """評価管理クラス"""
    
    def __init__(self):
        if not NOTION_API_KEY:
            raise ValueError("NOTION_API_KEYが設定されていません")
        
        if not NOTION_REVIEW_DB_ID:
            logger.warning("⚠️ NOTION_REVIEW_DB_IDが設定されていません。評価機能は使用できません。")
        
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }
        self.review_db_id = NOTION_REVIEW_DB_ID
        self.deal_db_id = NOTION_DEAL_DB_ID
        self.partner_db_id = NOTION_PARTNER_DB_ID
    
    def create_review(
        self,
        deal_id: str,
        partner_page_id: str,
        customer_name: str,
        star_rating: int,
        comment: str,
        anonymous: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        評価を作成
        
        Args:
            deal_id: 商談ID
            partner_page_id: パートナー工場のNotion Page ID
            customer_name: お客様名
            star_rating: 星評価（1〜5）
            comment: コメント
            anonymous: 匿名希望かどうか
        
        Returns:
            作成された評価データ
        """
        if not self.review_db_id:
            logger.error("❌ 評価DBが設定されていません")
            return None
        
        if not (1 <= star_rating <= 5):
            logger.error(f"❌ 無効な星評価: {star_rating}（1〜5の範囲で指定してください）")
            return None
        
        try:
            # 評価IDを生成
            review_id = self._get_next_review_id()
            
            # お客様名（匿名化）
            display_name = "匿名希望" if anonymous else customer_name
            
            # 商談ページを取得（リレーション用）
            deal_page_id = self._get_deal_page_id(deal_id)
            if not deal_page_id:
                logger.warning(f"⚠️ 商談が見つかりません: {deal_id}")
            
            # プロパティを構築
            properties = {
                "評価ID": {
                    "title": [{"text": {"content": review_id}}]
                },
                "星評価": {
                    "number": star_rating
                },
                "コメント": {
                    "rich_text": [{"text": {"content": comment}}]
                },
                "お客様名": {
                    "rich_text": [{"text": {"content": display_name}}]
                },
                "評価日時": {
                    "date": {"start": datetime.now(timezone.utc).isoformat()}
                },
                "承認ステータス": {
                    "select": {"name": "pending"}  # デフォルトは承認待ち
                }
            }
            
            # 商談とのリレーション
            if deal_page_id:
                properties["商談ID"] = {
                    "relation": [{"id": deal_page_id}]
                }
            
            # パートナー工場とのリレーション
            if partner_page_id:
                properties["パートナー工場ID"] = {
                    "relation": [{"id": partner_page_id}]
                }
            
            # ページを作成
            page_data = {
                "parent": {"database_id": self.review_db_id},
                "properties": properties
            }
            
            response = requests.post(
                NOTION_PAGES_URL,
                headers=self.headers,
                json=page_data,
                timeout=15
            )
            
            if not response.ok:
                logger.error(f"❌ 評価作成エラー: {response.status_code} - {response.text}")
                return None
            
            created_page = response.json()
            review_data = self._parse_review_page(created_page)
            
            logger.info(f"✅ 評価を作成しました: {review_id} (星評価: {star_rating})")
            
            # パートナー工場の評価情報を更新
            self._update_partner_shop_ratings(partner_page_id)
            
            return review_data
        
        except Exception as e:
            logger.error(f"❌ 評価作成エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_reviews(
        self,
        partner_page_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        評価一覧を取得
        
        Args:
            partner_page_id: パートナー工場のNotion Page ID（フィルタ用）
            status: 承認ステータス（pending / approved / rejected）
            limit: 取得件数
        
        Returns:
            評価リスト
        """
        if not self.review_db_id:
            logger.warning("⚠️ 評価DBが設定されていません")
            return []
        
        try:
            filters = []
            
            # パートナー工場でフィルタ
            if partner_page_id:
                filters.append({
                    "property": "パートナー工場ID",
                    "relation": {"contains": partner_page_id}
                })
            
            # 承認ステータスでフィルタ
            if status:
                filters.append({
                    "property": "承認ステータス",
                    "select": {"equals": status}
                })
            
            query = {
                "database_id": self.review_db_id,
                "page_size": limit,
                "sorts": [{
                    "property": "評価日時",
                    "direction": "descending"
                }]
            }
            
            if filters:
                if len(filters) > 1:
                    query["filter"] = {"and": filters}
                else:
                    query["filter"] = filters[0]
            
            response = requests.post(
                f"{NOTION_DATABASE_URL}/{self.review_db_id}/query",
                headers=self.headers,
                json=query,
                timeout=15
            )
            
            if not response.ok:
                logger.error(f"❌ 評価取得エラー: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            reviews = []
            
            for page in data.get("results", []):
                review = self._parse_review_page(page)
                if review:
                    reviews.append(review)
            
            return reviews
        
        except Exception as e:
            logger.error(f"❌ 評価取得エラー: {e}")
            return []
    
    def update_review_status(
        self,
        review_id: str,
        status: str,
        admin_comment: Optional[str] = None
    ) -> bool:
        """
        評価の承認ステータスを更新
        
        Args:
            review_id: 評価ID
            status: 新しいステータス（approved / rejected）
            admin_comment: 運営側のコメント（削除理由など）
        
        Returns:
            更新成功かどうか
        """
        if not self.review_db_id:
            return False
        
        if status not in ["approved", "rejected"]:
            logger.error(f"❌ 無効なステータス: {status}")
            return False
        
        try:
            # 評価ページを取得
            review_page_id = self._get_review_page_id(review_id)
            if not review_page_id:
                logger.error(f"❌ 評価が見つかりません: {review_id}")
                return False
            
            # パートナー工場IDを取得（更新用）
            review_data = self.get_review_by_id(review_id)
            partner_page_id = review_data.get("partner_page_id") if review_data else None
            
            # プロパティを更新
            properties = {
                "承認ステータス": {
                    "select": {"name": status}
                }
            }
            
            if admin_comment:
                properties["運営側のコメント"] = {
                    "rich_text": [{"text": {"content": admin_comment}}]
                }
            
            response = requests.patch(
                f"{NOTION_PAGES_URL}/{review_page_id}",
                headers=self.headers,
                json={"properties": properties},
                timeout=15
            )
            
            if not response.ok:
                logger.error(f"❌ 評価ステータス更新エラー: {response.status_code} - {response.text}")
                return False
            
            logger.info(f"✅ 評価ステータスを更新しました: {review_id} -> {status}")
            
            # パートナー工場の評価情報を更新
            if partner_page_id and status == "approved":
                self._update_partner_shop_ratings(partner_page_id)
            
            return True
        
        except Exception as e:
            logger.error(f"❌ 評価ステータス更新エラー: {e}")
            return False
    
    def get_review_by_id(self, review_id: str) -> Optional[Dict[str, Any]]:
        """評価IDで評価を取得"""
        reviews = self.get_reviews(limit=1000)
        for review in reviews:
            if review.get("review_id") == review_id:
                return review
        return None
    
    def _get_next_review_id(self) -> str:
        """次の評価IDを生成（REVIEW-YYYYMMDD-XXX形式）"""
        try:
            if not self.review_db_id:
                timestamp = datetime.now().strftime("%Y%m%d")
                return f"REVIEW-{timestamp}-001"
            
            # 既存の評価を取得して最大IDを探す
            response = requests.post(
                f"{NOTION_DATABASE_URL}/{self.review_db_id}/query",
                headers=self.headers,
                json={"page_size": 100},
                timeout=15
            )
            
            if not response.ok:
                timestamp = datetime.now().strftime("%Y%m%d")
                return f"REVIEW-{timestamp}-001"
            
            data = response.json()
            today = datetime.now().strftime("%Y%m%d")
            max_num = 0
            
            for page in data.get("results", []):
                props = page.get("properties", {})
                review_id_prop = props.get("評価ID", {})
                
                if review_id_prop.get("type") == "title":
                    title_array = review_id_prop.get("title", [])
                    if title_array:
                        review_id = title_array[0].get("plain_text", "")
                        # REVIEW-YYYYMMDD-XXX形式から数値を抽出
                        if review_id.startswith(f"REVIEW-{today}-"):
                            try:
                                num = int(review_id.split("-")[2])
                                max_num = max(max_num, num)
                            except (ValueError, IndexError):
                                pass
            
            # 次のIDを生成
            next_num = max_num + 1
            return f"REVIEW-{today}-{next_num:03d}"
        
        except Exception as e:
            logger.warning(f"⚠️ 評価ID生成エラー: {e}")
            timestamp = datetime.now().strftime("%Y%m%d")
            return f"REVIEW-{timestamp}-001"
    
    def _get_deal_page_id(self, deal_id: str) -> Optional[str]:
        """商談IDからNotion Page IDを取得"""
        if not self.deal_db_id:
            return None
        
        try:
            response = requests.post(
                f"{NOTION_DATABASE_URL}/{self.deal_db_id}/query",
                headers=self.headers,
                json={
                    "filter": {
                        "property": "商談ID",
                        "title": {"equals": deal_id}
                    },
                    "page_size": 1
                },
                timeout=15
            )
            
            if response.ok:
                data = response.json()
                results = data.get("results", [])
                if results:
                    return results[0].get("id")
            
            return None
        
        except Exception as e:
            logger.warning(f"⚠️ 商談ページID取得エラー: {e}")
            return None
    
    def _get_review_page_id(self, review_id: str) -> Optional[str]:
        """評価IDからNotion Page IDを取得"""
        if not self.review_db_id:
            return None
        
        try:
            response = requests.post(
                f"{NOTION_DATABASE_URL}/{self.review_db_id}/query",
                headers=self.headers,
                json={
                    "filter": {
                        "property": "評価ID",
                        "title": {"equals": review_id}
                    },
                    "page_size": 1
                },
                timeout=15
            )
            
            if response.ok:
                data = response.json()
                results = data.get("results", [])
                if results:
                    return results[0].get("id")
            
            return None
        
        except Exception as e:
            logger.warning(f"⚠️ 評価ページID取得エラー: {e}")
            return None
    
    def _parse_review_page(self, page: Dict) -> Optional[Dict[str, Any]]:
        """Notionページをパースして評価データに変換"""
        try:
            props = page.get("properties", {})
            
            # 評価ID
            review_id = ""
            review_id_prop = props.get("評価ID", {})
            if review_id_prop.get("type") == "title":
                title_array = review_id_prop.get("title", [])
                if title_array:
                    review_id = title_array[0].get("plain_text", "")
            
            # 星評価
            star_rating = props.get("星評価", {}).get("number", 0)
            
            # コメント
            comment = self._get_rich_text(props.get("コメント", {}))
            
            # お客様名
            customer_name = self._get_rich_text(props.get("お客様名", {}))
            
            # 評価日時
            review_date = None
            date_prop = props.get("評価日時", {})
            if date_prop.get("type") == "date":
                date_value = date_prop.get("date")
                if date_value:
                    review_date = date_value.get("start")
            
            # 承認ステータス
            status = props.get("承認ステータス", {}).get("select", {}).get("name", "pending")
            
            # 運営側のコメント
            admin_comment = self._get_rich_text(props.get("運営側のコメント", {}))
            
            # パートナー工場ID
            partner_page_ids = []
            partner_relation = props.get("パートナー工場ID", {})
            if partner_relation.get("type") == "relation":
                partner_page_ids = [rel.get("id") for rel in partner_relation.get("relation", [])]
            
            # 商談ID
            deal_page_ids = []
            deal_relation = props.get("商談ID", {})
            if deal_relation.get("type") == "relation":
                deal_page_ids = [rel.get("id") for rel in deal_relation.get("relation", [])]
            
            return {
                "review_id": review_id,
                "page_id": page.get("id"),
                "star_rating": star_rating,
                "comment": comment,
                "customer_name": customer_name,
                "review_date": review_date,
                "status": status,
                "admin_comment": admin_comment,
                "partner_page_id": partner_page_ids[0] if partner_page_ids else None,
                "deal_page_id": deal_page_ids[0] if deal_page_ids else None,
            }
        
        except Exception as e:
            logger.error(f"❌ 評価ページパースエラー: {e}")
            return None
    
    def _get_rich_text(self, prop: Dict) -> str:
        """Rich Textプロパティからテキストを取得"""
        if prop.get("type") == "rich_text":
            rich_text_array = prop.get("rich_text", [])
            if rich_text_array:
                return rich_text_array[0].get("plain_text", "")
        return ""
    
    def _update_partner_shop_ratings(self, partner_page_id: str):
        """
        パートナー工場の評価情報を更新（平均星評価、評価件数）
        
        Args:
            partner_page_id: パートナー工場のNotion Page ID
        """
        try:
            from data_access.partner_shop_manager import PartnerShopManager
            
            # 承認済みの評価のみを取得
            approved_reviews = self.get_reviews(
                partner_page_id=partner_page_id,
                status="approved",
                limit=1000
            )
            
            if not approved_reviews:
                return
            
            # 平均星評価を計算
            total_rating = sum(r.get("star_rating", 0) for r in approved_reviews)
            avg_rating = total_rating / len(approved_reviews) if approved_reviews else 0
            
            # 評価件数
            review_count = len(approved_reviews)
            
            # 最新の評価日時
            latest_review_date = None
            if approved_reviews:
                latest_review = max(approved_reviews, key=lambda x: x.get("review_date", "") or "")
                latest_review_date = latest_review.get("review_date")
            
            # パートナー工場の情報を更新
            partner_manager = PartnerShopManager()
            partner_manager.update_shop_ratings(
                page_id=partner_page_id,
                avg_rating=avg_rating,
                review_count=review_count,
                latest_review_date=latest_review_date
            )
            
            logger.info(f"✅ パートナー工場の評価情報を更新しました: {partner_page_id} (平均: {avg_rating:.1f}, 件数: {review_count})")
        
        except Exception as e:
            logger.error(f"❌ パートナー工場評価情報更新エラー: {e}")
            import traceback
            traceback.print_exc()


def get_review_manager() -> Optional[ReviewManager]:
    """ReviewManagerのインスタンスを取得"""
    try:
        return ReviewManager()
    except Exception as e:
        logger.warning(f"⚠️ ReviewManagerの初期化に失敗: {e}")
        return None



