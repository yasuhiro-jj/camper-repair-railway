#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
緊急用サーバー - 最もシンプルなFlaskサーバー
"""

try:
    from flask import Flask, jsonify
    print("✅ Flask import成功")
except ImportError as e:
    print(f"❌ Flask import失敗: {e}")
    print("解決法: pip install flask")
    exit(1)

import socket
import sys
import os

def check_port(port):
    """ポートの使用状況を確認"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def find_available_port():
    """利用可能なポートを検索"""
    for port in [5001, 5002, 8000, 8080, 9000]:
        if not check_port(port):
            return port
    return None

# Flask アプリケーション作成
app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>緊急サーバーテスト</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>✅ サーバー接続成功！</h1>
        <p>緊急サーバーが正常に動作しています。</p>
        <p>現在時刻: """ + str(__import__('datetime').datetime.now()) + """</p>
        <p><a href="/test">テストページ</a></p>
        <p><a href="/api">APIテスト</a></p>
    </body>
    </html>
    """

@app.route("/test")
def test():
    return """
    <html>
    <head>
        <title>テストページ</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>🔍 テストページ</h1>
        <p>このページが表示されれば、サーバーは正常に動作しています。</p>
        <p>Python バージョン: """ + sys.version + """</p>
        <p>作業ディレクトリ: """ + os.getcwd() + """</p>
        <p><a href="/">ホームに戻る</a></p>
    </body>
    </html>
    """

@app.route("/api")
def api():
    return jsonify({
        "status": "success",
        "message": "緊急サーバーAPI正常動作",
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "timestamp": str(__import__('datetime').datetime.now())
    })

if __name__ == "__main__":
    print("🚨 緊急サーバーを起動中...")
    print("=" * 50)
    
    # ポート検索
    port = find_available_port()
    if port is None:
        print("❌ 利用可能なポートが見つかりません")
        print("使用中のポート: 5001, 5002, 8000, 8080, 9000")
        exit(1)
    
    print(f"✅ ポート {port} を使用して起動します")
    print(f"🌐 アクセスURL: http://localhost:{port}")
    print(f"🔍 テストURL: http://localhost:{port}/test")
    print(f"📡 API URL: http://localhost:{port}/api")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='127.0.0.1', port=port, threaded=True)
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        print("\n🔧 対処法:")
        print("1. 管理者権限でAnacondaプロンプトを実行")
        print("2. WindowsファイアウォールでPythonを許可")
        print("3. ウイルス対策ソフトを一時的に無効化")
        print("4. 別のポートを試す")
