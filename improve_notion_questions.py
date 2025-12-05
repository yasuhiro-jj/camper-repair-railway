#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フェーズ2-3: Notion診断フローの質問文を一括改善
Notionから直接読み込んで改善し、Notionに書き戻す
"""

import os
import json
import sys
import time
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

# 既存のモジュールをインポート
from improve_question_text import QuestionImprover
from unified_backend_api import load_notion_diagnostic_data, initialize_services

try:
    from notion_client import Client
    NOTION_CLIENT_AVAILABLE = True
except ImportError:
    NOTION_CLIENT_AVAILABLE = False
    print("[WARNING] notion-clientライブラリが利用できません")


class NotionQuestionUpdater:
    """Notionの質問文を更新するクラス"""
    
    def __init__(self):
        print("[DEBUG] NotionQuestionUpdaterを初期化中...")
        self.notion_client = None
        print("[DEBUG] QuestionImproverを初期化中...")
        self.question_improver = QuestionImprover()
        self.node_db_id = None
        print("[DEBUG] Notionクライアントを初期化中...")
        self._initialize_notion_client()
        print("[DEBUG] 初期化完了")
    
    def _initialize_notion_client(self):
        """Notionクライアントを初期化"""
        if not NOTION_CLIENT_AVAILABLE:
            print("[ERROR] notion-clientが利用できません")
            return
        
        notion_api_key = os.getenv("NOTION_API_KEY")
        if not notion_api_key:
            print("[ERROR] NOTION_API_KEYが設定されていません")
            return
        
        try:
            self.notion_client = Client(auth=notion_api_key)
            self.node_db_id = os.getenv("NODE_DB_ID")
            
            if not self.node_db_id:
                print("[ERROR] NODE_DB_IDが設定されていません")
                return
            
            print("[SUCCESS] Notionクライアントを初期化しました")
        except Exception as e:
            print(f"[ERROR] Notionクライアント初期化エラー: {e}")
    
    def load_questions_from_notion(self) -> List[Dict[str, Any]]:
        """Notionから質問を読み込み"""
        if not self.notion_client or not self.node_db_id:
            print("[ERROR] Notionクライアントが初期化されていません")
            return []
        
        try:
            print("[INFO] Notionから診断データを取得中...")
            
            # unified_backend_apiからデータを取得
            # サービスを初期化（Notionクライアントを含む）
            initialize_services()
            diagnostic_data = load_notion_diagnostic_data(force_reload=True)
            
            if not diagnostic_data:
                print("[ERROR] 診断データが取得できませんでした")
                return []
            
            nodes = diagnostic_data.get("nodes", [])
            print(f"[SUCCESS] {len(nodes)}件のノードを取得しました")
            
            # 質問文があるノードのみを抽出
            questions = []
            for node in nodes:
                question = node.get("question", "")
                if question and question.strip():
                    questions.append({
                        "id": node.get("id", ""),
                        "title": node.get("title", ""),
                        "question": question,
                        "category": node.get("category", ""),
                        "node": node  # 元のノードデータも保持
                    })
            
            print(f"[INFO] 質問文があるノード: {len(questions)}件")
            return questions
        
        except Exception as e:
            print(f"[ERROR] Notionデータ取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_page_properties(self, page_id: str) -> Dict[str, Any]:
        """Notionページのプロパティを取得（デバッグ用）"""
        if not self.notion_client:
            return {}
        
        try:
            page = self.notion_client.pages.retrieve(page_id=page_id)
            return page.get("properties", {})
        except Exception as e:
            print(f"[DEBUG] プロパティ取得エラー: {e}")
            return {}
    
    def update_question_in_notion(
        self,
        page_id: str,
        improved_question: str
    ) -> bool:
        """Notionのページの質問文を更新"""
        if not self.notion_client:
            return False
        
        # まずページのプロパティを確認（デバッグ用）
        page_properties = self._get_page_properties(page_id)
        question_property_names = [
            name for name in page_properties.keys() 
            if "質問" in name or "question" in name.lower()
        ]
        if question_property_names:
            print(f"[DEBUG] 見つかった質問プロパティ: {question_property_names}")
        
        # プロパティ名の候補（優先順位順）
        property_candidates = [
            "質問内容",  # notion_client.pyで確認済み
            "質問文",
            "Question",
            "question"
        ]
        
        # 実際のページに存在するプロパティ名を優先
        if question_property_names:
            property_candidates = question_property_names + property_candidates
        
        # 各候補を試す
        last_error = None
        for prop_name in property_candidates:
            try:
                properties = {
                    prop_name: {
                        "rich_text": [
                            {
                                "text": {
                                    "content": improved_question
                                }
                            }
                        ]
                    }
                }
                
                # ページを更新
                self.notion_client.pages.update(
                    page_id=page_id,
                    properties=properties
                )
                
                print(f"[SUCCESS] プロパティ '{prop_name}' で更新成功")
                return True
            
            except Exception as e:
                last_error = e
                continue  # 次の候補を試す
        
        # すべての候補が失敗した場合
        print(f"[ERROR] 質問文更新エラー (ID: {page_id[:8]}...): {last_error}")
        print(f"[DEBUG] 試したプロパティ名: {', '.join(property_candidates)}")
        if question_property_names:
            print(f"[DEBUG] ページに存在する質問関連プロパティ: {question_property_names}")
        return False
    
    def improve_and_update_all(
        self,
        dry_run: bool = True,
        max_questions: Optional[int] = None,
        filter_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        すべての質問を改善してNotionに反映
        
        Args:
            dry_run: Trueの場合は更新せず、改善結果のみを表示
            max_questions: 最大処理数（Noneの場合はすべて）
            filter_category: カテゴリでフィルタリング
        
        Returns:
            処理結果のサマリー
        """
        
        # 質問を読み込み
        questions = self.load_questions_from_notion()
        
        if not questions:
            print("[ERROR] 質問が見つかりませんでした")
            return {"success": False, "error": "質問が見つかりません"}
        
        # フィルタリング
        if filter_category:
            questions = [q for q in questions if q.get("category") == filter_category]
            print(f"[INFO] カテゴリ '{filter_category}' でフィルタリング: {len(questions)}件")
        
        # 最大数で制限
        if max_questions:
            questions = questions[:max_questions]
            print(f"[INFO] 最大{max_questions}件に制限")
        
        print(f"\n[INFO] {len(questions)}件の質問を改善します...")
        if dry_run:
            print("[WARNING] DRY RUNモード: Notionには更新しません\n")
        else:
            print("[WARNING] 本番モード: Notionに実際に更新します\n")
            response = input("続行しますか？ (yes/no): ")
            if response.lower() != "yes":
                print("[CANCEL] 処理をキャンセルしました")
                return {"success": False, "error": "ユーザーがキャンセル"}
        
        # 改善結果を保存
        improvements = []
        success_count = 0
        update_count = 0
        
        for i, question_data in enumerate(questions, 1):
            node_id = question_data.get("id", "")
            title = question_data.get("title", "")
            original_question = question_data.get("question", "")
            category = question_data.get("category", "")
            
            print(f"\n[{i}/{len(questions)}] 処理中: {title or node_id[:8]}")
            print(f"  カテゴリ: {category}")
            print(f"  元の質問: {original_question[:60]}{'...' if len(original_question) > 60 else ''}")
            
            # 質問を改善
            result = self.question_improver.improve_question_text(
                original_question,
                category
            )
            
            if result.get("success"):
                improved_question = result.get("improved", original_question)
                print(f"  改善後: {improved_question[:60]}{'...' if len(improved_question) > 60 else ''}")
                print(f"  理由: {result.get('reason', '')[:50]}")
                
                improvements.append({
                    "node_id": node_id,
                    "title": title,
                    "category": category,
                    "original": original_question,
                    "improved": improved_question,
                    "reason": result.get("reason", ""),
                    "success": True
                })
                success_count += 1
                
                # Notionに更新（dry_runでない場合）
                if not dry_run:
                    if self.update_question_in_notion(node_id, improved_question):
                        update_count += 1
                        print(f"  [SUCCESS] Notionに更新しました")
                        # APIレート制限を避けるため少し待機
                        time.sleep(0.5)
                    else:
                        print(f"  [ERROR] Notion更新に失敗しました")
            else:
                print(f"  [ERROR] 改善失敗: {result.get('reason', '')}")
                improvements.append({
                    "node_id": node_id,
                    "title": title,
                    "category": category,
                    "original": original_question,
                    "improved": original_question,
                    "reason": result.get("reason", ""),
                    "success": False
                })
        
        # 結果をJSONに保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"notion_question_improvements_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "dry_run": dry_run,
                "total_questions": len(questions),
                "success_count": success_count,
                "update_count": update_count,
                "improvements": improvements
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n[SAVED] 改善結果を保存しました: {filename}")
        
        # サマリーを表示
        print("\n" + "=" * 60)
        print("処理サマリー")
        print("=" * 60)
        print(f"総質問数: {len(questions)}")
        print(f"改善成功: {success_count}件")
        print(f"改善失敗: {len(questions) - success_count}件")
        if not dry_run:
            print(f"Notion更新成功: {update_count}件")
        print("=" * 60)
        
        return {
            "success": True,
            "total_questions": len(questions),
            "success_count": success_count,
            "update_count": update_count,
            "filename": filename
        }


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Notion診断フローの質問文を一括改善")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="DRY RUNモード（Notionに更新しない）"
    )
    parser.add_argument(
        "--max",
        type=int,
        help="最大処理数"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="カテゴリでフィルタリング（例: エアコン）"
    )
    
    args = parser.parse_args()
    
    try:
        print("=" * 60)
        print("Notion診断フロー質問文一括改善ツール")
        print("=" * 60)
        print()
        
        updater = NotionQuestionUpdater()
        
        if not updater.notion_client:
            print("[ERROR] Notionクライアントが初期化できませんでした")
            return
        
        # 改善と更新を実行
        result = updater.improve_and_update_all(
            dry_run=args.dry_run if args.dry_run else False,
            max_questions=args.max,
            filter_category=args.category
        )
        
        if result.get("success"):
            print("\n[COMPLETE] 処理完了！")
        else:
            print(f"\n[ERROR] 処理失敗: {result.get('error', '')}")
    
    except Exception as e:
        print(f"\n[FATAL ERROR] 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

