#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIキー設定ガイド
"""

def setup_guide():
    print("=== APIキー設定ガイド ===")
    print()
    print("以下の手順でAPIキーを設定してください：")
    print()
    print("1. .envファイルを作成")
    print("   python create_env_file.py")
    print()
    print("2. .envファイルを開いて編集")
    print("   - your_openai_api_key_here を実際のAPIキーに変更")
    print("   - sk-で始まる形式であることを確認")
    print()
    print("3. 設定を確認")
    print("   python verify_setup.py")
    print()
    print("=== 必要なAPIキー ===")
    print("• OpenAI APIキー（必須）")
    print("  - https://platform.openai.com/account/api-keys")
    print("  - sk-で始まる形式")
    print()
    print("• SERP APIキー（オプション）")
    print("  - 検索機能用")
    print()
    print("• Notion APIキー（オプション）")
    print("  - データベース連携用")
    print()
    print("⚠️ 重要：.envファイルをGitにコミットしないでください")

if __name__ == "__main__":
    setup_guide()
