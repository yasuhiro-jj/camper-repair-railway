#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import requests
from urllib.parse import urlparse
import time

def extract_urls_from_file(file_path):
    """ファイルからURLを抽出"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # URLパターンを検索
        url_pattern = r'https://camper-repair\.net/[^\s,]+'
        urls = re.findall(url_pattern, content)
        
        return urls
    except Exception as e:
        print(f"ファイル読み込みエラー {file_path}: {e}")
        return []

def validate_url(url):
    """URLの適正性をチェック"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "URL形式が不正です"
        
        if parsed.scheme != 'https':
            return False, "HTTPSではありません"
        
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
    print("=== テキストファイルからURL抽出・チェック ===\n")
    
    # テキストファイルのリスト
    text_files = [
        "インバーター.txt",
        "バッテリー.txt", 
        "水道ポンプ.txt",
        "冷蔵庫.txt",
        "車体外装の破損.txt",
        "ウインドウ.txt",
        "排水タンク.txt",
        "雨漏り.txt",
        "外部電源.txt",
        "家具.txt",
        "ルーフベント　換気扇.txt",
        "電装系.txt",
        "FFヒーター.txt",
        "ガスコンロ.txt",
        "トイレ.txt",
        "室内LED.txt",
        "ソーラーパネル.txt",
        "異音.txt"
    ]
    
    all_urls = set()  # 重複を避けるためsetを使用
    
    print("1. ファイルからURL抽出")
    print("-" * 50)
    
    for file_name in text_files:
        if os.path.exists(file_name):
            urls = extract_urls_from_file(file_name)
            if urls:
                print(f"📄 {file_name}: {len(urls)}個のURLを発見")
                all_urls.update(urls)
            else:
                print(f"📄 {file_name}: URLなし")
        else:
            print(f"❌ {file_name}: ファイルが見つかりません")
    
    print(f"\n合計: {len(all_urls)}個のユニークなURLを発見")
    
    if not all_urls:
        print("URLが見つかりませんでした。")
        return
    
    print("\n2. URL形式チェック")
    print("-" * 50)
    
    valid_urls = []
    for url in sorted(all_urls):
        is_valid, message = validate_url(url)
        status = "✅" if is_valid else "❌"
        print(f"{status} {url}")
        if is_valid:
            valid_urls.append(url)
    
    print(f"\n有効なURL: {len(valid_urls)}/{len(all_urls)}")
    
    if not valid_urls:
        print("有効なURLが見つかりませんでした。")
        return
    
    print("\n3. アクセス可能性チェック（最初の5個のみ）")
    print("-" * 50)
    print("注意: 時間短縮のため最初の5個のみテストします")
    
    for i, url in enumerate(valid_urls[:5], 1):
        print(f"テスト中... {i}. {url}")
        is_accessible, message = test_url_accessibility(url)
        status = "✅" if is_accessible else "❌"
        print(f"{status} 結果: {message}")
        print()
        time.sleep(1)
    
    print("=== チェック完了 ===")
    print("✅: 適正/アクセス可能")
    print("❌: 不適正/アクセス不可")

if __name__ == "__main__":
    main()
