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
NOTION_DEAL_DB_ID = os.getenv("NOTION_DEAL_DB_ID") or os.getenv("DEAL_DB_ID")
NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2022-06-28")

# データベースIDをサニタイズ
def _sanitize_db_id(db_id: Optional[str]) -> Optional[str]:
    if not db_id:
        return None
    try:
        import re
        cleaned = re.sub(r"[^0-9a-fA-F]", "", db_id).lower()
        return cleaned
    except Exception:
        return db_id.replace("-", "") if db_id else None

NOTION_LOG_DB_ID = _sanitize_db_id(NOTION_LOG_DB_ID)
NOTION_DEAL_DB_ID = _sanitize_db_id(NOTION_DEAL_DB_ID)

NOTION_PAGES_URL = "https://api.notion.com/v1/pages"
NOTION_DATABASE_URL = "https://api.notion.com/v1/databases"
NOTION_COMMENTS_URL = "https://api.notion.com/v1/comments"

# ステータス定義（Phase 4対応）
STATUS_OPTIONS = ["受付", "診断中", "修理中", "完了", "キャンセル"]


class FactoryDashboardManager:
    """工場向けダッシュボード管理クラス（Phase 4）"""
    
    def __init__(self):
        if not NOTION_API_KEY:
            raise ValueError("NOTION_API_KEYが設定されていません")
        
        if not NOTION_LOG_DB_ID and not NOTION_DEAL_DB_ID:
            raise ValueError("NOTION_LOG_DB_IDまたはNOTION_DEAL_DB_IDのいずれかが設定されている必要があります")
        
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }
        self.log_db_id = NOTION_LOG_DB_ID
        self.deal_db_id = NOTION_DEAL_DB_ID
        
        # ステータスマッピング（商談DB → 工場ダッシュボード）
        self.status_mapping = {
            "pending": "受付",
            "contacted": "診断中",
            "in_progress": "修理中",
            "completed": "完了",
            "cancelled": "キャンセル"
        }
    
    def get_cases(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        sort_by: str = "timestamp",
        sort_direction: str = "descending",
        partner_page_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Notionから案件一覧を取得（チャットログDBと商談DBの両方から取得）
        
        Args:
            status: フィルタするステータス（Noneの場合は全件）
            limit: 取得件数
            sort_by: ソート項目（timestamp, category等）
            sort_direction: ソート方向（ascending/descending）
            partner_page_id: パートナー工場のNotion Page ID（指定された場合、その工場に紹介された案件のみ取得）
        
        Returns:
            案件リスト
        """
        cases = []
        log_cases = []
        deal_cases = []
        
        # チャットログDBから案件を取得
        if self.log_db_id:
            try:
                log_cases = self._get_cases_from_log_db(status, limit, sort_by, sort_direction, partner_page_id)
                cases.extend(log_cases)
            except Exception as e:
                logger.warning(f"⚠️ チャットログDBからの案件取得エラー: {e}")
        
        # 商談DBから案件を取得
        if self.deal_db_id:
            try:
                deal_cases = self._get_cases_from_deal_db(status, limit, sort_by, sort_direction, partner_page_id)
                cases.extend(deal_cases)
            except Exception as e:
                logger.warning(f"⚠️ 商談DBからの案件取得エラー: {e}")

        #region agent log
        import json as _json, time as _time
        try:
            with open(r"c:\Users\PC user\OneDrive\Desktop\移行用まとめフォルダー\.cursor\debug.log", "a", encoding="utf-8") as _f:
                _f.write(_json.dumps({
                    "sessionId": "debug-session",
                    "runId": "initial",
                    "hypothesisId": "H3",
                    "location": "factory_dashboard_manager.py:get_cases",
                    "message": "Notion case fetch summary",
                    "data": {
                        "status_filter": status,
                        "partner_page_id": partner_page_id,
                        "log_db_enabled": bool(self.log_db_id),
                        "deal_db_enabled": bool(self.deal_db_id),
                        "log_cases_count": len(log_cases),
                        "deal_cases_count": len(deal_cases)
                    },
                    "timestamp": int(_time.time() * 1000)
                }, ensure_ascii=False) + "\n")
        except Exception:
            pass
        #endregion
        
        # タイムスタンプでソート（新しい順）
        cases.sort(key=lambda x: x.get("timestamp") or x.get("created_time") or "", reverse=(sort_direction == "descending"))
        
        # 件数制限
        if limit:
            cases = cases[:limit]
        
        if partner_page_id:
            logger.info(f"✅ パートナー工場専用の案件取得成功: 合計{len(cases)}件（工場ID: {partner_page_id}）")
        else:
            logger.info(f"✅ 案件取得成功: 合計{len(cases)}件（チャットログ: {len([c for c in cases if c.get('source') == 'log'])}, 商談: {len([c for c in cases if c.get('source') == 'deal'])})")
        return cases
    
    def _get_cases_from_log_db(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        sort_by: str = "timestamp",
        sort_direction: str = "descending",
        partner_page_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """チャットログDBから案件を取得"""
        try:
            query = {
                "page_size": limit,
            }
            
            # フィルタを構築
            filters = []
            
            # パートナー工場でフィルタリング（チャットログDBにも工場情報がある場合）
            # 注意: チャットログDBには「紹介修理店」プロパティがない可能性があるため、
            # パートナー工場IDが指定されている場合は、後でフィルタリングする
            # （現時点ではチャットログDBには工場情報がないため、このフィルタは適用しない）
            
            # ステータスフィルタ
            if status:
                filters.append({
                    "property": "status",
                    "select": {"equals": status}
                })
            
            # フィルタを適用
            if filters:
                if len(filters) > 1:
                    query["filter"] = {"and": filters}
                else:
                    query["filter"] = filters[0]
            
            # ソート設定
            query["sorts"] = [{
                "property": sort_by if sort_by in ["timestamp", "category"] else "timestamp",
                "direction": sort_direction
            }]
            
            response = requests.post(
                f"{NOTION_DATABASE_URL}/{self.log_db_id}/query",
                headers=self.headers,
                json=query,
                timeout=15
            )
            
            if not response.ok:
                logger.error(f"NotionチャットログDB案件取得エラー: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            cases = []
            
            for page in data.get("results", []):
                case = self._parse_page(page)
                if case:
                    case["source"] = "log"  # ソースをマーク
                    # パートナー工場IDが指定されている場合、チャットログDBの案件は
                    # 工場情報がないため、商談DBからの案件のみを返す
                    # （チャットログDBには「紹介修理店」プロパティがない）
                    if not partner_page_id:
                        cases.append(case)
            
            return cases
        
        except Exception as e:
            logger.error(f"❌ チャットログDB案件取得エラー: {e}")
            return []
    
    def _get_cases_from_deal_db(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        sort_by: str = "timestamp",
        sort_direction: str = "descending",
        partner_page_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """商談DBから案件を取得"""
        try:
            # ステータスフィルタを商談DBのステータスに変換
            deal_status = None
            if status:
                # 工場ダッシュボードのステータス → 商談DBのステータスに逆マッピング
                reverse_mapping = {v: k for k, v in self.status_mapping.items()}
                deal_status = reverse_mapping.get(status)
            
            query = {
                "page_size": limit,
            }
            
            # フィルタを構築
            filters = []
            
            # パートナー工場でフィルタリング（この工場に紹介された案件のみ）
            if partner_page_id:
                filters.append({
                    "property": "紹介修理店",
                    "relation": {"contains": partner_page_id}
                })
                logger.info(f"🔍 パートナー工場でフィルタリング: {partner_page_id}")
            
            # ステータスフィルタ
            if deal_status:
                filters.append({
                    "property": "紹介ステータス",
                    "select": {"equals": deal_status}
                })
            
            # フィルタを適用
            if filters:
                if len(filters) > 1:
                    query["filter"] = {"and": filters}
                else:
                    query["filter"] = filters[0]
            
            # ソート設定
            query["sorts"] = [{
                "property": "問い合わせ日時",
                "direction": sort_direction
            }]
            
            response = requests.post(
                f"{NOTION_DATABASE_URL}/{self.deal_db_id}/query",
                headers=self.headers,
                json=query,
                timeout=15
            )
            
            if not response.ok:
                logger.error(f"Notion商談DB案件取得エラー: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            cases = []
            
            for page in data.get("results", []):
                case = self._parse_deal_page(page)
                if case:
                    case["source"] = "deal"  # ソースをマーク
                    cases.append(case)
            
            return cases
        
        except Exception as e:
            logger.error(f"❌ 商談DB案件取得エラー: {e}")
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
    
    def _parse_deal_page(self, page: Dict) -> Optional[Dict[str, Any]]:
        """商談DBのページをパースして案件データに変換"""
        try:
            props = page.get("properties", {})
            
            # 商談ID（タイトル）を取得
            deal_id = ""
            deal_id_prop = props.get("商談ID", {})
            if deal_id_prop.get("type") == "title":
                title_list = deal_id_prop.get("title", [])
                if title_list:
                    deal_id = title_list[0].get("text", {}).get("content", "")
            
            # 各種プロパティ取得
            customer_name = self._get_rich_text(props.get("顧客名", {}))
            phone = self._get_phone(props.get("電話番号", {}))
            email = self._get_email(props.get("メールアドレス", {}))
            prefecture = self._get_select(props.get("所在地（都道府県）", {}))
            symptom_category = self._get_select(props.get("症状カテゴリ", {}))
            symptom_detail = self._get_rich_text(props.get("症状詳細", {}))
            inquiry_date = self._get_date(props.get("問い合わせ日時", {}))
            deal_status = self._get_select(props.get("紹介ステータス", {}))
            
            # ステータスを工場ダッシュボードのステータスにマッピング
            dashboard_status = self.status_mapping.get(deal_status, "受付")
            
            # 紹介修理店のリレーションを取得
            partner_relation = props.get("紹介修理店", {})
            partner_page_ids = []
            if partner_relation.get("type") == "relation":
                partner_page_ids = [rel.get("id") for rel in partner_relation.get("relation", [])]
            
            return {
                "page_id": page.get("id"),
                "title": deal_id or customer_name or "未設定",
                "deal_id": deal_id,
                "customer_name": customer_name,
                "phone": phone,
                "email": email,
                "prefecture": prefecture,
                "symptom_category": symptom_category,
                "symptom_detail": symptom_detail,
                "status": dashboard_status,
                "deal_status": deal_status,  # 元のステータスも保持
                "timestamp": inquiry_date,
                "partner_page_ids": partner_page_ids,
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time"),
                "user_message": symptom_detail,  # 症状詳細をuser_messageとして使用
                "bot_message": "",  # 商談DBにはbot_messageがない
                "category": symptom_category,
                "comment": "",
                "image_url": None,
            }
        except Exception as e:
            logger.warning(f"⚠️ 商談DBページパースエラー: {e}")
            return None
    
    def _get_phone(self, prop: Dict) -> str:
        """Phone Numberプロパティから値を取得"""
        if not prop or prop.get("type") != "phone_number":
            return ""
        return prop.get("phone_number", "") or ""
    
    def _get_email(self, prop: Dict) -> str:
        """Emailプロパティから値を取得"""
        if not prop or prop.get("type") != "email":
            return ""
        return prop.get("email", "") or ""
    
    def update_status(self, page_id: str, status: str, source: Optional[str] = None) -> bool:
        """
        案件のステータスを更新（チャットログDBまたは商談DB）
        
        Args:
            page_id: NotionページID
            status: 新しいステータス（受付/診断中/修理中/完了/キャンセル）
            source: データソース（"log"または"deal"）。Noneの場合は自動判定
        
        Returns:
            成功時True
        """
        if status not in STATUS_OPTIONS:
            logger.warning(f"⚠️ 無効なステータス: {status}")
            return False
        
        # ソースが指定されていない場合、ページを取得して判定
        if not source:
            source = self._detect_source(page_id)
        
        # 商談DBの場合は、ステータスを商談DBの形式に変換
        if source == "deal":
            return self._update_deal_status(page_id, status)
        else:
            # チャットログDBの場合
            return self._update_log_status(page_id, status)
    
    def _detect_source(self, page_id: str) -> str:
        """ページIDからデータソースを判定"""
        try:
            # ページを取得してプロパティを確認
            response = requests.get(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                timeout=15
            )
            
            if response.ok:
                page = response.json()
                props = page.get("properties", {})
                
                # 商談DBのプロパティがあるか確認
                if "商談ID" in props or "紹介ステータス" in props:
                    return "deal"
                else:
                    return "log"
        except Exception as e:
            logger.warning(f"⚠️ ソース判定エラー: {e}")
        
        return "log"  # デフォルトはチャットログDB
    
    def _update_log_status(self, page_id: str, status: str) -> bool:
        """チャットログDBのステータスを更新"""
        try:
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
                logger.info(f"✅ チャットログDBステータス更新成功: {page_id} -> {status}")
                return True
            else:
                # statusプロパティが存在しない場合、コメントに追記
                logger.warning(f"⚠️ ステータス更新失敗（フォールバック）: {response.status_code}")
                return self._update_status_via_comment(page_id, status)
        
        except Exception as e:
            logger.error(f"❌ チャットログDBステータス更新エラー: {e}")
            return False
    
    def _update_deal_status(self, page_id: str, status: str) -> bool:
        """商談DBのステータスを更新"""
        try:
            # 工場ダッシュボードのステータス → 商談DBのステータスに変換
            reverse_mapping = {v: k for k, v in self.status_mapping.items()}
            deal_status = reverse_mapping.get(status)
            
            if not deal_status:
                logger.warning(f"⚠️ ステータスマッピングが見つかりません: {status}")
                return False
            
            properties = {
                "紹介ステータス": {
                    "select": {"name": deal_status}
                }
            }
            
            response = requests.patch(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                json={"properties": properties},
                timeout=15
            )
            
            if response.ok:
                logger.info(f"✅ 商談DBステータス更新成功: {page_id} -> {status} (deal_status: {deal_status})")
                
                # LINE通知を送信
                try:
                    self._send_status_update_notification(page_id, status)
                except Exception as notify_error:
                    # 通知エラーはログに記録するが、ステータス更新は成功とする
                    logger.warning(f"⚠️ LINE通知送信エラー（ステータス更新は正常に完了しました）: {notify_error}")
                
                # メール通知を送信
                try:
                    self._send_status_update_email(page_id, status)
                except Exception as email_error:
                    # 通知エラーはログに記録するが、ステータス更新は成功とする
                    logger.warning(f"⚠️ メール通知送信エラー（ステータス更新は正常に完了しました）: {email_error}")
                
                return True
            else:
                logger.error(f"❌ 商談DBステータス更新失敗: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"❌ 商談DBステータス更新エラー: {e}")
            return False
    
    def _send_status_update_notification(self, page_id: str, status: str):
        """ステータス更新時にLINE通知を送信"""
        try:
            # 商談情報を取得
            response = requests.get(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                timeout=15
            )
            
            if not response.ok:
                logger.warning(f"⚠️ 商談情報取得失敗: {response.status_code}")
                return
            
            page = response.json()
            props = page.get("properties", {})
            
            # LINEユーザーIDを取得
            line_user_id = self._get_rich_text(props.get("LINEユーザーID", {}))
            if not line_user_id:
                logger.info("⚠️ LINEユーザーIDが設定されていないため、LINE通知をスキップします")
                return
            
            # 通知方法を確認
            notification_method = self._get_select(props.get("通知方法", {}))
            if notification_method and notification_method.lower() != "line":
                logger.info(f"⚠️ 通知方法がLINEではないため、LINE通知をスキップします（通知方法: {notification_method}）")
                return
            
            # LINE通知モジュールをインポート
            from notification.line_notifier import LineNotifier
            
            line_notifier = LineNotifier()
            if not line_notifier.enabled:
                logger.info("⚠️ LINE通知機能が無効のため、LINE通知をスキップします")
                return
            
            # 顧客情報を取得
            customer_name = self._get_rich_text(props.get("顧客名", {})) or "お客様"
            deal_id_prop = props.get("商談ID", {})
            deal_id = ""
            if deal_id_prop.get("type") == "title":
                title_list = deal_id_prop.get("title", [])
                if title_list:
                    deal_id = title_list[0].get("text", {}).get("content", "")
            
            # 修理店名を取得
            partner_name = "修理店"
            partner_relation = props.get("紹介修理店", {})
            partner_page_ids = []
            if partner_relation.get("type") == "relation":
                partner_page_ids = [rel.get("id") for rel in partner_relation.get("relation", [])]
            
            if partner_page_ids:
                try:
                    from data_access.partner_shop_manager import PartnerShopManager
                    partner_manager = PartnerShopManager()
                    partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                    if partner_shop:
                        partner_name = partner_shop.get("name", "修理店")
                except Exception as e:
                    logger.warning(f"⚠️ 修理店情報取得エラー: {e}")
            
            # LINE通知を送信（日本語ステータスをそのまま渡す）
            result = line_notifier.send_status_update_notification(
                line_user_id=line_user_id,
                customer_name=customer_name,
                partner_name=partner_name,
                status=status,  # 日本語ステータス（診断中、修理中など）をそのまま渡す
                deal_id=deal_id,
                notes=None
            )
            
            if result.get("success"):
                logger.info(f"✅ LINE通知送信成功: {customer_name}様（ステータス: {status}）")
            else:
                logger.warning(f"⚠️ LINE通知送信失敗: {result.get('error', '不明なエラー')}")
                
        except Exception as e:
            # 通知エラーはログに記録するが、ステータス更新は成功とする
            logger.warning(f"⚠️ LINE通知送信エラー（ステータス更新は正常に完了しました）: {e}")
            import traceback
            traceback.print_exc()
    
    def _send_status_update_email(self, page_id: str, status: str):
        """ステータス更新時にメール通知を送信"""
        try:
            # 商談情報を取得
            response = requests.get(
                f"{NOTION_PAGES_URL}/{page_id}",
                headers=self.headers,
                timeout=15
            )
            
            if not response.ok:
                logger.warning(f"⚠️ 商談情報取得失敗: {response.status_code}")
                return
            
            page = response.json()
            props = page.get("properties", {})
            
            # メールアドレスを取得
            customer_email = self._get_email(props.get("メールアドレス", {}))
            if not customer_email:
                logger.info("⚠️ 顧客のメールアドレスが設定されていないため、メール通知をスキップします")
                return
            
            # 通知方法を確認
            notification_method = self._get_select(props.get("通知方法", {}))
            if notification_method and notification_method.lower() != "email":
                logger.info(f"⚠️ 通知方法がメールではないため、メール通知をスキップします（通知方法: {notification_method}）")
                return
            
            # メール送信モジュールをインポート
            from notification.email_sender import EmailSender
            
            email_sender = EmailSender()
            if not email_sender.enabled:
                logger.info("⚠️ メール送信機能が無効のため、メール通知をスキップします")
                return
            
            # 顧客情報を取得
            customer_name = self._get_rich_text(props.get("顧客名", {})) or "お客様"
            deal_id_prop = props.get("商談ID", {})
            deal_id = ""
            if deal_id_prop.get("type") == "title":
                title_list = deal_id_prop.get("title", [])
                if title_list:
                    deal_id = title_list[0].get("text", {}).get("content", "")
            
            # 修理店名を取得
            partner_name = "修理店"
            partner_relation = props.get("紹介修理店", {})
            partner_page_ids = []
            if partner_relation.get("type") == "relation":
                partner_page_ids = [rel.get("id") for rel in partner_relation.get("relation", [])]
            
            if partner_page_ids:
                try:
                    from data_access.partner_shop_manager import PartnerShopManager
                    partner_manager = PartnerShopManager()
                    partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                    if partner_shop:
                        partner_name = partner_shop.get("name", "修理店")
                except Exception as e:
                    logger.warning(f"⚠️ 修理店情報取得エラー: {e}")
            
            # ステータスを商談DBのステータスに変換
            reverse_mapping = {v: k for k, v in self.status_mapping.items()}
            deal_status = reverse_mapping.get(status, status)
            
            # メール通知を送信
            result = email_sender.send_status_update_to_customer(
                customer_email=customer_email,
                customer_name=customer_name,
                partner_name=partner_name,
                status=deal_status,  # 商談DBのステータス形式で送信
                deal_id=deal_id
            )
            
            if result:
                logger.info(f"✅ メール通知送信成功: {customer_name}様（{customer_email}）（ステータス: {status}）")
            else:
                logger.warning(f"⚠️ メール通知送信失敗: {customer_name}様（{customer_email}）")
                
        except Exception as e:
            # 通知エラーはログに記録するが、ステータス更新は成功とする
            logger.warning(f"⚠️ メール通知送信エラー（ステータス更新は正常に完了しました）: {e}")
            import traceback
            traceback.print_exc()
    
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
            
            if "comment" in props:
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
            else:
                # comment プロパティがない場合は Notion の comments API を使用
                return self._append_notion_comment(page_id, new_comment)
            if "comment" in props:
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
            else:
                return self._append_notion_comment(page_id, new_comment)
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
            
            if "comment" in props:
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
            else:
                # comment プロパティがない場合は NotionコメントAPIを利用
                if self._append_notion_comment(page_id, new_comment):
                    logger.info(f"✅ コメント追加成功（NotionコメントAPI）: {page_id}")
                    return True
                else:
                    logger.error("❌ コメント追加失敗: NotionコメントAPIでもエラー")
                    return False
        
        except Exception as e:
            logger.error(f"❌ コメント追加エラー: {e}")
            return False
    
    def _append_notion_comment(self, page_id: str, comment_text: str) -> bool:
        """NotionコメントAPI経由でコメントを追加"""
        try:
            payload = {
                "parent": {"page_id": page_id},
                "rich_text": [{
                    "text": {"content": comment_text[:1900]}
                }]
            }
            
            response = requests.post(
                NOTION_COMMENTS_URL,
                headers=self.headers,
                json=payload,
                timeout=15
            )
            
            if response.ok:
                return True
            else:
                logger.error(f"❌ NotionコメントAPI失敗: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ NotionコメントAPIエラー: {e}")
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

