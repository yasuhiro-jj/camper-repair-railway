#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
応答品質ログ記録モジュール
フェーズ2-1: ログ分析機能の追加
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# ログディレクトリの作成
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# ログファイルパス
RESPONSE_QUALITY_LOG = LOG_DIR / "response_quality.jsonl"
ERROR_LOG = LOG_DIR / "errors.jsonl"
PERFORMANCE_LOG = LOG_DIR / "performance.jsonl"


class ResponseLogger:
    """応答品質ログ記録クラス"""
    
    def __init__(self):
        self.log_dir = LOG_DIR
        self.log_dir.mkdir(exist_ok=True)
    
    def log_response_quality(
        self,
        message: str,
        response: str,
        intent: Dict[str, Any],
        sources: Dict[str, Any],
        session_id: Optional[str] = None,
        response_time: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        """
        応答品質をログに記録
        
        Args:
            message: ユーザーの質問
            response: AIの応答
            intent: 意図分析結果
            sources: 使用したソース（RAG, SERP, Notion）
            session_id: セッションID
            response_time: 応答時間（秒）
            error: エラーメッセージ（あれば）
        """
        try:
            # 6要素形式のチェック
            format_score = self._check_format_compliance(response)
            
            # ソース品質スコア
            source_score = self._calculate_source_score(sources)
            
            # 応答品質スコア
            quality_score = self._calculate_quality_score(response, format_score, source_score)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id or "unknown",
                "message": message[:500],  # 長すぎる場合は切り詰め
                "response_length": len(response),
                "intent": intent,
                "sources": {
                    "notion": {
                        "used": bool(sources.get("notion_results", {}).get("repair_cases") or sources.get("notion_results", {}).get("diagnostic_nodes")),
                        "count": len(sources.get("notion_results", {}).get("repair_cases", [])) + len(sources.get("notion_results", {}).get("diagnostic_nodes", []))
                    },
                    "rag": {
                        "used": bool(sources.get("rag_results", {}).get("documents")),
                        "count": len(sources.get("rag_results", {}).get("documents", []))
                    },
                    "serp": {
                        "used": bool(sources.get("serp_results", {}).get("results")),
                        "count": len(sources.get("serp_results", {}).get("results", []))
                    }
                },
                "quality_metrics": {
                    "format_score": format_score,
                    "source_score": source_score,
                    "quality_score": quality_score,
                    "has_empathy": "共感" in response or "お困り" in response or "よく分かります" in response,
                    "has_summary": "要点" in response or "原因" in response,
                    "has_steps": any(f"{i}." in response for i in range(1, 10)),
                    "has_action": "次アクション" in response or "推奨" in response,
                    "has_cost": "工賃" in response or "費用" in response or "料金" in response,
                    "has_time": "時間" in response or "分" in response or "時間" in response
                },
                "performance": {
                    "response_time": response_time,
                    "error": error
                }
            }
            
            # JSONL形式でログに記録
            with open(RESPONSE_QUALITY_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
            print(f"📊 応答品質ログ記録完了: 品質スコア={quality_score:.2f}")
            
        except Exception as e:
            print(f"⚠️ 応答品質ログ記録エラー: {e}")
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> None:
        """
        エラーをログに記録
        
        Args:
            error_type: エラータイプ（OpenAI, Notion, RAG, SERP, etc.）
            error_message: エラーメッセージ
            context: エラー発生時のコンテキスト
            session_id: セッションID
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id or "unknown",
                "error_type": error_type,
                "error_message": error_message,
                "context": context
            }
            
            with open(ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
            print(f"❌ エラーログ記録完了: {error_type}")
            
        except Exception as e:
            print(f"⚠️ エラーログ記録エラー: {e}")
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        パフォーマンスをログに記録
        
        Args:
            operation: 操作名（RAG検索, SERP検索, Notion検索, AI生成, etc.）
            duration: 実行時間（秒）
            success: 成功したかどうか
            details: 詳細情報
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "duration": duration,
                "success": success,
                "details": details or {}
            }
            
            with open(PERFORMANCE_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        except Exception as e:
            print(f"⚠️ パフォーマンスログ記録エラー: {e}")
    
    def _check_format_compliance(self, response: str) -> float:
        """
        6要素形式への準拠度をチェック
        
        Returns:
            0.0-1.0のスコア
        """
        score = 0.0
        elements = [
            ("共感", "共感リアクション"),
            ("要点", "要点"),
            ("手順", "手順"),
            ("次アクション", "次アクション"),
            ("工賃", "工賃目安"),
            ("作業時間", "作業時間")
        ]
        
        found_elements = 0
        for keyword, full_keyword in elements:
            if keyword in response or full_keyword in response:
                found_elements += 1
        
        # 6要素中いくつ見つかったかでスコアを計算
        score = found_elements / 6.0
        
        return score
    
    def _calculate_source_score(self, sources: Dict[str, Any]) -> float:
        """
        ソース品質スコアを計算
        
        Returns:
            0.0-1.0のスコア
        """
        score = 0.0
        
        # Notionソースがある場合（最優先）
        if sources.get("notion_results", {}).get("repair_cases") or sources.get("notion_results", {}).get("diagnostic_nodes"):
            score += 0.5
        
        # RAGソースがある場合
        if sources.get("rag_results", {}).get("documents"):
            score += 0.3
        
        # SERPソースがある場合
        if sources.get("serp_results", {}).get("results"):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_quality_score(
        self,
        response: str,
        format_score: float,
        source_score: float
    ) -> float:
        """
        総合品質スコアを計算
        
        Returns:
            0.0-1.0のスコア
        """
        # フォーマット準拠度: 40%
        # ソース品質: 30%
        # 応答の長さ（適切な長さか）: 20%
        # その他（専門用語の使用など）: 10%
        
        length_score = 0.0
        if 200 <= len(response) <= 2000:
            length_score = 1.0
        elif len(response) < 200:
            length_score = len(response) / 200.0
        else:
            length_score = max(0.0, 1.0 - (len(response) - 2000) / 1000.0)
        
        quality_score = (
            format_score * 0.4 +
            source_score * 0.3 +
            length_score * 0.2 +
            0.1  # ベーススコア
        )
        
        return min(quality_score, 1.0)
    
    def get_quality_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        品質統計を取得
        
        Args:
            days: 過去何日分のデータを取得するか
        
        Returns:
            統計情報の辞書
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            quality_scores = []
            format_scores = []
            source_scores = []
            error_count = 0
            
            if RESPONSE_QUALITY_LOG.exists():
                with open(RESPONSE_QUALITY_LOG, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            entry_date = datetime.fromisoformat(entry["timestamp"])
                            if entry_date >= cutoff_date:
                                quality_scores.append(entry["quality_metrics"]["quality_score"])
                                format_scores.append(entry["quality_metrics"]["format_score"])
                                source_scores.append(entry["quality_metrics"]["source_score"])
                        except:
                            continue
            
            if ERROR_LOG.exists():
                with open(ERROR_LOG, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            entry_date = datetime.fromisoformat(entry["timestamp"])
                            if entry_date >= cutoff_date:
                                error_count += 1
                        except:
                            continue
            
            stats = {
                "period_days": days,
                "total_responses": len(quality_scores),
                "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
                "average_format_score": sum(format_scores) / len(format_scores) if format_scores else 0.0,
                "average_source_score": sum(source_scores) / len(source_scores) if source_scores else 0.0,
                "error_count": error_count,
                "error_rate": error_count / len(quality_scores) if quality_scores else 0.0
            }
            
            return stats
            
        except Exception as e:
            print(f"⚠️ 統計取得エラー: {e}")
            return {}


# グローバルインスタンス
response_logger = ResponseLogger()

