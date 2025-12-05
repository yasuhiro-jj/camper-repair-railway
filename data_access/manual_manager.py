#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作業マニュアル管理モジュール（フェーズ2-3）
作業マニュアルの検索、取得、管理を行う
"""

import os
import requests
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_MANUAL_DB_ID = os.getenv("NOTION_MANUAL_DB_ID")
NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2022-06-28")

NOTION_PAGES_URL = "https://api.notion.com/v1/pages"
NOTION_DATABASE_URL = "https://api.notion.com/v1/databases"


class ManualManager:
    """作業マニュアル管理クラス"""
    
    def __init__(self):
        if not NOTION_API_KEY:
            raise ValueError("NOTION_API_KEYが設定されていません")
        if not NOTION_MANUAL_DB_ID:
            logger.warning("⚠️ NOTION_MANUAL_DB_IDが設定されていません。マニュアル検索機能は使用できません。")
        
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }
        self.db_id = NOTION_MANUAL_DB_ID
    
    def search_manuals(
        self,
        query: str,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        作業マニュアルを検索
        
        Args:
            query: 検索クエリ
            category: カテゴリでフィルタリング
            difficulty: 難易度でフィルタリング
            limit: 最大取得件数
        
        Returns:
            マニュアルのリスト
        """
        if not self.db_id:
            logger.warning("⚠️ マニュアルDBが設定されていません")
            return []
        
        try:
            # 検索フィルターを構築
            query_filters = []
            
            # クエリ検索（マニュアルID、タイトル、作業手順で検索）
            if query:
                query_filters.append({
                    "or": [
                        {
                            "property": "マニュアルID",
                            "title": {
                                "contains": query
                            }
                        },
                        {
                            "property": "タイトル",
                            "rich_text": {
                                "contains": query
                            }
                        },
                        {
                            "property": "作業手順",
                            "rich_text": {
                                "contains": query
                            }
                        }
                    ]
                })
            
            # カテゴリフィルター
            if category:
                query_filters.append({
                    "property": "カテゴリ",
                    "select": {
                        "equals": category
                    }
                })
            
            # 難易度フィルター
            if difficulty:
                query_filters.append({
                    "property": "難易度",
                    "select": {
                        "equals": difficulty
                    }
                })
            
            # フィルターを結合（フィルターがない場合はNoneを送信）
            filter_obj = None
            if len(query_filters) > 1:
                filter_obj = {"and": query_filters}
            elif len(query_filters) == 1:
                filter_obj = query_filters[0]
            
            # Notion APIで検索
            request_body = {
                "page_size": limit
            }
            if filter_obj:
                request_body["filter"] = filter_obj
            
            response = requests.post(
                f"{NOTION_DATABASE_URL}/{self.db_id}/query",
                headers=self.headers,
                json=request_body,
                timeout=15
            )
            
            if not response.ok:
                error_text = response.text
                logger.error(f"❌ マニュアル検索エラー: {response.status_code}")
                logger.error(f"   エラー詳細: {error_text}")
                return []
            
            results = response.json().get("results", [])
            manuals = []
            
            for page in results:
                manual = self._parse_manual_page(page)
                if manual:
                    manuals.append(manual)
            
            return manuals
        
        except Exception as e:
            logger.error(f"❌ マニュアル検索エラー: {e}")
            return []
    
    def get_manual(self, manual_id: str) -> Optional[Dict[str, Any]]:
        """
        マニュアルIDでマニュアルを取得
        
        Args:
            manual_id: マニュアルID
        
        Returns:
            マニュアル情報
        """
        try:
            response = requests.get(
                f"{NOTION_PAGES_URL}/{manual_id}",
                headers=self.headers,
                timeout=15
            )
            
            if not response.ok:
                logger.error(f"❌ マニュアル取得エラー: {response.status_code}")
                return None
            
            page = response.json()
            return self._parse_manual_page(page)
        
        except Exception as e:
            logger.error(f"❌ マニュアル取得エラー: {e}")
            return None
    
    def _parse_manual_page(self, page: Dict) -> Optional[Dict[str, Any]]:
        """Notionページをパースしてマニュアルデータに変換"""
        try:
            props = page.get("properties", {})
            
            # マニュアルID（タイトル）
            manual_id = ""
            title_prop = None
            for prop_name, prop_data in props.items():
                if prop_data.get("type") == "title":
                    title_list = prop_data.get("title", [])
                    if title_list:
                        manual_id = title_list[0].get("text", {}).get("content", "")
                    title_prop = prop_data
                    break
            
            # 各種プロパティ取得
            title = self._get_rich_text(props.get("タイトル", {}))
            category = self._get_select(props.get("カテゴリ", {}))
            steps = self._get_rich_text(props.get("作業手順", {}))
            tools = self._get_multi_select(props.get("必要な工具", {}))
            difficulty = self._get_select(props.get("難易度", {}))
            estimated_time = self._get_number(props.get("推定時間", {}))
            safety_notes = self._get_rich_text(props.get("安全注意事項", {}))
            tags = self._get_multi_select(props.get("タグ", {}))
            
            return {
                "id": page.get("id"),
                "manual_id": manual_id,
                "title": title or manual_id,
                "category": category,
                "steps": steps,
                "tools": tools,
                "difficulty": difficulty,
                "estimated_time": estimated_time,
                "safety_notes": safety_notes,
                "tags": tags,
                "url": page.get("url", ""),
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time")
            }
        
        except Exception as e:
            logger.warning(f"⚠️ マニュアルパースエラー: {e}")
            return None
    
    def _get_rich_text(self, prop: Dict) -> str:
        """Rich Textプロパティから値を取得"""
        if not prop:
            return ""
        
        rich_text = prop.get("rich_text", [])
        if not rich_text:
            return ""
        
        return "".join(item.get("plain_text", "") for item in rich_text)
    
    def _get_select(self, prop: Dict) -> str:
        """Selectプロパティから値を取得"""
        if not prop:
            return ""
        
        select = prop.get("select")
        if not select:
            return ""
        
        return select.get("name", "")
    
    def _get_multi_select(self, prop: Dict) -> List[str]:
        """Multi-selectプロパティから値を取得"""
        if not prop:
            return []
        
        multi_select = prop.get("multi_select", [])
        return [item.get("name", "") for item in multi_select]
    
    def _get_number(self, prop: Dict) -> Optional[float]:
        """Numberプロパティから値を取得"""
        if not prop:
            return None
        
        return prop.get("number")


# グローバルインスタンス
manual_manager = None

def get_manual_manager() -> Optional[ManualManager]:
    """ManualManagerのインスタンスを取得"""
    global manual_manager
    if manual_manager is None:
        try:
            manual_manager = ManualManager()
        except ValueError:
            return None
    return manual_manager

