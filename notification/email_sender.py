#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メール通知モジュール
- 修理店への通知
- 顧客への確認メール
- Resend API対応（優先）
- SendGrid API対応（フォールバック）
- SMTP対応（最終フォールバック）
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional

# Resend対応
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    print("⚠️ Resendがインストールされていません。")

# SendGrid対応
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("⚠️ SendGridがインストールされていません。")


class EmailSender:
    """メール送信クラス（Resend優先、SendGrid/SMTPフォールバック）"""
    
    def __init__(self):
        """初期化"""
        # Resend設定（最優先）
        self.resend_api_key = os.environ.get("RESEND_API_KEY")
        self.use_resend = RESEND_AVAILABLE and bool(self.resend_api_key)
        
        # SendGrid設定（フォールバック）
        self.sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
        self.use_sendgrid = SENDGRID_AVAILABLE and bool(self.sendgrid_api_key)
        
        # SMTP設定（最終フォールバック）
        self.smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER")
        self.smtp_password = os.environ.get("SMTP_PASSWORD")
        self.from_email = os.environ.get("FROM_EMAIL", self.smtp_user or "info@camper-repair.net")
        
        # Resend初期化
        if self.use_resend:
            resend.api_key = self.resend_api_key
        
        # メール送信が有効かどうか
        self.enabled = self.use_resend or self.use_sendgrid or bool(self.smtp_user and self.smtp_password)
        
        if self.use_resend:
            print("✅ Resend APIを使用してメールを送信します")
        elif self.use_sendgrid:
            print("✅ SendGrid APIを使用してメールを送信します")
        elif self.enabled:
            print("✅ SMTP経由でメールを送信します")
        else:
            print("⚠️ メール送信設定が不完全です")
    
    def send_to_partner(
        self, 
        partner_email: str,
        partner_name: str,
        customer_info: Dict
    ) -> bool:
        """
        修理店に問い合わせ通知を送信
        
        Args:
            partner_email: 修理店のメールアドレス
            partner_name: 修理店名
            customer_info: 顧客情報（name, phone, prefecture, category, detail）
        
        Returns:
            送信成功時True、失敗時False
        """
        if not self.enabled:
            print("⚠️ SMTP設定が不完全です。メール送信をスキップします。")
            return False
        
        if not partner_email:
            print("⚠️ 修理店のメールアドレスが設定されていません。")
            return False
        
        subject = "【新規問い合わせ】岡山キャンピングカー修理サポートセンター"
        
        body = f"""
{partner_name} 様

お世話になっております。
岡山キャンピングカー修理サポートセンターです。

新しい問い合わせが届きました。

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
        
        return self._send_email(partner_email, subject, body)
    
    def send_to_customer(
        self,
        customer_email: str,
        customer_name: str,
        partner_name: str
    ) -> bool:
        """
        顧客に確認メールを送信
        
        Args:
            customer_email: 顧客のメールアドレス
            customer_name: 顧客名
            partner_name: 紹介した修理店名
        
        Returns:
            送信成功時True、失敗時False
        """
        if not self.enabled:
            print("⚠️ SMTP設定が不完全です。メール送信をスキップします。")
            return False
        
        if not customer_email:
            print("⚠️ 顧客のメールアドレスが設定されていません。")
            return False
        
        subject = "【問い合わせ受付完了】岡山キャンピングカー修理サポートセンター"
        
        body = f"""
{customer_name} 様

お問い合わせいただきありがとうございます。
岡山キャンピングカー修理サポートセンターです。

以下の修理店にご連絡させていただきました。

【紹介修理店】
{partner_name}

修理店より直接ご連絡がございますので、
今しばらくお待ちください。

ご不明な点がございましたら、お気軽にお問い合わせください。

---
岡山キャンピングカー修理サポートセンター
https://camper-repair.net/
"""
        
        return self._send_email(customer_email, subject, body)
    
    def send_auto_reply_to_customer(
        self,
        customer_email: str,
        customer_name: str
    ) -> bool:
        """
        問い合わせ受付時の自動返信メールを送信（システムフロー図のステップ0に対応）
        
        Args:
            customer_email: 顧客のメールアドレス
            customer_name: 顧客名
        
        Returns:
            送信成功時True、失敗時False
        """
        if not self.enabled:
            print("⚠️ SMTP設定が不完全です。メール送信をスキップします。")
            return False
        
        if not customer_email:
            print("⚠️ 顧客のメールアドレスが設定されていません。")
            return False
        
        subject = "【自動返信】お問い合わせありがとうございます"
        
        # フロントエンドのURLを取得（環境変数から）
        base_url = os.environ.get("FRONTEND_URL", "https://camper-repair.net")
        
        body = f"""
{customer_name} 様

この度は、岡山キャンピングカー修理サポートセンターへ
お問い合わせいただき、誠にありがとうございます。

修理店の検索・問い合わせは、以下のページから
ご自身でお選びいただけます。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 修理店検索ページ
{base_url}/partner

💬 チャットボットで相談する
{base_url}/chat

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【修理店検索ページの使い方】
1. 都道府県と専門分野でフィルタ
2. 評価や実績を見て修理店を選択
3. 問い合わせフォームから修理店に直接連絡

【チャットボットの使い方】
1. 症状を入力してAI診断を受ける
2. 「修理店を紹介しますか？」と提案されたら「はい」を選択
3. 自動で修理店検索ページに遷移

ご不明な点がございましたら、お気軽にお問い合わせください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
岡山キャンピングカー修理サポートセンター
電話: 086-206-6622
メール: info@camper-repair.net
営業時間: 年中無休（9:00〜21:00）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return self._send_email(customer_email, subject, body)
    
    def send_progress_report_to_customer(
        self,
        customer_email: str,
        customer_name: str,
        partner_name: str,
        progress_message: str,
        report_count: int,
        deal_id: Optional[str] = None
    ) -> bool:
        """
        お客様に経過報告を送信

        Args:
            customer_email: 顧客のメールアドレス
            customer_name: 顧客名
            partner_name: 修理店名
            progress_message: 経過報告メッセージ
            report_count: 報告回数（1または2）
            deal_id: 商談ID（オプション）

        Returns:
            送信成功時True、失敗時False
        """
        if not self.enabled:
            print("⚠️ SMTP設定が不完全です。メール送信をスキップします。")
            return False

        if not customer_email:
            print("⚠️ 顧客のメールアドレスが設定されていません。")
            return False

        subject = f"【修理経過報告 #{report_count}】岡山キャンピングカー修理サポートセンター"
        
        deal_info = f"\n【商談ID】\n{deal_id}\n" if deal_id else ""

        body = f"""
{customer_name} 様

お世話になっております。
{partner_name}です。

修理の経過をご報告いたします。

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

        return self._send_email(customer_email, subject, body)
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        メール送信の実処理（Resend優先、SendGrid/SMTPフォールバック）
        
        Args:
            to_email: 送信先メールアドレス
            subject: 件名
            body: 本文
        
        Returns:
            送信成功時True、失敗時False
        """
        # Resend経由で送信（最優先）
        if self.use_resend:
            return self._send_via_resend(to_email, subject, body)
        
        # SendGrid経由で送信（フォールバック）
        if self.use_sendgrid:
            return self._send_via_sendgrid(to_email, subject, body)
        
        # SMTP経由で送信（最終フォールバック）
        return self._send_via_smtp(to_email, subject, body)
    
    def _send_via_resend(self, to_email: str, subject: str, body: str) -> bool:
        """
        Resend API経由でメール送信
        
        Args:
            to_email: 送信先メールアドレス
            subject: 件名
            body: 本文
        
        Returns:
            送信成功時True、失敗時False
        """
        try:
            if not self.resend_api_key:
                print("⚠️ RESEND_API_KEYが設定されていません。")
                return False
            
            params = {
                "from": f"岡山キャンピングカー修理サポートセンター <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "text": body,
            }
            
            response = resend.Emails.send(params)
            
            if response:
                print(f"✅ メール送信成功（Resend）: {to_email}")
                return True
            else:
                print(f"⚠️ Resend送信エラー")
                return False
            
        except Exception as e:
            print(f"❌ Resend送信失敗: {e}")
            print(f"   送信先: {to_email}")
            print(f"   件名: {subject}")
            # Resend失敗時はSendGridにフォールバック
            if self.use_sendgrid:
                print("   → SendGrid経由で再試行します")
                return self._send_via_sendgrid(to_email, subject, body)
            # SendGridも使えない場合はSMTPにフォールバック
            print("   → SMTP経由で再試行します")
            return self._send_via_smtp(to_email, subject, body)
    
    def _send_via_sendgrid(self, to_email: str, subject: str, body: str) -> bool:
        """
        SendGrid API経由でメール送信
        
        Args:
            to_email: 送信先メールアドレス
            subject: 件名
            body: 本文
        
        Returns:
            送信成功時True、失敗時False
        """
        try:
            if not self.sendgrid_api_key:
                print("⚠️ SENDGRID_API_KEYが設定されていません。")
                return False
            
            message = Mail(
                from_email=Email(self.from_email, "岡山キャンピングカー修理サポートセンター"),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", body)
            )
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ メール送信成功（SendGrid）: {to_email}")
                return True
            else:
                print(f"⚠️ SendGrid送信エラー（ステータス: {response.status_code}）")
                return False
            
        except Exception as e:
            print(f"❌ SendGrid送信失敗: {e}")
            print(f"   送信先: {to_email}")
            print(f"   件名: {subject}")
            # SendGrid失敗時はSMTPにフォールバック
            print("   → SMTP経由で再試行します")
            return self._send_via_smtp(to_email, subject, body)
    
    def _send_via_smtp(self, to_email: str, subject: str, body: str) -> bool:
        """
        SMTP経由でメール送信（フォールバック）
        
        Args:
            to_email: 送信先メールアドレス
            subject: 件名
            body: 本文
        
        Returns:
            送信成功時True、失敗時False
        """
        try:
            if not self.smtp_user or not self.smtp_password:
                print("⚠️ SMTP設定が不完全です。メール送信をスキップします。")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ メール送信成功（SMTP）: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP送信失敗: {e}")
            print(f"   送信先: {to_email}")
            print(f"   件名: {subject}")
            return False
    
    def send_status_update_to_customer(
        self,
        customer_email: str,
        customer_name: str,
        partner_name: str,
        status: str,
        deal_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        顧客にステータス更新通知を送信

        Args:
            customer_email: 顧客のメールアドレス
            customer_name: 顧客名
            partner_name: 紹介した修理店名
            status: ステータス（pending, contacted, completed, cancelled）
            deal_id: 商談ID（オプション）
            notes: 備考（オプション）

        Returns:
            送信成功時True、失敗時False
        """
        if not self.enabled:
            print("⚠️ SMTP設定が不完全です。メール送信をスキップします。")
            return False

        if not customer_email:
            print("⚠️ 顧客のメールアドレスが設定されていません。")
            return False

        status_messages = {
            "pending": "問い合わせを受付中",
            "contacted": "修理店より連絡済み",
            "completed": "修理が完了しました",
            "cancelled": "キャンセルされました"
        }
        
        status_message = status_messages.get(status, "ステータスが更新されました")
        subject = f"【{status_message}】岡山キャンピングカー修理サポートセンター"
        
        deal_info = f"\n【商談ID】\n{deal_id}\n" if deal_id else ""
        notes_info = f"\n【備考】\n{notes}\n" if notes else ""

        body = f"""
{customer_name} 様

お世話になっております。
岡山キャンピングカー修理サポートセンターです。

{status_message}のご連絡です。

{deal_info}
【修理店】
{partner_name}

{notes_info}
ご不明な点がございましたら、お気軽にお問い合わせください。

---
岡山キャンピングカー修理サポートセンター
https://camper-repair.net/
"""

        return self._send_email(customer_email, subject, body)
    
    def send_review_request(
        self,
        to_email: str,
        customer_name: str,
        partner_name: str,
        deal_id: str,
        review_url: str
    ) -> bool:
        """
        評価依頼メールを送信
        
        Args:
            to_email: お客様のメールアドレス
            customer_name: お客様名
            partner_name: パートナー工場名
            deal_id: 商談ID
            review_url: 評価フォームへのURL
        
        Returns:
            送信成功時True、失敗時False
        """
        if not self.enabled:
            print("⚠️ SMTP設定が不完全です。メール送信をスキップします。")
            return False
        
        if not to_email:
            print("⚠️ お客様のメールアドレスが設定されていません。")
            return False
        
        subject = "【ご評価のお願い】修理完了のご報告"
        
        # フロントエンドのURLを取得（環境変数から）
        base_url = os.environ.get("FRONTEND_URL", "https://camper-repair.net")
        full_review_url = f"{base_url}{review_url}"
        
        body = f"""
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
        
        return self._send_email(to_email, subject, body)
    
    def send_repair_complete_to_customer(
        self,
        customer_email: str,
        customer_name: str,
        partner_name: str,
        deal_id: str,
        repair_content: Optional[str] = None,
        deal_amount: Optional[float] = None
    ) -> bool:
        """
        修理完了通知と支払い案内を送信
        
        Args:
            customer_email: 顧客のメールアドレス
            customer_name: 顧客名
            partner_name: パートナー工場名
            deal_id: 商談ID
            repair_content: 修理内容（オプション）
            deal_amount: 修理代金（オプション）
        
        Returns:
            送信成功時True、失敗時False
        """
        if not self.enabled:
            print("⚠️ SMTP設定が不完全です。メール送信をスキップします。")
            return False
        
        if not customer_email:
            print("⚠️ 顧客のメールアドレスが設定されていません。")
            return False
        
        subject = "【修理完了のお知らせ】岡山キャンピングカー修理サポートセンター"
        
        # 専用口座情報を環境変数から取得
        bank_name = os.environ.get("PAYMENT_BANK_NAME", "○○銀行")
        bank_branch = os.environ.get("PAYMENT_BANK_BRANCH", "○○支店")
        account_number = os.environ.get("PAYMENT_ACCOUNT_NUMBER", "1234567")
        account_name = os.environ.get("PAYMENT_ACCOUNT_NAME", "岡山キャンピングカー修理サポートセンター")
        
        repair_info = f"\n【修理内容】\n{repair_content}\n" if repair_content else ""
        amount_info = f"\n【修理代金】\n{deal_amount:,.0f}円\n" if deal_amount else ""
        
        body = f"""
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
※ 請求書・領収書にはパートナー工場名を記載いたします

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
        
        return self._send_email(customer_email, subject, body)

