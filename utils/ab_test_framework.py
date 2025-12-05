#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A/Bテストフレームワーク

統合検索の異なるアルゴリズムを比較し、パフォーマンスを測定する
"""

import json
import hashlib
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class ABTestFramework:
    """A/Bテストフレームワーク"""
    
    def __init__(self, log_file: str = "ab_test_logs.jsonl"):
        """
        初期化
        
        Args:
            log_file: ログファイルのパス
        """
        self.log_file = Path(log_file)
        self.variants = {
            'control': {
                'name': '標準アルゴリズム',
                'description': '現在の統合検索アルゴリズム（デフォルト）'
            },
            'variant_a': {
                'name': '改善アルゴリズムA',
                'description': '重み付け改善版'
            },
            'variant_b': {
                'name': '改善アルゴリズムB',
                'description': '重複排除改善版'
            }
        }
        
        # メトリクスの初期化
        self.metrics = {
            'control': {
                'total_queries': 0,
                'total_clicks': 0,
                'total_satisfaction': 0.0,
                'total_time': 0.0,
                'satisfaction_count': 0
            },
            'variant_a': {
                'total_queries': 0,
                'total_clicks': 0,
                'total_satisfaction': 0.0,
                'total_time': 0.0,
                'satisfaction_count': 0
            },
            'variant_b': {
                'total_queries': 0,
                'total_clicks': 0,
                'total_satisfaction': 0.0,
                'total_time': 0.0,
                'satisfaction_count': 0
            }
        }
    
    def assign_variant(self, user_id: str, query: str = "") -> str:
        """
        ユーザーをバリアントに割り当て
        
        Args:
            user_id: ユーザーID
            query: 検索クエリ（オプション）
        
        Returns:
            割り当てられたバリアント名
        """
        # ハッシュベースの割り当て（一貫性を保つ）
        # user_id + query のハッシュを使用
        hash_input = f"{user_id}:{query}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # 33%ずつに分割
        remainder = hash_value % 100
        
        if remainder < 33:
            variant = 'control'
        elif remainder < 66:
            variant = 'variant_a'
        else:
            variant = 'variant_b'
        
        return variant
    
    def track_query(
        self,
        user_id: str,
        query: str,
        variant: str,
        results_count: int,
        response_time: float,
        metadata: Optional[Dict] = None
    ):
        """
        検索クエリを追跡
        
        Args:
            user_id: ユーザーID
            query: 検索クエリ
            variant: 使用したバリアント
            results_count: 結果数
            response_time: 応答時間（秒）
            metadata: 追加メタデータ
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'query',
            'user_id': user_id,
            'query': query,
            'variant': variant,
            'results_count': results_count,
            'response_time': response_time,
            'metadata': metadata or {}
        }
        
        self._log_event(event)
        
        # メトリクスを更新
        if variant in self.metrics:
            self.metrics[variant]['total_queries'] += 1
            self.metrics[variant]['total_time'] += response_time
    
    def track_click(
        self,
        user_id: str,
        query: str,
        variant: str,
        result_index: int,
        result_url: str
    ):
        """
        クリックイベントを追跡
        
        Args:
            user_id: ユーザーID
            query: 検索クエリ
            variant: 使用したバリアント
            result_index: クリックした結果のインデックス
            result_url: クリックしたURL
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'click',
            'user_id': user_id,
            'query': query,
            'variant': variant,
            'result_index': result_index,
            'result_url': result_url
        }
        
        self._log_event(event)
        
        # メトリクスを更新
        if variant in self.metrics:
            self.metrics[variant]['total_clicks'] += 1
    
    def track_satisfaction(
        self,
        user_id: str,
        query: str,
        variant: str,
        satisfaction_score: float  # 1.0-5.0
    ):
        """
        満足度を追跡
        
        Args:
            user_id: ユーザーID
            query: 検索クエリ
            variant: 使用したバリアント
            satisfaction_score: 満足度スコア（1.0-5.0）
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'satisfaction',
            'user_id': user_id,
            'query': query,
            'variant': variant,
            'satisfaction_score': satisfaction_score
        }
        
        self._log_event(event)
        
        # メトリクスを更新
        if variant in self.metrics:
            self.metrics[variant]['total_satisfaction'] += satisfaction_score
            self.metrics[variant]['satisfaction_count'] += 1
    
    def _log_event(self, event: Dict):
        """イベントをログファイルに記録"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[WARNING] A/Bテストログ記録エラー: {e}")
    
    def get_metrics(self, variant: Optional[str] = None) -> Dict[str, Any]:
        """
        メトリクスを取得
        
        Args:
            variant: 特定のバリアントのメトリクスを取得（Noneの場合はすべて）
        
        Returns:
            メトリクス辞書
        """
        if variant:
            return self._calculate_variant_metrics(variant)
        else:
            return {
                v: self._calculate_variant_metrics(v)
                for v in self.variants.keys()
            }
    
    def _calculate_variant_metrics(self, variant: str) -> Dict[str, Any]:
        """バリアントのメトリクスを計算"""
        if variant not in self.metrics:
            return {}
        
        m = self.metrics[variant]
        
        return {
            'variant': variant,
            'name': self.variants[variant]['name'],
            'total_queries': m['total_queries'],
            'total_clicks': m['total_clicks'],
            'click_rate': m['total_clicks'] / m['total_queries'] if m['total_queries'] > 0 else 0.0,
            'avg_response_time': m['total_time'] / m['total_queries'] if m['total_queries'] > 0 else 0.0,
            'avg_satisfaction': m['total_satisfaction'] / m['satisfaction_count'] if m['satisfaction_count'] > 0 else 0.0,
            'satisfaction_count': m['satisfaction_count']
        }
    
    def analyze_results(self) -> Dict[str, Any]:
        """
        A/Bテスト結果を分析
        
        Returns:
            分析結果
        """
        all_metrics = self.get_metrics()
        
        # コントロールを基準に比較
        control_metrics = all_metrics.get('control', {})
        
        analysis = {
            'control': control_metrics,
            'variants': {},
            'comparison': {}
        }
        
        for variant in ['variant_a', 'variant_b']:
            variant_metrics = all_metrics.get(variant, {})
            analysis['variants'][variant] = variant_metrics
            
            # コントロールとの比較
            comparison = {}
            
            # クリック率の比較
            control_ctr = control_metrics.get('click_rate', 0)
            variant_ctr = variant_metrics.get('click_rate', 0)
            if control_ctr > 0:
                comparison['click_rate_improvement'] = (
                    (variant_ctr - control_ctr) / control_ctr * 100
                )
            else:
                comparison['click_rate_improvement'] = 0.0
            
            # 応答時間の比較
            control_time = control_metrics.get('avg_response_time', 0)
            variant_time = variant_metrics.get('avg_response_time', 0)
            if control_time > 0:
                comparison['response_time_improvement'] = (
                    (control_time - variant_time) / control_time * 100
                )
            else:
                comparison['response_time_improvement'] = 0.0
            
            # 満足度の比較
            control_sat = control_metrics.get('avg_satisfaction', 0)
            variant_sat = variant_metrics.get('avg_satisfaction', 0)
            comparison['satisfaction_improvement'] = variant_sat - control_sat
            
            analysis['comparison'][variant] = comparison
        
        return analysis
    
    def get_recommended_variant(self) -> Optional[str]:
        """
        推奨バリアントを取得（最もパフォーマンスが良い）
        
        Returns:
            推奨バリアント名（Noneの場合はデータ不足）
        """
        analysis = self.analyze_results()
        
        # 各バリアントのスコアを計算
        scores = {}
        
        for variant in ['control', 'variant_a', 'variant_b']:
            metrics = analysis.get('variants', {}).get(variant) or analysis.get('control', {})
            
            if metrics.get('total_queries', 0) < 10:
                # データが少ない場合はスキップ
                continue
            
            # 総合スコア（クリック率 + 満足度 - 応答時間ペナルティ）
            click_rate = metrics.get('click_rate', 0) * 100
            satisfaction = metrics.get('avg_satisfaction', 0) * 20  # 5点満点を100点に変換
            response_time_penalty = min(metrics.get('avg_response_time', 0) * 10, 50)  # 最大50点のペナルティ
            
            total_score = click_rate + satisfaction - response_time_penalty
            scores[variant] = total_score
        
        if not scores:
            return None
        
        # 最もスコアが高いバリアントを返す
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def export_report(self, output_file: str = "ab_test_report.json"):
        """
        レポートをエクスポート
        
        Args:
            output_file: 出力ファイルパス
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'variants': self.variants,
            'metrics': self.get_metrics(),
            'analysis': self.analyze_results(),
            'recommended_variant': self.get_recommended_variant()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 A/Bテストレポートをエクスポートしました: {output_file}")


# グローバルインスタンス
ab_test_framework = ABTestFramework()


if __name__ == "__main__":
    print("=== A/Bテストフレームワーク ===")
    print("✅ モジュールが正常にロードされました")
    
    # テスト
    framework = ABTestFramework()
    
    # テストユーザーでバリアント割り当て
    test_users = ['user1', 'user2', 'user3', 'user4', 'user5']
    for user_id in test_users:
        variant = framework.assign_variant(user_id, "エアコンが効かない")
        print(f"ユーザー {user_id}: {variant}")
    
    # メトリクスを表示
    print("\nメトリクス:")
    metrics = framework.get_metrics()
    for variant, m in metrics.items():
        print(f"  {variant}: {m}")

