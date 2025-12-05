#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LINE通知モジュール
LINE Messaging APIを使用してプッシュメッセージを送信
"""

import os
import requests
from typing import Dict, Optional, List, Any
from datetime import datetime


class LineNotifier:
    """LINE通知クラス"""
    
    def __init__(self):
        """初期化"""
        self.channel_access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
        self.api_url = "https://api.line.me/v2/bot/message/push"
        self.enabled = bool(self.channel_access_token)
    
    def send_to_partner(
        self,
        line_user_id: str,
        partner_name: str,
        customer_info: Dict
    ) -> Dict[str, Any]:
        """
        修理店に問い合わせ通知を送信
        
        Args:
            line_user_id: 修理店のLINEユーザーID
            partner_name: 修理店名
            customer_info: 顧客情報（name, phone, prefecture, email, category, detail）
        
        Returns:
            送信結果（success: bool, message: str, error: Optional[str]）
        """
        if not self.enabled:
            print("⚠️ LINE_CHANNEL_ACCESS_TOKENが設定されていません。LINE通知をスキップします。")
            return {"success": False, "error": "LINE設定が不完全です"}
        
        if not line_user_id:
            print("⚠️ 修理店のLINEユーザーIDが設定されていません。")
            return {"success": False, "error": "LINEユーザーIDが設定されていません"}
        
        message = self._build_partner_message(partner_name, customer_info)
        
        return self._send_notification(line_user_id, message)
    
    def send_to_customer(
        self,
        line_user_id: str,
        customer_name: str,
        partner_name: str,
        deal_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        顧客に確認メールを送信
        
        Args:
            line_user_id: 顧客のLINEユーザーID
            customer_name: 顧客名
            partner_name: 紹介した修理店名
            deal_id: 商談ID（オプション）
        
        Returns:
            送信結果（success: bool, message: str, error: Optional[str]）
        """
        if not self.enabled:
            print("⚠️ LINE_CHANNEL_ACCESS_TOKENが設定されていません。LINE通知をスキップします。")
            return {"success": False, "error": "LINE設定が不完全です"}
        
        if not line_user_id:
            print("⚠️ 顧客のLINEユーザーIDが設定されていません。")
            return {"success": False, "error": "LINEユーザーIDが設定されていません"}
        
        message = self._build_customer_message(customer_name, partner_name, deal_id)
        
        return self._send_notification(line_user_id, message)
    
    def send_deal_notification(
        self,
        line_user_id: str,
        deal_info: Dict[str, any],
        image_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        商談通知を送信
        
        Args:
            line_user_id: LINEユーザーID
            deal_info: 商談情報
            image_urls: 画像URLリスト（オプション）
        
        Returns:
            送信結果
        """
        if not self.enabled:
            print("⚠️ LINE_CHANNEL_ACCESS_TOKENが設定されていません。LINE通知をスキップします。")
            return {"success": False, "error": "LINE設定が不完全です"}
        
        message = self._build_deal_message(deal_info)
        
        return self._send_notification(line_user_id, message, image_urls)
    
    def send_progress_report_notification(
        self,
        line_user_id: str,
        customer_name: str,
        partner_name: str,
        progress_message: str,
        report_count: int,
        deal_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        経過報告通知を送信

        Args:
            line_user_id: 顧客のLINEユーザーID
            customer_name: 顧客名
            partner_name: 修理店名
            progress_message: 経過報告メッセージ
            report_count: 報告回数（1または2）
            deal_id: 商談ID（オプション）

        Returns:
            送信結果
        """
        if not self.enabled:
            print("⚠️ LINE_CHANNEL_ACCESS_TOKENが設定されていません。LINE通知をスキップします。")
            return {"success": False, "error": "LINE設定が不完全です"}
        
        if not line_user_id:
            print("⚠️ 顧客のLINEユーザーIDが設定されていません。")
            return {"success": False, "error": "LINEユーザーIDが設定されていません"}
        
        message = self._build_progress_report_message(
            customer_name, partner_name, progress_message, report_count, deal_id
        )
        
        return self._send_notification(line_user_id, message)
    
    def _build_progress_report_message(
        self,
        customer_name: str,
        partner_name: str,
        progress_message: str,
        report_count: int,
        deal_id: Optional[str] = None
    ) -> str:
        """経過報告通知メッセージを構築"""
        deal_info = f"\n【商談ID】\n{deal_id}\n" if deal_id else ""
        
        return f"""🔧 修理経過報告 #{report_count}

{customer_name} 様

お世話になっております。
{partner_name}です。

{deal_info}
【経過報告】
{progress_message}

引き続き修理を進めてまいります。
ご不明な点がございましたら、お気軽にお問い合わせください。

---
{partner_name}
岡山キャンピングカー修理サポートセンター
https://camper-repair.net/
"""
    
    def _build_partner_message(self, partner_name: str, customer_info: Dict) -> str:
        """修理店向けメッセージを構築"""
        return f"""🔔 新しい問い合わせが届きました

{partner_name} 様

お世話になっております。
岡山キャンピングカー修理サポートセンターです。

【顧客情報】
お名前: {customer_info.get('name', '')}
電話番号: {customer_info.get('phone', '')}
所在地: {customer_info.get('prefecture', '')}
メールアドレス: {customer_info.get('email', '未入力')}

【症状】
カテゴリ: {customer_info.get('category', '')}
詳細:
{customer_info.get('detail', '')}

お手数ですが、お客様へのご連絡をお願いいたします。

---
岡山キャンピングカー修理サポートセンター
https://camper-repair.net/
"""
    
    def _build_customer_message(self, customer_name: str, partner_name: str, deal_id: Optional[str] = None) -> str:
        """顧客向けメッセージを構築"""
        deal_info = f"\n【商談ID】\n{deal_id}\n" if deal_id else ""
        
        return f"""✅ 問い合わせを受け付けました

{customer_name} 様

お問い合わせいただきありがとうございます。
岡山キャンピングカー修理サポートセンターです。

以下の修理店にご連絡させていただきました。

【紹介修理店】
{partner_name}
{deal_info}
修理店より直接ご連絡がございますので、
今しばらくお待ちください。

ご不明な点がございましたら、お気軽にお問い合わせください。

---
岡山キャンピングカー修理サポートセンター
https://camper-repair.net/
"""
    
    def send_status_update_notification(
        self,
        line_user_id: str,
        customer_name: str,
        partner_name: str,
        status: str,
        deal_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        ステータス更新通知を送信

        Args:
            line_user_id: 顧客のLINEユーザーID
            customer_name: 顧客名
            partner_name: 修理店名
            status: ステータス（pending, contacted, completed, cancelled）
            deal_id: 商談ID（オプション）
            notes: 備考（オプション）

        Returns:
            送信結果
        """
        if not self.enabled:
            print("⚠️ LINE_CHANNEL_ACCESS_TOKENが設定されていません。LINE通知をスキップします。")
            return {"success": False, "error": "LINE設定が不完全です"}
        
        if not line_user_id:
            print("⚠️ 顧客のLINEユーザーIDが設定されていません。")
            return {"success": False, "error": "LINEユーザーIDが設定されていません"}
        
        message = self._build_status_update_message(
            customer_name, partner_name, status, deal_id, notes
        )
        
        return self._send_notification(line_user_id, message)
    
    def _build_status_update_message(
        self,
        customer_name: str,
        partner_name: str,
        status: str,
        deal_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """ステータス更新通知メッセージを構築"""
        # 日本語ステータスと英語ステータスのマッピング
        status_messages = {
            # 英語ステータス
            "pending": "⏳ 問い合わせを受付中",
            "contacted": "📞 修理店より連絡済み",
            "completed": "✅ 修理が完了しました",
            "cancelled": "❌ キャンセルされました",
            # 日本語ステータス（工場ダッシュボード用）
            "受付": "⏳ 問い合わせを受付中",
            "診断中": "🔍 診断を実施中です",
            "修理中": "🔧 修理を実施中です",
            "完了": "✅ 修理が完了しました",
            "キャンセル": "❌ キャンセルされました",
            # その他のステータス
            "連絡済み": "📞 修理店より連絡済み",
        }
        
        # ステータスメッセージを取得
        status_message = status_messages.get(status, f"📋 ステータスが更新されました（{status}）")
        
        # ステータスに応じた詳細メッセージ
        status_details = {
            "診断中": "現在、お客様のキャンピングカーの症状を詳しく診断しております。\n診断が完了次第、修理内容と見積もりをご連絡いたします。",
            "修理中": "現在、お客様のキャンピングカーの修理を実施しております。\n修理が完了次第、ご連絡いたします。",
            "完了": "修理が完了いたしました。\nお客様に直接ご連絡させていただきますので、今しばらくお待ちください。",
        }
        
        detail_message = status_details.get(status, "")
        deal_info = f"\n【商談ID】\n{deal_id}\n" if deal_id else ""
        notes_info = f"\n【備考】\n{notes}\n" if notes else ""
        
        return f"""{status_message}

{customer_name} 様

お世話になっております。
岡山キャンピングカー修理サポートセンターです。

{deal_info}
【修理店】
{partner_name}

{detail_message}

{notes_info}
ご不明な点がございましたら、お気軽にお問い合わせください。

---
岡山キャンピングカー修理サポートセンター
https://camper-repair.net/
"""
    
    def _build_deal_message(self, deal_info: Dict[str, Any]) -> str:
        """商談通知メッセージを構築"""
        deal_id = deal_info.get("deal_id", "")
        customer_name = deal_info.get("customer_name", "")
        phone = deal_info.get("phone", "")
        prefecture = deal_info.get("prefecture", "")
        symptom_category = deal_info.get("symptom_category", "")
        symptom_detail = deal_info.get("symptom_detail", "")
        
        return f"""🔔 新しい問い合わせが届きました

【商談ID】
{deal_id}

【お客様情報】
お名前: {customer_name}
電話番号: {phone}
所在地: {prefecture}

【症状】
カテゴリ: {symptom_category}
詳細: {symptom_detail}

工場ダッシュボードで詳細を確認してください。
"""
    
    def _send_notification(
        self,
        line_user_id: str,
        message: str,
        image_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        LINE通知を送信
        
        Args:
            line_user_id: LINEユーザーID
            message: 送信するメッセージ
            image_urls: 画像URLリスト（オプション）
        
        Returns:
            送信結果
        """
        try:
            if not self.channel_access_token:
                return {"success": False, "error": "LINE_CHANNEL_ACCESS_TOKENが設定されていません"}
            
            headers = {
                "Authorization": f"Bearer {self.channel_access_token}",
                "Content-Type": "application/json"
            }
            
            messages = []
            
            # テキストメッセージを追加
            messages.append({
                "type": "text",
                "text": message
            })
            
            # 画像メッセージを追加（画像URLがある場合）
            if image_urls:
                for image_url in image_urls:
                    messages.append({
                        "type": "image",
                        "originalContentUrl": image_url,
                        "previewImageUrl": image_url
                    })
            
            payload = {
                "to": line_user_id,
                "messages": messages
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            print(f"✅ LINE通知送信成功: {line_user_id}")
            return {
                "success": True,
                "message": "通知を送信しました"
            }
            
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', str(e))
                except:
                    error_message = e.response.text or str(e)
            
            print(f"❌ LINE通知送信失敗: {error_message}")
            print(f"   送信先: {line_user_id}")
            return {
                "success": False,
                "error": error_message
            }
        except Exception as e:
            print(f"❌ LINE通知送信エラー: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_review_request(
        self,
        line_user_id: str,
        customer_name: str,
        partner_name: str,
        deal_id: str,
        review_url: str
    ) -> Dict[str, Any]:
        """
        評価依頼LINE通知を送信
        
        Args:
            line_user_id: お客様のLINEユーザーID
            customer_name: お客様名
            partner_name: パートナー工場名
            deal_id: 商談ID
            review_url: 評価フォームへのURL
        
        Returns:
            送信結果（success: bool, message: str, error: Optional[str]）
        """
        if not self.enabled:
            print("⚠️ LINE_CHANNEL_ACCESS_TOKENが設定されていません。LINE通知をスキップします。")
            return {"success": False, "error": "LINE設定が不完全です"}
        
        if not line_user_id:
            print("⚠️ お客様のLINEユーザーIDが設定されていません。")
            return {"success": False, "error": "LINEユーザーIDが設定されていません"}
        
        # フロントエンドのURLを取得（環境変数から）
        base_url = os.environ.get("FRONTEND_URL", "https://camper-repair.net")
        full_review_url = f"{base_url}{review_url}"
        
        message = f"""⭐ 修理完了のご報告

{customer_name} 様

この度は、岡山キャンピングカー修理サポートセンターをご利用いただき、誠にありがとうございました。

修理が完了いたしましたので、お客様のご評価をお願いいたします。

【修理店】
{partner_name}

【商談ID】
{deal_id}

【評価フォーム】
以下のリンクから評価をお願いいたします。
{full_review_url}

評価内容：
・星評価（1〜5段階）
・コメント

評価は、今後のサービス改善に活用させていただきます。
また、他のお客様が修理店を選ぶ際の参考にもなります。

ご協力のほど、よろしくお願いいたします。

---
岡山キャンピングカー修理サポートセンター
https://camper-repair.net/
"""
        
        return self._send_notification(line_user_id, message)
    
    def send_repair_complete_to_customer(
        self,
        line_user_id: str,
        customer_name: str,
        partner_name: str,
        deal_id: str,
        repair_content: Optional[str] = None,
        deal_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        修理完了通知と支払い案内を送信
        
        Args:
            line_user_id: 顧客のLINEユーザーID
            customer_name: 顧客名
            partner_name: パートナー工場名
            deal_id: 商談ID
            repair_content: 修理内容（オプション）
            deal_amount: 修理代金（オプション）
        
        Returns:
            送信結果
        """
        if not self.enabled:
            print("⚠️ LINE_CHANNEL_ACCESS_TOKENが設定されていません。LINE通知をスキップします。")
            return {"success": False, "error": "LINE設定が不完全です"}
        
        if not line_user_id:
            print("⚠️ 顧客のLINEユーザーIDが設定されていません。")
            return {"success": False, "error": "LINEユーザーIDが設定されていません"}
        
        # 専用口座情報を環境変数から取得
        bank_name = os.environ.get("PAYMENT_BANK_NAME", "○○銀行")
        bank_branch = os.environ.get("PAYMENT_BANK_BRANCH", "○○支店")
        account_number = os.environ.get("PAYMENT_ACCOUNT_NUMBER", "1234567")
        account_name = os.environ.get("PAYMENT_ACCOUNT_NAME", "岡山キャンピングカー修理サポートセンター")
        
        repair_info = f"\n【修理内容】\n{repair_content}\n" if repair_content else ""
        amount_info = f"\n【修理代金】\n{deal_amount:,.0f}円\n" if deal_amount else ""
        
        message = f"""✅ 修理完了のお知らせ

{customer_name} 様

お世話になっております。
岡山キャンピングカー修理サポートセンターです。

修理が完了いたしましたので、ご報告いたします。

【商談ID】
{deal_id}

【修理店】
{partner_name}
{repair_info}{amount_info}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【支払い方法のご案内】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【建前上の支払い先】
パートナー工場（{partner_name}）への支払い
※ 請求書・領収書にはパートナー工場名を記載

【実際の入金先】
以下のサポートセンター専用口座にお振込みください。

銀行名: {bank_name}
支店名: {bank_branch}
口座種別: 普通
口座番号: {account_number}
口座名義: {account_name}

※ 修理代金全額を上記口座にお振込みください
※ 振込手数料はお客様のご負担となります

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ご不明な点がございましたら、お気軽にお問い合わせください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
岡山キャンピングカー修理サポートセンター
電話: 086-206-6622
メール: info@camper-repair.net
営業時間: 年中無休（9:00〜21:00）
https://camper-repair.net/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return self._send_notification(line_user_id, message)

