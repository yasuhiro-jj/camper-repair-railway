#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修理専門アドバイスセンターの起動確認スクリプト
"""

import requests
import time
import webbrowser
import subprocess
import sys
import os

def check_server_status():
    """サーバーの状態をチェック"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=3)
        if response.status_code == 200:
            print("✅ サーバーは正常に動作しています")
            return True
        else:
            print(f"⚠️ サーバーが応答しません (ステータス: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ サーバーに接続できません: {e}")
        return False

def start_server():
    """サーバーを起動"""
    print("🚀 修理専門アドバイスセンターを起動中...")
    
    # バッチファイルが存在するかチェック
    if os.path.exists('start_repair_center.bat'):
        print("📁 バッチファイルを使用して起動します...")
        try:
            # バッチファイルを新しいウィンドウで起動
            subprocess.Popen(['cmd', '/c', 'start_repair_center.bat'], shell=True)
        except Exception as e:
            print(f"⚠️ バッチファイルの起動に失敗: {e}")
            print("🐍 Pythonスクリプトを直接起動します...")
            subprocess.Popen([sys.executable, 'repair_center_api.py'])
    else:
        print("🐍 Pythonスクリプトを直接起動します...")
        subprocess.Popen([sys.executable, 'repair_center_api.py'])
    
    # サーバー起動を待機
    print("⏳ サーバー起動を待機中...")
    for i in range(30):  # 30秒待機
        time.sleep(1)
        if check_server_status():
            break
        if i % 5 == 0:  # 5秒ごとに進捗表示
            print(f"   待機中... ({i+1}/30)")
    else:
        print("❌ サーバーの起動に失敗しました")
        return False
    
    return True

def open_browser():
    """ブラウザでページを開く"""
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 ブラウザでページを開きました")
        return True
    except Exception as e:
        print(f"❌ ブラウザの起動に失敗しました: {e}")
        return False

def main():
    print("🔧 修理専門アドバイスセンター 起動確認ツール")
    print("=" * 50)
    
    # サーバー状態をチェック
    if check_server_status():
        print("✅ サーバーは既に起動しています")
        open_browser()
    else:
        print("❌ サーバーが起動していません")
        
        # サーバーを起動
        if start_server():
            print("✅ サーバーの起動に成功しました")
            open_browser()
        else:
            print("❌ サーバーの起動に失敗しました")
            print("\n📋 手動起動方法:")
            print("1. start_repair_center.bat をダブルクリック")
            print("2. または python repair_center_api.py を実行")
            print("3. ブラウザで http://localhost:5000 にアクセス")
    
    print("\n🔗 アクセスURL:")
    print("   http://localhost:5000")
    print("\n⏹️  サーバーを停止するには Ctrl+C を押してください")

if __name__ == '__main__':
    main()
    input("\nEnterキーを押して終了...")
