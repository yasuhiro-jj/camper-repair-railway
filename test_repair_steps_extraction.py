#!/usr/bin/env python3
"""
修理手順と注意事項の抽出テスト
"""

import sys
import os

# 現在のディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# app.pyから関数をインポート
from app import (
    is_aircon_related_query,
    get_aircon_repair_costs,
    format_repair_advice_for_html
)

def test_aircon_content_extraction():
    """エアコン関連のコンテンツ抽出テスト"""
    print("🔍 エアコン関連のコンテンツ抽出テスト")
    print("=" * 60)
    
    # エアコン関連のクエリをテスト
    test_queries = [
        "エアコンが冷えない",
        "冷房が効かない", 
        "エアコンの異音がする",
        "リモコンが効かない",
        "エアコンの水漏れ"
    ]
    
    for query in test_queries:
        print(f"\n📝 クエリ: 「{query}」")
        print("-" * 40)
        
        # エアコン関連かどうかをチェック
        is_aircon = is_aircon_related_query(query)
        print(f"🔍 エアコン関連: {'✅ Yes' if is_aircon else '❌ No'}")
        
        if is_aircon:
            # 修理費用目安を取得
            costs = get_aircon_repair_costs()
            print(f"💰 修理費用目安（直接）:")
            print(f"   {costs[:100]}...")
            
            # format_repair_advice_for_html関数をテスト
            # 注意: 実際のRAG結果はNoneでテスト
            result = format_repair_advice_for_html(None, query)
            
            print(f"📊 結果の構造:")
            print(f"   - 成功: {result['success']}")
            print(f"   - 結果数: {len(result['results'])}")
            
            for i, item in enumerate(result['results']):
                print(f"   📋 結果 {i+1}:")
                print(f"      - タイトル: {item['title']}")
                print(f"      - カテゴリ: {item['category']}")
                print(f"      - ソース: {item['source']}")
                print(f"      - 関連度: {item['relevance']}")
                if 'repair_costs' in item:
                    print(f"      - 修理費用: {item['repair_costs'][:50]}...")
                if 'content' in item:
                    print(f"      - コンテンツ: {item['content'][:50]}...")

def test_expected_behavior():
    """期待される動作の説明"""
    print("\n🎯 期待される動作")
    print("=" * 60)
    print("""
エアコン関連のクエリ検索時の動作:

1. 💰 エアコン修理費用目安
   - 直接返される具体的な費用情報
   - 冷媒ガス補充: 15,000円〜30,000円
   - フィルター清掃・交換: 3,000円〜8,000円
   - など

2. 📄 テキストファイルからの情報 (RAGシステム経由)
   - エアコン.txtから抽出された詳細情報:
     * 詳細修理手順（トラブル箇所の特定、応急処置、本格修理）
     * 安全上の注意事項
     * 必要な工具・材料
     * 修理ケース例
     * 専門業者への相談目安

3. 🔗 関連ブログ記事 (RAGシステム経由)
   - エアコン修理に関するブログ記事のリンク
""")

if __name__ == "__main__":
    print("🚀 修理手順と注意事項の抽出テストを開始")
    print("=" * 60)
    
    try:
        test_aircon_content_extraction()
        test_expected_behavior()
        
        print("\n✅ テストが完了しました！")
        print("\n📋 まとめ:")
        print("- 修理費用目安: 直接返される")
        print("- 修理手順・注意事項: テキストファイルから抽出")
        print("- 両方が組み合わされて完全な修理アドバイスを提供")
        
    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
