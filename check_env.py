#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境変数設定確認スクリプト
.envファイルの設定状況を確認します
"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_env_var(name, required=True, min_length=None):
    """環境変数をチェック"""
    value = os.getenv(name)
    
    if not value:
        if required:
            print(f"[NG] {name}: 未設定（必須）")
            return False
        else:
            print(f"[WARN] {name}: 未設定（オプション）")
            return True
    
    if min_length and len(value) < min_length:
        print(f"[WARN] {name}: 設定済み（{len(value)}文字）ですが、{min_length}文字以上を推奨")
        return True
    
    # 機密情報は一部のみ表示
    if 'KEY' in name or 'SECRET' in name:
        display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
        print(f"[OK] {name}: 設定済み（{display_value}）")
    else:
        print(f"[OK] {name}: {value}")
    
    return True

def check_openai_key():
    """OPENAI_API_KEY を安全にチェック（全文は表示しない）"""
    name = "OPENAI_API_KEY"
    value = os.getenv(name)

    if not value:
        print(f"[NG] {name}: 未設定（必須）")
        return False

    raw = value
    # よくあるミス: 前後にクォート/空白/改行が混ざる
    trimmed = raw.strip().strip('"').strip("'").strip()
    if trimmed != raw:
        print(f"[WARN] {name}: 前後に空白/クォートが含まれている可能性があります（.env を見直してください）")
        value = trimmed

    # 形式の軽い検査（OpenAIキーは通常 sk- で始まる）
    looks_like_key = value.startswith("sk-") and len(value) >= 40
    if not value.startswith("sk-"):
        print(f"[WARN] {name}: 'sk-' で始まっていません（形式が怪しいです）")

    # 機密情報は一部のみ表示
    preview = f"{value[:10]}...{value[-5:]}" if len(value) > 20 else "***"
    print(f"[OK] {name}: 設定済み（{preview}）")
    print(f"   - 長さ: {len(value)} 文字")
    print(f"   - 先頭: {value[:7]}")

    # 目安情報
    if not looks_like_key:
        print("[WARN] 形式が不自然です。401(Unauthorized) が出る場合はキーが無効/コピーミスの可能性が高いです。")

    return True

def main():
    print("=" * 60)
    print("環境変数設定確認")
    print("=" * 60)
    print()
    
    # OpenAI 設定
    print("【OpenAI 設定】")
    openai_ok = check_openai_key()
    print()

    # JWT認証設定
    print("【JWT認証設定】")
    jwt_secret_ok = check_env_var('JWT_SECRET_KEY', required=True, min_length=32)
    check_env_var('JWT_ALGORITHM', required=False)
    check_env_var('JWT_EXPIRATION_HOURS', required=False)
    print()
    
    # メール通知設定
    print("【メール通知設定（Resend）】")
    resend_ok = check_env_var('RESEND_API_KEY', required=True)
    check_env_var('FROM_EMAIL', required=False)
    print()
    
    # SMTPフォールバック設定（オプション）
    print("【SMTPフォールバック設定（オプション）】")
    check_env_var('SMTP_HOST', required=False)
    check_env_var('SMTP_PORT', required=False)
    check_env_var('SMTP_USER', required=False)
    check_env_var('SMTP_PASSWORD', required=False)
    print()
    
    # Notion設定
    print("【Notion設定】")
    check_env_var('NOTION_API_KEY', required=True)
    check_env_var('NOTION_PARTNER_DB_ID', required=True)
    check_env_var('NOTION_DEAL_DB_ID', required=True)
    print()
    
    # 結果サマリー
    print("=" * 60)
    print("結果サマリー")
    print("=" * 60)
    
    if openai_ok and jwt_secret_ok and resend_ok:
        print("[OK] 必須環境変数がすべて設定されています")
        print()
        print("次のステップ:")
        print("1. バックエンドを起動して動作確認")
        print("2. python create_factory_account.py で初期アカウントを作成")
        print("3. テスト手順書に従ってテストを実行")
    else:
        print("[NG] 必須環境変数が不足しています")
        print()
        print("設定方法:")
        print("1. .env ファイルを作成（env.exampleをコピー）")
        print("2. 必要な環境変数を設定")
        print("3. 詳細は ENV_SETUP_GUIDE.md を参照")
    
    print()

if __name__ == '__main__':
    main()
