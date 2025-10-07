#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最適化されたNotionデータベース統合モジュール
パフォーマンス向上とキャッシュ機能を実装
"""

import os
import hashlib
from functools import lru_cache
from typing import Dict, List, Any, Optional
import streamlit as st
from notion_client import Client

class OptimizedNotionClient:
    """最適化されたNotionクライアント"""
    
    def __init__(self):
        self.client = None
        self.cache = {}
        self._initialize_client()
    
    def _initialize_client(self):
        """Notionクライアントを初期化"""
        try:
            api_key = (
                st.secrets.get("NOTION_API_KEY") or 
                st.secrets.get("NOTION_TOKEN") or 
                os.getenv("NOTION_API_KEY") or 
                os.getenv("NOTION_TOKEN")
            )
            
            if not api_key:
                return None
            
            self.client = Client(auth=api_key)
            
            # 接続テスト
            user = self.client.users.me()
            return True
            
        except Exception as e:
            print(f"Notion client initialization failed: {e}")
            return None
    
    @lru_cache(maxsize=100)
    def search_diagnostic_nodes(self, query: str = "") -> List[Dict]:
        """診断ノードを検索（キャッシュ付き）"""
        if not self.client:
            return []
        
        try:
            node_db_id = (
                st.secrets.get("NODE_DB_ID") or 
                st.secrets.get("NOTION_DIAGNOSTIC_DB_ID") or 
                os.getenv("NODE_DB_ID") or 
                os.getenv("NOTION_DIAGNOSTIC_DB_ID")
            )
            
            if not node_db_id:
                return []
            
            # クエリに基づくフィルタリング
            filter_conditions = {}
            if query:
                filter_conditions = {
                    "property": "名前",
                    "title": {
                        "contains": query
                    }
                }
            
            response = self.client.databases.query(
                database_id=node_db_id,
                filter=filter_conditions if filter_conditions else None
            )
            
            nodes = response.get("results", [])
            return self._process_diagnostic_nodes(nodes)
            
        except Exception as e:
            print(f"Error searching diagnostic nodes: {e}")
            return []
    
    @lru_cache(maxsize=100)
    def search_repair_cases(self, category: str = "") -> List[Dict]:
        """修理ケースを検索（キャッシュ付き）"""
        if not self.client:
            return []
        
        try:
            case_db_id = (
                st.secrets.get("CASE_DB_ID") or 
                st.secrets.get("NOTION_REPAIR_CASE_DB_ID") or 
                os.getenv("CASE_DB_ID") or 
                os.getenv("NOTION_REPAIR_CASE_DB_ID")
            )
            
            if not case_db_id:
                return []
            
            # カテゴリに基づくフィルタリング
            filter_conditions = {}
            if category:
                filter_conditions = {
                    "property": "カテゴリ",
                    "select": {
                        "equals": category
                    }
                }
            
            response = self.client.databases.query(
                database_id=case_db_id,
                filter=filter_conditions if filter_conditions else None
            )
            
            cases = response.get("results", [])
            return self._process_repair_cases(cases)
            
        except Exception as e:
            print(f"Error searching repair cases: {e}")
            return []
    
    @lru_cache(maxsize=100)
    def search_items(self, item_type: str = "") -> List[Dict]:
        """部品・工具を検索（キャッシュ付き）"""
        if not self.client:
            return []
        
        try:
            item_db_id = (
                st.secrets.get("ITEM_DB_ID") or 
                os.getenv("ITEM_DB_ID")
            )
            
            if not item_db_id:
                return []
            
            # アイテムタイプに基づくフィルタリング
            filter_conditions = {}
            if item_type:
                filter_conditions = {
                    "property": "カテゴリ",
                    "select": {
                        "equals": item_type
                    }
                }
            
            response = self.client.databases.query(
                database_id=item_db_id,
                filter=filter_conditions if filter_conditions else None
            )
            
            items = response.get("results", [])
            return self._process_items(items)
            
        except Exception as e:
            print(f"Error searching items: {e}")
            return []
    
    def _process_diagnostic_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """診断ノードデータを処理"""
        processed_nodes = []
        for node in nodes:
            properties = node.get("properties", {})
            processed_node = {
                "id": node["id"],
                "title": self._get_property_text(properties.get("名前", {})),
                "symptoms": self._get_property_text(properties.get("症状", {})),
                "category": self._get_property_text(properties.get("カテゴリ", {})),
                "is_terminal": self._get_property_checkbox(properties.get("終端フラグ", {})),
                "next_nodes": self._get_property_relation(properties.get("次のノード", {}))
            }
            processed_nodes.append(processed_node)
        return processed_nodes
    
    def _process_repair_cases(self, cases: List[Dict]) -> List[Dict]:
        """修理ケースデータを処理"""
        processed_cases = []
        for case in cases:
            properties = case.get("properties", {})
            processed_case = {
                "id": case["id"],
                "title": self._get_property_text(properties.get("ケース名", {})),
                "description": self._get_property_text(properties.get("説明", {})),
                "category": self._get_property_text(properties.get("カテゴリ", {})),
                "difficulty": self._get_property_text(properties.get("難易度", {})),
                "estimated_time": self._get_property_text(properties.get("推定時間", {})),
                "required_parts": self._get_property_multi_select(properties.get("必要な部品", {})),
                "required_tools": self._get_property_multi_select(properties.get("必要な工具", {})),
                "steps": self._get_property_text(properties.get("修理手順", {})),
                "cost_estimate": self._get_property_text(properties.get("費用目安", {}))
            }
            processed_cases.append(processed_case)
        return processed_cases
    
    def _process_items(self, items: List[Dict]) -> List[Dict]:
        """部品・工具データを処理"""
        processed_items = []
        for item in items:
            properties = item.get("properties", {})
            processed_item = {
                "id": item["id"],
                "name": self._get_property_text(properties.get("部品名", {})),
                "category": self._get_property_text(properties.get("カテゴリ", {})),
                "price": self._get_property_text(properties.get("価格", {})),
                "description": self._get_property_text(properties.get("説明", {})),
                "supplier": self._get_property_text(properties.get("仕入先", {})),
                "url": self._get_property_url(properties.get("URL", {}))
            }
            processed_items.append(processed_item)
        return processed_items
    
    def _get_property_text(self, prop: Dict) -> str:
        """テキストプロパティを取得"""
        if not prop:
            return ""
        
        prop_type = prop.get("type")
        if prop_type == "title":
            return "".join([x.get("plain_text", "") for x in prop["title"]])
        elif prop_type == "rich_text":
            return "".join([x.get("plain_text", "") for x in prop["rich_text"]])
        elif prop_type == "select":
            select_obj = prop.get("select")
            return select_obj.get("name", "") if select_obj else ""
        else:
            return str(prop.get(prop_type, ""))
    
    def _get_property_checkbox(self, prop: Dict) -> bool:
        """チェックボックスプロパティを取得"""
        if not prop:
            return False
        return prop.get("checkbox", False)
    
    def _get_property_multi_select(self, prop: Dict) -> List[str]:
        """マルチセレクトプロパティを取得"""
        if not prop:
            return []
        
        prop_type = prop.get("type")
        if prop_type == "multi_select":
            return [x.get("name", "") for x in prop.get("multi_select", [])]
        else:
            return []
    
    def _get_property_relation(self, prop: Dict) -> List[str]:
        """リレーションプロパティを取得"""
        if not prop:
            return []
        
        prop_type = prop.get("type")
        if prop_type == "relation":
            return [x.get("id", "") for x in prop.get("relation", [])]
        else:
            return []
    
    def _get_property_url(self, prop: Dict) -> str:
        """URLプロパティを取得"""
        if not prop:
            return ""
        
        prop_type = prop.get("type")
        if prop_type == "url":
            return prop.get("url", "")
        else:
            return ""
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self.search_diagnostic_nodes.cache_clear()
        self.search_repair_cases.cache_clear()
        self.search_items.cache_clear()
        self.cache.clear()

# グローバルインスタンス
notion_client = OptimizedNotionClient()

def get_optimized_notion_client() -> OptimizedNotionClient:
    """最適化されたNotionクライアントを取得"""
    return notion_client

def search_camper_repair_info(query: str) -> Dict[str, Any]:
    """キャンピングカー修理情報を統合検索（強化版）"""
    client = get_optimized_notion_client()
    
    # 各データベースから関連情報を検索
    diagnostic_nodes = client.search_diagnostic_nodes(query)
    repair_cases = client.search_repair_cases()
    items = client.search_items()
    
    # クエリに関連する修理ケースをフィルタリング（強化版）
    relevant_cases = []
    if query:
        query_lower = query.lower()
        query_words = query_lower.split()
        
        for case in repair_cases:
            case_title = case.get("title", "").lower()
            case_desc = case.get("description", "").lower()
            case_category = case.get("category", "").lower()
            
            # 直接マッチング
            if (query_lower in case_title or 
                query_lower in case_desc or
                query_lower in case_category):
                relevant_cases.append(case)
                continue
            
            # 部分マッチング
            for word in query_words:
                if (word in case_title or 
                    word in case_desc or
                    word in case_category):
                    if case not in relevant_cases:
                        relevant_cases.append(case)
                        break
            
            # バッテリー関連の特殊マッチング
            if any(term in query_lower for term in ["バッテリー", "充電", "電圧"]):
                if any(term in case_title for term in ["バッテリー", "充電", "電圧"]):
                    if case not in relevant_cases:
                        relevant_cases.append(case)
    
    # バッテリー関連の特殊処理
    if any(term in query.lower() for term in ["バッテリー", "充電", "電圧"]):
        battery_cases = [case for case in repair_cases if "バッテリー" in case.get("category", "").lower()]
        for case in battery_cases:
            if case not in relevant_cases:
                relevant_cases.append(case)
    
    return {
        "diagnostic_nodes": diagnostic_nodes,
        "repair_cases": relevant_cases if relevant_cases else repair_cases[:5],  # 最大5件
        "items": items[:10],  # 最大10件
        "query": query,
        "total_results": len(diagnostic_nodes) + len(relevant_cases) + len(items)
    }
