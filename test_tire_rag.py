#!/usr/bin/env python3
"""
タイヤテキストファイルのRAGテスト
"""

from enhanced_rag_system import create_enhanced_rag_system, enhanced_rag_retrieve

def test_tire_rag():
    """タイヤ関連のRAGテスト"""
    print("🔧 タイヤテキストファイルのRAGテスト開始")
    
    # RAGシステムを作成
    db = create_enhanced_rag_system()
    
    # タイヤ関連の質問でテスト
    test_questions = [
        "タイヤの空気圧管理について教えて",
        "CP規格とLT規格の違いは？",
        "タイヤの交換費用はどのくらい？",
        "タイヤのローテーションについて"
    ]
    
    for question in test_questions:
        print(f"\n📝 質問: {question}")
        results = enhanced_rag_retrieve(question, db)
        
        if results["text_file_content"]:
            print(f"✅ テキストファイルから回答: {results['text_file_content'][:200]}...")
        else:
            print("❌ テキストファイルからの回答なし")
        
        if results["blog_links"]:
            print(f"🔗 関連ブログ: {len(results['blog_links'])}件")
            for blog in results['blog_links']:
                print(f"  • {blog['title']}: {blog['url']}")

if __name__ == "__main__":
    test_tire_rag()
