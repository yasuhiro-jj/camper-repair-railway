#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドア検索のデバッグスクリプト
"""

import os
import re
import glob

def analyze_query(query):
    """クエリを解析して検索戦略を決定"""
    query_lower = query.lower()
    
    # クエリの種類を判定
    query_type = {
        'is_specific_problem': False,  # 具体的な問題
        'is_general_category': False,  # 一般的なカテゴリ
        'has_action_verb': False,     # 動作動詞を含む
        'has_symptom': False,         # 症状を含む
        'main_keywords': [],
        'context_keywords': [],
        'priority_score': 0
    }
    
    # 主要キーワードの抽出
    main_keywords = []
    if 'ドア' in query_lower or 'door' in query_lower:
        main_keywords.append('ドア')
    if '窓' in query_lower or 'window' in query_lower:
        main_keywords.append('窓')
    if '開閉' in query_lower or '開け閉め' in query_lower:
        main_keywords.append('開閉')
    if '不具合' in query_lower or '故障' in query_lower:
        main_keywords.append('不具合')
    
    query_type['main_keywords'] = main_keywords
    
    return query_type

def search_repair_advice_debug(query):
    """テキストデータから修理アドバイスを検索（デバッグ版）"""
    try:
        # ドア関連のテキストファイル
        text_files = [
            ("ドア・窓", "ドア・窓の開閉不良.txt"),
        ]
        
        results = []
        query_lower = query.lower()
        
        print(f"🔍 検索クエリ: {query}")
        print(f"🔍 クエリ解析: {analyze_query(query)}")
        
        # 全ファイルを検索
        for category, filename in text_files:
            try:
                if not os.path.exists(filename):
                    print(f"❌ ファイルが見つかりません: {filename}")
                    continue
                    
                print(f"📁 ファイルを読み込み中: {filename}")
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"📄 ファイルサイズ: {len(content)} 文字")
                
                # クエリ解析結果を取得
                query_analysis = analyze_query(query_lower)
                
                # 高度なキーワードマッチング
                matches = []
                query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 1]
                
                print(f"🔍 検索単語: {query_words}")
                print(f"🔍 主要キーワード: {query_analysis['main_keywords']}")
                
                # ファイルの関連性を事前チェック
                file_relevance = 0
                filename_lower = filename.lower()
                
                # ファイル名との関連性チェック
                if any(keyword in filename_lower for keyword in query_analysis['main_keywords']):
                    file_relevance += 30
                    print(f"✅ ファイル名マッチ: +30点")
                
                # カテゴリとの関連性チェック
                if any(keyword in category.lower() for keyword in query_analysis['main_keywords']):
                    file_relevance += 25
                    print(f"✅ カテゴリマッチ: +25点")
                
                print(f"📊 ファイル関連性スコア: {file_relevance}")
                
                # 主要キーワードの完全一致（高優先度）
                for keyword in query_analysis['main_keywords']:
                    if keyword in content.lower():
                        count = content.lower().count(keyword)
                        matches.append(('main_keyword', keyword, 40, count))
                        print(f"✅ 主要キーワードマッチ: {keyword} ({count}回) +{40*count}点")
                
                # 完全一致（最高優先度）
                if query_lower in content.lower():
                    count = content.lower().count(query_lower)
                    matches.append(('exact', query_lower, 60, count))
                    print(f"✅ 完全一致: {query_lower} ({count}回) +{60*count}点")
                
                # 部分一致
                for word in query_words:
                    if len(word) >= 3 and word in content.lower():
                        count = content.lower().count(word)
                        matches.append(('partial', word, 20, count))
                        print(f"✅ 部分一致: {word} ({count}回) +{20*count}点")
                
                if matches:
                    # 関連度スコアを計算
                    score = file_relevance
                    
                    for match_type, keyword, weight, count in matches:
                        score += count * weight
                    
                    print(f"📊 最終スコア: {score}")
                    
                    # 修理費用と代替品情報を抽出
                    costs = []
                    alternatives = []
                    urls = []
                    
                    # 費用抽出
                    cost_patterns = [
                        r'(\d+[,，]\d+円)',
                        r'(\d+円)',
                        r'(\d+万円)',
                        r'(\d+千円)',
                    ]
                    for pattern in cost_patterns:
                        cost_matches = re.findall(pattern, content)
                        costs.extend(cost_matches)
                    costs = list(set(costs))[:5]
                    
                    print(f"💰 抽出された費用: {costs}")
                    
                    results.append({
                        'title': f"{category}修理アドバイス",
                        'category': category,
                        'filename': filename,
                        'content': content[:500] + "..." if len(content) > 500 else content,
                        'costs': costs,
                        'alternatives': alternatives,
                        'urls': urls,
                        'score': score
                    })
                    
                    print(f"✅ 結果を追加: {category}")
                else:
                    print(f"❌ マッチなし: {category}")
                    
            except Exception as e:
                print(f"❌ ファイル {filename} の読み込み中にエラー: {str(e)}")
                continue
        
        # スコア順でソート
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"📊 最終結果数: {len(results)}")
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['title']} (スコア: {result['score']})")
        
        return results
        
    except Exception as e:
        print(f"❌ 検索処理中にエラー: {str(e)}")
        return []

if __name__ == "__main__":
    # テスト実行
    query = "ドアの開け閉めの不具合"
    results = search_repair_advice_debug(query)
    
    print(f"\n🎯 検索結果:")
    for result in results:
        print(f"📄 {result['title']}")
        print(f"   スコア: {result['score']}")
        print(f"   費用: {result['costs']}")
        print(f"   内容: {result['content'][:100]}...")
        print()
