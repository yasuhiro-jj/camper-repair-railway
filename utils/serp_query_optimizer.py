"""
SERP検索クエリ最適化モジュール

検索エンジン向けに最適化されたクエリを生成し、検索精度を向上させる
"""

import re
from typing import List, Dict, Any, Optional
from utils.query_expander import query_expander


class SerpQueryOptimizer:
    """SERP検索クエリ最適化クラス"""
    
    def __init__(self):
        # 検索意図のキーワード辞書
        self.intent_keywords = {
            'price': ['価格', '値段', '費用', 'いくら', 'コスト', '料金', '相場', '見積'],
            'latest': ['最新', '新しい', '最近', '今', '現在', '2024', '2025'],
            'parts': ['部品', 'パーツ', '交換', '購入', '販売', '通販'],
            'shop': ['業者', '工場', '店舗', 'ショップ', '修理店', 'どこ', '近く', '地域'],
            'review': ['レビュー', '評判', '口コミ', 'おすすめ', '比較', '評価'],
            'repair': ['修理', '直す', '対処', '解決', '方法', '手順'],
            'diagnosis': ['診断', '原因', '症状', 'チェック', '確認'],
            'diy': ['自分で', 'DIY', '自力', '素人', '初心者']
        }
        
        # 信頼できるドメイン（キャンピングカー関連）
        self.trusted_domains = [
            'camper-repair.net',
            'rv-japan.com',
            'camping-car.jp',
            'japan-rv.com',
            'campingcar-guide.com'
        ]
    
    def identify_search_intent(self, query: str) -> List[str]:
        """
        検索意図を特定
        
        Args:
            query: 検索クエリ
        
        Returns:
            検索意図のリスト
        """
        intents = []
        query_lower = query.lower()
        
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                intents.append(intent)
        
        # デフォルトの意図
        if not intents:
            intents.append('repair')
        
        return intents
    
    def optimize_query_for_serp(
        self,
        query: str,
        intent: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> str:
        """
        SERP検索用にクエリを最適化
        
        Args:
            query: 元のクエリ
            intent: 検索意図のリスト
            category: カテゴリ
        
        Returns:
            最適化されたクエリ
        """
        # 意図を特定
        if intent is None:
            intent = self.identify_search_intent(query)
        
        # 基本となるクエリ
        base_query = f"キャンピングカー {query}"
        
        # 意図に応じてキーワードを追加
        if 'price' in intent:
            # 価格情報の検索
            optimized = f"{base_query} 価格 費用 相場"
        
        elif 'latest' in intent:
            # 最新情報の検索
            optimized = f"{base_query} 最新 2024 2025"
        
        elif 'parts' in intent:
            # 部品情報の検索
            optimized = f"{base_query} 部品 交換 販売"
        
        elif 'shop' in intent:
            # 業者情報の検索
            optimized = f"{base_query} 修理店 工場 業者"
        
        elif 'review' in intent:
            # レビュー情報の検索
            optimized = f"{base_query} 評判 口コミ レビュー"
        
        elif 'repair' in intent:
            # 修理方法の検索
            optimized = f"{base_query} 修理方法 対処法"
        
        elif 'diagnosis' in intent:
            # 診断情報の検索
            optimized = f"{base_query} 症状 原因 診断"
        
        elif 'diy' in intent:
            # DIY情報の検索
            optimized = f"{base_query} DIY 自分で 方法"
        
        else:
            # 一般的な検索
            optimized = base_query
        
        return optimized
    
    def extract_search_keywords(self, query: str) -> List[str]:
        """
        クエリから検索キーワードを抽出
        
        Args:
            query: 検索クエリ
        
        Returns:
            キーワードのリスト
        """
        # query_expanderを使用してキーワード抽出
        keywords = query_expander.extract_keywords(query)
        
        # 追加の重要キーワードを抽出
        important_patterns = [
            r'(\w+が)?(効かない|動かない|故障|不具合|壊れた)',
            r'(\w+)?(修理|交換|点検)',
            r'(\w+)?(価格|費用|料金)',
        ]
        
        for pattern in important_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                if isinstance(match, tuple):
                    keywords.extend([m for m in match if m])
                else:
                    keywords.append(match)
        
        # 重複排除
        keywords = list(set(keywords))
        
        return keywords
    
    def generate_query_variations(
        self,
        query: str,
        max_variations: int = 3
    ) -> List[str]:
        """
        クエリのバリエーションを生成
        
        Args:
            query: 元のクエリ
            max_variations: 最大バリエーション数
        
        Returns:
            クエリバリエーションのリスト
        """
        variations = []
        
        # 1. 基本最適化版
        intent = self.identify_search_intent(query)
        optimized = self.optimize_query_for_serp(query, intent)
        variations.append(optimized)
        
        # 2. キーワード拡張版
        keywords = self.extract_search_keywords(query)
        if keywords:
            keyword_query = f"キャンピングカー {' '.join(keywords[:3])}"
            if keyword_query not in variations:
                variations.append(keyword_query)
        
        # 3. 同義語版
        expanded = query_expander.expand_query(query, max_expansions=2)
        for exp_query in expanded[1:]:  # 元のクエリは除く
            optimized_exp = f"キャンピングカー {exp_query}"
            if optimized_exp not in variations:
                variations.append(optimized_exp)
                if len(variations) >= max_variations:
                    break
        
        return variations[:max_variations]
    
    def should_use_serp(self, query: str, intent: Optional[Dict] = None) -> bool:
        """
        SERP検索を使用すべきか判定（拡張版）
        
        Args:
            query: 検索クエリ
            intent: 意図情報
        
        Returns:
            SERP検索を使用すべきか
        """
        # クエリから検索意図を特定
        search_intents = self.identify_search_intent(query)
        
        # 以下のいずれかの意図がある場合はSERPを使用
        serp_needed_intents = ['price', 'latest', 'parts', 'shop', 'review']
        
        return any(intent in serp_needed_intents for intent in search_intents)
    
    def get_search_parameters(self, query: str) -> Dict[str, Any]:
        """
        検索パラメータを取得
        
        Args:
            query: 検索クエリ
        
        Returns:
            検索パラメータの辞書
        """
        intent = self.identify_search_intent(query)
        optimized_query = self.optimize_query_for_serp(query, intent)
        variations = self.generate_query_variations(query)
        keywords = self.extract_search_keywords(query)
        
        return {
            'original_query': query,
            'optimized_query': optimized_query,
            'query_variations': variations,
            'keywords': keywords,
            'intent': intent,
            'should_use_serp': self.should_use_serp(query)
        }


class SerpResultFilter:
    """SERP検索結果フィルタリングクラス"""
    
    def __init__(self):
        # 信頼できるドメイン
        self.trusted_domains = [
            'camper-repair.net',
            'rv-japan.com',
            'camping-car.jp',
            'japan-rv.com',
            'campingcar-guide.com',
            'kuruma-news.jp',
            'response.jp'
        ]
        
        # 除外すべきドメイン（スパム、低品質）
        self.blocked_domains = [
            'example.com',
            'spam-site.com'
        ]
        
        # スパムキーワード
        self.spam_keywords = [
            '出会い', 'アダルト', 'ギャンブル', 'カジノ',
            '激安', '格安', '無料', 'ランキング'
        ]
    
    def is_spam(self, result: Dict[str, Any]) -> bool:
        """
        スパム判定
        
        Args:
            result: 検索結果
        
        Returns:
            スパムかどうか
        """
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        # ブロックドメインチェック
        if any(domain in url for domain in self.blocked_domains):
            return True
        
        # スパムキーワードチェック
        text = f"{title} {snippet}"
        if any(keyword in text for keyword in self.spam_keywords):
            return True
        
        return False
    
    def calculate_trust_score(self, url: str) -> float:
        """
        URLの信頼性スコアを計算
        
        Args:
            url: URL
        
        Returns:
            信頼性スコア（0.0〜1.0）
        """
        url_lower = url.lower()
        
        # 信頼できるドメインチェック
        for domain in self.trusted_domains:
            if domain in url_lower:
                return 1.0
        
        # 公式ドメイン
        if '.go.jp' in url_lower or '.or.jp' in url_lower:
            return 0.9
        
        # 一般的なドメイン
        if '.com' in url_lower or '.jp' in url_lower or '.net' in url_lower:
            return 0.7
        
        # その他
        return 0.5
    
    def calculate_relevance(
        self,
        query: str,
        title: str,
        snippet: str
    ) -> float:
        """
        関連性スコアを計算
        
        Args:
            query: 検索クエリ
            title: タイトル
            snippet: スニペット
        
        Returns:
            関連性スコア（0.0〜1.0）
        """
        score = 0.0
        
        # クエリのキーワードを抽出
        query_keywords = query.lower().split()
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        
        # タイトルマッチ
        title_matches = sum(1 for kw in query_keywords if kw in title_lower)
        if title_matches > 0:
            score += 0.5 * (title_matches / len(query_keywords))
        
        # スニペットマッチ
        snippet_matches = sum(1 for kw in query_keywords if kw in snippet_lower)
        if snippet_matches > 0:
            score += 0.3 * (snippet_matches / len(query_keywords))
        
        # キャンピングカー関連キーワード
        camper_keywords = ['キャンピングカー', 'キャンパー', 'RV', '修理', 'メンテナンス']
        camper_matches = sum(1 for kw in camper_keywords if kw.lower() in f"{title_lower} {snippet_lower}")
        if camper_matches > 0:
            score += 0.2 * min(camper_matches / 3, 1.0)
        
        return min(score, 1.0)
    
    def filter_and_score_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        min_relevance: float = 0.6,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        検索結果をフィルタリングしてスコアリング
        
        Args:
            results: 検索結果のリスト
            query: 検索クエリ
            min_relevance: 最小関連性スコア
            max_results: 最大結果数
        
        Returns:
            フィルタリング・スコアリングされた結果
        """
        filtered = []
        
        for result in results:
            # スパムチェック
            if self.is_spam(result):
                continue
            
            url = result.get('url', '')
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            # 関連性スコア
            relevance = self.calculate_relevance(query, title, snippet)
            
            # 信頼性スコア
            trust = self.calculate_trust_score(url)
            
            # 総合スコア（関連性70%、信頼性30%）
            total_score = relevance * 0.7 + trust * 0.3
            
            # 閾値チェック
            if total_score >= min_relevance:
                filtered.append({
                    **result,
                    'relevance_score': round(relevance, 3),
                    'trust_score': round(trust, 3),
                    'total_score': round(total_score, 3)
                })
        
        # スコア順でソート
        filtered.sort(key=lambda x: x['total_score'], reverse=True)
        
        return filtered[:max_results]


# グローバルインスタンス
serp_query_optimizer = SerpQueryOptimizer()
serp_result_filter = SerpResultFilter()


def optimize_serp_query(query: str, intent: Optional[List[str]] = None) -> str:
    """SERP検索用にクエリを最適化（簡易版）"""
    return serp_query_optimizer.optimize_query_for_serp(query, intent)


def filter_serp_results(results: List[Dict], query: str) -> List[Dict]:
    """SERP検索結果をフィルタリング（簡易版）"""
    return serp_result_filter.filter_and_score_results(results, query)


if __name__ == "__main__":
    print("=== SERP検索クエリ最適化モジュール ===\n")
    
    optimizer = SerpQueryOptimizer()
    
    test_queries = [
        "エアコンの修理費用はいくらですか",
        "バッテリー交換の部品を購入したい",
        "FFヒーター修理の業者を探しています",
        "冷蔵庫の最新モデルの評判"
    ]
    
    for query in test_queries:
        print(f"元のクエリ: {query}")
        
        params = optimizer.get_search_parameters(query)
        print(f"  意図: {params['intent']}")
        print(f"  最適化: {params['optimized_query']}")
        print(f"  SERP使用: {params['should_use_serp']}")
        print(f"  バリエーション: {params['query_variations']}")
        print()
    
    print("✅ モジュールが正常に動作しています")

