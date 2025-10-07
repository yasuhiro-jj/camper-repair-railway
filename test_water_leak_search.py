#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雨漏り検索のテストスクリプト
"""

from enhanced_rag_system import enhanced_rag_retrieve, create_enhanced_rag_system
import json

def test_water_leak_search():
    """雨漏り検索をテストする"""
    print("🔍 雨漏り検索テストを開始...")
    
    try:
        # RAGシステムを初期化
        print("📚 RAGシステムを初期化中...")
        db = create_enhanced_rag_system()
        print("✅ RAGシステム初期化完了")
        
        # 雨漏り検索をテスト
        print("🔍 雨漏り検索をテスト中...")
        results = enhanced_rag_retrieve('雨漏り', db, max_results=3)
        
        print("📊 検索結果:")
        print(f"  - manual_content: {len(results.get('manual_content', ''))}文字")
        print(f"  - text_file_content: {len(results.get('text_file_content', ''))}文字")
        print(f"  - blog_links: {len(results.get('blog_links', []))}件")
        
        # テキストファイル内容の詳細表示
        if results.get('text_file_content'):
            content = results['text_file_content']
            print(f"\n📄 テキストファイル内容（最初の500文字）:")
            print(content[:500])
            print("...")
        else:
            print("❌ テキストファイル内容が取得できませんでした")
        
        # マニュアル内容の詳細表示
        if results.get('manual_content'):
            content = results['manual_content']
            print(f"\n📖 マニュアル内容（最初の500文字）:")
            print(content[:500])
            print("...")
        else:
            print("❌ マニュアル内容が取得できませんでした")
        
        # ブログリンクの表示
        if results.get('blog_links'):
            print(f"\n🔗 ブログリンク:")
            for i, link in enumerate(results['blog_links'][:3]):
                print(f"  {i+1}. {link}")
        else:
            print("❌ ブログリンクが取得できませんでした")
            
        return results
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    test_water_leak_search()
