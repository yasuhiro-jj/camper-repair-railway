#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サーバー接続テスト用スクリプト
"""

import socket
import subprocess
import sys
import os
from datetime import datetime

def check_port_availability(port):
    """ポートの使用状況を確認"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            if result == 0:
                print(f"❌ ポート {port} は既に使用中です")
                return False
            else:
                print(f"✅ ポート {port} は利用可能です")
                return True
    except Exception as e:
        print(f"⚠️ ポート {port} チェックエラー: {e}")
        return False

def test_flask_installation():
    """Flaskのインストール状況を確認"""
    try:
        import flask
        print(f"✅ Flask {flask.__version__} がインストールされています")
        return True
    except ImportError:
        print("❌ Flaskがインストールされていません")
        return False

def create_minimal_server():
    """最小限のFlaskサーバーを作成"""
    server_code = '''
from flask import Flask, jsonify
import socket

app = Flask(__name__)

@app.route("/")
def hello():
    return jsonify({
        "message": "最小限サーバーが動作しています",
        "timestamp": "2024-01-01T00:00:00",
        "port": 5001
    })

@app.route("/test")
def test():
    return "テスト成功！"

if __name__ == "__main__":
    print("🚀 最小限サーバーを起動中...")
    print("🌐 アクセスURL: http://localhost:5001")
    print("🔍 テストURL: http://localhost:5001/test")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5001)
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        print("🔧 対処法:")
        print("1. ポート5001が使用中でないか確認")
        print("2. ファイアウォール設定を確認")
        print("3. 管理者権限で実行")
'''
    
    with open('minimal_server.py', 'w', encoding='utf-8') as f:
        f.write(server_code)
    
    print("📝 minimal_server.py を作成しました")

def main():
    print("🔍 サーバー接続診断を開始...")
    print("=" * 50)
    
    # 1. ポート確認
    print("1. ポート5001の使用状況を確認中...")
    port_available = check_port_availability(5001)
    
    # 2. Flask確認
    print("\n2. Flaskのインストール状況を確認中...")
    flask_installed = test_flask_installation()
    
    # 3. Python環境確認
    print("\n3. Python環境を確認中...")
    print(f"Python バージョン: {sys.version}")
    print(f"Python 実行パス: {sys.executable}")
    print(f"現在のディレクトリ: {os.getcwd()}")
    
    # 4. 最小限サーバー作成
    print("\n4. 最小限サーバーを作成中...")
    create_minimal_server()
    
    # 5. 診断結果
    print("\n" + "=" * 50)
    print("📋 診断結果:")
    
    if port_available and flask_installed:
        print("✅ 環境は正常です")
        print("\n🚀 次の手順:")
        print("1. Anacondaプロンプトを開く")
        print("2. プロジェクトディレクトリに移動")
        print("3. conda activate campingrepare")
        print("4. python minimal_server.py")
        print("5. ブラウザで http://localhost:5001 にアクセス")
    else:
        print("❌ 問題が検出されました")
        if not port_available:
            print("- ポート5001が使用中です")
        if not flask_installed:
            print("- Flaskがインストールされていません")
            print("  解決法: pip install flask")
    
    print("\n🔧 追加の対処法:")
    print("1. WindowsファイアウォールでPythonを許可")
    print("2. 管理者権限でAnacondaプロンプトを実行")
    print("3. 別のポート（5002, 8000, 8080）を試す")
    print("4. ウイルス対策ソフトを一時的に無効化")

if __name__ == "__main__":
    main()