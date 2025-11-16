#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移行前バックアップスクリプト
Gitコミット + ファイルシステムバックアップの両方を実行
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """コマンドを実行"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def git_backup():
    """Gitでバックアップを作成"""
    print("=" * 60)
    print("📦 Gitバックアップ開始")
    print("=" * 60)
    
    # Gitの状態確認
    success, stdout, stderr = run_command("git status")
    if not success:
        print("⚠️ Gitリポジトリが見つかりません。Gitバックアップをスキップします。")
        return False
    
    print("\n📋 Gitの状態:")
    print(stdout)
    
    # 変更があるか確認
    if "nothing to commit" in stdout or "変更されていない" in stdout:
        print("\n✅ 変更はありません。Gitバックアップは不要です。")
        return True
    
    # バックアップブランチを作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_branch = f"backup/pre-migration-{timestamp}"
    
    print(f"\n🔄 バックアップブランチを作成: {backup_branch}")
    
    # 現在のブランチを確認
    success, current_branch, _ = run_command("git branch --show-current")
    if success:
        current_branch = current_branch.strip()
        print(f"📌 現在のブランチ: {current_branch}")
    
    # すべての変更をステージング
    print("\n📝 変更をステージング中...")
    success, stdout, stderr = run_command("git add -A")
    if not success:
        print(f"❌ git add に失敗: {stderr}")
        return False
    
    # コミット
    commit_message = f"移行前バックアップ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"\n💾 コミット中: {commit_message}")
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        if "nothing to commit" in stderr.lower():
            print("✅ コミットする変更がありません。")
            return True
        print(f"⚠️ コミットに失敗（既にコミット済みの可能性）: {stderr}")
    
    # バックアップブランチを作成
    print(f"\n🌿 バックアップブランチを作成: {backup_branch}")
    success, stdout, stderr = run_command(f"git checkout -b {backup_branch}")
    if success:
        print(f"✅ バックアップブランチ作成成功: {backup_branch}")
        
        # 元のブランチに戻る
        if current_branch:
            print(f"\n↩️ 元のブランチに戻る: {current_branch}")
            run_command(f"git checkout {current_branch}")
        
        return True
    else:
        print(f"⚠️ バックアップブランチ作成に失敗: {stderr}")
        return False

def file_backup():
    """ファイルシステムでバックアップを作成"""
    print("\n" + "=" * 60)
    print("📦 ファイルシステムバックアップ開始")
    print("=" * 60)
    
    # 既存のバックアップスクリプトを実行
    backup_script = Path(__file__).parent / "create_backup.py"
    if backup_script.exists():
        print(f"\n🔄 既存のバックアップスクリプトを実行: {backup_script}")
        success, stdout, stderr = run_command(f'python "{backup_script}"')
        if success:
            print(stdout)
            return True
        else:
            print(f"⚠️ バックアップスクリプトの実行に失敗: {stderr}")
            return False
    else:
        print("⚠️ バックアップスクリプトが見つかりません。")
        return False

def main():
    print("=" * 60)
    print("🚀 移行前バックアッププロセス開始")
    print("=" * 60)
    print(f"📅 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Gitバックアップ
    git_success = git_backup()
    
    # ファイルシステムバックアップ
    file_success = file_backup()
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 バックアップ結果サマリー")
    print("=" * 60)
    print(f"Gitバックアップ: {'✅ 成功' if git_success else '⚠️ スキップ/失敗'}")
    print(f"ファイルバックアップ: {'✅ 成功' if file_success else '⚠️ 失敗'}")
    
    if git_success or file_success:
        print("\n✅ バックアッププロセス完了")
        print("\n💡 次のステップ:")
        print("   1. バックアップが正常に作成されたことを確認")
        print("   2. フェーズ0（既存資産の棚卸し）を開始")
    else:
        print("\n⚠️ バックアップに問題があります。確認してください。")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

