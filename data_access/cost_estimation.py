#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI工賃推定エンジン（フェーズ4-4）
症状から工賃・作業時間・部品代をAIで推定する機能
"""

import os
import re
from typing import Dict, Optional, Any, List
from datetime import datetime
from data_access.notion_client import NotionClient
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


class CostEstimationEngine:
    """
    AI工賃推定エンジン
    症状から工賃・作業時間・部品代を推定
    """
    
    def __init__(self):
        """初期化"""
        self.notion_client = NotionClient()
        
        # デフォルトの工賃単価（時間あたり）
        self.default_hourly_rate = 8000  # 円/時間
        
        # 難易度別の工賃倍率
        self.difficulty_multipliers = {
            "初級": 0.8,
            "中級": 1.0,
            "上級": 1.5
        }
    
    def estimate_cost(
        self,
        symptoms: str,
        category: Optional[str] = None,
        vehicle_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        症状から工賃・作業時間・部品代を推定
        
        Args:
            symptoms: 症状の詳細説明
            category: 症状カテゴリ（オプション）
            vehicle_info: 車両情報（オプション）
        
        Returns:
            推定結果（工賃、作業時間、部品代など）
        """
        try:
            # 1. Notionから類似ケースを検索
            similar_cases = self._search_similar_cases(symptoms, category)
            
            # 2. AIで工賃を推定
            estimation = self._ai_estimate_cost(
                symptoms=symptoms,
                category=category,
                vehicle_info=vehicle_info,
                similar_cases=similar_cases
            )
            
            # 3. 類似ケースのデータで補正
            if similar_cases:
                estimation = self._adjust_with_similar_cases(
                    estimation=estimation,
                    similar_cases=similar_cases
                )
            
            return estimation
            
        except Exception as e:
            print(f"❌ 工賃推定エラー: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_estimation(category)
    
    def _search_similar_cases(
        self,
        symptoms: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Notionから類似ケースを検索
        """
        try:
            # 修理ケースDBから検索
            case_db_id = os.getenv("CASE_DB_ID")
            if not case_db_id:
                return []
            
            # クエリを作成
            query = symptoms
            if category:
                query = f"{category} {symptoms}"
            
            # Notionで検索（簡易版：タイトルと症状詳細で検索）
            # 実際の実装では、NotionClientに検索機能を追加する必要があります
            # ここでは、全ケースを取得してフィルタリング
            
            all_cases = self.notion_client.get_all_pages(case_db_id, limit=50)
            
            # 類似度でソート（簡易版：キーワードマッチング）
            similar_cases = []
            keywords = self._extract_keywords(symptoms)
            
            for case in all_cases:
                case_text = self._get_case_text(case)
                match_score = self._calculate_match_score(keywords, case_text)
                
                if match_score > 0.3:  # 30%以上の類似度
                    similar_cases.append({
                        **case,
                        "match_score": match_score
                    })
            
            # スコアの高い順にソート
            similar_cases.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            
            return similar_cases[:5]  # 上位5件
            
        except Exception as e:
            print(f"⚠️ 類似ケース検索エラー: {e}")
            return []
    
    def _ai_estimate_cost(
        self,
        symptoms: str,
        category: Optional[str],
        vehicle_info: Optional[str],
        similar_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        AIを使って工賃を推定
        """
        if not openai_client:
            return self._get_default_estimation(category)
        
        try:
            # 類似ケースの情報を整理
            similar_cases_info = ""
            if similar_cases:
                similar_cases_info = "\n\n【類似ケースの参考情報】\n"
                for i, case in enumerate(similar_cases[:3], 1):
                    case_title = case.get("properties", {}).get("タイトル", {}).get("title", [{}])[0].get("plain_text", "")
                    case_cost = self._extract_cost_from_case(case)
                    similar_cases_info += f"{i}. {case_title}\n"
                    if case_cost:
                        similar_cases_info += f"   費用: {case_cost}\n"
            
            # プロンプトを作成
            prompt = f"""あなたはキャンピングカーの修理費用見積もりの専門家です。
以下の症状から、修理に必要な工賃・作業時間・部品代を推定してください。

【症状】
{symptoms}

【カテゴリ】
{category or "未指定"}

【車両情報】
{vehicle_info or "未指定"}
{similar_cases_info}

以下の形式でJSON形式で回答してください：
{{
    "estimated_work_hours": 2.5,
    "difficulty": "中級",
    "labor_cost_min": 15000,
    "labor_cost_max": 25000,
    "parts_cost_min": 5000,
    "parts_cost_max": 15000,
    "total_cost_min": 20000,
    "total_cost_max": 40000,
    "reasoning": "推定理由の説明"
}}

注意点：
- 作業時間は時間単位（例: 2.5時間）
- 難易度は「初級」「中級」「上級」のいずれか
- 費用は円単位で整数値
- 工賃は作業時間 × 時給（8,000円/時間）を基準に、難易度で調整
- 部品代は症状の複雑さを考慮
- 総額 = 工賃 + 部品代 + 診断料（3,000-5,000円）
"""
            
            # OpenAI APIを呼び出し
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはキャンピングカーの修理費用見積もりの専門家です。JSON形式で正確に回答してください。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # レスポンスをパース
            result_text = response.choices[0].message.content
            import json
            estimation = json.loads(result_text)
            
            # 診断料を追加
            diagnosis_fee = 4000  # デフォルト診断料
            estimation["diagnosis_fee"] = diagnosis_fee
            estimation["total_cost_min"] = estimation.get("labor_cost_min", 0) + estimation.get("parts_cost_min", 0) + diagnosis_fee
            estimation["total_cost_max"] = estimation.get("labor_cost_max", 0) + estimation.get("parts_cost_max", 0) + diagnosis_fee
            
            return estimation
            
        except Exception as e:
            print(f"⚠️ AI推定エラー: {e}")
            return self._get_default_estimation(category)
    
    def _adjust_with_similar_cases(
        self,
        estimation: Dict[str, Any],
        similar_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        類似ケースのデータで推定値を補正
        """
        try:
            # 類似ケースから費用情報を抽出
            costs = []
            for case in similar_cases:
                cost = self._extract_cost_from_case(case)
                if cost:
                    costs.append(cost)
            
            if not costs:
                return estimation
            
            # 平均値を計算
            avg_cost = sum(costs) / len(costs)
            
            # 推定値を補正（類似ケースの平均値とAI推定値の平均を取る）
            ai_total_min = estimation.get("total_cost_min", 0)
            ai_total_max = estimation.get("total_cost_max", 0)
            ai_total_avg = (ai_total_min + ai_total_max) / 2
            
            # 補正後の平均値
            adjusted_avg = (ai_total_avg + avg_cost) / 2
            
            # 範囲を調整
            adjustment_factor = adjusted_avg / ai_total_avg if ai_total_avg > 0 else 1.0
            
            estimation["total_cost_min"] = int(estimation.get("total_cost_min", 0) * adjustment_factor)
            estimation["total_cost_max"] = int(estimation.get("total_cost_max", 0) * adjustment_factor)
            estimation["similar_cases_count"] = len(costs)
            estimation["similar_cases_avg_cost"] = int(avg_cost)
            
            return estimation
            
        except Exception as e:
            print(f"⚠️ 補正エラー: {e}")
            return estimation
    
    def _extract_keywords(self, text: str) -> List[str]:
        """テキストからキーワードを抽出"""
        # 簡易版：名詞を抽出（実際は形態素解析を使用）
        keywords = []
        # 一般的な修理関連キーワード
        repair_keywords = [
            "エアコン", "バッテリー", "水漏れ", "雨漏り", "ドア", "窓",
            "トイレ", "冷蔵庫", "ガス", "電気", "エンジン", "ブレーキ",
            "交換", "修理", "故障", "不具合", "効かない", "動かない"
        ]
        
        for keyword in repair_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords
    
    def _get_case_text(self, case: Dict[str, Any]) -> str:
        """ケースからテキストを抽出"""
        text_parts = []
        
        # タイトル
        title = case.get("properties", {}).get("タイトル", {}).get("title", [{}])[0].get("plain_text", "")
        if title:
            text_parts.append(title)
        
        # 症状詳細
        symptoms = case.get("properties", {}).get("症状詳細", {}).get("rich_text", [{}])[0].get("plain_text", "")
        if symptoms:
            text_parts.append(symptoms)
        
        return " ".join(text_parts)
    
    def _calculate_match_score(self, keywords: List[str], text: str) -> float:
        """キーワードマッチングスコアを計算"""
        if not keywords:
            return 0.0
        
        matches = sum(1 for keyword in keywords if keyword in text)
        return matches / len(keywords) if keywords else 0.0
    
    def _extract_cost_from_case(self, case: Dict[str, Any]) -> Optional[int]:
        """ケースから費用情報を抽出"""
        try:
            # 費用フィールドを探す
            properties = case.get("properties", {})
            
            # 様々なフィールド名を試す
            cost_fields = ["費用", "工賃", "総額", "修理費用", "費用目安"]
            
            for field_name in cost_fields:
                if field_name in properties:
                    prop = properties[field_name]
                    
                    # Number型の場合
                    if "number" in prop:
                        cost = prop["number"]
                        if cost:
                            return int(cost)
                    
                    # Rich Text型の場合（テキストから数値を抽出）
                    if "rich_text" in prop:
                        text = prop["rich_text"][0].get("plain_text", "") if prop["rich_text"] else ""
                        cost = self._extract_number_from_text(text)
                        if cost:
                            return cost
            
            return None
            
        except Exception as e:
            print(f"⚠️ 費用抽出エラー: {e}")
            return None
    
    def _extract_number_from_text(self, text: str) -> Optional[int]:
        """テキストから数値を抽出"""
        # 数字を抽出（カンマ区切りも対応）
        numbers = re.findall(r'[\d,]+', text.replace(',', ''))
        if numbers:
            try:
                return int(numbers[0])
            except ValueError:
                return None
        return None
    
    def _get_default_estimation(self, category: Optional[str] = None) -> Dict[str, Any]:
        """デフォルトの推定値を返す"""
        # カテゴリ別のデフォルト値
        defaults = {
            "エアコン": {
                "estimated_work_hours": 3.0,
                "difficulty": "中級",
                "labor_cost_min": 20000,
                "labor_cost_max": 30000,
                "parts_cost_min": 10000,
                "parts_cost_max": 50000,
            },
            "バッテリー": {
                "estimated_work_hours": 1.0,
                "difficulty": "初級",
                "labor_cost_min": 2000,
                "labor_cost_max": 5000,
                "parts_cost_min": 6000,
                "parts_cost_max": 20000,
            },
            "水漏れ": {
                "estimated_work_hours": 2.0,
                "difficulty": "中級",
                "labor_cost_min": 10000,
                "labor_cost_max": 20000,
                "parts_cost_min": 3000,
                "parts_cost_max": 10000,
            },
        }
        
        default = defaults.get(category, {
            "estimated_work_hours": 2.0,
            "difficulty": "中級",
            "labor_cost_min": 10000,
            "labor_cost_max": 20000,
            "parts_cost_min": 5000,
            "parts_cost_max": 15000,
        })
        
        diagnosis_fee = 4000
        return {
            **default,
            "diagnosis_fee": diagnosis_fee,
            "total_cost_min": default["labor_cost_min"] + default["parts_cost_min"] + diagnosis_fee,
            "total_cost_max": default["labor_cost_max"] + default["parts_cost_max"] + diagnosis_fee,
            "reasoning": f"{category or '一般的な'}修理の標準的な費用見積もりです。",
            "similar_cases_count": 0
        }

