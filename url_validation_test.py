#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from urllib.parse import urlparse
import time

def validate_url(url):
    """URLの適正性をチェック"""
    try:
        # URLの形式チェック
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "URL形式が不正です"
        
        # HTTPSチェック
        if parsed.scheme != 'https':
            return False, "HTTPSではありません"
        
        # ドメインチェック
        if 'camper-repair.net' not in parsed.netloc:
            return False, "ドメインが不正です"
        
        return True, "URL形式は適正です"
        
    except Exception as e:
        return False, f"URL解析エラー: {e}"

def test_url_accessibility(url):
    """URLのアクセス可能性をテスト"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, f"アクセス可能 (ステータス: {response.status_code})"
        else:
            return False, f"アクセス不可 (ステータス: {response.status_code})"
            
    except requests.exceptions.Timeout:
        return False, "タイムアウト"
    except requests.exceptions.ConnectionError:
        return False, "接続エラー"
    except Exception as e:
        return False, f"エラー: {e}"

def main():
    print("=== URL適正性チェック ===\n")
    
    # テスト対象URL
    test_urls = [
        "https://camper-repair.net/blog/repair1/",
        "https://camper-repair.net/blog/risk1/",
        "https://camper-repair.net/battery-selection/",
        "https://camper-repair.net/blog/water-system/",
        "https://camper-repair.net/blog/electrical/",
        "https://camper-repair.net/blog/appliance/",
        "https://camper-repair.net/blog/gas-system/",
        "https://camper-repair.net/blog/body-repair/"
    ]
    
    print("1. URL形式チェック")
    print("-" * 50)
    
    for i, url in enumerate(test_urls, 1):
        is_valid, message = validate_url(url)
        status = "✅" if is_valid else "❌"
        print(f"{status} {i}. {url}")
        print(f"   結果: {message}")
        print()
    
    print("\n2. アクセス可能性チェック")
    print("-" * 50)
    print("注意: 実際のアクセステストは時間がかかる場合があります")
    
    for i, url in enumerate(test_urls, 1):
        print(f"テスト中... {i}. {url}")
        is_accessible, message = test_url_accessibility(url)
        status = "✅" if is_accessible else "❌"
        print(f"{status} 結果: {message}")
        print()
        time.sleep(1)  # サーバーに負荷をかけないよう待機
    
    print("=== チェック完了 ===")
    print("✅: 適正/アクセス可能")
    print("❌: 不適正/アクセス不可")

if __name__ == "__main__":
    main()
