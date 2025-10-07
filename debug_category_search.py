#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カテゴリー別検索のデバッグスクリプト
"""

from enhanced_rag_system import enhanced_rag_retrieve, create_enhanced_rag_system
import json

def test_category_search():
    """異なるカテゴリーで検索テストを実行"""
    print("🔍 カテゴリー別検索テストを開始...")
    
    try:
        # RAGシステムを初期化
        print("📚 RAGシステムを初期化中...")
        db = create_enhanced_rag_system()
        print("✅ RAGシステム初期化完了")
        
        # テストクエリ（異なるカテゴリー）
        test_queries = [
            "雨漏り",
            "バッテリー",
            "トイレ",
            "エアコン",
            "ドア",
            "窓",
            "冷蔵庫",
            "ガスコンロ"
        ]
        
        print("\n🔍 カテゴリー別検索テスト:")
        for query in test_queries:
            print(f"\n--- クエリ: '{query}' ---")
            
            try:
                results = enhanced_rag_retrieve(query, db, max_results=3)
                
                print(f"📊 検索結果:")
                print(f"  - manual_content: {len(results.get('manual_content', ''))}文字")
                print(f"  - text_file_content: {len(results.get('text_file_content', ''))}文字")
                print(f"  - blog_links: {len(results.get('blog_links', []))}件")
                
                # テキストファイル内容の詳細表示
                if results.get('text_file_content'):
                    content = results['text_file_content']
                    print(f"📄 テキストファイル内容（最初の200文字）:")
                    print(content[:200])
                    print("...")
                else:
                    print("❌ テキストファイル内容が取得できませんでした")
                
                # マニュアル内容の詳細表示
                if results.get('manual_content'):
                    content = results['manual_content']
                    print(f"📖 マニュアル内容（最初の200文字）:")
                    print(content[:200])
                    print("...")
                else:
                    print("❌ マニュアル内容が取得できませんでした")
                
                # ブログリンクの表示
                if results.get('blog_links'):
                    print(f"🔗 ブログリンク:")
                    for i, link in enumerate(results['blog_links'][:3]):
                        if isinstance(link, dict):
                            print(f"  {i+1}. {link.get('title', 'N/A')}")
                        else:
                            print(f"  {i+1}. {link}")
                else:
                    print("❌ ブログリンクが取得できませんでした")
                    
            except Exception as e:
                print(f"❌ 検索エラー: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_category_search()
