#!/usr/bin/env python3
"""
費用目安抽出のテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import extract_cost_information, format_repair_advice_for_html
from enhanced_rag_system import enhanced_rag_retrieve, create_enhanced_rag_system

def test_cost_extraction():
    """費用目安抽出のテスト"""
    print("=== 費用目安抽出テスト ===")
    
    # RAGシステムの初期化
    try:
        db = create_enhanced_rag_system()
        print("✅ RAGシステム初期化成功")
    except Exception as e:
        print(f"❌ RAGシステム初期化エラー: {e}")
        return
    
    # エアコン関連の検索テスト
    query = "エアコン 修理 費用"
    print(f"\n🔍 検索クエリ: {query}")
    
    try:
        # RAG検索実行
        rag_results = enhanced_rag_retrieve(query, db, max_results=5)
        print(f"📊 RAG検索結果:")
        print(f"  - manual_content: {len(rag_results.get('manual_content', ''))}文字")
        print(f"  - text_file_content: {len(rag_results.get('text_file_content', ''))}文字")
        print(f"  - blog_links: {len(rag_results.get('blog_links', []))}件")
        
        # テキストファイル内容の確認
        if rag_results.get('text_file_content'):
            content = rag_results['text_file_content']
            print(f"\n📄 テキストファイル内容（最初の500文字）:")
            print(content[:500])
            
            # 費用目安情報の抽出テスト
            cost_info = extract_cost_information(content)
            print(f"\n💰 抽出された費用目安情報:")
            if cost_info:
                print(cost_info)
            else:
                print("❌ 費用目安情報が見つかりませんでした")
                
                # デバッグ: 費用目安セクションの検索
                import re
                cost_pattern = r'## 修理費用目安\s*\n(.*?)(?=\n##|\n\*\*|$)'
                cost_match = re.search(cost_pattern, content, re.DOTALL)
                if cost_match:
                    print("✅ 費用目安セクションが見つかりました")
                    print(f"内容: {cost_match.group(1)[:200]}...")
                else:
                    print("❌ 費用目安セクションが見つかりませんでした")
                    
                    # 費用関連のキーワード検索
                    if '円' in content:
                        print("✅ '円'という文字が含まれています")
                        lines_with_yen = [line for line in content.split('\n') if '円' in line]
                        print(f"円を含む行数: {len(lines_with_yen)}")
                        for i, line in enumerate(lines_with_yen[:5]):
                            print(f"  {i+1}. {line.strip()}")
                    else:
                        print("❌ '円'という文字が含まれていません")
        else:
            print("❌ テキストファイル内容が取得できませんでした")
            
        # フォーマット結果のテスト
        print(f"\n🎯 フォーマット結果のテスト:")
        advice = format_repair_advice_for_html(rag_results, query)
        print(f"  - 結果数: {len(advice['results'])}")
        for i, result in enumerate(advice['results']):
            print(f"  {i+1}. {result['title']} ({result['category']})")
            if result['source'] == 'cost_info':
                print(f"      💰 費用目安情報: {result['content'][:100]}...")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cost_extraction()
