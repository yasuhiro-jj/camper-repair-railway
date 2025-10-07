#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セキュアなAPIキー設定
"""

import os

def setup_secure():
    print("=== セキュアなAPIキー設定 ===")
    print()
    print("⚠️ 重要：ソースコードにAPIキーを直接記載しないでください")
    print()
    print("推奨される方法：")
    print("1. .envファイルを使用")
    print("2. 環境変数として設定")
    print("3. システム環境変数として設定")
    print()
    print("実行方法：")
    print("python create_safe_env.py")
    print()
    print("その後、.envファイルを編集してAPIキーを設定してください")

if __name__ == "__main__":
    setup_secure()
