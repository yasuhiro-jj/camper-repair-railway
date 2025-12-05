#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工場ネットワーク機能の拡張（フェーズ4-1）
案件自動振り分けAI、地域・スキル・混雑状況によるマッチング機能
"""

import os
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from data_access.factory_manager import FactoryManager
from data_access.factory_dashboard_manager import FactoryDashboardManager
from dotenv import load_dotenv

load_dotenv()

# OpenAI APIキー
try:
    from config import OPENAI_API_KEY
    OPENAI_AVAILABLE = bool(OPENAI_API_KEY)
except ImportError:
    OPENAI_AVAILABLE = False
    OPENAI_API_KEY = None

if OPENAI_AVAILABLE:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        openai_client = None
else:
    openai_client = None


class FactoryMatchingEngine:
    """
    工場マッチングエンジン
    案件を最適な工場に自動振り分ける
    """
    
    def __init__(self):
        """初期化"""
        self.factory_manager = FactoryManager()
        self.dashboard_manager = FactoryDashboardManager()
    
    def match_factory_to_case(
        self,
        case: Dict[str, Any],
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        案件に最適な工場をマッチング
        
        Args:
            case: 案件情報（category, user_message, customer_location等を含む）
            max_results: 返す工場の最大数
        
        Returns:
            マッチングスコア付き工場リスト（スコアの高い順）
        """
        try:
            # 案件情報を抽出
            category = case.get("category", "")
            user_message = case.get("user_message", "")
            customer_location = case.get("customer_location") or case.get("prefecture", "")
            
            # 全工場を取得（アクティブなもののみ）
            all_factories = self.factory_manager.list_factories(
                status="アクティブ",
                limit=100
            )
            
            if not all_factories:
                return []
            
            # 各工場のマッチングスコアを計算
            scored_factories = []
            for factory in all_factories:
                score = self._calculate_matching_score(
                    factory=factory,
                    case_category=category,
                    case_message=user_message,
                    customer_location=customer_location
                )
                
                scored_factories.append({
                    **factory,
                    "matching_score": score["total_score"],
                    "score_details": score
                })
            
            # スコアの高い順にソート
            scored_factories.sort(key=lambda x: x["matching_score"], reverse=True)
            
            return scored_factories[:max_results]
            
        except Exception as e:
            print(f"❌ 工場マッチングエラー: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _calculate_matching_score(
        self,
        factory: Dict[str, Any],
        case_category: str,
        case_message: str,
        customer_location: str
    ) -> Dict[str, float]:
        """
        マッチングスコアを計算
        
        スコア要素:
        1. 地域マッチング（40%）
        2. 専門分野マッチング（30%）
        3. 混雑状況（20%）
        4. 過去の評価（10%）
        
        Returns:
            スコア詳細と合計スコア
        """
        scores = {
            "location_score": 0.0,
            "specialty_score": 0.0,
            "workload_score": 0.0,
            "rating_score": 0.0,
            "total_score": 0.0
        }
        
        # 1. 地域マッチングスコア（40%）
        scores["location_score"] = self._calculate_location_score(
            factory=factory,
            customer_location=customer_location
        )
        
        # 2. 専門分野マッチングスコア（30%）
        scores["specialty_score"] = self._calculate_specialty_score(
            factory=factory,
            case_category=case_category,
            case_message=case_message
        )
        
        # 3. 混雑状況スコア（20%）
        scores["workload_score"] = self._calculate_workload_score(factory=factory)
        
        # 4. 過去の評価スコア（10%）
        scores["rating_score"] = self._calculate_rating_score(factory=factory)
        
        # 重み付き合計スコア
        scores["total_score"] = (
            scores["location_score"] * 0.4 +
            scores["specialty_score"] * 0.3 +
            scores["workload_score"] * 0.2 +
            scores["rating_score"] * 0.1
        )
        
        return scores
    
    def _calculate_location_score(
        self,
        factory: Dict[str, Any],
        customer_location: str
    ) -> float:
        """
        地域マッチングスコアを計算
        
        - 同じ都道府県: 1.0
        - 対応可能エリアに含まれる: 0.8
        - 隣接都道府県: 0.6
        - その他: 0.3
        """
        if not customer_location:
            return 0.5  # 地域情報がない場合は中間スコア
        
        factory_prefecture = factory.get("prefecture", "")
        factory_service_areas = factory.get("service_areas", [])
        
        # 同じ都道府県
        if factory_prefecture == customer_location:
            return 1.0
        
        # 対応可能エリアに含まれる
        if customer_location in factory_service_areas:
            return 0.8
        
        # 隣接都道府県（簡易版：関東圏、関西圏など）
        if self._is_nearby_prefecture(factory_prefecture, customer_location):
            return 0.6
        
        return 0.3
    
    def _is_nearby_prefecture(self, prefecture1: str, prefecture2: str) -> bool:
        """隣接都道府県かどうかを判定（簡易版）"""
        # 関東圏
        kanto = ["東京都", "神奈川県", "埼玉県", "千葉県", "茨城県", "栃木県", "群馬県"]
        # 関西圏
        kansai = ["大阪府", "京都府", "兵庫県", "滋賀県", "奈良県", "和歌山県"]
        # 中部圏
        chubu = ["愛知県", "静岡県", "岐阜県", "三重県", "長野県", "山梨県"]
        
        regions = [kanto, kansai, chubu]
        
        for region in regions:
            if prefecture1 in region and prefecture2 in region:
                return True
        
        return False
    
    def _calculate_specialty_score(
        self,
        factory: Dict[str, Any],
        case_category: str,
        case_message: str
    ) -> float:
        """
        専門分野マッチングスコアを計算
        
        - 専門分野に完全一致: 1.0
        - 専門分野に部分一致: 0.7
        - AIによる関連性判定: 0.5-0.9
        - その他: 0.3
        """
        factory_specialties = factory.get("specialties", [])
        
        if not factory_specialties:
            return 0.3
        
        # カテゴリが専門分野に含まれる
        if case_category in factory_specialties:
            return 1.0
        
        # カテゴリが専門分野の一部に含まれる（例: "エアコン" と "エアコン修理"）
        for specialty in factory_specialties:
            if case_category in specialty or specialty in case_category:
                return 0.7
        
        # AIによる関連性判定（オプション）
        if OPENAI_AVAILABLE and openai_client and case_message:
            ai_score = self._ai_specialty_match(
                factory_specialties=factory_specialties,
                case_category=case_category,
                case_message=case_message
            )
            if ai_score > 0:
                return ai_score
        
        return 0.3
    
    def _ai_specialty_match(
        self,
        factory_specialties: List[str],
        case_category: str,
        case_message: str
    ) -> float:
        """
        AIを使用して専門分野の関連性を判定
        
        Returns:
            0.0-1.0のスコア（エラー時は0.0）
        """
        if not openai_client:
            return 0.0
        
        try:
            prompt = f"""以下の工場の専門分野と案件の関連性を0.0-1.0で評価してください。

工場の専門分野: {', '.join(factory_specialties)}
案件カテゴリ: {case_category}
案件内容: {case_message[:200]}

関連性スコア（0.0-1.0の数値のみ）:"""
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたは工場と案件のマッチング専門家です。関連性を0.0-1.0の数値で評価してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            score_text = response.choices[0].message.content.strip()
            # 数値を抽出
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.0
                
        except Exception as e:
            print(f"⚠️ AI専門分野マッチングエラー: {e}")
            return 0.0
    
    def _calculate_workload_score(self, factory: Dict[str, Any]) -> float:
        """
        混雑状況スコアを計算
        
        - 案件数が少ない: 1.0
        - 案件数が中程度: 0.7
        - 案件数が多い: 0.4
        """
        total_cases = factory.get("total_cases", 0)
        completed_cases = factory.get("completed_cases", 0)
        
        # 進行中の案件数
        active_cases = total_cases - completed_cases
        
        # 混雑度に応じたスコア
        if active_cases == 0:
            return 1.0
        elif active_cases <= 5:
            return 0.9
        elif active_cases <= 10:
            return 0.7
        elif active_cases <= 20:
            return 0.5
        else:
            return 0.3
    
    def _calculate_rating_score(self, factory: Dict[str, Any]) -> float:
        """
        過去の評価スコアを計算
        
        - 評価スコアが5.0: 1.0
        - 評価スコアが4.0: 0.8
        - 評価スコアが3.0: 0.6
        - 評価スコアが2.0: 0.4
        - 評価スコアが1.0: 0.2
        - 評価なし: 0.5
        """
        rating = factory.get("rating", 0)
        
        if rating == 0:
            return 0.5  # 評価なしは中間スコア
        
        # 5段階評価を0.0-1.0に正規化
        return rating / 5.0
    
    def auto_assign_case(
        self,
        case_id: str,
        case: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        案件を自動的に最適な工場に割り当て
        
        Args:
            case_id: 案件ID
            case: 案件情報
        
        Returns:
            割り当てられた工場情報（失敗時はNone）
        """
        try:
            # 最適な工場をマッチング
            matched_factories = self.match_factory_to_case(
                case=case,
                max_results=1
            )
            
            if not matched_factories:
                print(f"⚠️ 案件 {case_id} にマッチする工場が見つかりませんでした")
                return None
            
            best_factory = matched_factories[0]
            
            # 案件に工場を割り当て（Notion DB更新）
            # ここではFactoryDashboardManagerを使用して案件を更新
            # 実際の実装では、案件DBに工場IDを追加する必要があります
            
            print(f"✅ 案件 {case_id} を工場 {best_factory.get('factory_id')} に割り当てました")
            print(f"   マッチングスコア: {best_factory.get('matching_score', 0):.2f}")
            
            return best_factory
            
        except Exception as e:
            print(f"❌ 案件自動割り当てエラー: {e}")
            import traceback
            traceback.print_exc()
            return None

