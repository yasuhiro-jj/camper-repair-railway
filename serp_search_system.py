#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERP検索システム
Google Custom Search APIを使用したリアルタイム情報取得と最新の修理情報・部品価格検索
"""

import os
import json
import requests
import time
from typing import List, Dict, Optional, Any
import logging
from urllib.parse import quote_plus, urlparse
import re

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SERPSearchSystem:
    """SERP検索システムクラス"""
    
    def __init__(self):
        """SERP検索システムの初期化"""
        self.google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("SERP_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.serp_api_key = os.getenv("SERP_API_KEY")
        
        # 検索エンジンの設定
        self.search_engines = {
            'google_custom': {
                'enabled': bool(self.google_api_key and self.google_cse_id),
                'api_key': self.google_api_key,
                'cse_id': self.google_cse_id,
                'base_url': 'https://www.googleapis.com/customsearch/v1'
            },
            'serp_api': {
                'enabled': bool(self.serp_api_key and self._validate_serp_api_key()),
                'api_key': self.serp_api_key,
                'base_url': 'https://serpapi.com/search'
            }
        }
        
        # キャンピングカー関連の検索クエリ最適化
        self.query_optimizers = {
            'repair_info': self._optimize_repair_query,
            'parts_price': self._optimize_parts_price_query,
            'general_info': self._optimize_general_query
        }
        
        # 信頼できるドメインリスト（日本語サイトを優先）
        self.trusted_domains = [
            # 日本の主要ECサイト
            'amazon.co.jp', 'rakuten.co.jp', 'yahoo.co.jp', 'mercari.com', 'auctions.yahoo.co.jp',
            'paypaymall.yahoo.co.jp', 'shopping.yahoo.co.jp', 'zozo.jp', 'uniqlo.com',
            
            # キャンピングカー関連サイト
            'camper-repair.net', 'titan-rv.com', 'rvparts.com', 'campingworld.com',
            'etrailer.com', 'rvupgradestore.com', 'rvlife.com', 'rvtravel.com',
            
            # 自動車部品サイト
            'auto-parts.com', 'parts.com', 'autoparts.com', 'partssource.com',
            'napaonline.com', 'oreillyauto.com', 'autozone.com', 'pepboys.com',
            'advanceautoparts.com', 'carquest.com', 'rockauto.com', 'summitracing.com',
            'jegs.com', 'speedwaymotors.com', 'partsgiant.com', 'partsgeek.com',
            'autopartswarehouse.com', 'partstrain.com', 'carparts.com',
            'autopartscheap.com', 'partzilla.com',
            
            # マリン・RV関連
            'boats.net', 'marineengine.com', 'iboats.com', 'wholesalemarine.com',
            
            # 一般的な情報サイト
            'wikipedia.org', 'youtube.com', 'google.com', 'bing.com',
            'allabout.co.jp', 'kakaku.com', 'price.com', 'kakaku.com',
            
            # 技術情報サイト
            'stackoverflow.com', 'github.com', 'qiita.com', 'teratail.com',
            
            # ニュース・ブログサイト
            'nikkei.com', 'asahi.com', 'mainichi.jp', 'yomiuri.co.jp',
            'hatena.ne.jp', 'ameblo.jp', 'fc2.com', 'livedoor.com'
        ]
        
        logger.info(f"SERP検索システム初期化完了 - Google Custom Search: {self.search_engines['google_custom']['enabled']}, SERP API: {self.search_engines['serp_api']['enabled']}")
    
    def _validate_serp_api_key(self) -> bool:
        """SERP APIキーの有効性を検証"""
        if not self.serp_api_key:
            return False
        
        try:
            # 簡単なテストリクエストでAPIキーを検証
            test_params = {
                'api_key': self.serp_api_key,
                'q': 'test',
                'engine': 'google',
                'gl': 'jp',
                'hl': 'ja',
                'num': 1
            }
            
            response = requests.get(
                'https://serpapi.com/search',
                params=test_params,
                timeout=5
            )
            
            # 401エラーの場合は無効なAPIキー
            if response.status_code == 401:
                logger.warning("SERP APIキーが無効です。Google Custom Search APIのみを使用します。")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"SERP APIキーの検証中にエラーが発生しました: {str(e)}")
            return False
    
    def _optimize_repair_query(self, query: str) -> str:
        """修理情報検索用クエリの最適化"""
        # キャンピングカー修理関連のキーワードを追加
        repair_keywords = [
            "キャンピングカー", "RV", "修理", "故障", "トラブル",
            "メンテナンス", "点検", "交換", "修理方法"
        ]
        
        # クエリに修理関連キーワードが含まれていない場合は追加
        query_lower = query.lower()
        if not any(keyword in query_lower for keyword in repair_keywords):
            optimized_query = f"{query} キャンピングカー 修理 方法"
        else:
            optimized_query = query
        
        return optimized_query
    
    def _optimize_parts_price_query(self, query: str) -> str:
        """部品価格検索用クエリの最適化"""
        # 価格検索関連のキーワードを追加
        price_keywords = [
            "価格", "値段", "料金", "費用", "コスト",
            "購入", "通販", "販売", "在庫", "新品"
        ]
        
        query_lower = query.lower()
        if not any(keyword in query_lower for keyword in price_keywords):
            optimized_query = f"{query} 価格 通販 購入"
        else:
            optimized_query = query
        
        return optimized_query
    
    def _optimize_general_query(self, query: str) -> str:
        """一般的な情報検索用クエリの最適化"""
        # 一般的な情報検索用のキーワードを追加
        general_keywords = [
            "情報", "詳細", "仕様", "特徴", "比較",
            "レビュー", "口コミ", "評価", "おすすめ"
        ]
        
        query_lower = query.lower()
        if not any(keyword in query_lower for keyword in general_keywords):
            optimized_query = f"{query} キャンピングカー 情報"
        else:
            optimized_query = query
        
        return optimized_query
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """クエリの意図を分析"""
        query_lower = query.lower()
        
        intent_analysis = {
            'type': 'general',
            'confidence': 0.5,
            'keywords': [],
            'search_type': 'general_info'
        }
        
        # 修理関連の意図検出
        repair_indicators = [
            '修理', '故障', 'トラブル', '不具合', '問題', '異常',
            '動かない', '回らない', '出ない', '流れない', '漏れる',
            '切れる', '入らない', '鳴る', '発生', '異音', '騒音'
        ]
        
        if any(indicator in query_lower for indicator in repair_indicators):
            intent_analysis['type'] = 'repair'
            intent_analysis['confidence'] = 0.8
            intent_analysis['search_type'] = 'repair_info'
            intent_analysis['keywords'].extend([kw for kw in repair_indicators if kw in query_lower])
        
        # 価格・購入関連の意図検出
        price_indicators = [
            '価格', '値段', '料金', '費用', 'コスト', '購入', '買う',
            '通販', '販売', '在庫', '新品', '中古', '安い', '高い'
        ]
        
        if any(indicator in query_lower for indicator in price_indicators):
            intent_analysis['type'] = 'price'
            intent_analysis['confidence'] = 0.7
            intent_analysis['search_type'] = 'parts_price'
            intent_analysis['keywords'].extend([kw for kw in price_indicators if kw in query_lower])
        
        # 部品・製品関連の意図検出
        parts_indicators = [
            'バッテリー', 'インバーター', 'トイレ', 'ファン', 'ポンプ',
            'ヒーター', 'エアコン', '冷蔵庫', 'ガスコンロ', 'LED',
            'タイヤ', 'ソーラーパネル', 'ルーフベント', '窓', 'ドア'
        ]
        
        if any(indicator in query_lower for indicator in parts_indicators):
            intent_analysis['keywords'].extend([kw for kw in parts_indicators if kw in query_lower])
            if intent_analysis['type'] == 'general':
                intent_analysis['type'] = 'parts'
                intent_analysis['confidence'] = 0.6
        
        return intent_analysis
    
    def _search_google_custom(self, query: str, search_type: str = 'general_info') -> List[Dict[str, Any]]:
        """Google Custom Search APIを使用した検索"""
        if not self.search_engines['google_custom']['enabled']:
            return []
        
        try:
            # クエリ最適化
            optimized_query = self.query_optimizers.get(search_type, self._optimize_general_query)(query)
            
            # 検索パラメータ
            params = {
                'key': self.search_engines['google_custom']['api_key'],
                'cx': self.search_engines['google_custom']['cse_id'],
                'q': optimized_query,
                'num': 10,
                'lr': 'lang_ja',  # 日本語検索
                'safe': 'medium',
                'sort': 'date' if search_type == 'repair_info' else 'relevance'
            }
            
            # キャンピングカー関連サイトに限定（コメントアウトしてより広範囲に検索）
            # if search_type in ['repair_info', 'parts_price']:
            #     params['siteSearch'] = 'amazon.co.jp OR rakuten.co.jp OR yahoo.co.jp OR mercari.com OR auctions.yahoo.co.jp'
            
            response = requests.get(
                self.search_engines['google_custom']['base_url'],
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Google Custom Search API レスポンス: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                return self._parse_google_results(data, search_type)
            else:
                logger.warning(f"Google Custom Search API エラー: {response.status_code}")
                logger.warning(f"レスポンス内容: {response.text[:200]}...")
                return []
                
        except Exception as e:
            logger.error(f"Google Custom Search エラー: {str(e)}")
            return []
    
    def _search_serp_api(self, query: str, search_type: str = 'general_info') -> List[Dict[str, Any]]:
        """SERP APIを使用した検索"""
        if not self.search_engines['serp_api']['enabled']:
            return []
        
        try:
            # クエリ最適化
            optimized_query = self.query_optimizers.get(search_type, self._optimize_general_query)(query)
            
            # 検索パラメータ
            params = {
                'api_key': self.search_engines['serp_api']['api_key'],
                'q': optimized_query,
                'engine': 'google',
                'gl': 'jp',  # 日本
                'hl': 'ja',  # 日本語
                'num': 10
            }
            
            # 検索タイプに応じた追加パラメータ
            if search_type == 'parts_price':
                params['tbm'] = 'shop'  # ショッピング検索
            elif search_type == 'repair_info':
                params['tbs'] = 'qdr:m'  # 過去1ヶ月
            
            response = requests.get(
                self.search_engines['serp_api']['base_url'],
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_serp_results(data, search_type)
            elif response.status_code == 401:
                logger.warning("SERP API認証エラー: APIキーが無効です。新しいAPIキーを取得してください。")
                return []
            else:
                logger.warning(f"SERP API エラー: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"SERP API エラー: {str(e)}")
            return []
    
    def _parse_google_results(self, data: Dict[str, Any], search_type: str) -> List[Dict[str, Any]]:
        """Google検索結果の解析"""
        results = []
        
        if 'items' not in data:
            logger.warning("Google検索結果に'items'が含まれていません")
            return results
        
        logger.info(f"Google検索結果: {len(data['items'])}件のアイテムを処理中")
        
        for item in data['items']:
            # 信頼できるドメインかチェック（緩和版）
            domain = urlparse(item.get('link', '')).netloc.lower()
            content = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
            
            # より緩いフィルタリング条件
            is_trusted_domain = any(domain.endswith(trusted_domain) for trusted_domain in self.trusted_domains)
            has_camper_keywords = any(keyword in content for keyword in ['キャンピングカー', 'rv', 'camper', 'キャンピング', '車中泊', 'バンライフ', 'モーターホーム', 'バッテリー', '修理', '故障'])
            
            # 信頼できるドメインまたは関連キーワードがある場合は含める
            if not is_trusted_domain and not has_camper_keywords:
                logger.debug(f"フィルタリング: {item.get('title', '')[:50]}... (ドメイン: {domain})")
                continue
            
            result = {
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': 'google_custom',
                'search_type': search_type,
                'domain': domain,
                'relevance_score': self._calculate_relevance_score(item, search_type)
            }
            
            # 価格情報の抽出（ショッピング検索の場合）
            if search_type == 'parts_price':
                result['price_info'] = self._extract_price_info(item)
            
            results.append(result)
            logger.debug(f"結果追加: {result['title'][:50]}... (関連度: {result['relevance_score']:.2f})")
        
        logger.info(f"Google検索結果解析完了: {len(results)}件の結果")
        return results
    
    def _parse_serp_results(self, data: Dict[str, Any], search_type: str) -> List[Dict[str, Any]]:
        """SERP API検索結果の解析"""
        results = []
        
        # 通常の検索結果
        if 'organic_results' in data:
            for item in data['organic_results']:
                domain = urlparse(item.get('link', '')).netloc.lower()
                # 信頼できるドメインでない場合でも、キャンピングカー関連キーワードがあれば含める
                if not any(domain.endswith(trusted_domain) for trusted_domain in self.trusted_domains):
                    # キャンピングカー関連キーワードをチェック
                    content = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
                    camper_keywords = ['キャンピングカー', 'rv', 'camper', 'キャンピング', '車中泊', 'バンライフ', 'モーターホーム']
                    if not any(keyword in content for keyword in camper_keywords):
                        continue
                
                result = {
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'serp_api',
                    'search_type': search_type,
                    'domain': domain,
                    'relevance_score': self._calculate_relevance_score(item, search_type)
                }
                
                results.append(result)
        
        # ショッピング結果
        if 'shopping_results' in data and search_type == 'parts_price':
            for item in data['shopping_results']:
                domain = urlparse(item.get('link', '')).netloc.lower()
                # ショッピング結果はより緩くフィルタリング
                if not any(domain.endswith(trusted_domain) for trusted_domain in self.trusted_domains):
                    # 価格情報がある場合は含める
                    if not any(keyword in item.get('title', '').lower() for keyword in ['価格', '円', '¥', 'price']):
                        continue
                
                result = {
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'serp_api_shopping',
                    'search_type': search_type,
                    'domain': domain,
                    'relevance_score': self._calculate_relevance_score(item, search_type),
                    'price_info': self._extract_price_info(item)
                }
                
                results.append(result)
        
        return results
    
    def _calculate_relevance_score(self, item: Dict[str, Any], search_type: str) -> float:
        """関連度スコアの計算"""
        score = 0.5  # ベーススコア
        
        title = item.get('title', '').lower()
        snippet = item.get('snippet', '').lower()
        content = f"{title} {snippet}"
        
        # キャンピングカー関連キーワード
        camper_keywords = [
            'キャンピングカー', 'rv', 'camper', 'キャンピング', '車中泊',
            'バンライフ', 'モーターホーム', 'トレーラー'
        ]
        
        for keyword in camper_keywords:
            if keyword in content:
                score += 0.1
        
        # 修理関連キーワード
        repair_keywords = [
            '修理', '故障', 'トラブル', '不具合', '問題', '異常',
            'メンテナンス', '点検', '交換', '修理方法'
        ]
        
        for keyword in repair_keywords:
            if keyword in content:
                score += 0.05
        
        # 価格関連キーワード
        price_keywords = [
            '価格', '値段', '料金', '費用', 'コスト', '購入',
            '通販', '販売', '在庫', '新品', '中古'
        ]
        
        for keyword in price_keywords:
            if keyword in content:
                score += 0.05
        
        # ドメインの信頼度
        domain = urlparse(item.get('link', '')).netloc.lower()
        if any(domain.endswith(trusted_domain) for trusted_domain in self.trusted_domains):
            score += 0.2
        
        return min(score, 1.0)
    
    def _extract_price_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """価格情報の抽出"""
        price_info = {
            'price': None,
            'currency': 'JPY',
            'availability': None,
            'rating': None
        }
        
        # 価格の抽出
        price_patterns = [
            r'¥([\d,]+)',
            r'(\d{1,3}(?:,\d{3})*)円',
            r'(\d+\.\d{2})\s*USD',
            r'(\d+)\s*円'
        ]
        
        content = f"{item.get('title', '')} {item.get('snippet', '')}"
        
        for pattern in price_patterns:
            match = re.search(pattern, content)
            if match:
                price_info['price'] = match.group(1).replace(',', '')
                break
        
        # 在庫情報の抽出
        availability_patterns = [
            r'在庫あり', r'在庫なし', r'入荷待ち', r'販売中',
            r'在庫切れ', r'予約受付中', r'取り寄せ'
        ]
        
        for pattern in availability_patterns:
            if re.search(pattern, content):
                price_info['availability'] = pattern
                break
        
        # 評価の抽出
        rating_pattern = r'(\d+\.\d+)\s*★|(\d+\.\d+)\s*星|評価\s*(\d+\.\d+)'
        rating_match = re.search(rating_pattern, content)
        if rating_match:
            price_info['rating'] = rating_match.group(1) or rating_match.group(2) or rating_match.group(3)
        
        return price_info
    
    def search(self, query: str, search_types: List[str] = None) -> Dict[str, Any]:
        """統合検索の実行"""
        if not query.strip():
            return {'error': '検索クエリが空です'}
        
        # クエリ意図の分析
        intent_analysis = self._analyze_query_intent(query)
        
        # 検索タイプの決定
        if search_types is None:
            search_types = [intent_analysis['search_type']]
        
        all_results = []
        
        # 各検索エンジンで検索実行
        for search_type in search_types:
            # Google Custom Search
            google_results = self._search_google_custom(query, search_type)
            all_results.extend(google_results)
            
            # SERP API
            serp_results = self._search_serp_api(query, search_type)
            all_results.extend(serp_results)
            
            # API制限を考慮した待機
            time.sleep(0.5)
        
        # 結果の統合と重複除去
        unique_results = self._deduplicate_results(all_results)
        
        # 関連度順でソート
        unique_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return {
            'query': query,
            'intent_analysis': intent_analysis,
            'results': unique_results[:15],  # 上位15件
            'total_found': len(unique_results),
            'search_engines_used': [
                engine for engine, config in self.search_engines.items() 
                if config['enabled']
            ]
        }
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重複結果の除去"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def get_realtime_repair_info(self, query: str) -> Dict[str, Any]:
        """リアルタイム修理情報の取得"""
        return self.search(query, ['repair_info'])
    
    def get_parts_price_info(self, query: str) -> Dict[str, Any]:
        """部品価格情報の取得"""
        return self.search(query, ['parts_price'])
    
    def get_comprehensive_info(self, query: str) -> Dict[str, Any]:
        """包括的な情報取得"""
        return self.search(query, ['repair_info', 'parts_price', 'general_info'])


# グローバルインスタンス
serp_search_system = None

def get_serp_search_system() -> SERPSearchSystem:
    """SERP検索システムのインスタンスを取得"""
    global serp_search_system
    if serp_search_system is None:
        serp_search_system = SERPSearchSystem()
    return serp_search_system

def search_with_serp(query: str, search_type: str = 'comprehensive') -> Dict[str, Any]:
    """SERP検索の実行"""
    system = get_serp_search_system()
    
    if search_type == 'repair':
        return system.get_realtime_repair_info(query)
    elif search_type == 'price':
        return system.get_parts_price_info(query)
    else:
        return system.get_comprehensive_info(query)
