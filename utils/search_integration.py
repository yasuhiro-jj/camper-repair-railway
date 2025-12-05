"""
統合検索最適化モジュール

複数の検索ソース（RAG、SERP、Notion）の結果を統合し、
動的な重み付け、マージ、重複排除を行う
"""

import time
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher


class SearchIntegration:
    """統合検索クラス"""
    
    def __init__(self):
        # デフォルトの重み付け
        self.default_weights = {
            'notion': 1.0,   # 最優先（最も信頼性が高い）
            'rag': 0.8,      # 補完（技術的に詳細）
            'serp': 0.6      # 参考（最新情報・価格情報）
        }
    
    def calculate_dynamic_weights(
        self,
        query: str,
        intent: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        クエリと意図に基づいて動的に重みを計算
        
        Args:
            query: 検索クエリ
            intent: 意図情報
        
        Returns:
            各ソースの重み
        """
        # デフォルトの重みをコピー
        weights = self.default_weights.copy()
        
        # クエリの種類を特定
        query_lower = query.lower()
        
        # 1. 価格情報クエリ
        price_keywords = ['価格', '値段', '費用', 'いくら', 'コスト', '料金', '相場']
        if any(keyword in query_lower for keyword in price_keywords):
            weights['serp'] = 1.0      # SERP最優先
            weights['notion'] = 0.7    # Notionは補完
            weights['rag'] = 0.5       # RAGは参考
            print("💰 価格情報クエリ: SERP重視")
        
        # 2. 最新情報クエリ
        elif any(keyword in query_lower for keyword in ['最新', '新しい', '最近', '今', '現在', '2024', '2025']):
            weights['serp'] = 1.0      # SERP最優先
            weights['notion'] = 0.8    # Notionも重要
            weights['rag'] = 0.5       # RAGは古い可能性
            print("🆕 最新情報クエリ: SERP重視")
        
        # 3. 緊急度が高いクエリ
        elif intent.get('urgency') == 'high':
            weights['notion'] = 1.0    # Notion最優先（信頼性重視）
            weights['rag'] = 0.6       # RAGは補完
            weights['serp'] = 0.4      # SERPは参考程度
            print("🚨 緊急クエリ: Notion重視（信頼性優先）")
        
        # 4. 修理・診断クエリ
        elif any(keyword in query_lower for keyword in ['修理', '直す', '対処', '解決', '方法', '手順', '診断', '原因', '症状', 'チェック', '確認']):
            weights['rag'] = 1.0       # RAG最優先（技術情報豊富）
            weights['notion'] = 0.9    # Notionも重要
            weights['serp'] = 0.5      # SERPは補完
            print("🔧 修理・診断クエリ: RAG重視（技術情報優先）")
        
        # 5. 業者・工場検索クエリ
        elif any(keyword in query_lower for keyword in ['業者', '工場', '店舗', 'ショップ', '修理店', 'どこ', '近く']):
            weights['notion'] = 1.0    # Notion最優先（DB情報）
            weights['serp'] = 0.8      # SERPも重要
            weights['rag'] = 0.4       # RAGは参考
            print("🏭 業者検索クエリ: Notion重視（DB情報優先）")
        
        # 6. レビュー・評判クエリ
        elif any(keyword in query_lower for keyword in ['レビュー', '評判', '口コミ', 'おすすめ', '比較']):
            weights['serp'] = 1.0      # SERP最優先
            weights['notion'] = 0.7    # Notionも参考
            weights['rag'] = 0.5       # RAGは参考
            print("⭐ レビュークエリ: SERP重視")
        
        # 7. デフォルト（一般的なクエリ）
        else:
            # デフォルトの重みを使用
            print("📝 一般クエリ: バランス型")
        
        return weights
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        2つのテキストの類似度を計算
        
        Args:
            text1: テキスト1
            text2: テキスト2
        
        Returns:
            類似度スコア（0.0〜1.0）
        """
        # 空文字列チェック
        if not text1 or not text2:
            return 0.0
        
        # SequenceMatcherで類似度を計算
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def deduplicate_by_similarity(
        self,
        results: List[Dict[str, Any]],
        similarity_threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        類似度が高い結果を重複排除
        
        Args:
            results: 検索結果のリスト
            similarity_threshold: 類似度の閾値
        
        Returns:
            重複排除された結果
        """
        if not results:
            return []
        
        unique_results = []
        
        for result in results:
            is_duplicate = False
            result_content = result.get('content', '')
            
            # 既存の結果と比較
            for existing in unique_results:
                existing_content = existing.get('content', '')
                
                # 類似度を計算
                similarity = self.calculate_text_similarity(
                    result_content,
                    existing_content
                )
                
                # 閾値以上なら重複と判定
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    
                    # スコアが高い方を残す
                    if result.get('total_score', 0) > existing.get('total_score', 0):
                        # 既存の結果を削除して新しい結果を追加
                        unique_results.remove(existing)
                        unique_results.append(result)
                    
                    break
            
            # 重複でなければ追加
            if not is_duplicate:
                unique_results.append(result)
        
        return unique_results
    
    def deduplicate_by_url(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        URLベースで重複排除（高速）
        
        Args:
            results: 検索結果のリスト
        
        Returns:
            URL重複排除された結果
        """
        if not results:
            return []
        
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            
            # URLが存在し、まだ見ていない場合は追加
            if url:
                # URLを正規化（クエリパラメータを除去）
                normalized_url = url.split('?')[0].split('#')[0].rstrip('/')
                
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    unique_results.append(result)
                else:
                    # 重複URLの場合、スコアが高い方を残す
                    for i, existing in enumerate(unique_results):
                        existing_url = existing.get('url', '')
                        existing_normalized = existing_url.split('?')[0].split('#')[0].rstrip('/')
                        
                        if existing_normalized == normalized_url:
                            # スコアが高い方を残す
                            if result.get('weighted_score', 0) > existing.get('weighted_score', 0):
                                unique_results[i] = result
                            break
            else:
                # URLがない場合はそのまま追加（後で類似度ベースで処理）
                unique_results.append(result)
        
        return unique_results
    
    def merge_search_results(
        self,
        rag_results: Dict[str, Any],
        serp_results: Dict[str, Any],
        notion_results: Dict[str, Any],
        weights: Dict[str, float],
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        複数の検索結果をマージ
        
        Args:
            rag_results: RAG検索結果
            serp_results: SERP検索結果
            notion_results: Notion検索結果
            weights: 各ソースの重み
            max_results: 最大結果数
        
        Returns:
            マージされた結果のリスト
        """
        merged = []
        
        # 1. RAG検索結果を追加
        if rag_results and 'search_results' in rag_results:
            for result in rag_results['search_results']:
                merged.append({
                    'source': 'rag',
                    'title': result.get('title', '検索結果'),
                    'content': result.get('content', ''),
                    'url': result.get('url', ''),
                    'category': result.get('category', '不明'),
                    'base_score': result.get('relevance_score', 0.7),
                    'weighted_score': result.get('relevance_score', 0.7) * weights['rag'],
                    'metadata': result.get('metadata', {})
                })
        
        # RAG結果がresultsキーにある場合（強化版）
        elif rag_results and 'results' in rag_results:
            for result in rag_results['results']:
                merged.append({
                    'source': 'rag',
                    'title': result.get('title', '検索結果'),
                    'content': result.get('content', ''),
                    'url': result.get('url', ''),
                    'category': result.get('category', '不明'),
                    'base_score': result.get('relevance_score', 0.7),
                    'weighted_score': result.get('relevance_score', 0.7) * weights['rag'],
                    'metadata': result.get('metadata', {})
                })
        
        # 2. SERP検索結果を追加
        if serp_results and 'results' in serp_results:
            for result in serp_results['results']:
                merged.append({
                    'source': 'serp',
                    'title': result.get('title', '検索結果'),
                    'content': result.get('snippet', result.get('content', '')),
                    'url': result.get('url', ''),
                    'category': 'SERP検索',
                    'base_score': result.get('total_score', result.get('relevance', 0.6)),
                    'weighted_score': result.get('total_score', result.get('relevance', 0.6)) * weights['serp'],
                    'metadata': {
                        'trust_score': result.get('trust_score', 0.5),
                        'relevance_score': result.get('relevance_score', 0.5)
                    }
                })
        
        # 3. Notion検索結果を追加
        if notion_results:
            # 修理ケース
            for case in notion_results.get('repair_cases', []):
                merged.append({
                    'source': 'notion',
                    'title': case.get('title', '修理ケース'),
                    'content': case.get('solution', case.get('content', '')),
                    'url': case.get('url', ''),
                    'category': case.get('category', '修理ケース'),
                    'base_score': case.get('relevance_score', 0.8),
                    'weighted_score': case.get('relevance_score', 0.8) * weights['notion'],
                    'metadata': {
                        'matched_keywords': case.get('matched_keywords', []),
                        'database': 'repair_cases'
                    }
                })
            
            # 診断ノード
            for node in notion_results.get('diagnostic_nodes', []):
                merged.append({
                    'source': 'notion',
                    'title': node.get('title', '診断ノード'),
                    'content': node.get('diagnosis_result', node.get('question', '')),
                    'url': node.get('url', ''),
                    'category': node.get('category', '診断'),
                    'base_score': node.get('relevance_score', 0.8),
                    'weighted_score': node.get('relevance_score', 0.8) * weights['notion'],
                    'metadata': {
                        'matched_keywords': node.get('matched_keywords', []),
                        'database': 'diagnostic_nodes'
                    }
                })
        
        # 4. 重複排除（URLベース → 類似度ベース）
        print(f"📊 マージ前: {len(merged)}件")
        # まずURLベースで重複排除（高速）
        unique_results = self.deduplicate_by_url(merged)
        print(f"📊 URL重複排除後: {len(unique_results)}件")
        # 次に類似度ベースで重複排除（精度重視）
        unique_results = self.deduplicate_by_similarity(unique_results, similarity_threshold=0.85)
        print(f"📊 類似度重複排除後: {len(unique_results)}件")
        
        # 5. スコア順でソート
        sorted_results = sorted(
            unique_results,
            key=lambda x: x['weighted_score'],
            reverse=True
        )
        
        # 6. 総合スコアを追加（正規化）
        max_score = sorted_results[0]['weighted_score'] if sorted_results else 1.0
        for result in sorted_results:
            result['total_score'] = result['weighted_score'] / max_score if max_score > 0 else 0
        
        # 7. 最大件数に制限
        return sorted_results[:max_results]
    
    def get_source_distribution(self, results: List[Dict]) -> Dict[str, int]:
        """
        ソース別の結果分布を取得
        
        Args:
            results: 検索結果のリスト
        
        Returns:
            ソース別の件数
        """
        distribution = {
            'rag': 0,
            'serp': 0,
            'notion': 0
        }
        
        for result in results:
            source = result.get('source', 'unknown')
            if source in distribution:
                distribution[source] += 1
        
        return distribution


# グローバルインスタンス
search_integration = SearchIntegration()


def integrate_search_results(
    rag_results: Dict,
    serp_results: Dict,
    notion_results: Dict,
    query: str,
    intent: Dict
) -> List[Dict]:
    """
    統合検索（簡易版）
    
    Args:
        rag_results: RAG検索結果
        serp_results: SERP検索結果
        notion_results: Notion検索結果
        query: 検索クエリ
        intent: 意図情報
    
    Returns:
        統合された検索結果
    """
    # 動的な重み付けを計算
    weights = search_integration.calculate_dynamic_weights(query, intent)
    
    # 結果をマージ
    merged = search_integration.merge_search_results(
        rag_results,
        serp_results,
        notion_results,
        weights,
        max_results=10
    )
    
    return merged


if __name__ == "__main__":
    print("=== 統合検索最適化モジュール ===")
    print("✅ モジュールが正常にロードされました")
    
    # テスト
    integration = SearchIntegration()
    
    test_queries = [
        ("エアコンの修理費用はいくらですか", {'urgency': 'low'}),
        ("バッテリーが上がって動かない！", {'urgency': 'high'}),
        ("FFヒーターの最新モデル", {'urgency': 'low'}),
        ("修理業者を探しています", {'urgency': 'low'})
    ]
    
    print("\n動的な重み付けのテスト:")
    for query, intent in test_queries:
        print(f"\nクエリ: {query}")
        weights = integration.calculate_dynamic_weights(query, intent)
        print(f"  重み: {weights}")

