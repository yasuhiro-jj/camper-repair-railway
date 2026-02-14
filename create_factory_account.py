#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工場アカウント作成スクリプト
Notionパートナー修理店DBに認証情報を設定
"""

import bcrypt
import os
from datetime import datetime
from dotenv import load_dotenv
from data_access.notion_client import notion_client

load_dotenv()

notion = notion_client.client
NOTION_PARTNER_DB_ID = os.getenv('NOTION_PARTNER_DB_ID') or os.getenv('PARTNER_SHOP_DB_ID') or os.getenv('PARTNER_DB_ID')

if not NOTION_PARTNER_DB_ID:
    print("❌ NOTION_PARTNER_DB_IDが設定されていません")
    exit(1)

# ハイフンを削除して正規化
NOTION_PARTNER_DB_ID = NOTION_PARTNER_DB_ID.replace("-", "").lower()


def hash_password(password: str) -> str:
    """パスワードをハッシュ化"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_factory_account(
    shop_id: str,
    factory_name: str,
    login_id: str,
    password: str,
    prefecture: str = '',
    role: str = 'factory'
):
    """
    工場アカウントを作成
    
    Args:
        shop_id: 店舗ID（タイトルプロパティ）
        factory_name: 店舗名（rich_text）
        login_id: ログインID（rich_text）
        password: パスワード（平文）
        prefecture: 所在地（都道府県）（select）
        role: ロール（factory/admin）
    """
    password_hash = hash_password(password)
    
    try:
        # Notionページを作成
        properties = {
            "店舗ID": {
                "title": [{"text": {"content": shop_id}}]
            },
            "店舗名": {
                "rich_text": [{"text": {"content": factory_name}}]
            },
            "ログインID": {
                "rich_text": [{"text": {"content": login_id}}]
            },
            "パスワードハッシュ": {
                "rich_text": [{"text": {"content": password_hash}}]
            },
            "ロール": {
                "select": {"name": role}
            },
            "アカウント有効": {
                "checkbox": True
            }
        }
        
        # 所在地（都道府県）が指定されている場合は追加
        if prefecture:
            properties["所在地（都道府県）"] = {
                "select": {"name": prefecture}
            }
        
        new_page = notion.pages.create(
            parent={"database_id": NOTION_PARTNER_DB_ID},
            properties=properties
        )
        
        print(f"✅ アカウント作成成功")
        print(f"店舗ID: {shop_id}")
        print(f"店舗名: {factory_name}")
        print(f"ログインID: {login_id}")
        print(f"パスワード: {password}")
        print(f"所在地（都道府県）: {prefecture}")
        print(f"ロール: {role}")
        print(f"ページID: {new_page['id']}")
        
        return new_page['id']
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def update_existing_factory_account(
    factory_page_id: str,
    login_id: str,
    password: str,
    role: str = 'factory',
    prefecture: str = None
):
    """
    既存の工場アカウントに認証情報を追加
    
    Args:
        factory_page_id: 工場のNotionページID
        login_id: ログインID
        password: パスワード（平文）
        role: ロール（factory/admin）
        prefecture: 所在地（都道府県）（オプション）
    """
    password_hash = hash_password(password)
    
    try:
        # Notionページを更新
        properties = {
            "ログインID": {
                "rich_text": [{"text": {"content": login_id}}]
            },
            "パスワードハッシュ": {
                "rich_text": [{"text": {"content": password_hash}}]
            },
            "ロール": {
                "select": {"name": role}
            },
            "アカウント有効": {
                "checkbox": True
            }
        }
        
        # 所在地（都道府県）が指定されている場合は追加
        if prefecture:
            properties["所在地（都道府県）"] = {
                "select": {"name": prefecture}
            }
        
        updated_page = notion.pages.update(
            page_id=factory_page_id,
            properties=properties
        )
        
        print(f"✅ アカウント更新成功")
        print(f"ページID: {factory_page_id}")
        print(f"ログインID: {login_id}")
        print(f"パスワード: {password}")
        
        return updated_page['id']
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    print("=" * 60)
    print("工場アカウント作成スクリプト")
    print("=" * 60)
    print()
    
    # テストアカウント作成
    print("1. テスト工場アカウントを作成中...")
    create_factory_account(
        shop_id='FACTORY-001',
        factory_name='テスト修理工場',
        login_id='factory001',
        password='Password123!',
        prefecture='東京都',
        role='factory'
    )
    print()
    
    # 管理者アカウント作成
    print("2. 管理者アカウントを作成中...")
    create_factory_account(
        shop_id='ADMIN-001',
        factory_name='システム管理者',
        login_id='admin',
        password='Admin123!',
        prefecture='東京都',
        role='admin'
    )
    print()
    
    print("=" * 60)
    print("完了")
    print("=" * 60)
    print()
    print("既存の工場に認証情報を追加する場合は、")
    print("update_existing_factory_account() 関数を使用してください。")
