#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フェーズ2-3: フィードバックメッセージ生成機能
ユーザーの回答に対して適切なフィードバックメッセージを生成する
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional
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


class FeedbackGenerator:
    """診断フローのフィードバックメッセージを生成するクラス"""
    
    def __init__(self):
        self.client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
        
        # フィードバックテンプレート
        self.templates = {
            "symptom_confirmed": [
                "なるほど、{symptom}の症状ですね。",
                "了解しました。{symptom}についてもう少し詳しく教えてください。",
                "{symptom}ということですね。承知しました。"
            ],
            "urgency_high": [
                "この症状は緊急性が高いです。すぐに対処しましょう。",
                "危険な状態かもしれません。専門家に相談することをお勧めします。",
                "早めの対応が必要です。安全のため、使用を控えてください。"
            ],
            "simple_fix": [
                "この症状なら、ご自身で対処できるかもしれません。",
                "比較的簡単な修理で直る可能性があります。",
                "DIYで対応できそうな症状ですね。"
            ],
            "complex_issue": [
                "この症状は専門的な知識が必要です。",
                "プロの整備士に診てもらうことをお勧めします。",
                "専門店での点検が必要な症状です。"
            ],
            "reassurance": [
                "心配いりません。一つずつ確認していきましょう。",
                "大丈夫です。適切に対処すれば解決できます。",
                "落ち着いて対応すれば問題ありません。"
            ],
            "empathy": [
                "それは大変ですね。",
                "お困りのようですね。",
                "ご不便をおかけしています。"
            ],
            "next_step": [
                "次に{next_action}を確認しましょう。",
                "では、{next_action}について教えてください。",
                "{next_action}の状態を見てみましょう。"
            ],
            "positive": [
                "良い情報です！",
                "それなら安心ですね。",
                "問題なさそうですね。"
            ]
        }
    
    def generate_feedback(
        self,
        user_answer: str,
        question_context: Dict[str, Any],
        use_ai: bool = True
    ) -> str:
        """
        ユーザーの回答に対するフィードバックを生成
        
        Args:
            user_answer: ユーザーの回答
            question_context: 質問のコンテキスト（カテゴリ、緊急度など）
            use_ai: AI生成を使用するかどうか
        
        Returns:
            フィードバックメッセージ
        """
        
        if use_ai and self.client:
            return self._generate_ai_feedback(user_answer, question_context)
        else:
            return self._generate_template_feedback(user_answer, question_context)
    
    def _generate_ai_feedback(
        self,
        user_answer: str,
        question_context: Dict[str, Any]
    ) -> str:
        """AIでフィードバックを生成"""
        
        try:
            prompt = self._build_feedback_prompt(user_answer, question_context)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはキャンピングカーの修理診断システムのアシスタントです。"
                                   "ユーザーの回答に対して、共感的で親しみやすいフィードバックを提供してください。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            feedback = response.choices[0].message.content.strip()
            return feedback
        
        except Exception as e:
            print(f"AI生成エラー: {e}", file=sys.stderr)
            return self._generate_template_feedback(user_answer, question_context)
    
    def _build_feedback_prompt(
        self,
        user_answer: str,
        question_context: Dict[str, Any]
    ) -> str:
        """フィードバック生成プロンプトを構築"""
        
        category = question_context.get("category", "一般")
        urgency = question_context.get("urgency", "通常")
        symptom = question_context.get("symptom", "")
        
        prompt = f"""ユーザーの回答に対して、適切なフィードバックメッセージを生成してください。

【ユーザーの回答】
{user_answer}

【コンテキスト】
- カテゴリ: {category}
- 緊急度: {urgency}
- 症状: {symptom}

【フィードバックの要件】
1. 共感的で親しみやすい表現
2. 30文字以内の短いメッセージ
3. ユーザーを安心させる
4. 次のステップへの誘導（必要に応じて）

【出力】
フィードバックメッセージのみを出力してください（説明不要）。
"""
        
        return prompt
    
    def _generate_template_feedback(
        self,
        user_answer: str,
        question_context: Dict[str, Any]
    ) -> str:
        """テンプレートからフィードバックを生成"""
        
        urgency = question_context.get("urgency", "通常")
        category = question_context.get("category", "")
        symptom = question_context.get("symptom", user_answer)
        
        # 緊急度に応じてフィードバックを選択
        if urgency in ["高", "緊急"]:
            template_key = "urgency_high"
        elif "簡単" in str(question_context.get("difficulty", "")):
            template_key = "simple_fix"
        elif "複雑" in str(question_context.get("difficulty", "")):
            template_key = "complex_issue"
        else:
            template_key = "symptom_confirmed"
        
        # テンプレートから選択
        import random
        templates = self.templates.get(template_key, self.templates["symptom_confirmed"])
        feedback = random.choice(templates)
        
        # プレースホルダーを置換
        feedback = feedback.replace("{symptom}", symptom or "その症状")
        feedback = feedback.replace("{next_action}", question_context.get("next_action", "次の項目"))
        
        return feedback
    
    def generate_contextual_feedback(
        self,
        user_answer: str,
        current_node: Dict[str, Any],
        next_node: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        コンテキストに応じた詳細なフィードバックを生成
        
        Returns:
            フィードバック情報（メッセージ、アイコン、タイプなど）
        """
        
        question_context = {
            "category": current_node.get("category", ""),
            "urgency": current_node.get("urgency", "通常"),
            "symptom": user_answer
        }
        
        # フィードバックメッセージを生成
        message = self.generate_feedback(user_answer, question_context, use_ai=False)
        
        # フィードバックタイプを判定
        feedback_type = self._determine_feedback_type(current_node, user_answer)
        
        # アイコンを選択
        icon = self._select_icon(feedback_type)
        
        result = {
            "message": message,
            "type": feedback_type,
            "icon": icon,
            "show_urgency_warning": current_node.get("urgency") in ["高", "緊急"],
            "next_step_hint": self._generate_next_step_hint(current_node, next_node)
        }
        
        return result
    
    def _determine_feedback_type(
        self,
        node: Dict[str, Any],
        user_answer: str
    ) -> str:
        """フィードバックタイプを判定"""
        
        urgency = node.get("urgency", "通常")
        
        # キーワードマッチング
        answer_lower = user_answer.lower()
        
        if urgency in ["高", "緊急"]:
            return "warning"
        elif any(word in answer_lower for word in ["ない", "問題ない", "正常"]):
            return "positive"
        elif any(word in answer_lower for word in ["わからない", "不明"]):
            return "neutral"
        else:
            return "info"
    
    def _select_icon(self, feedback_type: str) -> str:
        """フィードバックタイプに応じたアイコンを選択"""
        
        icons = {
            "warning": "⚠️",
            "positive": "✅",
            "neutral": "ℹ️",
            "info": "💡",
            "empathy": "🤝",
            "reassurance": "😊"
        }
        
        return icons.get(feedback_type, "💬")
    
    def _generate_next_step_hint(
        self,
        current_node: Dict[str, Any],
        next_node: Optional[Dict[str, Any]]
    ) -> str:
        """次のステップのヒントを生成"""
        
        if not next_node:
            return "もう少しで診断が完了します。"
        
        next_category = next_node.get("category", "")
        if next_category:
            return f"次は{next_category}について確認します。"
        
        return "次の質問に進みます。"


def test_feedback_generator():
    """フィードバック生成のテスト"""
    
    generator = FeedbackGenerator()
    
    # テストケース
    test_cases = [
        {
            "user_answer": "エアコンから変な音がします",
            "context": {
                "category": "エアコン",
                "urgency": "中",
                "symptom": "異音"
            }
        },
        {
            "user_answer": "バッテリーが上がりやすい",
            "context": {
                "category": "バッテリー",
                "urgency": "高",
                "symptom": "充電不良"
            }
        },
        {
            "user_answer": "問題ありません",
            "context": {
                "category": "水道ポンプ",
                "urgency": "低",
                "symptom": "正常"
            }
        }
    ]
    
    print("[TEST] フィードバック生成テスト\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}] テストケース")
        print(f"  ユーザー回答: {test_case['user_answer']}")
        print(f"  カテゴリ: {test_case['context']['category']}")
        print(f"  緊急度: {test_case['context']['urgency']}")
        
        feedback = generator.generate_feedback(
            test_case["user_answer"],
            test_case["context"],
            use_ai=False  # テストではテンプレートを使用
        )
        
        print(f"  フィードバック: {feedback}")
        print()


def main():
    """メイン処理"""
    test_feedback_generator()


if __name__ == "__main__":
    main()

