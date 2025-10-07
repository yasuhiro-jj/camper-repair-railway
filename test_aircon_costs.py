#!/usr/bin/env python3
"""
エアコン修理費用目安の表示テスト
"""

import sys
import os

# 現在のディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# app.pyから関数をインポート
from app import (
    is_aircon_related_query, 
    get_aircon_repair_costs,
    is_battery_related_query,
    get_battery_repair_costs,
    is_toilet_related_query,
    get_toilet_repair_costs,
    is_water_leak_related_query,
    get_water_leak_repair_costs,
    format_repair_advice_for_html
)

def test_aircon_detection():
    """エアコン関連クエリの検出テスト"""
    print("🔍 エアコン関連クエリの検出テスト")
    print("=" * 50)
    
    test_queries = [
        "エアコンが冷えない",
        "冷房が効かない",
        "暖房が暖まらない",
        "フィルターが汚れている",
        "リモコンが効かない",
        "温度調節ができない",
        "冷媒が漏れている",
        "コンプレッサーが動かない",
        "ACが故障した",
        "クーラーが壊れた",
        "ヒーターが効かない",
        "空調システムの故障"
    ]
    
    for query in test_queries:
        is_aircon = is_aircon_related_query(query)
        status = "✅ エアコン関連" if is_aircon else "❌ エアコン関連ではない"
        print(f"「{query}」 → {status}")

def test_other_detections():
    """その他の修理項目の検出テスト"""
    print("\n🔍 その他の修理項目の検出テスト")
    print("=" * 50)
    
    # バッテリーテスト
    battery_queries = ["バッテリーが上がった", "充電できない", "電圧が低い"]
    print("🔋 バッテリー関連:")
    for query in battery_queries:
        is_battery = is_battery_related_query(query)
        status = "✅ バッテリー関連" if is_battery else "❌ バッテリー関連ではない"
        print(f"「{query}」 → {status}")
    
    # トイレテスト
    toilet_queries = ["トイレが流れない", "水が漏れる", "ポンプが動かない"]
    print("\n🚽 トイレ関連:")
    for query in toilet_queries:
        is_toilet = is_toilet_related_query(query)
        status = "✅ トイレ関連" if is_toilet else "❌ トイレ関連ではない"
        print(f"「{query}」 → {status}")
    
    # 雨漏りテスト
    water_leak_queries = ["雨漏りしている", "水漏れがある", "シーリングが劣化"]
    print("\n🌧️ 雨漏り関連:")
    for query in water_leak_queries:
        is_water_leak = is_water_leak_related_query(query)
        status = "✅ 雨漏り関連" if is_water_leak else "❌ 雨漏り関連ではない"
        print(f"「{query}」 → {status}")

def test_repair_costs():
    """修理費用目安の表示テスト"""
    print("\n💰 修理費用目安の表示テスト")
    print("=" * 50)
    
    # エアコン修理費用
    print("❄️ エアコン修理費用目安:")
    aircon_costs = get_aircon_repair_costs()
    print(aircon_costs)
    
    print("\n🔋 バッテリー修理費用目安:")
    battery_costs = get_battery_repair_costs()
    print(battery_costs)
    
    print("\n🚽 トイレ修理費用目安:")
    toilet_costs = get_toilet_repair_costs()
    print(toilet_costs)
    
    print("\n🌧️ 雨漏り修理費用目安:")
    water_leak_costs = get_water_leak_repair_costs()
    print(water_leak_costs)

def test_format_function():
    """format_repair_advice_for_html関数のテスト"""
    print("\n🔧 format_repair_advice_for_html関数のテスト")
    print("=" * 50)
    
    test_queries = [
        "エアコンが冷えない",
        "バッテリーが上がった",
        "トイレが流れない",
        "雨漏りしている"
    ]
    
    for query in test_queries:
        print(f"\n📝 クエリ: 「{query}」")
        result = format_repair_advice_for_html(None, query)
        
        if result["results"]:
            for item in result["results"]:
                print(f"  📋 タイトル: {item['title']}")
                print(f"  📂 カテゴリ: {item['category']}")
                print(f"  🔗 ソース: {item['source']}")
                if 'repair_costs' in item:
                    print(f"  💰 修理費用目安:")
                    print(f"     {item['repair_costs'][:100]}...")
        else:
            print("  ❌ 結果が見つかりませんでした")

if __name__ == "__main__":
    print("🚀 エアコン修理費用目安の表示テストを開始")
    print("=" * 60)
    
    try:
        test_aircon_detection()
        test_other_detections()
        test_repair_costs()
        test_format_function()
        
        print("\n✅ すべてのテストが完了しました！")
        
    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
