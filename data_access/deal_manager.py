#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商談管理モジュール（フェーズ4-2）
商談のCRUD操作とID自動採番を実装
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from data_access.notion_client import notion_client


class DealManager:
    """商談管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.notion = notion_client.client
        self.deal_db_id = self._get_database_id()
        
        if not self.deal_db_id:
            raise ValueError("NOTION_DEAL_DB_IDが設定されていません")
    
    def _get_database_id(self) -> Optional[str]:
        """データベースIDを取得"""
        db_id = (
            os.getenv("NOTION_DEAL_DB_ID") or
            os.getenv("DEAL_DB_ID")
        )
        if db_id:
            # ハイフンを削除して正規化
            return db_id.replace("-", "").lower()
        return None
    
    def _get_next_deal_id(self) -> str:
        """
        次の商談IDを生成（DEAL-20241103-001形式）
        
        Returns:
            次の商談ID（例: DEAL-20241103-001）
        """
        try:
            today = datetime.now().strftime("%Y%m%d")
            prefix = f"DEAL-{today}-"
            
            # 今日の日付で始まる商談を取得
            response = self.notion.databases.query(
                database_id=self.deal_db_id,
                filter={
                    "property": "商談ID",
                    "title": {"starts_with": prefix}
                },
                page_size=100
            )
            
            max_num = 0
            for page in response.get("results", []):
                props = page.get("properties", {})
                deal_id_prop = props.get("商談ID", {})
                
                if deal_id_prop.get("type") == "title":
                    title_array = deal_id_prop.get("title", [])
                    if title_array:
                        deal_id = title_array[0].get("plain_text", "")
                        # DEAL-YYYYMMDD-XXX形式から数値を抽出
                        if deal_id.startswith(prefix):
                            try:
                                num = int(deal_id.split("-")[2])
                                max_num = max(max_num, num)
                            except (ValueError, IndexError):
                                pass
            
            # 次のIDを生成
            next_num = max_num + 1
            return f"{prefix}{next_num:03d}"
            
        except Exception as e:
            print(f"⚠️ ID自動採番エラー: {e}")
            # エラー時はタイムスタンプベースのIDを生成
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"DEAL-{timestamp}"

    def _now_jst_iso(self) -> str:
        """JST(Asia/Tokyo)のタイムゾーン付きISO文字列を返す（Notionの日時ズレ対策）"""
        return datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
    
    def create_inquiry(
        self,
        customer_name: str,
        phone: str,
        prefecture: str,
        symptom_category: str,
        symptom_detail: str,
        partner_page_id: str,
        email: Optional[str] = None,
        notification_method: Optional[str] = None,
        line_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        新規問い合わせを商談DBに記録
        
        Args:
            customer_name: 顧客名
            phone: 電話番号
            prefecture: 都道府県
            symptom_category: 症状カテゴリ
            symptom_detail: 症状詳細
            partner_page_id: 紹介修理店のNotion Page ID
            email: メールアドレス（オプション）
        
        Returns:
            作成された商談データ
        """
        try:
            # 商談IDを生成
            deal_id = self._get_next_deal_id()
            
            # プロパティを構築
            properties = {
                "商談ID": {
                    "title": [{"text": {"content": deal_id}}]
                },
                "顧客名": {
                    "rich_text": [{"text": {"content": customer_name}}]
                },
                "電話番号": {
                    "phone_number": phone
                },
                "所在地（都道府県）": {
                    "select": {"name": prefecture}
                },
                "症状カテゴリ": {
                    "select": {"name": symptom_category}
                },
                "症状詳細": {
                    "rich_text": [{"text": {"content": symptom_detail}}]
                },
                "紹介修理店": {
                    "relation": [{"id": partner_page_id}]
                },
                "問い合わせ日時": {
                    "date": {"start": self._now_jst_iso()}
                },
                "紹介ステータス": {
                    "select": {"name": "pending"}
                },
                "手数料率": {
                    "number": 15.0  # デフォルト15%
                },
                "支払いステータス": {
                    "select": {"name": "未払い"}
                }
            }
            
            # メールアドレスがあれば追加
            if email:
                properties["メールアドレス"] = {
                    "email": email
                }
            
            # 通知方法があれば追加
            if notification_method:
                properties["通知方法"] = {
                    "select": {"name": notification_method}
                }
            
            # LINEユーザーIDがあれば追加
            if line_user_id:
                properties["LINEユーザーID"] = {
                    "rich_text": [{"text": {"content": line_user_id}}]
                }
            
            # Notionにページ作成
            new_page = self.notion.pages.create(
                parent={"database_id": self.deal_db_id},
                properties=properties
            )
            
            return self._parse_deal_page(new_page)
            
        except Exception as e:
            print(f"❌ 商談作成エラー: {e}")
            raise
    
    def list_deals(
        self,
        status: Optional[str] = None,
        partner_page_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        商談一覧を取得
        
        Args:
            status: 紹介ステータスでフィルタ（pending, contacted, completed, cancelled）
            partner_page_id: パートナー修理店のPage IDでフィルタ
            limit: 取得件数
        
        Returns:
            商談リスト
        """
        try:
            filters = []
            
            # ステータスフィルタ
            if status:
                filters.append({
                    "property": "紹介ステータス",
                    "select": {"equals": status}
                })
            
            # パートナー修理店フィルタ
            if partner_page_id:
                filters.append({
                    "property": "紹介修理店",
                    "relation": {"contains": partner_page_id}
                })
            
            query = {
                "database_id": self.deal_db_id,
                "page_size": limit,
                "sorts": [{
                    "property": "問い合わせ日時",
                    "direction": "descending"
                }]
            }
            
            if filters:
                query["filter"] = {"and": filters} if len(filters) > 1 else filters[0]
            
            response = self.notion.databases.query(**query)
            
            deals = []
            for page in response.get("results", []):
                deals.append(self._parse_deal_page(page))
            
            return deals
            
        except Exception as e:
            print(f"❌ 商談一覧取得エラー: {e}")
            return []
    
    def get_deal(self, deal_id: str) -> Optional[Dict[str, Any]]:
        """
        商談詳細を取得
        
        Args:
            deal_id: 商談ID（DEAL-20241103-001形式）またはNotion Page ID
        
        Returns:
            商談情報（見つからない場合はNone）
        """
        try:
            # 商談IDで検索
            response = self.notion.databases.query(
                database_id=self.deal_db_id,
                filter={
                    "property": "商談ID",
                    "title": {"equals": deal_id}
                }
            )
            
            if response.get("results"):
                return self._parse_deal_page(response["results"][0])
            
            return None
            
        except Exception as e:
            print(f"❌ 商談取得エラー: {e}")
            return None
    
    def update_deal_status(
        self,
        deal_id: str,
        status: str,
        send_notification: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        商談ステータスを更新
        
        Args:
            deal_id: 商談ID
            status: 新しいステータス（pending, contacted, completed, cancelled）
            send_notification: LINE通知を送信するかどうか（デフォルト: True）
        
        Returns:
            更新された商談情報
        """
        try:
            deal = self.get_deal(deal_id)
            if not deal:
                return None
            
            page_id = deal["page_id"]
            
            properties = {
                "紹介ステータス": {
                    "select": {"name": status}
                }
            }
            
            # 成約済みの場合は成約日を設定
            if status == "completed" and not deal.get("deal_date"):
                properties["成約日"] = {
                    "date": {"start": self._now_jst_iso()}
                }
            
            # Notionでページ更新
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            updated_deal = self._parse_deal_page(updated_page)
            
            # 通知を送信（LINE + メール）
            if send_notification:
                self._send_status_update_notification(updated_deal, status)
                self._send_status_update_email(updated_deal, status)
            
            # 商談完了時に修理完了通知と評価依頼通知を送信
            if status == "completed":
                self._send_repair_complete_notification(updated_deal)
                self._send_review_request_notification(updated_deal)
            
            return updated_deal
        except Exception as e:
            print(f"❌ 商談ステータス更新エラー: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_deals_by_partner(
        self,
        partner_page_id: str,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        パートナー工場に関連する商談を取得
        
        Args:
            partner_page_id: パートナー工場のNotion Page ID
            status: ステータスでフィルタ（completed等）
            limit: 取得件数
        
        Returns:
            商談リスト
        """
        try:
            filters = [{
                "property": "紹介修理店",
                "relation": {"contains": partner_page_id}
            }]
            
            if status:
                filters.append({
                    "property": "紹介ステータス",
                    "select": {"equals": status}
                })
            
            query = {
                "database_id": self.deal_db_id,
                "page_size": limit,
                "filter": {"and": filters} if len(filters) > 1 else filters[0]
            }
            
            response = self.notion.databases.query(**query)
            
            deals = []
            for page in response.get("results", []):
                deal = self._parse_deal_page(page)
                if deal:
                    deals.append(deal)
            
            return deals
        
        except Exception as e:
            print(f"❌ パートナー工場の商談取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _send_status_update_notification(self, deal: Dict[str, Any], status: str):
        """ステータス更新時にLINE通知を送信"""
        try:
            # LINE通知が有効で、LINEユーザーIDがある場合のみ送信
            line_user_id = deal.get("line_user_id")
            if not line_user_id:
                print("⚠️ LINEユーザーIDが設定されていないため、LINE通知をスキップします")
                return
            
            # 通知方法がLINEの場合のみ送信
            notification_method = deal.get("notification_method", "").lower()
            if notification_method != "line":
                print(f"⚠️ 通知方法がLINEではないため、LINE通知をスキップします（通知方法: {notification_method}）")
                return
            
            # LINE通知モジュールをインポート
            from notification.line_notifier import LineNotifier
            
            line_notifier = LineNotifier()
            if not line_notifier.enabled:
                print("⚠️ LINE通知機能が無効のため、LINE通知をスキップします")
                return
            
            # 修理店名を取得
            partner_name = "修理店"
            partner_page_ids = deal.get("partner_page_ids", [])
            if partner_page_ids:
                try:
                    from data_access.partner_shop_manager import PartnerShopManager
                    partner_manager = PartnerShopManager()
                    partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                    if partner_shop:
                        partner_name = partner_shop.get("name", "修理店")
                except Exception as e:
                    print(f"⚠️ 修理店情報取得エラー: {e}")
            
            # LINE通知を送信
            customer_name = deal.get("customer_name", "お客様")
            deal_id = deal.get("deal_id", "")
            
            result = line_notifier.send_status_update_notification(
                line_user_id=line_user_id,
                customer_name=customer_name,
                partner_name=partner_name,
                status=status,
                deal_id=deal_id,
                notes=None
            )
            
            if result.get("success"):
                print(f"✅ LINE通知送信成功: {customer_name}様（ステータス: {status}）")
            else:
                print(f"⚠️ LINE通知送信失敗: {result.get('error', '不明なエラー')}")
                
        except Exception as e:
            # 通知エラーはログに記録するが、ステータス更新は成功とする
            print(f"⚠️ LINE通知送信エラー（ステータス更新は正常に完了しました）: {e}")
            import traceback
            traceback.print_exc()
    
    def _send_status_update_email(self, deal: Dict[str, Any], status: str):
        """ステータス更新時にメール通知を送信"""
        try:
            # メールアドレスがある場合のみ送信
            customer_email = deal.get("email")
            if not customer_email:
                print("⚠️ 顧客のメールアドレスが設定されていないため、メール通知をスキップします")
                return
            
            # 通知方法がメールの場合のみ送信
            notification_method = deal.get("notification_method", "").lower()
            if notification_method != "email":
                print(f"⚠️ 通知方法がメールではないため、メール通知をスキップします（通知方法: {notification_method}）")
                return
            
            # メール送信モジュールをインポート
            from notification.email_sender import EmailSender
            
            email_sender = EmailSender()
            if not email_sender.enabled:
                print("⚠️ メール送信機能が無効のため、メール通知をスキップします")
                return
            
            # 修理店名を取得
            partner_name = "修理店"
            partner_page_ids = deal.get("partner_page_ids", [])
            if partner_page_ids:
                try:
                    from data_access.partner_shop_manager import PartnerShopManager
                    partner_manager = PartnerShopManager()
                    partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                    if partner_shop:
                        partner_name = partner_shop.get("name", "修理店")
                except Exception as e:
                    print(f"⚠️ 修理店情報取得エラー: {e}")
            
            # メール通知を送信
            customer_name = deal.get("customer_name", "お客様")
            deal_id = deal.get("deal_id", "")
            
            result = email_sender.send_status_update_to_customer(
                customer_email=customer_email,
                customer_name=customer_name,
                partner_name=partner_name,
                status=status,
                deal_id=deal_id
            )
            
            if result:
                print(f"✅ メール通知送信成功: {customer_name}様（{customer_email}）（ステータス: {status}）")
            else:
                print(f"⚠️ メール通知送信失敗: {customer_name}様（{customer_email}）")
                
        except Exception as e:
            # 通知エラーはログに記録するが、ステータス更新は成功とする
            print(f"⚠️ メール通知送信エラー（ステータス更新は正常に完了しました）: {e}")
            import traceback
            traceback.print_exc()
    
    def _send_review_request_notification(self, deal: Dict[str, Any]):
        """商談完了時に評価依頼通知を送信"""
        try:
            # 評価依頼URLを生成（フロントエンドの評価フォームページ）
            deal_id = deal.get("deal_id", "")
            partner_page_ids = deal.get("partner_page_ids", [])
            partner_page_id = partner_page_ids[0] if partner_page_ids else ""
            customer_name = deal.get("customer_name", "")
            
            # URLパラメータを構築
            params = [f"deal_id={deal_id}"]
            if partner_page_id:
                params.append(f"partner_page_id={partner_page_id}")
            if customer_name:
                params.append(f"customer_name={customer_name}")
            
            review_url = f"/review?{'&'.join(params)}"
            
            # メール通知の場合
            email = deal.get("email")
            notification_method = deal.get("notification_method", "").lower()
            
            if email and notification_method == "email":
                from notification.email_sender import EmailSender
                email_sender = EmailSender()
                
                customer_name = deal.get("customer_name", "お客様")
                partner_name = "修理店"
                partner_page_ids = deal.get("partner_page_ids", [])
                if partner_page_ids:
                    try:
                        from data_access.partner_shop_manager import PartnerShopManager
                        partner_manager = PartnerShopManager()
                        partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                        if partner_shop:
                            partner_name = partner_shop.get("name", "修理店")
                    except Exception:
                        pass
                
                email_sender.send_review_request(
                    to_email=email,
                    customer_name=customer_name,
                    partner_name=partner_name,
                    deal_id=deal_id,
                    review_url=review_url
                )
            
            # LINE通知の場合
            line_user_id = deal.get("line_user_id")
            if line_user_id and notification_method == "line":
                from notification.line_notifier import LineNotifier
                line_notifier = LineNotifier()
                
                if line_notifier.enabled:
                    customer_name = deal.get("customer_name", "お客様")
                    partner_name = "修理店"
                    partner_page_ids = deal.get("partner_page_ids", [])
                    if partner_page_ids:
                        try:
                            from data_access.partner_shop_manager import PartnerShopManager
                            partner_manager = PartnerShopManager()
                            partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                            if partner_shop:
                                partner_name = partner_shop.get("name", "修理店")
                        except Exception:
                            pass
                    
                    line_notifier.send_review_request(
                        line_user_id=line_user_id,
                        customer_name=customer_name,
                        partner_name=partner_name,
                        deal_id=deal_id,
                        review_url=review_url
                    )
        
        except Exception as e:
            print(f"⚠️ 評価依頼通知送信エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def _send_repair_complete_notification(self, deal: Dict[str, Any]):
        """修理完了時に修理完了通知と支払い案内を送信"""
        try:
            deal_id = deal.get("deal_id", "")
            customer_name = deal.get("customer_name", "お客様")
            email = deal.get("email")
            line_user_id = deal.get("line_user_id")
            notification_method = deal.get("notification_method", "").lower()
            deal_amount = deal.get("deal_amount")
            symptom_detail = deal.get("symptom_detail", "")
            
            # 修理店名を取得
            partner_name = "修理店"
            partner_page_ids = deal.get("partner_page_ids", [])
            if partner_page_ids:
                try:
                    from data_access.partner_shop_manager import PartnerShopManager
                    partner_manager = PartnerShopManager()
                    partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                    if partner_shop:
                        partner_name = partner_shop.get("name", "修理店")
                except Exception as e:
                    pass
            
            # メール通知の場合
            if email and notification_method == "email":
                from notification.email_sender import EmailSender
                email_sender = EmailSender()
                
                email_sender.send_repair_complete_to_customer(
                    customer_email=email,
                    customer_name=customer_name,
                    partner_name=partner_name,
                    deal_id=deal_id,
                    repair_content=symptom_detail,
                    deal_amount=deal_amount
                )
            
            # LINE通知の場合
            if line_user_id and notification_method == "line":
                from notification.line_notifier import LineNotifier
                line_notifier = LineNotifier()
                
                if line_notifier.enabled:
                    line_notifier.send_repair_complete_to_customer(
                        line_user_id=line_user_id,
                        customer_name=customer_name,
                        partner_name=partner_name,
                        deal_id=deal_id,
                        repair_content=symptom_detail,
                        deal_amount=deal_amount
                    )
        
        except Exception as e:
            print(f"⚠️ 修理完了通知送信エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def update_deal_amount(
        self,
        deal_id: str,
        deal_amount: float,
        commission_rate: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        成約金額を更新（手数料も自動計算）
        
        Args:
            deal_id: 商談ID
            deal_amount: 成約金額
            commission_rate: 手数料率（デフォルト15%）
        
        Returns:
            更新された商談情報
        """
        try:
            deal = self.get_deal(deal_id)
            if not deal:
                return None
            
            page_id = deal["page_id"]
            rate = commission_rate or deal.get("commission_rate", 15.0)
            commission_amount = deal_amount * (rate / 100)
            
            properties = {
                "成約金額": {
                    "number": deal_amount
                },
                "手数料率": {
                    "number": rate
                },
                "手数料金額": {
                    "number": commission_amount
                }
            }
            
            # Notionでページ更新
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            updated_deal = self._parse_deal_page(updated_page)
            
            # パートナー工場の統計情報を更新（修理回数、修理金額の合計）
            partner_page_ids = updated_deal.get("partner_page_ids", [])
            if partner_page_ids:
                try:
                    from data_access.partner_shop_manager import PartnerShopManager
                    partner_manager = PartnerShopManager()
                    partner_manager.update_shop_statistics(partner_page_ids[0])
                except Exception as e:
                    print(f"⚠️ パートナー工場統計情報更新エラー: {e}")
            
            return updated_deal
            
        except Exception as e:
            print(f"❌ 成約金額更新エラー: {e}")
            raise
    
    def add_customer_note(
        self,
        deal_id: str,
        customer_note: str
    ) -> Optional[Dict[str, Any]]:
        """
        お客様からの備考を追加

        Args:
            deal_id: 商談ID
            customer_note: お客様からの備考

        Returns:
            更新された商談情報
        """
        try:
            deal = self.get_deal(deal_id)
            if not deal:
                return None
            
            page_id = deal["page_id"]
            
            # 既存の備考を取得
            existing_notes = deal.get("notes", "")
            
            # タイムスタンプ付きで備考を追加
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_note = f"{existing_notes}\n\n【お客様からのメッセージ - {timestamp}】\n{customer_note}" if existing_notes else f"【お客様からのメッセージ - {timestamp}】\n{customer_note}"
            
            properties = {
                "備考": {
                    "rich_text": [{"text": {"content": new_note}}]
                }
            }
            
            # Notionでページ更新
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            return self._parse_deal_page(updated_page)
            
        except Exception as e:
            print(f"❌ お客様備考追加エラー: {e}")
            raise
    
    def add_progress_report(
        self,
        deal_id: str,
        progress_message: str,
        max_reports: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        工場側からの経過報告を追加（最大2回まで）

        Args:
            deal_id: 商談ID
            progress_message: 経過報告メッセージ
            max_reports: 最大報告回数（デフォルト: 2）

        Returns:
            更新された商談情報（制限に達した場合はNone）
        """
        try:
            deal = self.get_deal(deal_id)
            if not deal:
                return None
            
            # 現在の報告回数を取得（Notion側が未設定の場合はNoneになるので0に正規化）
            raw_count = deal.get("progress_report_count")
            current_count = raw_count if isinstance(raw_count, int) and raw_count >= 0 else 0
            
            # 最大回数に達している場合はエラー
            if current_count >= max_reports:
                raise ValueError(f"経過報告は最大{max_reports}回まで送信できます。既に{current_count}回送信されています。")
            
            page_id = deal["page_id"]
            
            # 既存の備考を取得
            existing_notes = deal.get("notes", "")
            
            # タイムスタンプ付きで経過報告を追加
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_note = f"{existing_notes}\n\n【経過報告 #{current_count + 1} - {timestamp}】\n{progress_message}" if existing_notes else f"【経過報告 #1 - {timestamp}】\n{progress_message}"
            
            # 報告回数をインクリメント
            new_count = current_count + 1
            
            properties = {
                "備考": {
                    "rich_text": [{"text": {"content": new_note}}]
                },
                "経過報告回数": {
                    "number": new_count
                }
            }
            
            # Notionでページ更新
            updated_page = self.notion.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            return self._parse_deal_page(updated_page)
            
        except Exception as e:
            print(f"❌ 経過報告追加エラー: {e}")
            raise
    
    def _parse_deal_page(self, page: Dict) -> Dict[str, Any]:
        """Notionページを商談情報にパース"""
        props = page.get("properties", {})
        
        # 紹介修理店のリレーションを取得
        partner_relation = props.get("紹介修理店", {})
        partner_page_ids = []
        if partner_relation.get("type") == "relation":
            partner_page_ids = [rel.get("id") for rel in partner_relation.get("relation", [])]
        
        return {
            "page_id": page["id"],
            "deal_id": self._get_property_title(props, "商談ID"),
            "customer_name": self._get_property_text(props, "顧客名"),
            "phone": self._get_property_phone(props, "電話番号"),
            "email": self._get_property_email(props, "メールアドレス"),
            "prefecture": self._get_property_select(props, "所在地（都道府県）"),
            "symptom_category": self._get_property_select(props, "症状カテゴリ"),
            "symptom_detail": self._get_property_text(props, "症状詳細"),
            "partner_page_ids": partner_page_ids,
            "inquiry_date": self._get_property_date(props, "問い合わせ日時"),
            "status": self._get_property_select(props, "紹介ステータス"),
            "deal_date": self._get_property_date(props, "成約日"),
            "deal_amount": self._get_property_number(props, "成約金額"),
            "commission_rate": self._get_property_number(props, "手数料率"),
            "commission_amount": self._get_property_number(props, "手数料金額"),
            "payment_status": self._get_property_select(props, "支払いステータス"),
            "notification_method": self._get_property_select(props, "通知方法"),
            "line_user_id": self._get_property_text(props, "LINEユーザーID"),
            "notes": self._get_property_text(props, "備考"),
            "progress_report_count": self._get_property_number(props, "経過報告回数"),
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

