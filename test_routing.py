#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ルーティングエンジンの回帰テストスイート
"""

import json
import unittest
from typing import Dict, List, Any
from unified_backend_api import route_next_node, score_candidate

class TestRoutingEngine(unittest.TestCase):
    """ルーティングエンジンのテストクラス"""
    
    def setUp(self):
        """テストデータのセットアップ"""
        self.test_nodes = [
            {
                "id": "node_001",
                "title": "バッテリー故障診断",
                "category": "バッテリー",
                "routing_config": {
                    "threshold": 1.5,
                    "safety_words": ["危険", "緊急", "火災"],
                    "next_nodes_map": [
                        {
                            "id": "node_002",
                            "label": "バッテリー上がり",
                            "keywords": ["上がらない", "始動しない", "エンジンかからない"],
                            "weight": 2.0
                        },
                        {
                            "id": "node_003",
                            "label": "バッテリー液不足",
                            "keywords": ["液", "水", "不足", "減る"],
                            "weight": 1.5
                        },
                        {
                            "id": "node_004",
                            "label": "安全確認",
                            "keywords": ["危険", "緊急"],
                            "weight": 3.0,
                            "safety": True
                        }
                    ]
                }
            },
            {
                "id": "node_005",
                "title": "エアコン故障診断",
                "category": "エアコン",
                "routing_config": {
                    "threshold": 1.0,
                    "safety_words": [],
                    "next_nodes_map": [
                        {
                            "id": "node_006",
                            "label": "エアコン効かない",
                            "keywords": ["効かない", "冷えない", "温まらない"],
                            "weight": 2.0
                        },
                        {
                            "id": "node_007",
                            "label": "異音がする",
                            "keywords": ["音", "異音", "うるさい"],
                            "weight": 1.5
                        }
                    ]
                }
            }
        ]
        
        self.context = {"nodes": self.test_nodes}
    
    def test_score_candidate_basic(self):
        """基本的なスコアリングテスト"""
        candidate = {
            "keywords": ["上がらない", "始動しない"],
            "weight": 2.0
        }
        
        # 完全一致
        result = score_candidate("エンジンが上がらない", candidate)
        self.assertEqual(result["score"], 2.0)
        self.assertEqual(result["hits"], ["上がらない"])
        
        # 部分一致
        result = score_candidate("バッテリーが始動しません", candidate)
        self.assertEqual(result["score"], 2.0)
        self.assertEqual(result["hits"], ["始動しない"])
        
        # 複数一致
        result = score_candidate("エンジンが上がらないし始動しない", candidate)
        self.assertEqual(result["score"], 4.0)
        self.assertEqual(result["hits"], ["上がらない", "始動しない"])
        
        # 不一致
        result = score_candidate("トイレが詰まった", candidate)
        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["hits"], [])
    
    def test_score_candidate_noun_symptom_pairs(self):
        """名詞×症状ペアの加点テスト"""
        candidate = {
            "keywords": ["水圧"],
            "weight": 1.0
        }
        
        # ペア加点
        result = score_candidate("水圧が弱い", candidate)
        self.assertEqual(result["score"], 1.3)  # 1.0 + 0.3
        
        # ペアなし
        result = score_candidate("水圧の問題", candidate)
        self.assertEqual(result["score"], 1.0)
    
    def test_route_next_node_safety_word(self):
        """安全ワード検出テスト"""
        result = route_next_node(
            "node_001",
            "バッテリーから危険な音がする",
            self.context
        )
        
        self.assertEqual(result["nextNodeId"], "node_004")
        self.assertTrue(result["decision_detail"]["safety_triggered"])
        self.assertIn("危険", result["decision_detail"]["matched_keywords"])
    
    def test_route_next_node_threshold_met(self):
        """閾値クリアテスト"""
        result = route_next_node(
            "node_001",
            "エンジンが上がらない",
            self.context
        )
        
        self.assertEqual(result["nextNodeId"], "node_002")
        self.assertEqual(result["decision_detail"]["reason"], "threshold_met")
        self.assertEqual(result["decision_detail"]["score"], 2.0)
        self.assertIn("上がらない", result["decision_detail"]["matched_keywords"])
    
    def test_route_next_node_clarification_needed(self):
        """確認質問テスト"""
        result = route_next_node(
            "node_001",
            "バッテリーの問題",
            self.context
        )
        
        self.assertIsNone(result.get("nextNodeId"))
        self.assertIsNotNone(result.get("ask"))
        self.assertEqual(result["decision_detail"]["reason"], "clarification_needed")
        self.assertIn("scores", result["decision_detail"])
    
    def test_route_next_node_no_routing_config(self):
        """routing_configなしテスト"""
        node_without_config = {
            "id": "node_999",
            "title": "設定なしノード"
        }
        context_no_config = {"nodes": [node_without_config]}
        
        result = route_next_node(
            "node_999",
            "テストメッセージ",
            context_no_config
        )
        
        self.assertIsNone(result.get("nextNodeId"))
        self.assertIsNotNone(result.get("ask"))
        self.assertEqual(result["decision_detail"]["reason"], "no_routing_config")
    
    def test_route_next_node_node_not_found(self):
        """ノード未発見テスト"""
        result = route_next_node(
            "non_existent_node",
            "テストメッセージ",
            self.context
        )
        
        self.assertIsNone(result.get("nextNodeId"))
        self.assertIsNotNone(result.get("ask"))
        self.assertEqual(result["decision_detail"]["reason"], "node_not_found")

class TestRoutingRegression(unittest.TestCase):
    """回帰テスト用のゴールデンセット"""
    
    def setUp(self):
        """ゴールデンセットのセットアップ"""
        self.golden_test_cases = [
            {
                "name": "バッテリー上がり",
                "node_id": "node_001",
                "user_answer": "エンジンが上がらない",
                "expected_next_node": "node_002",
                "expected_reason": "threshold_met"
            },
            {
                "name": "バッテリー液不足",
                "node_id": "node_001", 
                "user_answer": "バッテリーの液が減っている",
                "expected_next_node": "node_003",
                "expected_reason": "threshold_met"
            },
            {
                "name": "安全ワード検出",
                "node_id": "node_001",
                "user_answer": "危険な状況です",
                "expected_next_node": "node_004",
                "expected_reason": "safety_word_detected"
            },
            {
                "name": "エアコン効かない",
                "node_id": "node_005",
                "user_answer": "エアコンが冷えない",
                "expected_next_node": "node_006",
                "expected_reason": "threshold_met"
            },
            {
                "name": "曖昧な症状",
                "node_id": "node_001",
                "user_answer": "何かおかしい",
                "expected_reason": "clarification_needed"
            }
        ]
        
        # テスト用ノード（TestRoutingEngineと同じ）
        self.test_nodes = [
            {
                "id": "node_001",
                "title": "バッテリー故障診断",
                "category": "バッテリー",
                "routing_config": {
                    "threshold": 1.5,
                    "safety_words": ["危険", "緊急", "火災"],
                    "next_nodes_map": [
                        {
                            "id": "node_002",
                            "label": "バッテリー上がり",
                            "keywords": ["上がらない", "始動しない", "エンジンかからない"],
                            "weight": 2.0
                        },
                        {
                            "id": "node_003",
                            "label": "バッテリー液不足",
                            "keywords": ["液", "水", "不足", "減る"],
                            "weight": 1.5
                        },
                        {
                            "id": "node_004",
                            "label": "安全確認",
                            "keywords": ["危険", "緊急"],
                            "weight": 3.0,
                            "safety": True
                        }
                    ]
                }
            },
            {
                "id": "node_005",
                "title": "エアコン故障診断",
                "category": "エアコン",
                "routing_config": {
                    "threshold": 1.0,
                    "safety_words": [],
                    "next_nodes_map": [
                        {
                            "id": "node_006",
                            "label": "エアコン効かない",
                            "keywords": ["効かない", "冷えない", "温まらない"],
                            "weight": 2.0
                        },
                        {
                            "id": "node_007",
                            "label": "異音がする",
                            "keywords": ["音", "異音", "うるさい"],
                            "weight": 1.5
                        }
                    ]
                }
            }
        ]
        
        self.context = {"nodes": self.test_nodes}
    
    def test_golden_set(self):
        """ゴールデンセットの回帰テスト"""
        for test_case in self.golden_test_cases:
            with self.subTest(test_case=test_case["name"]):
                result = route_next_node(
                    test_case["node_id"],
                    test_case["user_answer"],
                    self.context
                )
                
                # 期待される次のノードをチェック
                if "expected_next_node" in test_case:
                    self.assertEqual(
                        result.get("nextNodeId"),
                        test_case["expected_next_node"],
                        f"テストケース '{test_case['name']}' で期待される次のノードが一致しません"
                    )
                
                # 期待される理由をチェック
                self.assertEqual(
                    result["decision_detail"]["reason"],
                    test_case["expected_reason"],
                    f"テストケース '{test_case['name']}' で期待される理由が一致しません"
                )
                
                print(f"✅ {test_case['name']}: {result['decision_detail']['reason']}")

def run_tests():
    """テスト実行"""
    print("🧪 ルーティングエンジンのテストを開始...")
    
    # 基本テストスイート
    basic_suite = unittest.TestLoader().loadTestsFromTestCase(TestRoutingEngine)
    basic_result = unittest.TextTestRunner(verbosity=2).run(basic_suite)
    
    # 回帰テストスイート
    regression_suite = unittest.TestLoader().loadTestsFromTestCase(TestRoutingRegression)
    regression_result = unittest.TextTestRunner(verbosity=2).run(regression_suite)
    
    # 結果サマリー
    total_tests = basic_result.testsRun + regression_result.testsRun
    total_failures = len(basic_result.failures) + len(regression_result.failures)
    total_errors = len(basic_result.errors) + len(regression_result.errors)
    
    print(f"\n📊 テスト結果サマリー:")
    print(f"   総テスト数: {total_tests}")
    print(f"   成功: {total_tests - total_failures - total_errors}")
    print(f"   失敗: {total_failures}")
    print(f"   エラー: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 全てのテストが成功しました！")
        return True
    else:
        print("❌ 一部のテストが失敗しました。")
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
