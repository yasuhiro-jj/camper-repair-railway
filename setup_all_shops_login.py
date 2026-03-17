#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHOP-001〜004, ADMIN-001 にログイン用の認証情報を一括設定
実行後、README記載のログインID・パスワードで工場ダッシュボードにログインできます。
"""

import os
from dotenv import load_dotenv
from create_factory_account import update_existing_factory_account
from data_access.partner_shop_manager import PartnerShopManager

load_dotenv()

# アカウント設定（README・工場用・管理者用アクセス方法.md と一致）
ACCOUNTS = [
    {"shop_id": "SHOP-001", "login_id": "shop001", "password": "Shop001Pass!", "role": "factory"},
    {"shop_id": "SHOP-002", "login_id": "shop002", "password": "Shop002Pass!", "role": "factory"},
    {"shop_id": "SHOP-003", "login_id": "shop003", "password": "Shop003Pass!", "role": "factory"},
    {"shop_id": "SHOP-004", "login_id": "shop004", "password": "Shop004Pass!", "role": "factory"},
    {"shop_id": "ADMIN-001", "login_id": "admin001", "password": "Admin001Pass!", "role": "admin"},
]


def main():
    print("=" * 60)
    print("工場・管理者アカウント ログイン設定（一括）")
    print("=" * 60)

    manager = PartnerShopManager()
    success_count = 0

    for acc in ACCOUNTS:
        shop_id = acc["shop_id"]
        login_id = acc["login_id"]
        password = acc["password"]
        role = acc["role"]

        shop = manager.get_shop(shop_id)
        if not shop:
            print(f"⏭️  {shop_id}: Notionに存在しません（スキップ）")
            continue

        page_id = shop.get("page_id")
        shop_name = shop.get("name", "不明")
        print(f"\n📌 {shop_id} ({shop_name})")
        print(f"   ログインID: {login_id} / パスワード: {password}")

        result = update_existing_factory_account(
            factory_page_id=page_id,
            login_id=login_id,
            password=password,
            role=role
        )

        if result:
            print(f"   ✅ 設定完了")
            success_count += 1
        else:
            print(f"   ❌ 設定失敗")

    print()
    print("=" * 60)
    print(f"完了: {success_count}/{len(ACCOUNTS)} 件設定")
    print("=" * 60)
    print()
    print("本番URL: https://camper-repair-railway-upoj.vercel.app/factory/login")
    print()


if __name__ == "__main__":
    main()
