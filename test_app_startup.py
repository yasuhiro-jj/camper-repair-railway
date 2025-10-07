#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アプリケーション起動テストスクリプト
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

def test_app_startup():
    """アプリケーションの起動テスト"""
    print("🔧 キャンピングカー修理AI アプリケーション起動テスト")
    print("=" * 50)
    
    # 現在のディレクトリを確認
    current_dir = Path.cwd()
    print(f"📁 現在のディレクトリ: {current_dir}")
    
    # app.pyの存在確認
    app_path = current_dir / "app.py"
    if not app_path.exists():
        print("❌ app.pyが見つかりません")
        return False
    
    print("✅ app.pyが見つかりました")
    
    # 依存関係の確認
    try:
        import flask
        import langchain_openai
        import langchain_chroma
        print("✅ 必要なライブラリがインストールされています")
    except ImportError as e:
        print(f"❌ 必要なライブラリが不足しています: {e}")
        print("pip install -r requirements.txt を実行してください")
        return False
    
    # 環境変数の確認
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("⚠️ OPENAI_API_KEYが設定されていません")
        print("環境変数を設定するか、config.pyで設定してください")
    else:
        print("✅ OPENAI_API_KEYが設定されています")
    
    # アプリケーションの起動テスト
    print("\n🚀 アプリケーション起動テスト中...")
    try:
        # バックグラウンドでアプリケーションを起動
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 少し待機
        time.sleep(3)
        
        # ヘルスチェック
        try:
            response = requests.get("http://localhost:5001/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ アプリケーションが正常に起動しました")
                print("🌐 http://localhost:5001 にアクセス可能です")
                
                # プロセスを終了
                process.terminate()
                return True
            else:
                print(f"❌ ヘルスチェック失敗: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ 接続エラー: {e}")
        
        # プロセスを終了
        process.terminate()
        
    except Exception as e:
        print(f"❌ アプリケーション起動エラー: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_app_startup()
    if success:
        print("\n🎉 テスト完了: アプリケーションは正常に動作します")
    else:
        print("\n❌ テスト失敗: アプリケーションの起動に問題があります")
        print("\n解決方法:")
        print("1. 環境変数を設定してください")
        print("2. pip install -r requirements.txt を実行してください")
        print("3. start_backend_local.bat を実行してください")