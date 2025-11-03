#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
プロジェクトバックアップスクリプト
重要なファイルをバックアップフォルダにコピーします
"""

import os
import shutil
import datetime
from pathlib import Path

# バックアップ先のディレクトリ
BACKUP_DIR = Path.home() / "Desktop" / "camper-repair-backups"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = BACKUP_DIR / f"backup_{TIMESTAMP}"

# プロジェクトのルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.resolve()

# バックアップ対象のファイル・ディレクトリ（相対パス）
BACKUP_TARGETS = [
    # 主要なPythonファイル
    "unified_backend_api.py",
    "save_to_notion.py",
    "repair_category_manager.py",
    "serp_search_system.py",
    "repair_advice_api.py",
    
    # データアクセスモジュール
    "data_access/",
    
    # 設定ファイル
    "requirements.txt",
    "requirements_railway.txt",
    "requirements_deploy.txt",
    "requirements_no_chroma.txt",
    "railway.json",
    "Procfile",
    "env.example",
    "railway_env_example.txt",
    "category_definitions.json",
    
    # フロントエンド
    "templates/",
    "static/",
    "repair_advice_center.html",
    
    # 知識ベース（テキストファイル）
    "*.txt",
    
    # ドキュメント
    "README.md",
    "RAILWAY_DEPLOY_GUIDE.md",
    "*.md",
]

# 除外するパターン
EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
    ".pyo",
    ".pyd",
    ".env",
    ".env.local",
    "chroma_db",
    "venv",
    "env",
    "ENV",
    ".git",
    "cache.db",
    "*.log",
    "node_modules",
    ".vscode",
    ".idea",
    "*.swp",
    "*.swo",
    "Thumbs.db",
    "Desktop.ini",
    ".DS_Store",
]

def should_exclude(path: Path) -> bool:
    """ファイル/ディレクトリを除外すべきか判定"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False

def copy_file(src: Path, dst: Path):
    """ファイルをコピー"""
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  ✅ {src.name}")
    except Exception as e:
        print(f"  ❌ {src.name}: {e}")

def copy_directory(src: Path, dst: Path):
    """ディレクトリを再帰的にコピー（除外パターンを適用）"""
    try:
        for root, dirs, files in os.walk(src):
            # 除外ディレクトリを削除
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
            
            for file in files:
                src_file = Path(root) / file
                if should_exclude(src_file):
                    continue
                
                rel_path = src_file.relative_to(src)
                dst_file = dst / rel_path
                
                try:
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dst_file)
                except Exception as e:
                    print(f"  ❌ {rel_path}: {e}")
        print(f"  ✅ {src.name}/")
    except Exception as e:
        print(f"  ❌ {src.name}/: {e}")

def main():
    print("=" * 60)
    print("📦 プロジェクトバックアップ開始")
    print("=" * 60)
    print(f"\n📁 バックアップ先: {BACKUP_PATH}")
    print(f"📂 プロジェクトルート: {PROJECT_ROOT}")
    
    # バックアップディレクトリを作成
    BACKUP_PATH.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    skipped_count = 0
    
    print("\n🔄 ファイルをコピー中...")
    
    # バックアップ対象を処理
    for target in BACKUP_TARGETS:
        src_path = PROJECT_ROOT / target
        
        if not src_path.exists():
            print(f"  ⚠️ {target}: 見つかりません")
            skipped_count += 1
            continue
        
        if src_path.is_file():
            if should_exclude(src_path):
                print(f"  ⏭️ {target}: 除外対象")
                skipped_count += 1
                continue
            
            dst_path = BACKUP_PATH / target
            copy_file(src_path, dst_path)
            copied_count += 1
        
        elif src_path.is_dir():
            if should_exclude(src_path):
                print(f"  ⏭️ {target}: 除外対象")
                skipped_count += 1
                continue
            
            dst_path = BACKUP_PATH / target
            copy_directory(src_path, dst_path)
            copied_count += 1
        
        elif "*" in target:
            # ワイルドカードパターン
            pattern = target.replace("*", "")
            for file_path in PROJECT_ROOT.glob(target):
                if should_exclude(file_path):
                    continue
                rel_path = file_path.relative_to(PROJECT_ROOT)
                dst_path = BACKUP_PATH / rel_path
                copy_file(file_path, dst_path)
                copied_count += 1
    
    # バックアップ情報を保存
    backup_info = {
        "timestamp": TIMESTAMP,
        "backup_path": str(BACKUP_PATH),
        "project_root": str(PROJECT_ROOT),
        "copied_count": copied_count,
        "skipped_count": skipped_count,
    }
    
    info_file = BACKUP_PATH / "backup_info.txt"
    with open(info_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("バックアップ情報\n")
        f.write("=" * 60 + "\n")
        f.write(f"作成日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"バックアップパス: {BACKUP_PATH}\n")
        f.write(f"プロジェクトルート: {PROJECT_ROOT}\n")
        f.write(f"コピーしたファイル数: {copied_count}\n")
        f.write(f"スキップしたファイル数: {skipped_count}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("除外したパターン:\n")
        for pattern in EXCLUDE_PATTERNS:
            f.write(f"  - {pattern}\n")
    
    print("\n" + "=" * 60)
    print("✅ バックアップ完了")
    print("=" * 60)
    print(f"\n📊 統計:")
    print(f"  - コピーしたファイル数: {copied_count}")
    print(f"  - スキップしたファイル数: {skipped_count}")
    print(f"\n📁 バックアップ先: {BACKUP_PATH}")
    print(f"\n💡 バックアップ情報: {info_file}")

if __name__ == "__main__":
    main()

