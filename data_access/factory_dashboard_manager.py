#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工場向けダッシュボード用 Notion管理モジュール（Phase 4）
案件一覧の取得、ステータス更新、コメント追加を実装
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
NOTION_LOG_DB_ID = os.getenv("NOTION_LOG_DB_ID") or os.getenv("NOTION_DB_CHAT_LOGS")
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

NOTION_LOG_DB_ID = _sanitize_db_id(NOTION_LOG_DB_ID)

NOTION_PAGES_URL = "https://api.notion.com/v1/pages"
NOTION_DATABASE_URL = "https://api.notion.com/v1/databases"

# ステータス定義（Phase 4対応）
STATUS_OPTIONS = ["受付", "診断中", "修理中", "完了", "キャンセル"]


class FactoryDashboardManager:
    """工場向けダッシュボード管理クラス（Phase 4）"""
    
    def __init__(self):
        if not NOTION_API_KEY or not NOTION_LOG_DB_ID:
            raise ValueError("Notion環境変数が設定されていません")
        
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }
        self.db_id = NOTION_LOG_DB_ID
    
    def get_cases(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        sort_by: str = "timestamp",
        sort_direction: str = "descending"
    ) -> List[Dict[str, Any]]:
        """
        Notionから案件一覧を取得
        
        Args:
            status: フィルタするステータス（Noneの場合は全件）
            limit: 取得件数
            sort_by: ソート項目（timestamp, category等）
            sort_direction: ソート方向（ascending/descending）
        
        Returns:
            案件リスト
        """
        try:
            query = {
                "database_id": self.db_id,
                "page_size": limit,
            }
            
            # フィルタ追加（ステータスがある場合）
            if status:
                query["filter"] = {
                    "property": "status",
                    "select": {"equals": status}
                }
            
            # ソート設定
            query["sorts"] = [{
                "property": sort_by if sort_by in ["timestamp", "category"] else "timestamp",
                "direction": sort_direction
            }]
            
            response = requests.post(
                f"{NOTION_DATABASE_URL}/{self.db_id}/query",
                headers=self.headers,
                json=query,
                timeout=15
            )
            
            if not response.ok:
                logger.error(f"Notion案件取得エラー: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            cases = []
            
            for page in data.get("results", []):
                case = self._parse_page(page)
                if case:
                    cases.append(case)
            
            logger.info(f"✅ 案件取得成功: {len(cases)}件")
            return cases
        
        except Exception as e:
            logger.error(f"❌ 案件取得エラー: {e}")
            return []
    
    def _parse_page(self, page: Dict) -> Optional[Dict[str, Any]]:
        """Notionページをパースして案件データに変換"""
        try:
            props = page.get("properties", {})
            
            # タイトル取得
            title = ""
            for prop_name, prop_data in props.items():
                if prop_data.get("type") == "title":
                    title_list = prop_data.get("title", [])
                    if title_list:
                        title = title_list[0].get("text", {}).get("content", "")
                    break
            
            # 各種プロパティ取得
            user_message = self._get_rich_text(props.get("user_message", {}))
            bot_message = self._get_rich_text(props.get("bot_message", {}))
            session_id = self._get_rich_text(props.get("session_id", {}))
            category = self._get_select(props.get("category", {}))
            status = self._get_select(props.get("status", {}))
            timestamp = self._get_date(props.get("timestamp", {}))
            comment = self._get_rich_text(props.get("comment", {}))
            image_url = self._get_url(props.get("image_url", {}))
            
            return {
                "page_id": page.get("id"),
                "title": title or session_id or "未設定",
                "user_message": user_message,
                "bot_message": bot_message,
                "session_id": session_id,
                "category": category,
                "status": status or "受付",  # デフォルトは「受付」
                "timestamp": timestamp,
                "comment": comment,
                "image_url": image_url,
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time"),
            }
        except Exception as e:
            logger.warning(f"⚠️ ページパースエラー: {e}")
            return None
    
    def _get_rich_text(self, prop: Dict) -> str:
        """Rich Textプロパティから値を取得"""
        if not prop or prop.get("type") != "rich_text":
            return ""
        rich_text = prop.get("rich_text", [])
        if rich_text:
            return rich_text[0].get("text", {}).get("content", "")
        return ""
    
    def _get_select(self, prop: Dict) -> Optional[str]:
        """Selectプロパティから値を取得"""
        if not prop or prop.get("type") != "select":
            return None
        select_data = prop.get("select")
        if select_data:
            return select_data.get("name")
        return None
    
    def _get_date(self, prop: Dict) -> Optional[str]:
        """Dateプロパティから値を取得"""
        if not prop:
            return None
        if prop.get("type") == "date":
            date_data = prop.get("date")
            if date_data:
                return date_data.get("start")
        elif prop.get("type") == "rich_text":
            # rich_textの場合も試行
            return self._get_rich_text(prop)
        return None
    
    def _get_url(self, prop: Dict) -> Optional[str]:
        """URLプロパティから値を取得"""
        if not prop or prop.get("type") != "url":
            return None
        return prop.get("url")
    
    def update_status(self, page_id: str, status: str) -> bool:
        """
        案件のステータスを更新
        
        Args:
            page_id: NotionページID
            status: 新しいステータス（受付/診断中/修理中/完了/キャンセル）
        
        Returns:
            成功時True
        """
        if status not in STATUS_OPTIONS:
            logger.warning(f"⚠️ 無効なステータス: {status}")
            return False
        
        try:
            # statusプロパティが存在するか確認
            # 存在しない場合はコメントに追記する方式にフォールバック
            properties = {
                "status": {
                    "select": {"name": status}
                }
            }
            
            response = requests.patch(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                json={"properties": properties},
                timeout=15
            )
            
            if response.ok:
                logger.info(f"✅ ステータス更新成功: {page_id} -> {status}")
                return True
            else:
                # statusプロパティが存在しない場合、コメントに追記
                logger.warning(f"⚠️ ステータス更新失敗（フォールバック）: {response.status_code}")
                return self._update_status_via_comment(page_id, status)
        
        except Exception as e:
            logger.error(f"❌ ステータス更新エラー: {e}")
            return False
    
    def _update_status_via_comment(self, page_id: str, status: str) -> bool:
        """ステータスプロパティがない場合、コメントに追記"""
        try:
            # 既存のコメントを取得
            page = requests.get(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                timeout=15
            ).json()
            
            props = page.get("properties", {})
            existing_comment = self._get_rich_text(props.get("comment", {}))
            
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            new_comment = f"{existing_comment}\n\n[{timestamp}] ステータス: {status}" if existing_comment else f"[{timestamp}] ステータス: {status}"
            
            properties = {
                "comment": {
                    "rich_text": [{"text": {"content": new_comment}}]
                }
            }
            
            response = requests.patch(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                json={"properties": properties},
                timeout=15
            )
            
            return response.ok
        except Exception as e:
            logger.error(f"❌ コメント経由ステータス更新エラー: {e}")
            return False
    
    def add_comment(self, page_id: str, comment: str) -> bool:
        """
        案件にコメントを追加
        
        Args:
            page_id: NotionページID
            comment: 追加するコメント
        
        Returns:
            成功時True
        """
        try:
            # 既存のコメントを取得
            page = requests.get(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                timeout=15
            ).json()
            
            props = page.get("properties", {})
            existing_comment = self._get_rich_text(props.get("comment", {}))
            
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            new_comment = f"{existing_comment}\n\n[{timestamp}] {comment}" if existing_comment else f"[{timestamp}] {comment}"
            
            properties = {
                "comment": {
                    "rich_text": [{"text": {"content": new_comment}}]
                }
            }
            
            response = requests.patch(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                json={"properties": properties},
                timeout=15
            )
            
            if response.ok:
                logger.info(f"✅ コメント追加成功: {page_id}")
                return True
            else:
                logger.error(f"❌ コメント追加失敗: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"❌ コメント追加エラー: {e}")
            return False
    
    def update_image_url(self, page_id: str, image_url: str) -> bool:
        """
        案件に画像URLを追加
        
        Args:
            page_id: NotionページID
            image_url: 画像URL
        
        Returns:
            成功時True
        """
        try:
            properties = {
                "image_url": {
                    "url": image_url
                }
            }
            
            response = requests.patch(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                json={"properties": properties},
                timeout=15
            )
            
            if response.ok:
                logger.info(f"✅ 画像URL更新成功: {page_id}")
                return True
            else:
                logger.warning(f"⚠️ 画像URL更新失敗（プロパティが存在しない可能性）: {response.status_code}")
                # プロパティが存在しない場合、コメントに追記
                return self.add_comment(page_id, f"画像URL: {image_url}")
        
        except Exception as e:
            logger.error(f"❌ 画像URL更新エラー: {e}")
            return False

