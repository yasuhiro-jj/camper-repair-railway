"""
強化版RAG検索モジュール

クエリ拡張、閾値フィルタリング、リランキングを含む高精度RAG検索
"""

import time
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document

# クエリ拡張モジュールをインポート
try:
    from utils.query_expander import query_expander
    QUERY_EXPANDER_AVAILABLE = True
except ImportError:
    QUERY_EXPANDER_AVAILABLE = False
    print("⚠️ query_expander のインポートに失敗しました")


def deduplicate_results(results: List[Dict], similarity_threshold: float = 0.9) -> List[Dict]:
    """
    検索結果の重複を排除
    
    Args:
        results: 検索結果のリスト
        similarity_threshold: 重複判定の類似度閾値
    
    Returns:
        重複排除された結果
    """
    if not results:
        return []
    
    unique_results = []
    seen_contents = set()
    
    for result in results:
        content = result.get('content', '')
        
        # 簡易的な重複チェック（完全一致）
        content_hash = hash(content[:200])  # 最初の200文字でハッシュ化
        
        if content_hash not in seen_contents:
            seen_contents.add(content_hash)
            unique_results.append(result)
    
    return unique_results


def calculate_relevance_score(query: str, document: Document, base_score: float) -> float:
    """
    関連性スコアを計算
    
    Args:
        query: 検索クエリ
        document: ドキュメント
        base_score: ベーススコア（類似度スコア）
    
    Returns:
        計算された関連性スコア
    """
    score = base_score
    
    # クエリのキーワードがドキュメントに含まれているか
    query_keywords = query.lower().split()
    content_lower = document.page_content.lower()
    
    # キーワードマッチボーナス
    keyword_matches = sum(1 for kw in query_keywords if kw in content_lower)
    if keyword_matches > 0:
        score += 0.1 * (keyword_matches / len(query_keywords))
    
    # メタデータによるボーナス
    metadata = document.metadata
    
    # ソースタイプによるボーナス
    source_type = metadata.get('source_type', '')
    if source_type == 'notion':
        score += 0.1  # Notionデータは信頼性が高い
    elif source_type == 'blog':
        score += 0.05  # ブログ記事も有用
    
    # カテゴリマッチボーナス
    if 'category' in metadata:
        category = metadata['category']
        if category.lower() in query.lower():
            score += 0.15
    
    return min(score, 1.0)  # 最大1.0に制限


def enhanced_rag_retrieve_v2(
    query: str,
    db: Chroma,
    max_results: int = 5,
    relevance_threshold: float = 0.65,
    use_query_expansion: bool = True,
    category: str = None
) -> Dict[str, Any]:
    """
    強化版RAG検索
    
    Args:
        query: 検索クエリ
        db: Chromaデータベース
        max_results: 最大結果数
        relevance_threshold: 関連性スコアの閾値
        use_query_expansion: クエリ拡張を使用するか
        category: カテゴリ（オプション）
    
    Returns:
        検索結果の辞書
    """
    start_time = time.time()
    
    print(f"🔍 強化版RAG検索開始: クエリ='{query}'")
    
    all_results = []
    queries_used = [query]  # 元のクエリ
    
    try:
        # 1. クエリ拡張（オプション）
        if use_query_expansion and QUERY_EXPANDER_AVAILABLE:
            print("📝 クエリを拡張中...")
            
            # コンテキストを考慮した拡張
            expansion_result = query_expander.expand_with_context(query, category)
            
            # 拡張されたクエリ
            expanded_queries = expansion_result['expanded_queries'][:3]  # 最大3つ
            queries_used = expanded_queries
            
            # 関連語も検索に含める
            if expansion_result['related_terms']:
                related_query = f"{query} {' '.join(expansion_result['related_terms'][:2])}"
                queries_used.append(related_query)
            
            print(f"✅ {len(queries_used)}個のクエリで検索: {queries_used}")
        
        # 2. 各クエリで検索実行
        for search_query in queries_used:
            try:
                # 類似度検索（スコア付き）
                results_with_scores = db.similarity_search_with_relevance_scores(
                    search_query,
                    k=max_results * 2  # 余分に取得してフィルタリング
                )
                
                # 結果を整形
                for doc, score in results_with_scores:
                    # 関連性スコアを再計算
                    enhanced_score = calculate_relevance_score(query, doc, score)
                    
                    all_results.append({
                        'document': doc,
                        'score': enhanced_score,
                        'original_score': score,
                        'query_used': search_query,
                        'content': doc.page_content,
                        'metadata': doc.metadata
                    })
            
            except Exception as e:
                print(f"⚠️ クエリ '{search_query}' の検索エラー: {e}")
                continue
        
        # 3. 重複排除
        print(f"📊 重複排除前: {len(all_results)}件")
        unique_results = deduplicate_results(all_results)
        print(f"📊 重複排除後: {len(unique_results)}件")
        
        # 4. 閾値フィルタリング
        filtered_results = [
            r for r in unique_results 
            if r['score'] >= relevance_threshold
        ]
        print(f"📊 閾値フィルタリング後: {len(filtered_results)}件 (閾値: {relevance_threshold})")
        
        # 5. スコア順でソート
        sorted_results = sorted(
            filtered_results,
            key=lambda x: x['score'],
            reverse=True
        )
        
        # 6. 最大件数に制限
        final_results = sorted_results[:max_results]
        
        # 7. 結果を整形
        formatted_results = []
        for i, result in enumerate(final_results):
            doc = result['document']
            metadata = result['metadata']
            
            formatted_results.append({
                'title': metadata.get('title', f'検索結果 {i+1}'),
                'content': result['content'],
                'source': metadata.get('source', 'RAG検索'),
                'source_type': metadata.get('source_type', 'unknown'),
                'category': metadata.get('category', '不明'),
                'url': metadata.get('url', ''),
                'relevance_score': round(result['score'], 3),
                'original_score': round(result['original_score'], 3),
                'query_used': result['query_used']
            })
        
        duration = time.time() - start_time
        
        return {
            'results': formatted_results,
            'total_found': len(all_results),
            'after_deduplication': len(unique_results),
            'after_filtering': len(filtered_results),
            'returned': len(final_results),
            'queries_used': queries_used,
            'duration': round(duration, 2),
            'relevance_threshold': relevance_threshold
        }
    
    except Exception as e:
        print(f"❌ RAG検索エラー: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'results': [],
            'error': str(e),
            'duration': time.time() - start_time
        }


def simple_rag_search(query: str, db: Chroma, max_results: int = 5) -> List[Dict]:
    """
    シンプルなRAG検索（後方互換性のため）
    
    Args:
        query: 検索クエリ
        db: Chromaデータベース
        max_results: 最大結果数
    
    Returns:
        検索結果のリスト
    """
    try:
        results = db.similarity_search(query, k=max_results)
        
        formatted = []
        for doc in results:
            formatted.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'source': doc.metadata.get('source', 'RAG検索')
            })
        
        return formatted
    
    except Exception as e:
        print(f"❌ RAG検索エラー: {e}")
        return []


# テスト用
if __name__ == "__main__":
    print("=== RAG検索強化モジュール ===")
    print("✅ モジュールが正常にロードされました")
    
    if QUERY_EXPANDER_AVAILABLE:
        print("✅ クエリ拡張機能が利用可能です")
    else:
        print("⚠️ クエリ拡張機能は利用できません")

