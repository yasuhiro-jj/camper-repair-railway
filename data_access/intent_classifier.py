#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意図分類モジュール（Phase 3）
LangChainを使用したユーザー意図の分類
"""

from typing import Dict, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import json

# カテゴリ定義（ロードマップ準拠）
CATEGORIES = [
    "バッテリー",
    "電気系統",
    "水回り",
    "雨漏り",
    "冷却・エアコン",
    "FFヒーター",
    "トイレ",
    "その他"
]

class IntentClassifier:
    """意図分類クラス（ロードマップ準拠）"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        意図分類器を初期化
        
        Args:
            openai_api_key: OpenAI APIキー（環境変数から取得可能）
        """
        import os
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI APIキーが設定されていません")
        
        self.model = ChatOpenAI(
            api_key=self.openai_api_key,
            model_name="gpt-4o-mini",
            temperature=0.3  # 分類の一貫性を保つため低めに設定
        )
        
        # 分類用プロンプト
        self.classification_prompt = ChatPromptTemplate.from_messages([
            ("system", """あなたはキャンピングカー修理の専門家です。
ユーザーの質問を以下のカテゴリに分類してください：

カテゴリ一覧：
- バッテリー: バッテリー関連（充電、電圧、始動不良など）
- 電気系統: 電気配線、コンセント、スイッチ、LEDなど
- 水回り: 給水、排水、ポンプ、蛇口など
- 雨漏り: 水漏れ、シーリング、屋根など
- 冷却・エアコン: エアコン、冷蔵庫の冷却機能など
- FFヒーター: FFヒーター、暖房システムなど
- トイレ: トイレ関連のトラブル
- その他: 上記に該当しない場合

分類結果はJSON形式で返してください：
{{"category": "カテゴリ名", "confidence": 0.0-1.0, "keywords": ["キーワード1", "キーワード2"]}}"""),
            ("human", "{question}")
        ])
        
        self.parser = JsonOutputParser()
    
    def classify(self, question: str) -> Dict[str, any]:
        """
        ユーザーの質問を分類
        
        Args:
            question: ユーザーの質問
        
        Returns:
            Dict: {
                "category": str,
                "confidence": float,
                "keywords": List[str]
            }
        """
        try:
            chain = self.classification_prompt | self.model | self.parser
            result = chain.invoke({"question": question})
            
            # 結果の検証と正規化
            category = result.get("category", "その他")
            confidence = float(result.get("confidence", 0.5))
            keywords = result.get("keywords", [])
            
            # カテゴリが有効か確認
            if category not in CATEGORIES:
                category = "その他"
                confidence = 0.3
            
            return {
                "category": category,
                "confidence": confidence,
                "keywords": keywords[:5] if isinstance(keywords, list) else []
            }
        except Exception as e:
            print(f"⚠️ 意図分類エラー（フォールバック）: {e}")
            # フォールバック: 簡易キーワードマッチング
            return self._fallback_classify(question)
    
    def _fallback_classify(self, question: str) -> Dict[str, any]:
        """フォールバック分類（簡易キーワードマッチング）"""
        question_lower = question.lower()
        
        # キーワードマッチング
        category_keywords = {
            "バッテリー": ["バッテリー", "充電", "電圧", "始動", "上がり"],
            "電気系統": ["電気", "配線", "コンセント", "スイッチ", "led", "照明"],
            "水回り": ["水", "給水", "排水", "ポンプ", "蛇口", "タンク"],
            "雨漏り": ["雨漏り", "水漏れ", "シーリング", "屋根", "天井"],
            "冷却・エアコン": ["エアコン", "冷房", "冷蔵庫", "冷却"],
            "FFヒーター": ["ffヒーター", "ff", "ヒーター", "暖房"],
            "トイレ": ["トイレ", "便器", "水洗"]
        }
        
        best_category = "その他"
        best_score = 0
        
        for cat, keywords in category_keywords.items():
            score = sum(1 for kw in keywords if kw in question_lower)
            if score > best_score:
                best_score = score
                best_category = cat
        
        # キーワード抽出
        import re
        japanese_words = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', question)
        keywords = [w for w in japanese_words if len(w) >= 2][:5]
        
        confidence = min(0.5 + (best_score * 0.1), 0.9) if best_score > 0 else 0.3
        
        return {
            "category": best_category,
            "confidence": confidence,
            "keywords": keywords
        }


def get_confidence_level(confidence: float) -> str:
    """
    信頼度をlow/medium/highに変換
    
    Args:
        confidence: 0.0-1.0の信頼度スコア
    
    Returns:
        str: "low", "medium", "high"
    """
    if confidence >= 0.7:
        return "high"
    elif confidence >= 0.4:
        return "medium"
    else:
        return "low"

