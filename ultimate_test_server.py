#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
究極テストサーバー - 最もシンプルなHTTPサーバー
"""

import socket
import threading
import time
import sys
import os
from datetime import datetime

def create_simple_http_server(port):
    """最もシンプルなHTTPサーバーを作成"""
    try:
        # ソケットを作成
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', port))
        server_socket.listen(5)
        
        print(f"✅ サーバーがポート {port} で起動しました")
        print(f"🌐 アクセスURL: http://localhost:{port}")
        print(f"🌐 アクセスURL: http://127.0.0.1:{port}")
        print("=" * 50)
        
        while True:
            try:
                # クライアントからの接続を待機
                client_socket, address = server_socket.accept()
                print(f"📡 接続を受け付けました: {address}")
                
                # HTTPレスポンスを送信
                response = f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 500

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>🎉 接続成功！</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f8ff; }}
        .success {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 10px; }}
        .info {{ background: #e2e3e5; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="success">
        <h1>🎉 接続成功！</h1>
        <p>究極テストサーバーが正常に動作しています。</p>
        <p>現在時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>ポート: {port}</p>
        <p>Python バージョン: {sys.version.split()[0]}</p>
        <p>作業ディレクトリ: {os.getcwd()}</p>
    </div>
    
    <div class="info">
        <h3>🔧 次のステップ:</h3>
        <p>1. このページが表示されれば接続は成功です</p>
        <p>2. 修理アドバイスセンターの統合バックエンドを起動できます</p>
        <p>3. 検索機能のテストが可能です</p>
    </div>
    
    <div class="info">
        <h3>📋 利用可能なエンドポイント:</h3>
        <p>• <a href="/">ホームページ</a></p>
        <p>• <a href="/test">テストページ</a></p>
        <p>• <a href="/api">API情報</a></p>
    </div>
</body>
</html>"""

                client_socket.send(response.encode('utf-8'))
                client_socket.close()
                
            except Exception as e:
                print(f"⚠️ クライアント処理エラー: {e}")
                
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        return False
    finally:
        try:
            server_socket.close()
        except:
            pass

def find_available_port():
    """利用可能なポートを検索"""
    ports_to_try = [5001, 5002, 8000, 8080, 9000, 3000, 4000, 6000]
    
    for port in ports_to_try:
        try:
            # ポートが使用中かチェック
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)
            result = test_socket.connect_ex(('127.0.0.1', port))
            test_socket.close()
            
            if result != 0:  # 接続できない = ポートが空いている
                print(f"✅ ポート {port} が利用可能です")
                return port
            else:
                print(f"❌ ポート {port} は使用中です")
                
        except Exception as e:
            print(f"⚠️ ポート {port} チェックエラー: {e}")
    
    return None

def main():
    print("🚨 究極テストサーバーを起動中...")
    print("=" * 50)
    print("📋 システム情報:")
    print(f"Python バージョン: {sys.version}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    print(f"現在時刻: {datetime.now()}")
    print("=" * 50)
    
    # 利用可能なポートを検索
    port = find_available_port()
    if port is None:
        print("❌ 利用可能なポートが見つかりません")
        print("🔧 対処法:")
        print("1. 他のアプリケーションを終了してください")
        print("2. 管理者権限で実行してください")
        print("3. システムを再起動してください")
        return
    
    print(f"\n🚀 サーバーをポート {port} で起動中...")
    print("=" * 50)
    print("🌐 アクセス先:")
    print(f"   http://localhost:{port}")
    print(f"   http://127.0.0.1:{port}")
    print("=" * 50)
    print("⚠️ 注意: Ctrl+C でサーバーを停止できます")
    print("=" * 50)
    
    try:
        create_simple_http_server(port)
    except KeyboardInterrupt:
        print("\n\n🛑 サーバーを停止しました")
    except Exception as e:
        print(f"\n❌ サーバーエラー: {e}")
        print("🔧 対処法:")
        print("1. 管理者権限でAnacondaプロンプトを実行")
        print("2. WindowsファイアウォールでPythonを許可")
        print("3. ウイルス対策ソフトを一時的に無効化")

if __name__ == "__main__":
    main()
