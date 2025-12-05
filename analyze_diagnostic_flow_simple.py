#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フェーズ2-3: 診断フローの分析スクリプト（簡易版）
NotionクライアントをインポートせずにAPIを直接使用
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv
from notion_client import Client

# 環境変数を読み込み
load_dotenv()


def format_database_id(db_id: str) -> str:
    """データベースIDをNotionの形式にフォーマット"""
    # ハイフンを削除
    clean_id = db_id.replace("-", "")
    
    # UUID形式に変換: 8-4-4-4-12
    if len(clean_id) == 32:
        formatted_id = f"{clean_id[0:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:32]}"
        return formatted_id
    
    # すでに正しい形式の場合はそのまま返す
    return db_id


def load_diagnostic_data_simple() -> Dict[str, Any]:
    """Notion APIから直接診断データを取得（簡易版）"""
    
    notion_api_key = os.getenv("NOTION_API_KEY")
    node_db_id = os.getenv("NODE_DB_ID")
    
    if not notion_api_key or not node_db_id:
        print("❌ 環境変数が設定されていません")
        return {"nodes": []}
    
    try:
        print("📥 Notionから診断データを取得中...")
        notion = Client(auth=notion_api_key)
        
        # データベースIDをフォーマット
        formatted_db_id = format_database_id(node_db_id)
        print(f"🔑 データベースID: {formatted_db_id}")
        
        # 診断フローDBから全ノードを取得
        results = notion.databases.query(database_id=formatted_db_id)
        
        nodes = []
        for page in results.get("results", []):
            props = page.get("properties", {})
            
            # タイトル取得
            title_prop = props.get("Title", {}) or props.get("ノードID", {})
            title = ""
            if title_prop.get("title"):
                title = title_prop["title"][0].get("plain_text", "") if title_prop["title"] else ""
            
            # 質問文取得
            question_prop = props.get("質問文", {}) or props.get("Question", {})
            question = ""
            if question_prop.get("rich_text"):
                question = question_prop["rich_text"][0].get("plain_text", "") if question_prop["rich_text"] else ""
            
            # カテゴリ取得
            category_prop = props.get("カテゴリ", {}) or props.get("Category", {})
            category = ""
            if category_prop.get("select"):
                category = category_prop["select"].get("name", "")
            
            # 緊急度取得
            urgency_prop = props.get("緊急度", {}) or props.get("Urgency", {})
            urgency = ""
            if urgency_prop.get("select"):
                urgency = urgency_prop["select"].get("name", "")
            
            # 選択肢取得
            choices_prop = props.get("選択肢", {}) or props.get("Choices", {})
            choices = []
            if choices_prop.get("multi_select"):
                choices = [c.get("name", "") for c in choices_prop["multi_select"]]
            
            node = {
                "id": page.get("id", ""),
                "title": title,
                "question": question,
                "category": category,
                "urgency": urgency,
                "choices": choices
            }
            
            nodes.append(node)
        
        print(f"✅ {len(nodes)}件のノードを取得しました")
        return {"nodes": nodes}
    
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
        "avg_choices": 0,
        "avg_question_length": 0,
        "max_question_length": 0,
        "min_question_length": float('inf')
    }
    
    total_choices = 0
    
    for node in nodes:
        # カテゴリ別の集計
        category = node.get("category", "不明")
        if category:
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        # 緊急度の集計
        urgency = node.get("urgency", "不明")
        if urgency:
            stats["urgency_levels"][urgency] = stats["urgency_levels"].get(urgency, 0) + 1
        
        # 質問文の長さ
        question = node.get("question", "")
        question_length = len(question)
        if question_length > 0:
            stats["question_lengths"].append(question_length)
            stats["max_question_length"] = max(stats["max_question_length"], question_length)
            stats["min_question_length"] = min(stats["min_question_length"], question_length)
        
        # 選択肢の数
        choices = node.get("choices", [])
        if choices:
            choices_count = len(choices)
            stats["choices_distribution"].append(choices_count)
            total_choices += choices_count
    
    # 平均値の計算
    if stats["choices_distribution"]:
        stats["avg_choices"] = sum(stats["choices_distribution"]) / len(stats["choices_distribution"])
    if stats["question_lengths"]:
        stats["avg_question_length"] = sum(stats["question_lengths"]) / len(stats["question_lengths"])
    
    if stats["min_question_length"] == float('inf'):
        stats["min_question_length"] = 0
    
    return stats


def find_bottlenecks(diagnostic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """ボトルネックを特定"""
    
    bottlenecks = []
    nodes = diagnostic_data.get("nodes", [])
    
    for node in nodes:
        node_id = node.get("id", "不明")
        title = node.get("title", "")
        question = node.get("question", "")
        
        # 1. 長すぎる質問文（100文字以上）
        if len(question) > 100:
            bottlenecks.append({
                "node_id": title if title else node_id[:8],
                "type": "長すぎる質問",
                "severity": "中",
                "detail": f"質問文が{len(question)}文字と長すぎます（推奨: 50文字以内）",
                "question_preview": question[:50] + "..."
            })
        
        # 2. 選択肢が多すぎるノード（5択以上）
        choices = node.get("choices", [])
        if len(choices) >= 5:
            bottlenecks.append({
                "node_id": title if title else node_id[:8],
                "type": "選択肢が多すぎる",
                "severity": "高",
                "detail": f"{len(choices)}個の選択肢があります（推奨: 3-4個以内）",
                "choices_count": len(choices)
            })
        
        # 3. 専門用語が多いノード
        technical_terms = [
            "コンプレッサー", "オルタネーター", "インバーター", "ソレノイド",
            "バルブ", "レギュレーター", "コンデンサー", "モジュール", "センサー"
        ]
        found_terms = [term for term in technical_terms if term in question]
        if len(found_terms) >= 2:
            bottlenecks.append({
                "node_id": title if title else node_id[:8],
                "type": "専門用語が多い",
                "severity": "中",
                "detail": f"専門用語が{len(found_terms)}個含まれています: {', '.join(found_terms)}",
                "question_preview": question[:50] + "..."
            })
    
    return bottlenecks


def generate_analysis_report(diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
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
    print(f"平均選択肢数: {stats['avg_choices']:.2f}")
    print(f"平均質問文長: {stats['avg_question_length']:.1f}文字")
    print(f"最長質問文: {stats['max_question_length']}文字")
    print(f"最短質問文: {stats['min_question_length']}文字\n")
    
    # カテゴリ別の集計
    print("📂 カテゴリ別ノード数")
    print("-" * 80)
    if stats['categories']:
        for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}件")
    else:
        print("  カテゴリ情報がありません")
    print()
    
    # 緊急度別の集計
    print("⚠️ 緊急度別ノード数")
    print("-" * 80)
    if stats['urgency_levels']:
        for urgency, count in sorted(stats['urgency_levels'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {urgency}: {count}件")
    else:
        print("  緊急度情報がありません")
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
    
    # 改善提案
    print("💡 改善提案")
    print("-" * 80)
    
    suggestions = []
    
    if stats['avg_question_length'] > 60:
        suggestions.append("• 質問文を短くすることを検討（目標: 50文字以内）")
    
    if stats['avg_choices'] > 4:
        suggestions.append(f"• 選択肢を減らすことを検討（現在平均: {stats['avg_choices']:.1f}個、目標: 3-4個）")
    
    if len([b for b in bottlenecks if b.get('type') == '専門用語が多い']) > 0:
        suggestions.append("• 専門用語を平易な言葉に置き換える")
    
    if len(bottlenecks) > 5:
        suggestions.append(f"• {len(bottlenecks)}個のボトルネックを改善")
    
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
        "bottlenecks": bottlenecks,
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
    try:
        print("🚀 診断フロー分析を開始します...\n")
        
        # 診断データを読み込み
        diagnostic_data = load_diagnostic_data_simple()
        
        if not diagnostic_data or not diagnostic_data.get("nodes"):
            print("❌ 診断データが見つかりません")
            return
        
        # 分析レポートを生成
        report = generate_analysis_report(diagnostic_data)
        
        print("\n✅ 分析が完了しました！")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

