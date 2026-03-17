#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHOP-002（東京モバイル修理センター）にログイン用の認証情報を設定
実行後、指定したログインID・パスワードで工場ダッシュボードにログインできます。
"""

import os
from dotenv import load_dotenv
from create_factory_account import update_existing_factory_account
from data_access.partner_shop_manager import PartnerShopManager

load_dotenv()

def main():
    print("=" * 60)
    print("SHOP-002（東京モバイル修理センター）ログイン設定")
    print("=" * 60)
    
    manager = PartnerShopManager()
    shop = manager.get_shop("SHOP-002")
    
    if not shop:
        print("❌ SHOP-002 が見つかりません。NotionパートナーDBを確認してください。")
        return
    
    page_id = shop.get("page_id")
    shop_name = shop.get("name", "不明")
    print(f"✅ 対象: {shop_name} (page_id: {page_id})")
    print()
    
    # ログインID・パスワードを設定（必要に応じて変更してください）
    login_id = "shop002"  # ログインID
    password = "Shop002Pass!"  # パスワード（8文字以上、大文字・小文字・数字を含む）
    
    print(f"設定する認証情報:")
    print(f"  ログインID: {login_id}")
    print(f"  パスワード: {password}")
    print()
    
    result = update_existing_factory_account(
        factory_page_id=page_id,
        login_id=login_id,
        password=password,
        role="factory"
    )
    
    if result:
        print()
        print("=" * 60)
        print("✅ 設定完了！")
        print("=" * 60)
        print()
        print("以下の情報でログインできます:")
        print(f"  URL: http://localhost:3000/factory/login")
        print(f"  ログインID: {login_id}")
        print(f"  パスワード: {password}")
        print()
        print("※ パスワードを変更する場合は、このスクリプトの")
        print("  login_id と password を編集して再実行してください。")
    else:
        print("❌ 設定に失敗しました。")

if __name__ == "__main__":
    main()
