"""
クエリ拡張モジュール

検索クエリを同義語や関連語で拡張し、検索精度を向上させる
"""

import re
from typing import List, Dict, Set

# キャンピングカー修理専門の同義語辞書
SYNONYMS_DICT = {
    # 主要カテゴリ
    "エアコン": ["冷房", "クーラー", "空調", "エアコンディショナー", "AC", "A/C"],
    "バッテリー": ["蓄電池", "電池", "バッテリ", "充電池"],
    "冷蔵庫": ["クーラーボックス", "冷凍庫", "冷却装置"],
    "トイレ": ["便器", "トイレット", "水洗トイレ", "ポータブルトイレ"],
    "FFヒーター": ["FFストーブ", "FF暖房", "暖房機", "ヒーター"],
    "ソーラーパネル": ["太陽光パネル", "ソーラー", "太陽電池"],
    "インバーター": ["電源変換器", "DC-ACコンバーター"],
    "サブバッテリー": ["サブバッテリ", "補助バッテリー", "走行充電"],
    "外部電源": ["AC電源", "100V電源", "ショア電源"],
    "給水": ["水タンク", "清水タンク", "給水タンク"],
    "排水": ["排水タンク", "汚水タンク", "グレータンク"],
    "ポンプ": ["水ポンプ", "ウォーターポンプ", "給水ポンプ"],
    
    # 症状・状態
    "故障": ["不具合", "トラブル", "異常", "エラー", "壊れた", "動かない"],
    "効かない": ["効果ない", "作動しない", "機能しない", "使えない"],
    "漏れる": ["漏水", "水漏れ", "リーク", "漏れ"],
    "上がる": ["放電", "バッテリー切れ", "充電切れ"],
    "異音": ["変な音", "音がする", "ノイズ", "きしみ音", "異常音"],
    "臭い": ["におい", "異臭", "悪臭", "臭気"],
    "煙": ["煙が出る", "発煙", "白煙", "黒煙"],
    
    # 作業・修理
    "修理": ["メンテナンス", "修繕", "補修", "直す", "リペア"],
    "交換": ["取替", "取り替え", "載せ替え", "換装"],
    "点検": ["チェック", "確認", "診断", "検査"],
    "清掃": ["掃除", "クリーニング", "洗浄", "手入れ"],
    "調整": ["セッティング", "設定", "チューニング"],
    
    # 部品
    "ヒューズ": ["フューズ", "保護装置"],
    "リレー": ["リレースイッチ", "継電器"],
    "配線": ["ケーブル", "ワイヤー", "電線", "コード"],
    "コネクタ": ["端子", "接続部", "プラグ"],
    "フィルター": ["濾過器", "ろ過フィルター", "エアフィルター"],
    
    # 費用関連
    "価格": ["値段", "費用", "料金", "金額", "相場", "コスト"],
    "工賃": ["作業料", "技術料", "手数料", "労務費"],
    "見積": ["見積もり", "概算", "費用見積"],
}

# 専門用語の説明辞書（平易な言葉への変換）
TECHNICAL_TERMS = {
    "コンプレッサー": "圧縮機",
    "オルタネーター": "発電機",
    "レギュレーター": "調整器",
    "サーモスタット": "温度調整器",
    "インバータ": "電源変換器",
}

# カテゴリ関連語辞書
RELATED_TERMS = {
    "エアコン": ["冷媒", "ガス", "温度", "風量", "コンプレッサー", "室外機"],
    "バッテリー": ["電圧", "充電", "放電", "オルタネーター", "ケーブル"],
    "冷蔵庫": ["冷却", "温度", "霜", "コンプレッサー", "冷媒"],
    "トイレ": ["給水", "排水", "ポンプ", "タンク", "便器"],
    "FFヒーター": ["燃料", "点火", "排気", "吸気", "温度"],
}


class QueryExpander:
    """クエリ拡張クラス"""
    
    def __init__(self):
        self.synonyms = SYNONYMS_DICT
        self.technical_terms = TECHNICAL_TERMS
        self.related_terms = RELATED_TERMS
    
    def expand_query(self, query: str, max_expansions: int = 5) -> List[str]:
        """
        クエリを同義語で拡張
        
        Args:
            query: 元のクエリ
            max_expansions: 最大拡張数
        
        Returns:
            拡張されたクエリのリスト
        """
        expanded = [query]  # 元のクエリも含める
        
        # 同義語で拡張
        for keyword, synonyms in self.synonyms.items():
            if keyword in query:
                # 同義語を使った新しいクエリを生成
                for synonym in synonyms[:max_expansions - 1]:
                    new_query = query.replace(keyword, synonym)
                    if new_query not in expanded:
                        expanded.append(new_query)
                
                # 最大数に達したら終了
                if len(expanded) >= max_expansions:
                    break
        
        return expanded[:max_expansions]
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        クエリから重要なキーワードを抽出
        
        Args:
            query: 検索クエリ
        
        Returns:
            抽出されたキーワードのリスト
        """
        keywords = []
        
        # 同義語辞書のキーワードを検索
        for keyword in self.synonyms.keys():
            if keyword in query:
                keywords.append(keyword)
        
        # 技術用語を検索
        for term in self.technical_terms.keys():
            if term in query:
                keywords.append(term)
        
        # 重複排除
        keywords = list(set(keywords))
        
        return keywords
    
    def add_related_terms(self, query: str) -> List[str]:
        """
        関連語を追加してクエリを強化
        
        Args:
            query: 元のクエリ
        
        Returns:
            関連語を含むクエリのリスト
        """
        enhanced = [query]
        
        # カテゴリを特定
        for category, related in self.related_terms.items():
            if category in query:
                # 関連語を追加
                for term in related[:3]:  # 最大3つの関連語
                    enhanced_query = f"{query} {term}"
                    enhanced.append(enhanced_query)
                break
        
        return enhanced
    
    def simplify_technical_terms(self, query: str) -> str:
        """
        専門用語を平易な言葉に変換
        
        Args:
            query: 元のクエリ
        
        Returns:
            平易な言葉に変換されたクエリ
        """
        simplified = query
        
        for technical, simple in self.technical_terms.items():
            if technical in simplified:
                simplified = simplified.replace(technical, simple)
        
        return simplified
    
    def get_all_synonyms(self, keyword: str) -> List[str]:
        """
        指定されたキーワードのすべての同義語を取得
        
        Args:
            keyword: キーワード
        
        Returns:
            同義語のリスト
        """
        # 完全一致を検索
        if keyword in self.synonyms:
            return self.synonyms[keyword]
        
        # 部分一致を検索
        for key, synonyms in self.synonyms.items():
            if keyword in key or key in keyword:
                return synonyms
            # 同義語の中に含まれているか
            if keyword in synonyms:
                return [key] + [s for s in synonyms if s != keyword]
        
        return []
    
    def expand_with_context(self, query: str, category: str = None) -> Dict[str, any]:
        """
        コンテキストを考慮した高度なクエリ拡張
        
        Args:
            query: 元のクエリ
            category: カテゴリ（オプション）
        
        Returns:
            拡張結果の辞書
        """
        result = {
            'original': query,
            'expanded_queries': [],
            'keywords': [],
            'related_terms': [],
            'simplified': query
        }
        
        # 1. 基本的な拡張
        result['expanded_queries'] = self.expand_query(query)
        
        # 2. キーワード抽出
        result['keywords'] = self.extract_keywords(query)
        
        # 3. 関連語の追加
        if category and category in self.related_terms:
            result['related_terms'] = self.related_terms[category]
        else:
            # カテゴリが不明な場合は、クエリから推測
            for cat, terms in self.related_terms.items():
                if cat in query:
                    result['related_terms'] = terms
                    break
        
        # 4. 専門用語の簡略化
        result['simplified'] = self.simplify_technical_terms(query)
        
        return result


# グローバルインスタンス
query_expander = QueryExpander()


def expand_query(query: str, max_expansions: int = 5) -> List[str]:
    """
    クエリを拡張（簡易版）
    
    Args:
        query: 検索クエリ
        max_expansions: 最大拡張数
    
    Returns:
        拡張されたクエリのリスト
    """
    return query_expander.expand_query(query, max_expansions)


def extract_keywords(query: str) -> List[str]:
    """
    クエリからキーワードを抽出（簡易版）
    
    Args:
        query: 検索クエリ
    
    Returns:
        キーワードのリスト
    """
    return query_expander.extract_keywords(query)


if __name__ == "__main__":
    # テスト
    expander = QueryExpander()
    
    print("=== クエリ拡張テスト ===\n")
    
    test_queries = [
        "エアコンが効かない",
        "バッテリーが上がった",
        "冷蔵庫の温度が下がらない",
        "FFヒーターが点火しない"
    ]
    
    for query in test_queries:
        print(f"元のクエリ: {query}")
        
        # 基本拡張
        expanded = expander.expand_query(query, max_expansions=3)
        print(f"拡張クエリ: {expanded}")
        
        # キーワード抽出
        keywords = expander.extract_keywords(query)
        print(f"キーワード: {keywords}")
        
        # 高度な拡張
        result = expander.expand_with_context(query)
        print(f"関連語: {result['related_terms']}")
        print(f"簡略化: {result['simplified']}")
        print()

