#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フェーズ2-3: 診断フローの分析スクリプト
診断フローを分析してボトルネックや改善点を特定する
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

try:
    from data_access.notion_client import notion_client
    NOTION_AVAILABLE = True
    print("✅ Notionクライアントをインポートしました")
except ImportError as e:
    NOTION_AVAILABLE = False
    print(f"⚠️ Notionクライアントが利用できません: {e}")


def load_diagnostic_data() -> Dict[str, Any]:
    """診断データを読み込み"""
    if not NOTION_AVAILABLE:
        print("⚠️ Notionクライアントが利用できません")
        return {"nodes": []}
    
    try:
        # Notionクライアントを直接使用
        print("📥 Notionから診断データを取得中...")
        diagnostic_data = notion_client.load_diagnostic_data()
        print(f"✅ {len(diagnostic_data.get('nodes', []))}件のノードを取得しました")
        return diagnostic_data if diagnostic_data else {"nodes": []}
    except Exception as e:
        print(f"⚠️ 診断データ読み込みエラー: {e}")
        import traceback
        traceback.print_exc()
        return {"nodes": []}


def analyze_diagnostic_flow(diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
    """診断フローを分析してボトルネックを特定"""
    
    nodes = diagnostic_data.get("nodes", [])
    
    if not nodes:
        return {
            "error": "診断ノードが見つかりません",
            "total_nodes": 0
        }
    
    # 統計情報を収集
    stats = {
        "total_nodes": len(nodes),
        "categories": {},
        "urgency_levels": {},
        "choices_distribution": [],
        "question_lengths": [],
        "has_routing_config": 0,
        "no_routing_config": 0,
        "avg_choices": 0,
        "avg_question_length": 0,
        "max_question_length": 0,
        "min_question_length": float('inf')
    }
    
    total_choices = 0
    
    for node in nodes:
        # カテゴリ別の集計
        category = node.get("category", "不明")
        stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        # 緊急度の集計
        urgency = node.get("urgency", "不明")
        stats["urgency_levels"][urgency] = stats["urgency_levels"].get(urgency, 0) + 1
        
        # 質問文の長さ
        question = node.get("question", "")
        question_length = len(question)
        stats["question_lengths"].append(question_length)
        stats["max_question_length"] = max(stats["max_question_length"], question_length)
        stats["min_question_length"] = min(stats["min_question_length"], question_length)
        
        # 選択肢の数
        routing_config = node.get("routing_config", {})
        if routing_config and "next_nodes_map" in routing_config:
            stats["has_routing_config"] += 1
            next_nodes = routing_config.get("next_nodes_map", [])
            choices_count = len(next_nodes)
            stats["choices_distribution"].append(choices_count)
            total_choices += choices_count
        else:
            stats["no_routing_config"] += 1
    
    # 平均値の計算
    if nodes:
        if stats["choices_distribution"]:
            stats["avg_choices"] = sum(stats["choices_distribution"]) / len(stats["choices_distribution"])
        stats["avg_question_length"] = sum(stats["question_lengths"]) / len(stats["question_lengths"])
    
    return stats


def find_bottlenecks(diagnostic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """ボトルネックを特定"""
    
    bottlenecks = []
    nodes = diagnostic_data.get("nodes", [])
    
    for node in nodes:
        node_id = node.get("id", "不明")
        question = node.get("question", "")
        
        # 1. 長すぎる質問文（100文字以上）
        if len(question) > 100:
            bottlenecks.append({
                "node_id": node_id,
                "type": "長すぎる質問",
                "severity": "中",
                "detail": f"質問文が{len(question)}文字と長すぎます（推奨: 50文字以内）",
                "question_preview": question[:50] + "..."
            })
        
        # 2. 選択肢が多すぎるノード（5択以上）
        routing_config = node.get("routing_config", {})
        if routing_config and "next_nodes_map" in routing_config:
            next_nodes = routing_config.get("next_nodes_map", [])
            if len(next_nodes) >= 5:
                bottlenecks.append({
                    "node_id": node_id,
                    "type": "選択肢が多すぎる",
                    "severity": "高",
                    "detail": f"{len(next_nodes)}個の選択肢があります（推奨: 3-4個以内）",
                    "choices_count": len(next_nodes)
                })
        
        # 3. ルーティング設定がないノード
        if not routing_config or "next_nodes_map" not in routing_config:
            # 診断結果ノードでなければ問題
            if not node.get("diagnosis_result"):
                bottlenecks.append({
                    "node_id": node_id,
                    "type": "ルーティング設定なし",
                    "severity": "高",
                    "detail": "次のノードへのルーティング設定がありません",
                    "question_preview": question[:50] + "..."
                })
        
        # 4. 専門用語が多いノード
        technical_terms = [
            "コンプレッサー", "オルタネーター", "インバーター", "ソレノイド",
            "バルブ", "レギュレーター", "コンデンサー", "モジュール", "センサー"
        ]
        found_terms = [term for term in technical_terms if term in question]
        if len(found_terms) >= 2:
            bottlenecks.append({
                "node_id": node_id,
                "type": "専門用語が多い",
                "severity": "中",
                "detail": f"専門用語が{len(found_terms)}個含まれています: {', '.join(found_terms)}",
                "question_preview": question[:50] + "..."
            })
    
    return bottlenecks


def identify_redundant_nodes(diagnostic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """不要なノードを特定"""
    
    redundant = []
    nodes = diagnostic_data.get("nodes", [])
    
    for i, node in enumerate(nodes):
        node_id = node.get("id", "不明")
        question = node.get("question", "")
        routing_config = node.get("routing_config", {})
        
        # 1. 次のノードが1つしかない（分岐がない）
        if routing_config and "next_nodes_map" in routing_config:
            next_nodes = routing_config.get("next_nodes_map", [])
            if len(next_nodes) == 1:
                redundant.append({
                    "node_id": node_id,
                    "reason": "分岐なし（統合可能）",
                    "recommendation": "前後のノードと統合を検討",
                    "question_preview": question[:50] + "..."
                })
        
        # 2. 質問が類似している（簡易チェック）
        for j, other_node in enumerate(nodes):
            if i < j:  # 重複チェックを避ける
                other_question = other_node.get("question", "")
                # 簡易的な類似度チェック（共通する文字列の割合）
                if question and other_question:
                    similarity = calculate_simple_similarity(question, other_question)
                    if similarity > 0.7:
                        redundant.append({
                            "node_id": node_id,
                            "reason": f"質問が類似（類似度: {similarity:.2f}）",
                            "similar_to": other_node.get("id", "不明"),
                            "recommendation": "質問を統合または差別化を検討",
                            "question_preview": question[:50] + "...",
                            "similar_question_preview": other_question[:50] + "..."
                        })
    
    return redundant


def calculate_simple_similarity(text1: str, text2: str) -> float:
    """簡易的な類似度計算（共通する単語の割合）"""
    # 文字ベースの簡易計算
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 or not words2:
        return 0.0
    
    common_words = words1.intersection(words2)
    total_words = len(words1.union(words2))
    
    return len(common_words) / total_words if total_words > 0 else 0.0


def calculate_flow_depth(diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
    """フローの深さ（最大ステップ数）を計算"""
    nodes = diagnostic_data.get("nodes", [])
    
    # グラフ構造を構築
    graph = {}
    start_nodes = []
    end_nodes = []
    
    for node in nodes:
        node_id = node.get("id")
        routing_config = node.get("routing_config", {})
        
        # 開始ノードを特定（categoryが"開始"のノード）
        if node.get("category") == "開始" or not routing_config:
            if node.get("diagnosis_result"):  # 診断結果があれば終了ノード
                end_nodes.append(node_id)
            else:
                start_nodes.append(node_id)
        
        # 隣接ノードを記録
        if routing_config and "next_nodes_map" in routing_config:
            next_nodes = routing_config.get("next_nodes_map", [])
            graph[node_id] = [n.get("id") for n in next_nodes if n.get("id")]
        else:
            graph[node_id] = []
            if node.get("diagnosis_result"):
                end_nodes.append(node_id)
    
    # BFSで最大深さを計算
    max_depth = 0
    paths = []
    
    for start_node in start_nodes:
        depth = bfs_max_depth(graph, start_node, end_nodes)
        if depth > max_depth:
            max_depth = depth
        paths.append({
            "start_node": start_node,
            "max_depth": depth
        })
    
    return {
        "max_depth": max_depth,
        "start_nodes_count": len(start_nodes),
        "end_nodes_count": len(end_nodes),
        "paths": paths
    }


def bfs_max_depth(graph: Dict[str, List[str]], start_node: str, end_nodes: List[str]) -> int:
    """BFSを使って開始ノードから終了ノードまでの最大深さを計算"""
    from collections import deque
    
    if start_node in end_nodes:
        return 0
    
    visited = set()
    queue = deque([(start_node, 0)])
    max_depth = 0
    
    while queue:
        current_node, depth = queue.popleft()
        
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        if current_node in end_nodes:
            max_depth = max(max_depth, depth)
            continue
        
        # 次のノードをキューに追加
        for next_node in graph.get(current_node, []):
            if next_node not in visited:
                queue.append((next_node, depth + 1))
    
    return max_depth


def generate_analysis_report(diagnostic_data: Dict[str, Any]) -> str:
    """分析レポートを生成"""
    
    print("\n" + "=" * 80)
    print("🔍 診断フロー分析レポート")
    print("=" * 80)
    print(f"📅 分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 統計情報
    stats = analyze_diagnostic_flow(diagnostic_data)
    print("📊 基本統計")
    print("-" * 80)
    print(f"総ノード数: {stats['total_nodes']}")
    print(f"ルーティング設定あり: {stats['has_routing_config']}")
    print(f"ルーティング設定なし: {stats['no_routing_config']}")
    print(f"平均選択肢数: {stats['avg_choices']:.2f}")
    print(f"平均質問文長: {stats['avg_question_length']:.1f}文字")
    print(f"最長質問文: {stats['max_question_length']}文字")
    print(f"最短質問文: {stats['min_question_length']}文字\n")
    
    # カテゴリ別の集計
    print("📂 カテゴリ別ノード数")
    print("-" * 80)
    for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}件")
    print()
    
    # 緊急度別の集計
    print("⚠️ 緊急度別ノード数")
    print("-" * 80)
    for urgency, count in sorted(stats['urgency_levels'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {urgency}: {count}件")
    print()
    
    # フローの深さ
    depth_info = calculate_flow_depth(diagnostic_data)
    print("🔢 フローの深さ")
    print("-" * 80)
    print(f"最大ステップ数: {depth_info['max_depth']}")
    print(f"開始ノード数: {depth_info['start_nodes_count']}")
    print(f"終了ノード数: {depth_info['end_nodes_count']}")
    print()
    
    # ボトルネック
    bottlenecks = find_bottlenecks(diagnostic_data)
    print(f"⚠️ ボトルネック ({len(bottlenecks)}件)")
    print("-" * 80)
    if bottlenecks:
        # 重要度順にソート
        severity_order = {"高": 0, "中": 1, "低": 2}
        bottlenecks_sorted = sorted(bottlenecks, key=lambda x: severity_order.get(x.get("severity", "低"), 3))
        
        for i, bottleneck in enumerate(bottlenecks_sorted[:10], 1):  # 上位10件
            print(f"{i}. [{bottleneck['severity']}] {bottleneck['type']}")
            print(f"   ノードID: {bottleneck['node_id']}")
            print(f"   詳細: {bottleneck['detail']}")
            if 'question_preview' in bottleneck:
                print(f"   質問: {bottleneck['question_preview']}")
            print()
    else:
        print("ボトルネックは見つかりませんでした。")
    print()
    
    # 不要なノード
    redundant = identify_redundant_nodes(diagnostic_data)
    print(f"🔄 不要なノード候補 ({len(redundant)}件)")
    print("-" * 80)
    if redundant:
        for i, item in enumerate(redundant[:5], 1):  # 上位5件
            print(f"{i}. ノードID: {item['node_id']}")
            print(f"   理由: {item['reason']}")
            print(f"   推奨: {item['recommendation']}")
            if 'question_preview' in item:
                print(f"   質問: {item['question_preview']}")
            print()
    else:
        print("不要なノードは見つかりませんでした。")
    print()
    
    # 改善提案
    print("💡 改善提案")
    print("-" * 80)
    
    suggestions = []
    
    if stats['avg_question_length'] > 60:
        suggestions.append("• 質問文を短くすることを検討（目標: 50文字以内）")
    
    if stats['avg_choices'] > 4:
        suggestions.append(f"• 選択肢を減らすことを検討（現在平均: {stats['avg_choices']:.1f}個、目標: 3-4個）")
    
    if depth_info['max_depth'] > 5:
        suggestions.append(f"• フローのステップ数を削減（現在: {depth_info['max_depth']}ステップ、目標: 3-5ステップ）")
    
    if len([b for b in bottlenecks if b.get('type') == '専門用語が多い']) > 0:
        suggestions.append("• 専門用語を平易な言葉に置き換える")
    
    if len(redundant) > 0:
        suggestions.append(f"• {len(redundant)}個の不要なノード候補を統合または削除")
    
    if not suggestions:
        suggestions.append("• 特に大きな問題は見つかりませんでした！")
    
    for suggestion in suggestions:
        print(suggestion)
    
    print("\n" + "=" * 80)
    print("分析完了 ✅")
    print("=" * 80 + "\n")
    
    # レポートをJSONで保存
    report = {
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "depth_info": depth_info,
        "bottlenecks": bottlenecks,
        "redundant_nodes": redundant,
        "suggestions": suggestions
    }
    
    # レポートをファイルに保存
    report_filename = f"diagnostic_flow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 詳細レポートを保存しました: {report_filename}")
    
    return report


def main():
    """メイン処理"""
    print("🚀 診断フロー分析を開始します...\n")
    
    # 診断データを読み込み
    diagnostic_data = load_diagnostic_data()
    
    if not diagnostic_data or not diagnostic_data.get("nodes"):
        print("❌ 診断データが見つかりません")
        return
    
    # 分析レポートを生成
    report = generate_analysis_report(diagnostic_data)
    
    print("\n✅ 分析が完了しました！")


if __name__ == "__main__":
    main()

