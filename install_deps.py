#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
必要な依存関係をインストールするスクリプト
"""

import subprocess
import sys

def install_package(package):
    """パッケージをインストール"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} のインストールが完了しました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} のインストールに失敗しました: {e}")
        return False

def main():
    """メイン処理"""
    print("🚀 必要な依存関係をインストール中...")
    
    packages = [
        "flask",
        "flask-cors",
        "requests",
        "python-dotenv"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 インストール結果: {success_count}/{len(packages)} 成功")
    
    if success_count == len(packages):
        print("✅ すべての依存関係のインストールが完了しました！")
        print("🌐 サーバーを起動できます")
    else:
        print("⚠️ 一部の依存関係のインストールに失敗しました")
        print("🔧 手動でインストールしてください")

if __name__ == "__main__":
    main()
