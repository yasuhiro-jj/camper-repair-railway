"""
強化版Notion検索モジュール

複数キーワード検索、リレーション活用、スコアリングによる高精度Notion検索
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# クエリ拡張モジュールをインポート
try:
    from utils.query_expander import query_expander
    QUERY_EXPANDER_AVAILABLE = True
except ImportError:
    QUERY_EXPANDER_AVAILABLE = False
    print("⚠️ query_expander のインポートに失敗しました")


class NotionSearchEnhanced:
    """強化版Notion検索クラス"""
    
    def __init__(self, notion_client):
        """
        初期化
        
        Args:
            notion_client: Notionクライアントインスタンス
        """
        self.notion = notion_client
    
    def extract_keywords_from_query(self, query: str) -> List[str]:
        """
        クエリからキーワードを抽出
        
        Args:
            query: 検索クエリ
        
        Returns:
            キーワードのリスト
        """
        keywords = []
        
        # query_expanderを使用してキーワード抽出
        if QUERY_EXPANDER_AVAILABLE:
            keywords = query_expander.extract_keywords(query)
        
        # 追加のキーワード抽出（簡易版）
        # 助詞を除外して名詞を抽出
        query_words = query.split()
        stop_words = ['が', 'を', 'に', 'は', 'の', 'で', 'と', 'や', 'から', 'まで', 'へ']
        
        for word in query_words:
            # 助詞を除外
            cleaned_word = word
            for stop in stop_words:
                cleaned_word = cleaned_word.replace(stop, '')
            
            if len(cleaned_word) > 1 and cleaned_word not in keywords:
                keywords.append(cleaned_word)
        
        # 重複排除
        keywords = list(set(keywords))
        
        return keywords
    
    def search_with_multiple_keywords(
        self,
        database_id: str,
        keywords: List[str],
        property_names: List[str] = None
    ) -> List[Dict]:
        """
        複数キーワードでNotion検索
        
        Args:
            database_id: データベースID
            keywords: キーワードのリスト
            property_names: 検索対象のプロパティ名リスト
        
        Returns:
            検索結果のリスト
        """
        if not property_names:
            # デフォルトの検索対象プロパティ
            property_names = ['タイトル', '内容', '症状', '解決方法', 'Title']
        
        all_results = []
        seen_ids = set()
        
        for keyword in keywords:
            try:
                # 各プロパティで検索
                for prop_name in property_names:
                    # プロパティタイプに応じたフィルター構築
                    filter_conditions = []
                    
                    # タイトルプロパティ
                    if prop_name in ['タイトル', 'Title', 'Name']:
                        filter_conditions.append({
                            "property": prop_name,
                            "title": {"contains": keyword}
                        })
                    else:
                        # リッチテキストプロパティ
                        filter_conditions.append({
                            "property": prop_name,
                            "rich_text": {"contains": keyword}
                        })
                    
                    for condition in filter_conditions:
                        try:
                            results = self.notion.databases.query(
                                database_id=database_id,
                                filter=condition
                            )
                            
                            for result in results.get("results", []):
                                result_id = result['id']
                                if result_id not in seen_ids:
                                    seen_ids.add(result_id)
                                    result['matched_keyword'] = keyword
                                    result['matched_property'] = prop_name
                                    all_results.append(result)
                        
                        except Exception as e:
                            print(f"⚠️ プロパティ '{prop_name}' での検索エラー: {e}")
                            continue
            
            except Exception as e:
                print(f"⚠️ キーワード '{keyword}' での検索エラー: {e}")
                continue
        
        return all_results
    
    def get_related_items_via_relation(
        self,
        page: Dict,
        relation_property: str,
        max_depth: int = 1
    ) -> List[Dict]:
        """
        リレーションを辿って関連アイテムを取得
        
        Args:
            page: Notionページ
            relation_property: リレーションプロパティ名
            max_depth: 最大探索深度
        
        Returns:
            関連アイテムのリスト
        """
        related_items = []
        
        try:
            # リレーションプロパティを取得
            relations = page.get('properties', {}).get(relation_property, {}).get('relation', [])
            
            for relation in relations:
                try:
                    # 関連ページを取得
                    related_page_id = relation['id']
                    related_page = self.notion.pages.retrieve(page_id=related_page_id)
                    
                    related_items.append({
                        'page': related_page,
                        'relation_type': relation_property,
                        'depth': 1
                    })
                    
                    # 深度2以上の場合は再帰的に取得
                    if max_depth > 1:
                        deeper_items = self.get_related_items_via_relation(
                            related_page,
                            relation_property,
                            max_depth - 1
                        )
                        for item in deeper_items:
                            item['depth'] += 1
                        related_items.extend(deeper_items)
                
                except Exception as e:
                    print(f"⚠️ 関連ページ取得エラー: {e}")
                    continue
        
        except Exception as e:
            print(f"⚠️ リレーション取得エラー: {e}")
        
        return related_items
    
    def calculate_relevance_score(
        self,
        page: Dict,
        query: str,
        keywords: List[str]
    ) -> float:
        """
        ページの関連性スコアを計算
        
        Args:
            page: Notionページ
            query: 元のクエリ
            keywords: キーワードのリスト
        
        Returns:
            関連性スコア（0.0〜1.0）
        """
        score = 0.0
        properties = page.get('properties', {})
        
        # 1. タイトルマッチ（重要度: 高）
        title = self._get_property_text(properties, 'タイトル')
        if not title:
            title = self._get_property_text(properties, 'Title')
        
        if title:
            title_lower = title.lower()
            
            # 完全一致
            if query.lower() in title_lower:
                score += 0.5
            
            # キーワードマッチ
            keyword_matches = sum(1 for kw in keywords if kw.lower() in title_lower)
            if keyword_matches > 0:
                score += 0.3 * (keyword_matches / len(keywords))
        
        # 2. 内容マッチ（重要度: 中）
        content_properties = ['内容', '症状', '解決方法', 'Content', 'Description']
        for prop_name in content_properties:
            content = self._get_property_text(properties, prop_name)
            if content:
                content_lower = content.lower()
                
                # キーワードマッチ
                keyword_matches = sum(1 for kw in keywords if kw.lower() in content_lower)
                if keyword_matches > 0:
                    score += 0.15 * (keyword_matches / len(keywords))
                    break  # 最初にマッチしたコンテンツのみカウント
        
        # 3. カテゴリマッチ（重要度: 中）
        category = self._get_property_select(properties, 'カテゴリ')
        if not category:
            category = self._get_property_select(properties, 'Category')
        
        if category:
            if any(kw.lower() in category.lower() for kw in keywords):
                score += 0.2
        
        # 4. ステータス（重要度: 低）
        status = self._get_property_select(properties, 'ステータス')
        if not status:
            status = self._get_property_select(properties, 'Status')
        
        if status and status in ['完了', '解決済み', 'Completed']:
            score += 0.1  # 完了した案件は信頼性が高い
        
        # 5. 最新性（重要度: 低）
        updated_time = page.get('last_edited_time')
        if updated_time:
            recency_score = self._calculate_recency_score(updated_time)
            score += recency_score * 0.1
        
        return min(score, 1.0)
    
    def _calculate_recency_score(self, timestamp: str) -> float:
        """
        最新性スコアを計算
        
        Args:
            timestamp: タイムスタンプ文字列
        
        Returns:
            最新性スコア（0.0〜1.0）
        """
        try:
            # ISO 8601形式のタイムスタンプをパース
            updated_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(updated_time.tzinfo)
            
            # 経過日数を計算
            days_old = (now - updated_time).days
            
            # スコア計算（新しいほど高スコア）
            if days_old <= 7:
                return 1.0  # 1週間以内
            elif days_old <= 30:
                return 0.8  # 1ヶ月以内
            elif days_old <= 90:
                return 0.6  # 3ヶ月以内
            elif days_old <= 180:
                return 0.4  # 6ヶ月以内
            elif days_old <= 365:
                return 0.2  # 1年以内
            else:
                return 0.1  # 1年以上
        
        except Exception as e:
            print(f"⚠️ 最新性スコア計算エラー: {e}")
            return 0.5  # デフォルト値
    
    def _get_property_text(self, properties: Dict, property_name: str) -> str:
        """プロパティからテキストを取得"""
        prop = properties.get(property_name, {})
        
        # タイトルプロパティ
        if prop.get('type') == 'title':
            title_list = prop.get('title', [])
            if title_list:
                return ''.join([t.get('plain_text', '') for t in title_list])
        
        # リッチテキストプロパティ
        elif prop.get('type') == 'rich_text':
            rich_text_list = prop.get('rich_text', [])
            if rich_text_list:
                return ''.join([t.get('plain_text', '') for t in rich_text_list])
        
        return ''
    
    def _get_property_select(self, properties: Dict, property_name: str) -> str:
        """プロパティからセレクト値を取得"""
        prop = properties.get(property_name, {})
        
        if prop.get('type') == 'select':
            select_obj = prop.get('select')
            if select_obj:
                return select_obj.get('name', '')
        
        return ''
    
    def search_notion_databases(
        self,
        query: str,
        databases: Dict[str, str],
        max_results_per_db: int = 10,
        min_relevance: float = 0.6,
        use_relations: bool = True
    ) -> Dict[str, Any]:
        """
        複数のNotionデータベースを横断検索
        
        Args:
            query: 検索クエリ
            databases: データベース名とIDの辞書
            max_results_per_db: データベースごとの最大結果数
            min_relevance: 最小関連性スコア
            use_relations: リレーションを活用するか
        
        Returns:
            検索結果の辞書
        """
        start_time = time.time()
        
        print(f"🔍 強化版Notion検索開始: クエリ='{query}'")
        
        # 1. キーワード抽出
        keywords = self.extract_keywords_from_query(query)
        print(f"📝 抽出キーワード: {keywords}")
        
        all_results = {
            'cases': [],
            'nodes': [],
            'items': [],
            'factories': [],
            'builders': [],
            'metadata': {
                'query': query,
                'keywords': keywords,
                'databases_searched': list(databases.keys())
            }
        }
        
        # 2. 各データベースを検索
        for db_name, db_id in databases.items():
            try:
                print(f"📂 {db_name} を検索中...")
                
                # 複数キーワードで検索
                results = self.search_with_multiple_keywords(
                    database_id=db_id,
                    keywords=keywords
                )
                
                print(f"  取得: {len(results)}件")
                
                # スコアリング
                scored_results = []
                for result in results:
                    relevance_score = self.calculate_relevance_score(
                        result,
                        query,
                        keywords
                    )
                    
                    if relevance_score >= min_relevance:
                        result['relevance_score'] = relevance_score
                        result['database_name'] = db_name
                        scored_results.append(result)
                
                # スコア順でソート
                scored_results.sort(
                    key=lambda x: x['relevance_score'],
                    reverse=True
                )
                
                # 最大件数に制限
                scored_results = scored_results[:max_results_per_db]
                
                print(f"  フィルタリング後: {len(scored_results)}件（スコア>={min_relevance}）")
                
                # 3. リレーションを活用（オプション）
                if use_relations and scored_results:
                    print(f"  リレーションを探索中...")
                    
                    for result in scored_results[:3]:  # 上位3件のみ
                        # 関連アイテムを取得
                        relation_properties = ['工場', '使用部品', '関連ケース', 'Factory', 'Parts']
                        
                        for rel_prop in relation_properties:
                            related = self.get_related_items_via_relation(
                                result,
                                rel_prop,
                                max_depth=1
                            )
                            
                            if related:
                                result[f'related_{rel_prop}'] = related
                                print(f"    {rel_prop}: {len(related)}件の関連アイテム")
                
                # 4. 結果を分類
                if 'case' in db_name.lower() or 'ケース' in db_name:
                    all_results['cases'].extend(scored_results)
                elif 'node' in db_name.lower() or 'ノード' in db_name or 'flow' in db_name.lower():
                    all_results['nodes'].extend(scored_results)
                elif 'item' in db_name.lower() or 'アイテム' in db_name or 'parts' in db_name.lower():
                    all_results['items'].extend(scored_results)
                elif 'factory' in db_name.lower() or '工場' in db_name:
                    all_results['factories'].extend(scored_results)
                elif 'builder' in db_name.lower() or 'ビルダー' in db_name:
                    all_results['builders'].extend(scored_results)
            
            except Exception as e:
                print(f"⚠️ {db_name} の検索エラー: {e}")
                continue
        
        duration = time.time() - start_time
        
        # 統計情報を追加
        all_results['metadata']['duration'] = round(duration, 2)
        all_results['metadata']['total_results'] = (
            len(all_results['cases']) +
            len(all_results['nodes']) +
            len(all_results['items']) +
            len(all_results['factories']) +
            len(all_results['builders'])
        )
        
        print(f"✅ Notion検索完了: {all_results['metadata']['total_results']}件 ({duration:.2f}秒)")
        
        return all_results


# グローバル関数（簡易版）
def create_enhanced_notion_search(notion_client):
    """強化版Notion検索インスタンスを作成"""
    return NotionSearchEnhanced(notion_client)


if __name__ == "__main__":
    print("=== 強化版Notion検索モジュール ===")
    print("✅ モジュールが正常にロードされました")
    
    if QUERY_EXPANDER_AVAILABLE:
        print("✅ クエリ拡張機能が利用可能です")
    else:
        print("⚠️ クエリ拡張機能は利用できません（基本機能のみ）")

