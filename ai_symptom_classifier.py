#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フェーズ2-3: AI症状分類機能
ユーザーの自由記述から症状カテゴリを自動判定する
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# UTF-8エンコーディングを設定
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 環境変数を読み込み
load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SymptomClassifier:
    """症状を自動分類するクラス"""
    
    def __init__(self):
        self.client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
        
        # カテゴリ定義（キャンピングカー修理）
        self.categories = {
            "エアコン": {
                "keywords": ["エアコン", "冷房", "暖房", "温度", "コンプレッサー", "冷却", "風"],
                "description": "エアコンの冷暖房機能に関する問題"
            },
            "バッテリー": {
                "keywords": ["バッテリー", "充電", "電圧", "放電", "始動", "電源"],
                "description": "バッテリーの充電・放電に関する問題"
            },
            "水道ポンプ": {
                "keywords": ["水", "ポンプ", "水圧", "蛇口", "給水", "水道"],
                "description": "水道ポンプや給水システムの問題"
            },
            "トイレ": {
                "keywords": ["トイレ", "便器", "水洗", "排水", "タンク"],
                "description": "トイレ設備に関する問題"
            },
            "雨漏り": {
                "keywords": ["雨漏り", "水漏れ", "浸水", "シーリング", "防水"],
                "description": "雨漏りや水漏れに関する問題"
            },
            "FFヒーター": {
                "keywords": ["ヒーター", "暖房", "燃焼", "炎", "FF"],
                "description": "FFヒーターの暖房機能に関する問題"
            },
            "インバーター": {
                "keywords": ["インバーター", "AC", "電源", "変換", "電圧"],
                "description": "インバーターや電源変換に関する問題"
            },
            "冷蔵庫": {
                "keywords": ["冷蔵庫", "冷凍", "冷却", "温度管理"],
                "description": "冷蔵庫の冷却機能に関する問題"
            },
            "ソーラーパネル": {
                "keywords": ["ソーラー", "太陽光", "発電", "パネル"],
                "description": "ソーラーパネルの発電に関する問題"
            },
            "ドア・窓": {
                "keywords": ["ドア", "窓", "開閉", "鍵", "蝶番"],
                "description": "ドアや窓の開閉に関する問題"
            },
            "その他": {
                "keywords": [],
                "description": "上記に当てはまらない問題"
            }
        }
    
    def classify_symptom(
        self,
        user_description: str,
        use_ai: bool = True,
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        ユーザーの症状説明からカテゴリを判定
        
        Args:
            user_description: ユーザーの症状説明
            use_ai: AI判定を使用するかどうか
            confidence_threshold: 確信度の閾値
        
        Returns:
            判定結果（カテゴリ、確信度、理由など）
        """
        
        if use_ai and self.client:
            return self._classify_with_ai(user_description, confidence_threshold)
        else:
            return self._classify_with_keywords(user_description)
    
    def _classify_with_ai(
        self,
        user_description: str,
        confidence_threshold: float
    ) -> Dict[str, Any]:
        """AIで症状を分類"""
        
        try:
            prompt = self._build_classification_prompt(user_description)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはキャンピングカーの修理診断の専門家です。"
                                   "ユーザーの症状説明から、最も適切なカテゴリを判定してください。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # 低めの温度で一貫性を保つ
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            result = self._parse_classification_result(result_text)
            
            # 確信度が閾値以下の場合は曖昧と判定
            if result["confidence"] < confidence_threshold:
                result["needs_clarification"] = True
                result["clarification_questions"] = self._generate_clarification_questions(
                    user_description,
                    result["category"]
                )
            
            return result
        
        except Exception as e:
            print(f"AI分類エラー: {e}", file=sys.stderr)
            return self._classify_with_keywords(user_description)
    
    def _build_classification_prompt(self, user_description: str) -> str:
        """分類プロンプトを構築"""
        
        categories_list = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.categories.items()
        ])
        
        prompt = f"""ユーザーの症状説明から、最も適切なカテゴリを1つ選択してください。

【ユーザーの症状説明】
{user_description}

【カテゴリ一覧】
{categories_list}

【出力形式】
以下のJSON形式で出力してください：
{{
  "category": "カテゴリ名",
  "confidence": 0.0-1.0の確信度,
  "reason": "判定理由（50文字以内）",
  "keywords_found": ["見つかったキーワード1", "見つかったキーワード2"]
}}

【注意事項】
- confidenceは必ず0.0から1.0の数値で指定
- 明確に判定できない場合はconfidenceを低めに設定
- reasonは簡潔に（50文字以内）
"""
        
        return prompt
    
    def _parse_classification_result(self, result_text: str) -> Dict[str, Any]:
        """AI分類結果を解析"""
        
        try:
            # JSON部分を抽出
            if "{" in result_text and "}" in result_text:
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                json_str = result_text[json_start:json_end]
                
                result = json.loads(json_str)
                
                # 必須フィールドの検証
                if "category" not in result:
                    result["category"] = "その他"
                if "confidence" not in result:
                    result["confidence"] = 0.5
                if "reason" not in result:
                    result["reason"] = "AI判定"
                if "keywords_found" not in result:
                    result["keywords_found"] = []
                
                result["method"] = "ai"
                return result
            else:
                # JSON形式でない場合
                return {
                    "category": "その他",
                    "confidence": 0.3,
                    "reason": "判定不可",
                    "keywords_found": [],
                    "method": "ai_fallback"
                }
        
        except json.JSONDecodeError:
            return {
                "category": "その他",
                "confidence": 0.3,
                "reason": "解析エラー",
                "keywords_found": [],
                "method": "ai_error"
            }
    
    def _classify_with_keywords(self, user_description: str) -> Dict[str, Any]:
        """キーワードマッチングで症状を分類"""
        
        description_lower = user_description.lower()
        scores = {}
        
        # 各カテゴリのキーワードマッチング
        for category_name, category_info in self.categories.items():
            if category_name == "その他":
                continue
            
            keywords = category_info["keywords"]
            matched_keywords = [
                kw for kw in keywords
                if kw.lower() in description_lower
            ]
            
            scores[category_name] = {
                "score": len(matched_keywords),
                "keywords": matched_keywords
            }
        
        # 最高スコアのカテゴリを選択
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1]["score"])
            category_name = best_category[0]
            category_score = best_category[1]
            
            if category_score["score"] > 0:
                confidence = min(category_score["score"] / 3.0, 1.0)  # 最大3つのキーワードで正規化
                
                return {
                    "category": category_name,
                    "confidence": confidence,
                    "reason": f"{len(category_score['keywords'])}個のキーワードが一致",
                    "keywords_found": category_score["keywords"],
                    "method": "keyword"
                }
        
        # マッチなしの場合
        return {
            "category": "その他",
            "confidence": 0.2,
            "reason": "キーワードが見つかりませんでした",
            "keywords_found": [],
            "method": "keyword_fallback"
        }
    
    def _generate_clarification_questions(
        self,
        user_description: str,
        possible_category: str
    ) -> List[str]:
        """曖昧な症状に対する追加質問を生成"""
        
        clarification_questions = {
            "エアコン": [
                "エアコンをつけた時の症状ですか？",
                "冷房と暖房、どちらの使用時ですか？"
            ],
            "バッテリー": [
                "エンジンの始動に問題がありますか？",
                "電圧計の表示は確認できますか？"
            ],
            "水道ポンプ": [
                "蛇口から水は出ますか？",
                "ポンプの動作音は聞こえますか？"
            ],
            "FFヒーター": [
                "ヒーターの電源は入りますか？",
                "燃焼音や炎は確認できますか？"
            ]
        }
        
        return clarification_questions.get(possible_category, [
            "もう少し詳しく教えていただけますか？",
            "いつから症状が出ていますか？"
        ])
    
    def classify_with_multi_candidates(
        self,
        user_description: str,
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        複数の候補カテゴリを確信度順に返す
        
        Args:
            user_description: ユーザーの症状説明
            top_n: 返す候補数
        
        Returns:
            確信度順にソートされたカテゴリリスト
        """
        
        description_lower = user_description.lower()
        candidates = []
        
        # キーワードマッチングで全カテゴリをスコアリング
        for category_name, category_info in self.categories.items():
            if category_name == "その他":
                continue
            
            keywords = category_info["keywords"]
            matched_keywords = [
                kw for kw in keywords
                if kw.lower() in description_lower
            ]
            
            if matched_keywords:
                score = len(matched_keywords)
                confidence = min(score / 3.0, 1.0)
                
                candidates.append({
                    "category": category_name,
                    "confidence": confidence,
                    "keywords_found": matched_keywords,
                    "description": category_info["description"]
                })
        
        # 確信度順にソート
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        
        return candidates[:top_n]


def test_symptom_classifier():
    """症状分類のテスト"""
    
    classifier = SymptomClassifier()
    
    # テストケース
    test_cases = [
        "エアコンが冷えません。コンプレッサーの音もしません。",
        "バッテリーが上がりやすく、エンジンがかかりにくいです。",
        "水道の水圧が弱くて、シャワーが使えません。",
        "トイレの水が流れなくなりました。",
        "雨が降ると天井から水が漏れてきます。",
        "なんか調子が悪いんです。"  # 曖昧なケース
    ]
    
    print("[TEST] 症状分類テスト（キーワードベース）\n")
    
    for i, description in enumerate(test_cases, 1):
        print(f"[{i}] 症状: {description}")
        
        result = classifier.classify_symptom(description, use_ai=False)
        
        print(f"  カテゴリ: {result['category']}")
        print(f"  確信度: {result['confidence']:.2f}")
        print(f"  理由: {result['reason']}")
        print(f"  キーワード: {', '.join(result['keywords_found'])}")
        print()
        
        # 複数候補も表示
        if result['confidence'] < 0.7:
            print("  [追加] 他の可能性:")
            candidates = classifier.classify_with_multi_candidates(description)
            for j, candidate in enumerate(candidates[:3], 1):
                print(f"    {j}. {candidate['category']} ({candidate['confidence']:.2f})")
            print()


def main():
    """メイン処理"""
    test_symptom_classifier()


if __name__ == "__main__":
    main()

