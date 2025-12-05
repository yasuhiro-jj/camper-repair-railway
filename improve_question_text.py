#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フェーズ2-3: 質問文の自然化機能
診断フローの質問文をAIで改善し、より親しみやすく自然な表現にする
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
    print("[WARNING] OpenAIライブラリが利用できません")


class QuestionImprover:
    """質問文を改善するクラス"""
    
    def __init__(self):
        self.client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                print("[SUCCESS] OpenAIクライアントを初期化しました")
            else:
                print("[WARNING] OPENAI_API_KEYが設定されていません")
    
    def improve_question_text(
        self,
        original_question: str,
        category: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        質問文を自然な表現に改善
        
        Args:
            original_question: 元の質問文
            category: カテゴリ（バッテリー、エアコンなど）
            context: 追加コンテキスト
        
        Returns:
            改善結果（改善後の質問、理由、代替案など）
        """
        
        if not self.client:
            return {
                "original": original_question,
                "improved": original_question,
                "reason": "OpenAIクライアントが利用できません",
                "success": False
            }
        
        # プロンプトを構築
        prompt = self._build_improvement_prompt(original_question, category, context)
        
        try:
            # OpenAI APIを呼び出し
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはキャンピングカーの修理診断システムの質問文を改善する専門家です。"
                                   "ユーザーフレンドリーで親しみやすく、わかりやすい質問文を作成してください。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # レスポンスを解析
            improved_text = response.choices[0].message.content.strip()
            result = self._parse_improvement_result(improved_text, original_question)
            result["success"] = True
            
            return result
        
        except Exception as e:
            print(f"[ERROR] OpenAI API呼び出しエラー: {e}")
            return {
                "original": original_question,
                "improved": original_question,
                "reason": f"エラー: {str(e)}",
                "success": False
            }
    
    def _build_improvement_prompt(
        self,
        original_question: str,
        category: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """改善プロンプトを構築"""
        
        prompt = f"""以下の診断質問を、より親しみやすく自然な表現に改善してください。

【元の質問】
{original_question}

【カテゴリ】
{category if category else '一般'}

【改善方針】
1. 親しみやすく、共感的な表現にする
2. 専門用語を避け、一般の方にもわかりやすい言葉を使う
3. 短く簡潔に（50文字以内を目標）
4. 疑問形で終わる
5. ユーザーが答えやすい質問にする

【出力形式】
以下のJSON形式で出力してください：
{{
  "improved": "改善後の質問文",
  "reason": "改善理由",
  "alternatives": ["代替案1", "代替案2"]
}}

専門用語の平易化例：
- コンプレッサー → 圧縮機 or エアコンの心臓部
- オルタネーター → 発電機
- インバーター → 電圧変換器
- ソレノイド → 電磁スイッチ

表現の改善例：
- 「作動状態を確認してください」→ 「動いていますか？」
- 「異音が発生していますか」→ 「変な音がしますか？」
- 「電圧低下の症状はありますか」→ 「電気が弱くなっていませんか？」
"""
        
        if context:
            prompt += f"\n【追加情報】\n{json.dumps(context, ensure_ascii=False, indent=2)}"
        
        return prompt
    
    def _parse_improvement_result(
        self,
        api_response: str,
        original_question: str
    ) -> Dict[str, Any]:
        """API レスポンスを解析"""
        
        try:
            # JSON形式のレスポンスを期待
            if "{" in api_response and "}" in api_response:
                # JSON部分を抽出
                json_start = api_response.find("{")
                json_end = api_response.rfind("}") + 1
                json_str = api_response[json_start:json_end]
                
                result = json.loads(json_str)
                result["original"] = original_question
                return result
            else:
                # JSON形式でない場合は、テキストをそのまま使用
                return {
                    "original": original_question,
                    "improved": api_response,
                    "reason": "自動改善",
                    "alternatives": []
                }
        
        except json.JSONDecodeError:
            # JSON解析失敗時は、テキストをそのまま使用
            return {
                "original": original_question,
                "improved": api_response,
                "reason": "自動改善",
                "alternatives": []
            }
    
    def improve_batch(
        self,
        questions: List[Dict[str, Any]],
        max_questions: int = 10
    ) -> List[Dict[str, Any]]:
        """複数の質問を一括で改善"""
        
        results = []
        total = min(len(questions), max_questions)
        
        print(f"[INFO] {total}件の質問を改善します...\n")
        
        for i, question_data in enumerate(questions[:max_questions], 1):
            question = question_data.get("question", "")
            category = question_data.get("category", "")
            node_id = question_data.get("id", "")
            
            if not question:
                continue
            
            print(f"[{i}/{total}] 改善中: {node_id}")
            print(f"  元の質問: {question[:50]}{'...' if len(question) > 50 else ''}")
            
            result = self.improve_question_text(question, category)
            
            if result["success"]:
                print(f"  改善後: {result['improved'][:50]}{'...' if len(result['improved']) > 50 else ''}")
                print(f"  理由: {result.get('reason', '')}\n")
            else:
                print(f"  [WARNING] 改善失敗: {result.get('reason', '')}\n")
            
            result["node_id"] = node_id
            result["category"] = category
            results.append(result)
        
        return results
    
    def save_improvements(
        self,
        improvements: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> str:
        """改善結果をJSONファイルに保存"""
        
        if not filename:
            filename = f"improved_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(improvements, f, ensure_ascii=False, indent=2)
        
        print(f"[SAVED] 改善結果を保存しました: {filename}")
        return filename


def load_diagnostic_data_from_file(filename: str) -> Dict[str, Any]:
    """ファイルから診断データを読み込み"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"[ERROR] ファイル読み込みエラー: {e}")
        return {"nodes": []}


def create_sample_questions() -> List[Dict[str, Any]]:
    """サンプル質問を作成（テスト用）"""
    return [
        {
            "id": "sample-001",
            "question": "エアコンコンプレッサーの作動状態を確認してください。異音が発生していますか？",
            "category": "エアコン"
        },
        {
            "id": "sample-002",
            "question": "バッテリーの電圧降下の症状はありますか？エンジン始動時に電圧が低下しますか？",
            "category": "バッテリー"
        },
        {
            "id": "sample-003",
            "question": "水道ポンプの動作は正常ですか？水圧が弱い、または水が出ない症状がありますか？",
            "category": "水道ポンプ"
        },
        {
            "id": "sample-004",
            "question": "FFヒーターの燃焼状態を確認してください。炎が弱い、または異常燃焼の症状はありますか？",
            "category": "FFヒーター"
        },
        {
            "id": "sample-005",
            "question": "インバーターの出力電圧は正常ですか？AC100V出力時に電圧変動がありますか？",
            "category": "インバーター"
        }
    ]


def main():
    """メイン処理"""
    print("[START] 質問文改善ツールを起動しました\n", flush=True)
    
    # QuestionImproverを初期化
    improver = QuestionImprover()
    
    # サンプル質問で テスト
    print("[INFO] サンプル質問で改善をテストします...\n")
    sample_questions = create_sample_questions()
    
    # 質問を改善
    improvements = improver.improve_batch(sample_questions, max_questions=5)
    
    # 結果を保存
    filename = improver.save_improvements(improvements)
    
    # サマリーを表示
    print("\n[SUMMARY] 改善サマリー:")
    print(f"  - 処理した質問数: {len(improvements)}")
    success_count = sum(1 for imp in improvements if imp.get("success", False))
    print(f"  - 成功: {success_count}件")
    print(f"  - 失敗: {len(improvements) - success_count}件")
    
    print("\n[INFO] 実際の診断データで改善する場合:")
    print("  1. export_diagnostic_data.pyで診断データをエクスポート")
    print("  2. このスクリプトを修正して、エクスポートしたJSONファイルを読み込み")
    print("  3. 全質問を一括改善")
    
    print("\n[COMPLETE] 処理完了！")


if __name__ == "__main__":
    main()

