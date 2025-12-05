#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診断データをNotionからエクスポートしてJSONに保存
既存のunified_backend_api.pyを使用してデータを取得
"""

import json
import sys
from datetime import datetime

# UTF-8エンコーディングを設定
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print("=" * 60)
print("診断データのエクスポート")
print("=" * 60)
print()

# 既存のシステムから診断データを取得
try:
    print("[1/4] モジュールをインポート中...")
    from unified_backend_api import load_notion_diagnostic_data, initialize_services
    print("      OK: モジュールのインポート成功\n")
    
    print("[2/4] Notionクライアントを初期化中...")
    initialize_services()
    print("      OK: クライアント初期化完了\n")
    
    print("[3/4] 診断データを取得中...")
    diagnostic_data = load_notion_diagnostic_data(force_reload=True)
    
    if not diagnostic_data:
        print("      ERROR: 診断データが取得できませんでした")
        exit(1)
    
    nodes = diagnostic_data.get("nodes", [])
    print(f"      OK: {len(nodes)}件のノードを取得しました\n")
    
    print("[4/4] JSONファイルに保存中...")
    filename = f"diagnostic_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(diagnostic_data, f, ensure_ascii=False, indent=2)
    print(f"      OK: 保存完了: {filename}\n")
    
    # 簡易統計を表示
    print("=" * 60)
    print("簡易統計")
    print("=" * 60)
    print(f"総ノード数: {len(nodes)}")
    
    categories = {}
    for node in nodes:
        category = node.get("category", "不明")
        if category:
            categories[category] = categories.get(category, 0) + 1
    
    if categories:
        print("\nカテゴリ別ノード数:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {category}: {count}件")
    
    print("\n" + "=" * 60)
    print("エクスポート完了！")
    print("=" * 60)
    print(f"\nこのファイルを使って分析を実行できます:")
    print(f"  python analyze_diagnostic_flow.py {filename}")

except Exception as e:
    print(f"\nERROR: エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
