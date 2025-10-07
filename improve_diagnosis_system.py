#!/usr/bin/env python3
"""
症状診断システムの改善案
"""

def create_enhanced_diagnosis_system():
    """症状診断システムの改善案"""
    
    improvements = {
        "診断フローの強化": {
            "現在": "基本的な質問と回答",
            "改善案": [
                "症状の詳細度を段階的に深掘り",
                "ユーザーの技術レベルに応じた質問",
                "緊急度の判定（即座に修理が必要か、時間があるか）",
                "過去の修理履歴の考慮"
            ]
        },
        
        "診断結果の差別化": {
            "現在": "一般的な修理手順",
            "改善案": [
                "具体的な診断名（例：「バッテリー電圧低下」）",
                "確信度の表示（例：「80%の確率でバッテリー問題」）",
                "緊急度の表示（例：「緊急：即座に修理が必要」）",
                "費用目安の表示（例：「修理費用：5,000-15,000円」）"
            ]
        },
        
        "インタラクションの改善": {
            "現在": "質問→回答の単純な流れ",
            "改善案": [
                "症状の写真・動画のアップロード機能",
                "音声での症状説明",
                "リアルタイム診断チャット",
                "診断履歴の保存・参照"
            ]
        },
        
        "専門性の強化": {
            "現在": "一般的な修理アドバイス",
            "改善案": [
                "車種・年式に特化した診断",
                "季節・環境要因の考慮",
                "メーカー別の特殊な症状",
                "最新の技術情報の反映"
            ]
        }
    }
    
    return improvements

def create_diagnosis_prompt_template():
    """症状診断専用のプロンプトテンプレート"""
    
    template = """
あなたはキャンピングカーの症状診断専門家です。

【診断の特徴】
- 段階的な質問で症状を特定
- 具体的な診断名を提示
- 確信度と緊急度を表示
- 費用目安を含む

【診断フロー】
1. 症状の詳細確認
2. 関連症状の確認
3. 環境・使用状況の確認
4. 診断結果の提示
5. 具体的な対処法の提案

【回答形式】
## 🔍 診断結果
**診断名**: [具体的な診断名]
**確信度**: [XX%]
**緊急度**: [緊急/要注意/通常]

## 💰 費用目安
- 部品代: [XX,XXX円]
- 工賃: [XX,XXX円]
- 合計: [XX,XXX円]

## 🛠️ 対処法
1. [即座に実行すべき対処法]
2. [専門家に相談すべき症状]
3. [予防策]

## ⚠️ 注意事項
[安全上の注意点]

現在の症状: {symptoms}
診断フロー: {diagnostic_flow}
関連データ: {related_data}
"""
    
    return template

def create_diagnosis_vs_chat_comparison():
    """診断システムとチャットシステムの差別化"""
    
    comparison = {
        "症状診断システム": {
            "目的": "症状から原因を特定",
            "アプローチ": "段階的質問による診断",
            "出力": "具体的な診断名と対処法",
            "特徴": [
                "専門的な診断プロセス",
                "確信度と緊急度の表示",
                "費用目安の提供",
                "段階的な症状確認"
            ]
        },
        
        "総合チャット": {
            "目的": "一般的な修理相談",
            "アプローチ": "RAG検索による情報提供",
            "出力": "汎用的な修理アドバイス",
            "特徴": [
                "幅広い修理情報の検索",
                "ブログ記事や商品情報の提供",
                "一般的なメンテナンスアドバイス",
                "Q&A形式の相談"
            ]
        }
    }
    
    return comparison

if __name__ == "__main__":
    print("症状診断システムの改善案")
    print("=" * 50)
    
    improvements = create_enhanced_diagnosis_system()
    for category, details in improvements.items():
        print(f"\n📋 {category}")
        print(f"現在: {details['現在']}")
        print("改善案:")
        for improvement in details['改善案']:
            print(f"  • {improvement}")
    
    print("\n" + "=" * 50)
    print("診断システムとチャットシステムの差別化")
    
    comparison = create_diagnosis_vs_chat_comparison()
    for system, details in comparison.items():
        print(f"\n🔧 {system}")
        print(f"目的: {details['目的']}")
        print(f"アプローチ: {details['アプローチ']}")
        print(f"出力: {details['出力']}")
        print("特徴:")
        for feature in details['特徴']:
            print(f"  • {feature}")
