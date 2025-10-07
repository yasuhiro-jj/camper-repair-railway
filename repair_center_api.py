#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修理専門アドバイスセンター API
HTMLフロントエンドと連携するためのバックエンドAPI
"""

import os
import re
import glob
import json
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import logging

# RAGシステムのインポート
try:
    from enhanced_rag_system import create_enhanced_rag_system, enhanced_rag_retrieve, format_blog_links
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("Warning: RAGシステムが利用できません。単純検索モードで動作します。")

# SERP検索システムのインポート
try:
    from serp_search_system import get_serp_search_system, search_with_serp
    SERP_AVAILABLE = True
except ImportError:
    SERP_AVAILABLE = False
    print("Warning: SERP検索システムが利用できません。SERP検索機能は無効です。")

# Notion APIのインポート
try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    print("Warning: Notionクライアントが利用できません。Notion検索機能は無効です。")

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # CORSを有効にしてHTMLからAPIを呼び出せるようにする

# RAGシステムの初期化
rag_db = None
if RAG_AVAILABLE:
    try:
        rag_db = create_enhanced_rag_system()
        logger.info("RAGシステムが正常に初期化されました")
    except Exception as e:
        logger.warning(f"RAGシステムの初期化に失敗: {str(e)}")
        rag_db = None

# SERP検索システムの初期化
serp_system = None
if SERP_AVAILABLE:
    try:
        serp_system = get_serp_search_system()
        logger.info("SERP検索システムが正常に初期化されました")
    except Exception as e:
        logger.warning(f"SERP検索システムの初期化に失敗: {str(e)}")
        serp_system = None

# Notionクライアントの初期化
notion_client = None
if NOTION_AVAILABLE:
    try:
        notion_api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
        if notion_api_key:
            notion_client = Client(auth=notion_api_key)
            logger.info("Notionクライアントが正常に初期化されました")
        else:
            logger.warning("Notion APIキーが設定されていません")
    except Exception as e:
        logger.warning(f"Notionクライアントの初期化に失敗: {str(e)}")
        notion_client = None

def parse_markdown_content(content):
    """マークダウンコンテンツを解析して構造化"""
    import re
    
    # マークダウン記法を除去してプレーンテキストに変換
    # ヘッダー（# ## ###）を除去
    content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
    
    # リスト記法（- * +）を除去
    content = re.sub(r'^[\s]*[-*+]\s+', '', content, flags=re.MULTILINE)
    
    # 太字・斜体記法を除去
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    content = re.sub(r'\*(.*?)\*', r'\1', content)
    
    # リンク記法を除去（URLは保持）
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    
    # コードブロックを除去
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r'`([^`]+)`', r'\1', content)
    
    return content

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
    
    # 具体的な問題パターン
    problem_patterns = [
        r'(ファン|fan|換気|vent).*?(回らない|動かない|動作しない|故障|不具合)',
        r'(トイレ|toilet).*?(ファン|fan|換気|vent).*?(回らない|動かない|動作しない)',
        r'(水|water).*?(出ない|流れない|漏れる|漏れ)',
        r'(電源|power).*?(入らない|切れる|落ちる)',
        r'(異音|音|騒音|noise).*?(する|発生|鳴る)',
        r'(雨漏り|雨漏|漏水|水漏れ|浸水).*?(する|発生|起きる|ある)',
        r'(シーリング|コーキング|パッキン).*?(劣化|破損|剥がれ|割れ)',
        r'(天井|屋根|ルーフ).*?(水滴|水|濡れ|シミ)',
        r'(窓|ウインドウ).*?(水|濡れ|染み|漏れ)'
    ]
    
    for pattern in problem_patterns:
        if re.search(pattern, query_lower):
            query_type['is_specific_problem'] = True
            query_type['priority_score'] += 50
            break
    
    # 動作動詞の検出
    action_verbs = ['回らない', '動かない', '動作しない', '出ない', '流れない', '漏れる', '漏れ', '切れる', '入らない', '鳴る', '発生', 'する', '起きる', 'ある']
    for verb in action_verbs:
        if verb in query_lower:
            query_type['has_action_verb'] = True
            query_type['priority_score'] += 20
            break
    
    # 症状の検出
    symptoms = ['故障', '不具合', '異音', '騒音', '漏れ', '雨漏り', '水漏れ', '漏水', '浸水', '切れ', '落ち', '止まる', '動かない', '濡れ', 'シミ', '水滴']
    for symptom in symptoms:
        if symptom in query_lower:
            query_type['has_symptom'] = True
            query_type['priority_score'] += 15
            break
    
    # 主要キーワードの抽出
    main_keywords = []
    if 'ファン' in query_lower or 'fan' in query_lower:
        main_keywords.append('ファン')
    if 'トイレ' in query_lower or 'toilet' in query_lower:
        main_keywords.append('トイレ')
    if '換気' in query_lower or 'vent' in query_lower:
        main_keywords.append('換気')
    if '雨漏り' in query_lower or '雨漏' in query_lower:
        main_keywords.append('雨漏り')
    if '水漏れ' in query_lower or '漏水' in query_lower:
        main_keywords.append('水漏れ')
    if 'シーリング' in query_lower or 'コーキング' in query_lower:
        main_keywords.append('シーリング')
    if '天井' in query_lower or '屋根' in query_lower or 'ルーフ' in query_lower:
        main_keywords.append('天井')
    if '窓' in query_lower or 'ウインドウ' in query_lower:
        main_keywords.append('窓')
    if 'バッテリー' in query_lower or 'battery' in query_lower:
        main_keywords.append('バッテリー')
    if 'エアコン' in query_lower or 'aircon' in query_lower:
        main_keywords.append('エアコン')
    if '冷蔵庫' in query_lower or 'refrigerator' in query_lower:
        main_keywords.append('冷蔵庫')
    if 'ドア' in query_lower or 'door' in query_lower:
        main_keywords.append('ドア')
    if '窓' in query_lower or 'window' in query_lower:
        main_keywords.append('窓')
    if '開閉' in query_lower or '開け閉め' in query_lower:
        main_keywords.append('開閉')
    if '不具合' in query_lower or '故障' in query_lower:
        main_keywords.append('不具合')
    
    query_type['main_keywords'] = main_keywords
    
    # 文脈キーワードの抽出
    context_keywords = []
    if '回らない' in query_lower:
        context_keywords.extend(['動作しない', '動かない', '故障', '不具合'])
    if 'ファン' in query_lower:
        context_keywords.extend(['モーター', '換気', '排気', '風量'])
    if 'トイレ' in query_lower:
        context_keywords.extend(['カセット', 'マリン', 'ベンチレーター'])
    if '雨漏り' in query_lower or '水漏れ' in query_lower:
        context_keywords.extend(['シーリング', 'コーキング', 'パッキン', '防水', '天井', '屋根', '窓', '濡れ', 'シミ', '水滴'])
    if 'シーリング' in query_lower or 'コーキング' in query_lower:
        context_keywords.extend(['パッキン', '防水', '劣化', '剥がれ', '割れ', '補修'])
    if '天井' in query_lower or '屋根' in query_lower:
        context_keywords.extend(['ルーフ', 'パネル', '継ぎ目', 'ジョイント', 'シーリング', '防水'])
    if '窓' in query_lower or 'ウインドウ' in query_lower:
        context_keywords.extend(['モール', 'パッキン', '枠', 'ガラス', '防水', 'シール'])
    if 'バッテリー' in query_lower:
        context_keywords.extend(['充電', '電圧', 'サブバッテリー', '鉛バッテリー', 'リチウム'])
    if 'エアコン' in query_lower:
        context_keywords.extend(['冷房', '暖房', '温度', 'フィルター', '冷媒'])
    if '冷蔵庫' in query_lower:
        context_keywords.extend(['冷凍', 'コンプレッサー', '冷却', '温度'])
    
    query_type['context_keywords'] = context_keywords
    
    return query_type

def get_related_keywords(query):
    """クエリに関連するキーワードを取得"""
    query_lower = query.lower()
    related_keywords = []
    
    # キーワードマッピング
    keyword_mapping = {
        "バッテリー": ["充電", "電圧", "サブバッテリー", "鉛バッテリー", "リチウム"],
        "インバーター": ["DC-AC", "正弦波", "電源変換", "出力", "容量"],
        "トイレ": ["カセット", "マリン", "フラッパー", "ファン", "換気"],
        "ルーフベント": ["換気扇", "マックスファン", "ファン", "換気", "ベント"],
        "水道": ["ポンプ", "給水", "水", "圧力", "タンク"],
        "冷蔵庫": ["冷凍", "コンプレッサー", "冷却", "温度"],
        "ガス": ["コンロ", "ヒーター", "FF", "燃焼", "点火"],
        "電気": ["LED", "照明", "電装", "配線", "ヒューズ"],
        "雨漏り": ["防水", "シール", "シーリング", "漏れ", "水"],
        "異音": ["音", "騒音", "振動", "ノイズ", "うるさい"],
        "ファン": ["モーター", "換気", "排気", "風量", "回転"],
        "エアコン": ["冷房", "暖房", "温度", "フィルター", "冷媒"],
        "ドア": ["窓", "開閉", "パッキン", "シール", "ガタつき", "ヒンジ", "ロック", "建付け", "隙間風", "開け閉め", "不具合", "故障", "動作不良", "固い", "動かない", "閉まらない", "開かない"],
        "窓": ["ウインドウ", "開閉", "パッキン", "シール", "ガラス", "レール", "網戸", "シェード", "開け閉め", "不具合", "故障", "動作不良", "固い", "動かない", "閉まらない", "開かない"],
        "開閉": ["ドア", "窓", "ヒンジ", "レール", "動作不良", "固い", "動かない", "不具合", "故障", "開け閉め", "閉まらない", "開かない"],
        "開け閉め": ["ドア", "窓", "ヒンジ", "レール", "動作不良", "固い", "動かない", "不具合", "故障", "開閉", "閉まらない", "開かない"],
        "不具合": ["ドア", "窓", "ヒンジ", "レール", "動作不良", "固い", "動かない", "開け閉め", "開閉", "閉まらない", "開かない", "故障"],
        "ヒューズ": ["リレー", "電気", "ショート", "断線", "電源"],
        "ポンプ": ["水", "給水", "圧力", "流量", "モーター"],
        "ソーラー": ["パネル", "発電", "太陽光", "充電", "バッテリー"],
        "タイヤ": ["空気圧", "パンク", "摩耗", "交換", "ホイール"],
        "ヒーター": ["暖房", "ガス", "FF", "燃焼", "温度"],
        "LED": ["照明", "電球", "光", "電気", "電装"],
        "家具": ["テーブル", "椅子", "ベッド", "収納", "固定"],
        "排水": ["タンク", "水", "配管", "詰まり", "漏れ"]
    }
    
    # クエリに関連するキーワードを検索
    for main_keyword, related_list in keyword_mapping.items():
        if main_keyword in query_lower:
            related_keywords.extend(related_list)
        
        # 逆方向の検索も行う
        for related_word in related_list:
            if related_word in query_lower and main_keyword not in related_keywords:
                related_keywords.append(main_keyword)
    
    # 重複を除去
    return list(set(related_keywords))

def format_search_results(results, query):
    """検索結果を整理して表示用にフォーマット"""
    formatted_results = []
    query_analysis = analyze_query(query)
    
    for i, result in enumerate(results):
        # 基本情報
        formatted_result = {
            'rank': i + 1,
            'title': result.get('title', '修理アドバイス'),
            'category': result.get('category', ''),
            'filename': result.get('filename', ''),
            'score': result.get('score', 0),
            'source': result.get('source', 'text_file'),
            'relevance_level': get_relevance_level(result.get('score', 0))
        }
        
        # 内容の整理（より詳細に）
        content = result.get('content', '')
        formatted_result['summary'] = extract_summary(content, query_analysis)
        formatted_result['full_content'] = content  # 制限を解除して全内容を表示
        formatted_result['structured_content'] = extract_structured_content(content, query_analysis)
        
        # 修理費用の整理（より詳細に）
        costs = result.get('costs', [])
        formatted_result['repair_costs'] = {
            'items': costs,
            'summary': format_cost_summary(costs),
            'detailed_breakdown': extract_detailed_costs(content)
        }
        
        # 推奨製品の整理（より詳細に）
        alternatives = result.get('alternatives', [])
        formatted_result['recommended_products'] = {
            'items': alternatives,
            'count': len(alternatives),
            'detailed_products': extract_detailed_products(content)
        }
        
        # 代用品・代替品の抽出
        formatted_result['substitute_products'] = extract_substitute_products(content)
        
        # 部品購入情報の抽出
        formatted_result['part_purchase_info'] = extract_part_purchase_info(content)
        
        # 関連URLの整理（より詳細に）
        urls = result.get('urls', [])
        formatted_result['related_links'] = {
            'items': urls,
            'count': len(urls),
            'additional_resources': extract_additional_resources(content)
        }
        
        # 修理手順の抽出
        formatted_result['repair_steps'] = extract_repair_steps(content)
        
        # 注意事項・警告の抽出
        formatted_result['warnings'] = extract_warnings(content)
        
        # 関連度の詳細情報
        formatted_result['relevance_details'] = {
            'main_keywords_matched': get_matched_keywords(content, query_analysis['main_keywords']),
            'context_keywords_matched': get_matched_keywords(content, query_analysis['context_keywords']),
            'is_exact_match': query.lower() in content.lower(),
            'confidence_score': calculate_confidence_score(result, query_analysis)
        }
        
        formatted_results.append(formatted_result)
    
    return formatted_results

def get_relevance_level(score):
    """スコアに基づいて関連度レベルを決定"""
    if score >= 100:
        return "high"
    elif score >= 50:
        return "medium"
    elif score >= 20:
        return "low"
    else:
        return "very_low"

def extract_summary(content, query_analysis):
    """内容から関連する部分を要約として抽出"""
    # クエリに関連する部分を探す
    main_keywords = query_analysis['main_keywords']
    context_keywords = query_analysis['context_keywords']
    
    # 関連する段落を抽出
    paragraphs = content.split('\n\n')
    relevant_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph_lower = paragraph.lower()
        # 主要キーワードまたは文脈キーワードを含む段落を優先
        if any(keyword.lower() in paragraph_lower for keyword in main_keywords + context_keywords):
            relevant_paragraphs.append(paragraph.strip())
    
    # 関連する段落が見つからない場合は最初の段落を使用
    if not relevant_paragraphs:
        relevant_paragraphs = [paragraphs[0]] if paragraphs else [content[:300]]
    
    # 要約を作成（最大300文字）
    summary = ' '.join(relevant_paragraphs[:2])
    if len(summary) > 300:
        summary = summary[:300] + "..."
    
    return summary

def format_cost_summary(costs):
    """修理費用の要約を作成"""
    if not costs:
        return "費用情報なし"
    
    # 費用を数値でソート
    numeric_costs = []
    for cost in costs:
        # 数字を抽出
        import re
        numbers = re.findall(r'[\d,]+', cost.replace(',', ''))
        if numbers:
            try:
                numeric_costs.append((int(numbers[0].replace(',', '')), cost))
            except:
                numeric_costs.append((0, cost))
    
    if numeric_costs:
        numeric_costs.sort()
        min_cost = numeric_costs[0][1]
        max_cost = numeric_costs[-1][1]
        return f"費用目安: {min_cost} ～ {max_cost}"
    
    return f"費用目安: {', '.join(costs[:3])}"

def get_matched_keywords(content, keywords):
    """コンテンツでマッチしたキーワードを取得"""
    content_lower = content.lower()
    matched = []
    for keyword in keywords:
        if keyword.lower() in content_lower:
            matched.append(keyword)
    return matched

def extract_structured_content(content, query_analysis):
    """構造化されたコンテンツを抽出"""
    import re
    
    structured = {
        'problem_description': '',
        'causes': [],
        'solutions': [],
        'tools_needed': [],
        'difficulty_level': '',
        'estimated_time': ''
    }
    
    # 雨漏り関連の特別な処理
    if '雨漏り' in query_analysis.get('main_keywords', []) or '雨漏り' in content:
        structured = extract_rain_leak_specific_content(content)
    # トイレ関連の特別な処理
    elif 'トイレ' in query_analysis.get('main_keywords', []) or 'トイレ' in content:
        structured = extract_toilet_specific_content(content)
    
    # 問題の説明を抽出
    problem_patterns = [
        r'問題[:：]\s*(.+?)(?:\n|$)',
        r'症状[:：]\s*(.+?)(?:\n|$)',
        r'故障[:：]\s*(.+?)(?:\n|$)'
    ]
    
    for pattern in problem_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            structured['problem_description'] = matches[0].strip()
            break
    
    # 原因を抽出
    cause_patterns = [
        r'原因[:：]\s*(.+?)(?:\n\n|\n\d+\.|$)',
        r'考えられる原因[:：]\s*(.+?)(?:\n\n|\n\d+\.|$)',
        r'主な原因[:：]\s*(.+?)(?:\n\n|\n\d+\.|$)'
    ]
    
    for pattern in cause_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        if matches:
            causes_text = matches[0]
            causes = re.split(r'\n[-•]\s*', causes_text)
            structured['causes'] = [cause.strip() for cause in causes if cause.strip()][:5]
            break
    
    # 解決策を抽出
    solution_patterns = [
        r'解決方法[:：]\s*(.+?)(?:\n\n|\n\d+\.|$)',
        r'修理手順[:：]\s*(.+?)(?:\n\n|\n\d+\.|$)',
        r'対処法[:：]\s*(.+?)(?:\n\n|\n\d+\.|$)'
    ]
    
    for pattern in solution_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        if matches:
            solutions_text = matches[0]
            solutions = re.split(r'\n[-•]\s*', solutions_text)
            structured['solutions'] = [solution.strip() for solution in solutions if solution.strip()][:8]
            break
    
    # 必要な工具を抽出
    tool_patterns = [
        r'必要な工具[:：]\s*(.+?)(?:\n\n|\n\d+\.|$)',
        r'使用工具[:：]\s*(.+?)(?:\n\n|\n\d+\.|$)',
        r'工具[:：]\s*(.+?)(?:\n\n|\n\d+\.|$)'
    ]
    
    for pattern in tool_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        if matches:
            tools_text = matches[0]
            tools = re.split(r'\n[-•]\s*', tools_text)
            structured['tools_needed'] = [tool.strip() for tool in tools if tool.strip()][:5]
            break
    
    return structured

def extract_rain_leak_specific_content(content):
    """雨漏り専用の構造化コンテンツを抽出"""
    import re
    
    structured = {
        'problem_description': 'キャンピングカーの雨漏り・水漏れトラブル',
        'causes': [],
        'solutions': [],
        'tools_needed': [],
        'difficulty_level': '中級〜上級',
        'estimated_time': '1時間〜1日'
    }
    
    # 雨漏り専用の原因を抽出
    rain_leak_causes = [
        'シーリング・コーキングの劣化',
        'パッキンの硬化・破損',
        'ルーフベント周りのシール剥がれ',
        '窓枠のモール隙間',
        'アンテナベースのシール割れ',
        '配線取り出し部の防水不良',
        'FRPジョイントの亀裂',
        '水切りトレイの詰まり',
        'ブレーキランプのガスケット劣化',
        '経年劣化による防水材の剥がれ'
    ]
    
    structured['causes'] = rain_leak_causes
    
    # 雨漏り専用の解決方法を追加（費用情報付き）
    rain_leak_solutions_with_cost = [
        {
            'title': 'シーリング・コーキングの打ち直し',
            'cost': '5,000円～15,000円',
            'description': 'ブチルテープ＋ウレタンシーラントでの補修'
        },
        {
            'title': 'パッキン・ガスケットの交換',
            'cost': '3,000円～8,000円',
            'description': '発泡ゴムガスケットへの交換'
        },
        {
            'title': '窓枠モールの防水シール新調',
            'cost': '8,000円～20,000円',
            'description': '窓枠を外しての防水シール交換'
        },
        {
            'title': 'ルーフパネルジョイントの補修',
            'cost': '15,000円～30,000円',
            'description': 'FRPパテでの再接合とコーキング'
        },
        {
            'title': '水切りトレイの清掃・点検',
            'cost': '2,000円～5,000円',
            'description': 'ドレインホースの清掃と点検'
        },
        {
            'title': 'アンテナベースのシール交換',
            'cost': '5,000円～12,000円',
            'description': 'ブチル＋ウレタンハイブリッドシール'
        },
        {
            'title': '配線部の防水加工',
            'cost': '3,000円～10,000円',
            'description': 'グロメット・パッキンの交換'
        },
        {
            'title': '応急処置（ブチルテープ）',
            'cost': '1,000円～3,000円',
            'description': '緊急防水テープでの応急処置'
        }
    ]
    
    structured['solutions'] = rain_leak_solutions_with_cost
    
    # 雨漏り専用の工具を追加
    rain_leak_tools = [
        'ドライバーセット',
        'コーキングガン',
        'ブチルテープ',
        'ウレタンシーラント',
        '防水ガスケット',
        'FRPパテ',
        'トップコート',
        '清掃用ブラシ',
        'エアブロー',
        '防水スプレー',
        '養生テープ',
        'ゴム手袋'
    ]
    
    structured['tools_needed'] = rain_leak_tools
    
    return structured

def extract_toilet_specific_content(content):
    """トイレ専用の構造化コンテンツを抽出"""
    import re
    
    structured = {
        'problem_description': 'キャンピングカー用トイレ（カセット／マリントイレ）のトラブル',
        'causes': [],
        'solutions': [],
        'tools_needed': [],
        'difficulty_level': '中級',
        'estimated_time': '30分〜2時間'
    }
    
    # トイレ専用の解決方法を追加（費用情報付き）
    toilet_solutions_with_cost = [
        {
            'title': 'カセットタンクの清掃とメンテナンス',
            'cost': '0円（自分で作業）',
            'description': '清掃用品のみ必要'
        },
        {
            'title': 'ポンプの動作確認と清掃',
            'cost': '3,000円～8,000円',
            'description': 'ポンプ清掃・部品交換費用'
        },
        {
            'title': 'シール・パッキンの点検と交換',
            'cost': '5,000円～15,000円',
            'description': '部品代＋工賃'
        },
        {
            'title': '電源・配線の確認',
            'cost': '2,000円～10,000円',
            'description': '電気工事費用'
        },
        {
            'title': '水タンクの水量確認',
            'cost': '0円～3,000円',
            'description': '給水系統の点検・修理'
        },
        {
            'title': '異物の除去',
            'cost': '1,000円～5,000円',
            'description': '清掃・分解作業費用'
        },
        {
            'title': '薬剤の補充',
            'cost': '500円～2,000円',
            'description': '薬剤代のみ'
        },
        {
            'title': '排水弁の動作確認',
            'cost': '3,000円～8,000円',
            'description': '弁の点検・交換費用'
        }
    ]
    
    structured['solutions'] = toilet_solutions_with_cost
    
    # トイレ専用の原因を追加
    toilet_causes = [
        'カセットタンクの汚れ・詰まり',
        'ポンプの故障・詰まり',
        'シール・パッキンの劣化',
        '電源・配線の問題',
        '水タンクの水不足',
        '異物の混入',
        '薬剤の不足',
        '排水弁の故障'
    ]
    
    structured['causes'] = toilet_causes
    
    # トイレ専用の工具を追加
    toilet_tools = [
        'ドライバーセット',
        'マルチメーター',
        'ゴム手袋',
        'ブラシ・スポンジ',
        'トイレ用洗剤',
        '新しいシール・パッキン',
        'トイレ用薬剤',
        'タオル・雑巾'
    ]
    
    structured['tools_needed'] = toilet_tools
    
    return structured

def extract_detailed_costs(content):
    """詳細な費用情報を抽出"""
    import re
    
    detailed_costs = []
    
    # 費用の詳細パターン（より詳細な根拠を含む）
    cost_patterns = [
        # 範囲指定の費用（根拠付き）
        r'(\d{1,3}(?:,\d{3})*円)\s*[-~]\s*(\d{1,3}(?:,\d{3})*円)\s*(.+?)(?:\n|$)',
        r'(\d{1,3}(?:,\d{3})*円)\s*～\s*(\d{1,3}(?:,\d{3})*円)\s*(.+?)(?:\n|$)',
        # 単一費用（根拠付き）
        r'(\d{1,3}(?:,\d{3})*円)\s*(.+?)(?:\n|$)',
        # 費用項目別
        r'費用[:：]\s*(\d{1,3}(?:,\d{3})*円)\s*(.+?)(?:\n|$)',
        # 工賃・部品代別
        r'工賃[:：]\s*(\d{1,3}(?:,\d{3})*円)\s*(.+?)(?:\n|$)',
        r'部品代[:：]\s*(\d{1,3}(?:,\d{3})*円)\s*(.+?)(?:\n|$)',
        # 交換費用
        r'交換[:：]\s*(\d{1,3}(?:,\d{3})*円)\s*(.+?)(?:\n|$)',
        r'修理[:：]\s*(\d{1,3}(?:,\d{3})*円)\s*(.+?)(?:\n|$)',
        # 雨漏り関連の費用パターン
        r'約(\d{1,3}(?:,\d{3})*円)\s*(.+?)(?:\n|$)',
        r'(\d{1,3}(?:,\d{3})*円)\s*で(.+?)(?:\n|$)',
        r'(\d{1,3}(?:,\d{3})*円)\s*ほど(.+?)(?:\n|$)',
        r'(\d{1,3}(?:,\d{3})*円)\s*程度(.+?)(?:\n|$)',
        # 時間単位の費用
        r'(\d{1,3}(?:,\d{3})*円)\s*で(\d+時間|半日|1日)(.+?)(?:\n|$)',
        r'(\d+時間|半日|1日)\s*で(\d{1,3}(?:,\d{3})*円)(.+?)(?:\n|$)'
    ]
    
    for pattern in cost_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            if len(match) == 3:
                detailed_costs.append({
                    'min_cost': match[0],
                    'max_cost': match[1],
                    'description': match[2].strip(),
                    'reason': extract_cost_reason(match[2].strip())
                })
            elif len(match) == 2:
                detailed_costs.append({
                    'cost': match[0],
                    'description': match[1].strip(),
                    'reason': extract_cost_reason(match[1].strip())
                })
    
    return detailed_costs[:5]

def extract_cost_reason(description):
    """費用の根拠を抽出"""
    import re
    
    reasons = []
    
    # 根拠となるキーワードを抽出
    reason_patterns = [
        r'(交換が必要)',
        r'(新品交換)',
        r'(中古品)',
        r'(部品代のみ)',
        r'(工賃込み)',
        r'(取り付け工賃)',
        r'(診断費用)',
        r'(緊急対応)',
        r'(専門業者)',
        r'(DIY可能)',
        r'(簡単交換)',
        r'(複雑な修理)',
        r'(分解が必要)',
        r'(専用工具が必要)'
    ]
    
    for pattern in reason_patterns:
        matches = re.findall(pattern, description, re.IGNORECASE)
        for match in matches:
            if match not in reasons:
                reasons.append(match)
    
    return reasons

def extract_detailed_products(content):
    """詳細な製品情報を抽出"""
    import re
    
    detailed_products = []
    
    # 製品の詳細パターン
    product_patterns = [
        r'【([^】]+)】\s*[:：]?\s*(.+?)(?:\n|$)',
        r'「([^」]+)」\s*[:：]?\s*(.+?)(?:\n|$)',
        r'([A-Za-z0-9\s\-]+型)\s*[:：]?\s*(.+?)(?:\n|$)',
        r'([A-Za-z0-9\s\-]+シリーズ)\s*[:：]?\s*(.+?)(?:\n|$)'
    ]
    
    for pattern in product_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            if len(match) == 2:
                detailed_products.append({
                    'name': match[0].strip(),
                    'description': match[1].strip()
                })
    
    return detailed_products[:5]

def validate_url(url):
    """URLの検証と安全性チェック"""
    if not url:
        return None
    
    import re
    from urllib.parse import urlparse
    
    # 基本的なURL形式チェック
    if not re.match(r'^https?://', url):
        return None
    
    try:
        parsed = urlparse(url)
        
        # 信頼できるドメインかチェック
        trusted_domains = [
            'amazon.co.jp', 'amazon.com',
            'rakuten.co.jp', 'rakuten.com',
            'yahoo.co.jp', 'yahoo.com',
            'mercari.com', 'auctions.yahoo.co.jp',
            'camper-repair.net', 'titan-rv.com',
            'auto-parts.com', 'parts.com',
            'autoparts.com', 'partssource.com',
            'napaonline.com', 'oreillyauto.com',
            'autozone.com', 'pepboys.com',
            'advanceautoparts.com', 'carquest.com',
            'aap.com', 'worldpac.com',
            'rockauto.com', 'summitracing.com',
            'jegs.com', 'speedwaymotors.com',
            'dennis-kirk.com', 'tuckerrocky.com',
            'partsgiant.com', 'partsgeek.com',
            'autopartswarehouse.com', 'partstrain.com',
            'carparts.com', 'parts.com',
            'autopartscheap.com', 'partzilla.com',
            'boats.net', 'marineengine.com',
            'iboats.com', 'wholesalemarine.com'
        ]
        
        domain = parsed.netloc.lower()
        
        # 信頼できるドメインかチェック
        is_trusted = any(domain.endswith(trusted_domain) for trusted_domain in trusted_domains)
        
        if not is_trusted:
            return None
        
        # URLの長さチェック（異常に長いURLは除外）
        if len(url) > 500:
            return None
        
        # 危険なパターンをチェック
        dangerous_patterns = [
            r'javascript:', r'data:', r'vbscript:', r'onload=', r'onerror=',
            r'<script', r'</script>', r'<iframe', r'</iframe>',
            r'\.exe$', r'\.bat$', r'\.cmd$', r'\.scr$', r'\.pif$',
            r'\.com\.exe', r'\.js\.exe', r'\.vbs\.exe'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return None
        
        return url
        
    except Exception:
        return None

def extract_substitute_products(content):
    """代用品・代替品情報を抽出"""
    import re
    
    substitute_products = []
    
    # 代用品・代替品のパターン（より広範囲に対応）
    substitute_patterns = [
        r'代用品[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'代替品[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'代替[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'代用[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'推奨製品[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'推奨[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'おすすめ[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'お勧め[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'※\s*代用[品]*[:：]\s*(.+?)(?:\n|$)',
        r'※\s*代替[品]*[:：]\s*(.+?)(?:\n|$)',
        # より広範囲なパターン
        r'参考[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'関連[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'類似[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'同様[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        # URLを含む行の抽出
        r'https?://[^\s]+.*?(?:\n|$)',
        r'www\.[^\s]+.*?(?:\n|$)',
        # 製品名とURLが一緒に記載されている場合
        r'([^:：\n]+)[:：]\s*(https?://[^\s]+)',
        r'([^:：\n]+)[:：]\s*(www\.[^\s]+)'
    ]
    
    for pattern in substitute_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            # 製品名とURLの処理
            if isinstance(match, tuple) and len(match) == 2:
                # 製品名とURLが分離されている場合
                product_name = match[0].strip()
                url_text = match[1].strip()
                url = validate_url(url_text) if url_text.startswith(('http', 'www')) else None
                
                if product_name and len(product_name) > 2:
                    substitute_products.append({
                        'name': product_name,
                        'url': url,
                        'type': 'substitute'
                    })
            else:
                # 製品名を分割
                products = re.split(r'[,、]', match.strip())
                for product in products:
                    product = product.strip()
                    if len(product) > 2 and not product.startswith('※'):
                        # URLを含む場合は分離
                        url_match = re.search(r'(https?://[^\s<>"\']+)', product)
                        url = validate_url(url_match.group(1)) if url_match else None
                        product_name = re.sub(r'\s*https?://[^\s<>"\']+', '', product).strip()
                        
                        # 製品名が残っている場合のみ追加
                        if product_name and len(product_name) > 2:
                            substitute_products.append({
                                'name': product_name,
                                'url': url,
                                'type': 'substitute'
                            })
    
    # 重複を除去
    seen = set()
    unique_products = []
    for product in substitute_products:
        if product['name'] not in seen:
            seen.add(product['name'])
            unique_products.append(product)
    
    return unique_products[:8]

def extract_part_purchase_info(content):
    """部品購入情報を抽出"""
    import re
    
    part_info = []
    
    # 部品購入関連のパターン
    purchase_patterns = [
        r'購入[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'部品[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'商品[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'製品[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'交換部品[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'必要な部品[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'購入先[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'おすすめ[:：]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
        r'※\s*購入[:：]\s*(.+?)(?:\n|$)',
        r'※\s*部品[:：]\s*(.+?)(?:\n|$)'
    ]
    
    for pattern in purchase_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            # 部品名を分割
            parts = re.split(r'[,、]', match.strip())
            for part in parts:
                part = part.strip()
                if len(part) > 2 and not part.startswith('※'):
                    # URLを含む場合は分離
                    url_match = re.search(r'(https?://[^\s<>"\']+)', part)
                    url = validate_url(url_match.group(1)) if url_match else None
                    part_name = re.sub(r'\s*https?://[^\s<>"\']+', '', part).strip()
                    
                    if part_name:
                        part_info.append({
                            'name': part_name,
                            'url': url,
                            'type': 'part'
                        })
    
    # 重複を除去
    seen = set()
    unique_parts = []
    for part in part_info:
        if part['name'] not in seen:
            seen.add(part['name'])
            unique_parts.append(part)
    
    return unique_parts[:8]

def extract_additional_resources(content):
    """追加リソースを抽出"""
    import re
    
    resources = []
    
    # リソースパターン
    resource_patterns = [
        r'参考[:：]\s*(.+?)(?:\n|$)',
        r'関連情報[:：]\s*(.+?)(?:\n|$)',
        r'詳細[:：]\s*(.+?)(?:\n|$)',
        r'マニュアル[:：]\s*(.+?)(?:\n|$)'
    ]
    
    for pattern in resource_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            resources.append(match.strip())
    
    return resources[:3]

def extract_repair_steps(content):
    """修理手順を抽出"""
    import re
    
    steps = []
    
    # 手順パターン
    step_patterns = [
        r'(\d+\.\s*.+?)(?:\n\d+\.|$)',
        r'手順\d*[:：]\s*(.+?)(?:\n手順|$)',
        r'ステップ\d*[:：]\s*(.+?)(?:\nステップ|$)'
    ]
    
    for pattern in step_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            steps.append(match.strip())
    
    return steps[:10]

def extract_warnings(content):
    """警告・注意事項を抽出"""
    import re
    
    warnings = []
    
    # 警告パターン
    warning_patterns = [
        r'注意[:：]\s*(.+?)(?:\n\n|\n注意|$)',
        r'警告[:：]\s*(.+?)(?:\n\n|\n警告|$)',
        r'危険[:：]\s*(.+?)(?:\n\n|\n危険|$)',
        r'⚠️\s*(.+?)(?:\n|$)',
        r'🚨\s*(.+?)(?:\n|$)'
    ]
    
    for pattern in warning_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            warnings.append(match.strip())
    
    return warnings[:5]

def calculate_confidence_score(result, query_analysis):
    """信頼度スコアを計算"""
    score = result.get('score', 0)
    
    # 基本スコア
    confidence = min(score / 100, 1.0)
    
    # クエリ分析に基づく調整
    if query_analysis['is_specific_problem']:
        confidence *= 1.2
    if query_analysis['has_action_verb']:
        confidence *= 1.1
    if query_analysis['has_symptom']:
        confidence *= 1.1
    
    return min(confidence, 1.0)

def search_notion_database(query):
    """Notionデータベースから関連情報を検索"""
    if not notion_client:
        return []
    
    try:
        results = []
        query_lower = query.lower()
        
        # データベースIDの取得
        node_db_id = os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
        case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
        item_db_id = os.getenv("ITEM_DB_ID")
        
        # 修理ケースデータベースを検索
        if case_db_id:
            try:
                response = notion_client.databases.query(
                    database_id=case_db_id,
                    page_size=5
                )
                
                for case in response.get("results", []):
                    properties = case.get("properties", {})
                    
                    # タイトルを取得
                    title = "ケース情報"
                    if "title" in properties and properties["title"].get("title"):
                        title = properties["title"]["title"][0]["text"]["content"]
                    elif "タイトル" in properties and properties["タイトル"].get("title"):
                        title = properties["タイトル"]["title"][0]["text"]["content"]
                    
                    # 説明を取得
                    description = ""
                    if "説明" in properties and properties["説明"].get("rich_text"):
                        description = properties["説明"]["rich_text"][0]["text"]["content"]
                    elif "解決方法" in properties and properties["解決方法"].get("rich_text"):
                        description = properties["解決方法"]["rich_text"][0]["text"]["content"]
                    
                    # カテゴリを取得
                    category = ""
                    if "カテゴリ" in properties and properties["カテゴリ"].get("select"):
                        category = properties["カテゴリ"]["select"]["name"]
                    
                    # キーワードマッチング
                    if (query_lower in title.lower() or 
                        query_lower in description.lower() or
                        query_lower in category.lower()):
                        
                        # 必要な部品を取得
                        parts = []
                        if "必要な部品" in properties and properties["必要な部品"].get("multi_select"):
                            parts = [item["name"] for item in properties["必要な部品"]["multi_select"]]
                        
                        # 必要な工具を取得
                        tools = []
                        if "必要な工具" in properties and properties["必要な工具"].get("multi_select"):
                            tools = [item["name"] for item in properties["必要な工具"]["multi_select"]]
                        
                        results.append({
                            'title': title,
                            'category': category,
                            'description': description,
                            'parts': parts,
                            'tools': tools,
                            'source': 'notion_case'
                        })
            except Exception as e:
                logger.warning(f"修理ケースDB検索エラー: {str(e)}")
        
        # 部品・工具データベースを検索
        if item_db_id:
            try:
                response = notion_client.databases.query(
                    database_id=item_db_id,
                    page_size=3
                )
                
                for item in response.get("results", []):
                    properties = item.get("properties", {})
                    
                    # 部品名を取得
                    item_name = ""
                    if "部品名" in properties and properties["部品名"].get("title"):
                        item_name = properties["部品名"]["title"][0]["text"]["content"]
                    elif "名前" in properties and properties["名前"].get("title"):
                        item_name = properties["名前"]["title"][0]["text"]["content"]
                    
                    # カテゴリを取得
                    category = ""
                    if "カテゴリ" in properties and properties["カテゴリ"].get("select"):
                        category = properties["カテゴリ"]["select"]["name"]
                    
                    # キーワードマッチング
                    if (query_lower in item_name.lower() or 
                        query_lower in category.lower()):
                        
                        # 説明を取得
                        description = ""
                        if "説明" in properties and properties["説明"].get("rich_text"):
                            description = properties["説明"]["rich_text"][0]["text"]["content"]
                        
                        # 価格を取得
                        price = ""
                        if "価格" in properties and properties["価格"].get("number"):
                            price = str(properties["価格"]["number"])
                        
                        results.append({
                            'title': f"推奨部品: {item_name}",
                            'category': category,
                            'description': description,
                            'parts': [item_name],
                            'tools': [],
                            'price': price,
                            'source': 'notion_item'
                        })
            except Exception as e:
                logger.warning(f"部品・工具DB検索エラー: {str(e)}")
        
        return results[:5]  # 最大5件まで返す
        
    except Exception as e:
        logger.error(f"Notion検索エラー: {str(e)}")
        return []

def search_with_serp_integration(query):
    """SERP検索システムを使用したリアルタイム情報取得"""
    if not serp_system:
        return []
    
    try:
        # SERP検索の実行
        serp_results = search_with_serp(query, 'comprehensive')
        
        if not serp_results or 'results' not in serp_results:
            return []
        
        # SERP結果をAPI形式に変換
        formatted_results = []
        
        for result in serp_results['results']:
            # 価格情報の抽出
            costs = []
            if result.get('price_info') and result['price_info'].get('price'):
                costs.append(f"{result['price_info']['price']}円")
            
            # 代替品情報の抽出
            alternatives = []
            if result.get('title'):
                # タイトルから製品名を抽出
                title = result['title']
                # 製品名のパターンマッチング
                product_patterns = [
                    r'([A-Za-z0-9\s\-]+)（[^）]+）',
                    r'【([^】]+)】',
                    r'「([^」]+)」',
                    r'([A-Za-z0-9\s\-]+)型',
                    r'([A-Za-z0-9\s\-]+)シリーズ'
                ]
                
                for pattern in product_patterns:
                    matches = re.findall(pattern, title)
                    for match in matches:
                        if isinstance(match, tuple):
                            product_name = match[0].strip()
                        else:
                            product_name = match.strip()
                        
                        if len(product_name) >= 3 and product_name not in alternatives:
                            alternatives.append(product_name)
            
            # URLの検証
            urls = []
            if result.get('url'):
                validated_url = validate_url(result['url'])
                if validated_url:
                    urls.append(validated_url)
            
            formatted_result = {
                'title': f"リアルタイム情報: {result.get('title', '検索結果')}",
                'category': "SERP検索",
                'content': result.get('snippet', ''),
                'costs': costs,
                'alternatives': alternatives[:3],  # 最大3件
                'urls': urls,
                'score': int(result.get('relevance_score', 0.5) * 100),  # 0-100スケールに変換
                'source': 'serp',
                'domain': result.get('domain', ''),
                'search_type': result.get('search_type', 'general_info'),
                'price_info': result.get('price_info', {}),
                'realtime': True  # リアルタイム情報のフラグ
            }
            
            formatted_results.append(formatted_result)
        
        return formatted_results[:5]  # 最大5件まで返す
        
    except Exception as e:
        logger.error(f"SERP検索統合エラー: {str(e)}")
        return []

def search_with_rag(query):
    """RAGシステムを使用した高度な検索"""
    if not rag_db:
        return None
    
    try:
        # RAGシステムで検索実行
        rag_results = enhanced_rag_retrieve(query, rag_db, max_results=5)
        
        # 結果を整形
        results = []
        
        # テキストファイルの内容を処理
        if rag_results.get('text_file_content'):
            content = rag_results['text_file_content']
            
            # マークダウンデータが構造化されているかチェック
            structured_data = None
            if isinstance(content, dict) and 'solutions' in content:
                structured_data = content
                content = str(content)  # 文字列としても保持
            
            # 修理費用と代替品情報を詳細抽出
            costs = []
            alternatives = []
            urls = []
            
            # 詳細な費用抽出
            cost_patterns = [
                r'(\d+[,，]\d+円)',  # カンマ区切り
                r'(\d+円)',  # 単純な円
                r'(\d+万円)',  # 万円
                r'(\d+千円)',  # 千円
                r'(\d+[,，]\d+万円)',  # カンマ区切り万円
            ]
            for pattern in cost_patterns:
                matches = re.findall(pattern, content)
                costs.extend(matches)
            costs = list(set(costs))[:5]  # 重複除去して最大5件
            
            # 詳細な製品名・URL抽出
            product_patterns = [
                r'[A-Za-z0-9\s]+（[^）]+）',  # 既存パターン
                r'【[^】]+】',  # 【】で囲まれた製品名
                r'「[^」]+」',  # 「」で囲まれた製品名
                r'[A-Za-z0-9\s]+型',  # 型番
                r'[A-Za-z0-9\s]+シリーズ',  # シリーズ名
            ]
            for pattern in product_patterns:
                matches = re.findall(pattern, content)
                alternatives.extend(matches)
            alternatives = list(set(alternatives))[:5]  # 重複除去して最大5件
            
            # URL抽出
            url_patterns = [
                r'https?://[^\s]+',  # HTTP/HTTPS URL
                r'www\.[^\s]+',  # www URL
            ]
            for pattern in url_patterns:
                matches = re.findall(pattern, content)
                urls.extend(matches)
            urls = list(set(urls))[:3]  # 重複除去して最大3件
            
            # 構造化データがある場合は、それを使用
            if structured_data:
                result = {
                    'title': "AI検索結果 - 修理アドバイス",
                    'category': "RAG検索",
                    'content': content[:2000],
                    'costs': costs,
                    'alternatives': alternatives,
                    'urls': urls,
                    'score': 100,
                    'structured_content': structured_data
                }
            else:
                result = {
                    'title': "AI検索結果 - 修理アドバイス",
                    'category': "RAG検索",
                    'content': content[:2000],
                    'costs': costs,
                    'alternatives': alternatives,
                    'urls': urls,
                    'score': 100
                }
            
            results.append(result)
        
        # ブログリンクを追加
        if rag_results.get('blog_links'):
            blog_content = []
            blog_urls = []
            for blog in rag_results['blog_links']:
                blog_content.append(f"• {blog['title']}: {blog['url']}")
                blog_urls.append(blog['url'])
            
            results.append({
                'title': "関連ブログ記事",
                'category': "ブログ",
                'content': '\n'.join(blog_content),
                'costs': [],
                'alternatives': [],
                'urls': blog_urls,
                'score': 80
            })
        
        return results
        
    except Exception as e:
        logger.error(f"RAG検索エラー: {str(e)}")
        return None

def search_repair_advice(query):
    """テキストデータから修理アドバイスを検索（全ファイル対応版）"""
    try:
        # 全検索対象のテキストファイル（既存のリスト）
        text_files = [
            ("バッテリー", "バッテリー.txt"),
            ("雨漏り", "雨漏り.txt"),
            ("エアコン", "エアコン.txt"),
            ("冷蔵庫", "冷蔵庫.txt"),
            ("トイレ", "トイレ.txt"),
            ("トイレファン", "ベンチレーター付きトイレファンの故障.txt"),
            ("サブバッテリー", "サブバッテリー詳細.txt"),
            ("ドア・窓", "ドア・窓の開閉不良.txt"),
            ("ヒューズ・リレー", "ヒューズ切れ・リレー不良.txt"),
            ("ガスコンロ", "ガスコンロ.txt"),
            ("水道ポンプ", "水道ポンプ.txt"),
            ("ソーラーパネル", "ソーラーパネル.txt"),
            ("車体外装", "車体外装の破損.txt"),
            ("インバーター", "インバーター.txt"),
            ("タイヤ", "キャンピングカー　タイヤ　.txt"),
            ("電装系", "電装系.txt"),
            ("FFヒーター", "FFヒーター.txt"),
            ("ウインドウ", "ウインドウ.txt"),
            ("ルーフベント", "ルーフベント　換気扇.txt"),
            ("外部電源", "外部電源.txt"),
            ("室内LED", "室内LED.txt"),
            ("家具", "家具.txt"),
            ("排水タンク", "排水タンク.txt"),
            ("異音", "異音.txt")
        ]
        
        # クエリ解析結果を取得
        query_analysis = analyze_query(query_lower)
        
        # ドア関連のクエリの場合は、ドア関連ファイルを優先的に検索
        if ('ドア' in query_analysis.get('main_keywords', []) or 
            '窓' in query_analysis.get('main_keywords', []) or 
            '開閉' in query_analysis.get('main_keywords', [])):
            # ドア関連ファイルを先頭に移動
            door_files = [f for f in text_files if 'ドア' in f[0] or '窓' in f[0] or 'ウインドウ' in f[0]]
            other_files = [f for f in text_files if f not in door_files]
            text_files = door_files + other_files
            logger.info(f"ドア関連クエリのため、ドア関連ファイルを優先: {[f[1] for f in door_files]}")
        
        # マークダウンファイルも検索対象に追加
        markdown_files = glob.glob("*.md")
        for md_file in markdown_files:
            if not any(f[1] == md_file for f in text_files):
                category_name = md_file.replace(".md", "").replace("_", "・")
                text_files.append((category_name, md_file))
        
        # 追加のテキストファイルを動的に検索
        additional_files = glob.glob("*.txt")
        for filename in additional_files:
            # 既存リストにないファイルを追加
            if not any(f[1] == filename for f in text_files):
                # ファイル名からカテゴリ名を推測
                category_name = filename.replace(".txt", "").replace("　", "・")
                text_files.append((category_name, filename))
        
        results = []
        query_lower = query.lower()
        
        logger.info(f"検索対象ファイル数: {len(text_files)}")
        logger.info(f"検索対象ファイル: {[f[1] for f in text_files[:5]]}")  # 最初の5ファイルをログ出力
        
        # 全ファイルを検索
        for category, filename in text_files:
            try:
                if not os.path.exists(filename):
                    logger.info(f"ファイルが存在しません: {filename}")
                    continue
                    
                logger.info(f"ファイルを読み込み中: {filename}")
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                logger.info(f"ファイルサイズ: {len(content)} 文字")
                
                # マークダウン解析（.mdファイルの場合）
                if filename.endswith('.md'):
                    content = parse_markdown_content(content)
                
                # クエリ解析結果は既に取得済み
                
                # 高度なキーワードマッチング
                matches = []
                query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 1]
                
                # ファイルの関連性を事前チェック
                file_relevance = 0
                filename_lower = filename.lower()
                
                # ファイル名との関連性チェック
                if any(keyword in filename_lower for keyword in query_analysis['main_keywords']):
                    file_relevance += 30
                
                # カテゴリとの関連性チェック
                if any(keyword in category.lower() for keyword in query_analysis['main_keywords']):
                    file_relevance += 25
                
                # 関連性が低すぎる場合はスキップ
                if file_relevance < 10 and not query_analysis['is_specific_problem']:
                    continue
                
                # 主要キーワードの完全一致（高優先度）
                for keyword in query_analysis['main_keywords']:
                    if keyword in content.lower():
                        matches.append(('main_keyword', keyword, 40))
                
                # 文脈キーワードの一致
                for keyword in query_analysis['context_keywords']:
                    if keyword in content.lower():
                        matches.append(('context_keyword', keyword, 25))
                
                # 完全一致（最高優先度）
                if query_lower in content.lower():
                    matches.append(('exact', query_lower, 60))
                
                # 部分一致
                for word in query_words:
                    if len(word) >= 3 and word in content.lower():
                        matches.append(('partial', word, 20))
                
                # 関連キーワードマッチング
                related_keywords = get_related_keywords(query_lower)
                for keyword in related_keywords:
                    if keyword in content.lower():
                        matches.append(('related', keyword, 10))
                
                # カテゴリマッチング
                if any(keyword in category.lower() for keyword in query_analysis['main_keywords']):
                    matches.append(('category', category, 30))
                
                # ファイル名マッチング
                if any(keyword in filename_lower for keyword in query_analysis['main_keywords']):
                    matches.append(('filename', filename, 25))
                
                if matches:
                    logger.info(f"マッチが見つかりました: {len(matches)}件")
                    # 関連度スコアを計算（改善版）
                    score = file_relevance  # ファイル関連性スコアをベースに
                    
                    for match_type, keyword, weight in matches:
                        count = content.lower().count(keyword) if isinstance(keyword, str) else 1
                        score += count * weight
                        logger.info(f"  マッチ: {keyword} ({count}回) +{count * weight}点")
                    
                    # クエリ解析に基づくボーナス
                    if query_analysis['is_specific_problem']:
                        score *= 2.0  # 具体的な問題の場合は大幅ボーナス
                    
                    if query_analysis['has_action_verb']:
                        score *= 1.3  # 動作動詞がある場合はボーナス
                    
                    if query_analysis['has_symptom']:
                        score *= 1.2  # 症状がある場合はボーナス
                    
                    # 内容の長さによる正規化
                    if len(content) > 1000:
                        score *= 0.9
                    elif len(content) < 200:
                        score *= 0.7  # 内容が短すぎる場合は減点
                    
                    # 修理費用と代替品情報を詳細抽出
                    costs = []
                    alternatives = []
                    urls = []
                    
                    # 詳細な費用抽出
                    cost_patterns = [
                        r'(\d+[,，]\d+円)',  # カンマ区切り
                        r'(\d+円)',  # 単純な円
                        r'(\d+万円)',  # 万円
                        r'(\d+千円)',  # 千円
                        r'(\d+[,，]\d+万円)',  # カンマ区切り万円
                    ]
                    for pattern in cost_patterns:
                        matches = re.findall(pattern, content)
                        costs.extend(matches)
                    costs = list(set(costs))[:5]  # 重複除去して最大5件
                    
                    # 製品名・代替品抽出（改善版）
                    product_patterns = [
                        r'【([^】]+)】',  # 【】で囲まれた製品名
                        r'「([^」]+)」',  # 「」で囲まれた製品名
                        r'([A-Za-z0-9\s\-]+)（[^）]+）',  # （）で囲まれた製品名
                        r'([A-Za-z0-9\s\-]+)型',  # 型番
                        r'([A-Za-z0-9\s\-]+)シリーズ',  # シリーズ名
                        r'([A-Za-z0-9\s\-]+)エアコン',  # エアコン製品
                        r'([A-Za-z0-9\s\-]+)バッテリー',  # バッテリー製品
                        r'([A-Za-z0-9\s\-]+)ファン',  # ファン製品
                    ]
                    for pattern in product_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            # 製品名の妥当性をチェック
                            if isinstance(match, tuple):
                                product_name = match[0].strip()
                            else:
                                product_name = match.strip()
                            
                            # 無効な文字を除外
                            if (len(product_name) >= 3 and 
                                not product_name.startswith('Case') and
                                not product_name.startswith('【') and
                                not product_name.startswith('「') and
                                not any(char in product_name for char in ['・', '、', '，', '；'])):
                                alternatives.append(product_name)
                    
                    # 重複除去と最大件数制限
                    alternatives = list(dict.fromkeys(alternatives))[:5]  # 順序を保持して重複除去
                    
                    # URL抽出（改善版）
                    url_patterns = [
                        r'https?://[^\s<>"{}|\\^`\[\]]+',  # HTTP/HTTPS URL
                        r'www\.[^\s<>"{}|\\^`\[\]]+\.[a-zA-Z]{2,}',  # www URL
                    ]
                    for pattern in url_patterns:
                        url_matches = re.findall(pattern, content)
                        # URLの妥当性をチェック
                        for url in url_matches:
                            # 不正な文字や記号を除去
                            url = url.strip('.,;!?')
                            
                            # www URLの場合はhttps://を追加
                            if url.startswith('www.'):
                                url = 'https://' + url
                            
                            # URL検証を適用
                            validated_url = validate_url(url)
                            if validated_url:
                                urls.append(validated_url)
                    
                    # 重複除去と最大件数制限
                    urls = list(dict.fromkeys(urls))[:3]  # 順序を保持して重複除去
                    
                    results.append({
                        'title': f"{category}修理アドバイス",
                        'category': category,
                        'filename': filename,
                        'content': content[:1500],  # 内容を1500文字に拡張
                        'costs': costs,
                        'alternatives': alternatives,
                        'urls': urls,
                        'score': score
                    })
                    
                    # 8件見つかったら終了（より多くの情報を提供）
                    if len(results) >= 8:
                        break
            except Exception as e:
                logger.warning(f"ファイル {filename} の読み込み中にエラー: {str(e)}")
                continue
        
        # スコア順でソート
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
        
    except Exception as e:
        logger.error(f"検索処理中にエラー: {str(e)}")
        return []

def get_general_repair_advice(query):
    """キーワードに基づく一般的な修理アドバイス"""
    query_lower = query.lower()
    
    advice_map = {
        'バッテリー': """
**バッテリー関連の一般的なアドバイス:**
- 定期的な電圧チェック（12.6V以上が正常）
- 充電器の適切な使用
- 過放電の防止
- 端子の清掃と点検
- 2-3年での交換を推奨
        """,
        '雨漏り': """
**雨漏り関連の一般的なアドバイス:**
- シーリング材の定期点検
- 早期発見と応急処置
- 専門業者による根本的な修理
- 防水テープでの応急処置
- 定期的なメンテナンス
        """,
        'エアコン': """
**エアコン関連の一般的なアドバイス:**
- フィルターの定期清掃
- 冷媒ガスの点検
- 室外機の清掃
- 適切な温度設定
- 専門業者による定期点検
        """,
        'トイレ': """
**トイレ関連の一般的なアドバイス:**
- 定期的な清掃と消毒
- 水タンクの点検
- パッキンの交換
- 臭気対策
- 専門業者による定期メンテナンス
        """
    }
    
    # キーワードマッチング
    for keyword, advice in advice_map.items():
        if keyword in query_lower:
            return advice
    
    # デフォルトのアドバイス
    return """
**一般的な修理アドバイス:**
- 定期的な点検とメンテナンス
- 早期発見と適切な対応
- 専門業者への相談
- 安全第一の作業
- 適切な工具と部品の使用
    """

@app.route('/')
def index():
    """メインページ（HTMLファイルを返す）"""
    try:
        with open('repair_advice_center.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "HTMLファイルが見つかりません。", 404

@app.route('/api/search', methods=['POST'])
def api_search():
    """検索API"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': '検索キーワードが指定されていません。'
            }), 400
        
        logger.info(f"検索クエリ: {query}")
        
        # クエリ解析結果をログ出力
        query_analysis = analyze_query(query)
        logger.info(f"クエリ解析結果: {query_analysis}")
        
        # 統合検索の実行
        all_results = []
        
        # 1. RAGシステムで検索を試行
        rag_results = search_with_rag(query)
        if rag_results:
            all_results.extend(rag_results)
            logger.info(f"RAG検索で{len(rag_results)}件の結果を取得")
        
        # 2. Notionデータベース検索
        notion_results = search_notion_database(query)
        if notion_results:
            # Notion結果をAPI形式に変換
            for notion_result in notion_results:
                all_results.append({
                    'title': notion_result['title'],
                    'category': notion_result['category'],
                    'content': notion_result['description'],
                    'costs': [notion_result.get('price', '')] if notion_result.get('price') else [],
                    'alternatives': notion_result.get('parts', []),
                    'urls': [],
                    'score': 90,  # Notion結果は高スコア
                    'source': 'notion'
                })
            logger.info(f"Notion検索で{len(notion_results)}件の結果を取得")
        
        # 3. SERP検索（リアルタイム情報取得）
        serp_results = search_with_serp_integration(query)
        if serp_results:
            all_results.extend(serp_results)
            logger.info(f"SERP検索で{len(serp_results)}件の結果を取得")
        
        # 4. 従来のテキストファイル検索（フォールバック）
        # ドア関連のクエリの場合は必ずテキスト検索を実行
        if len(all_results) < 3 or ('ドア' in query_analysis.get('main_keywords', []) or '窓' in query_analysis.get('main_keywords', []) or '開閉' in query_analysis.get('main_keywords', [])):
            logger.info("結果が不十分なため、テキストファイル検索を実行します")
            text_results = search_repair_advice(query)
            if text_results:
                all_results.extend(text_results)
                logger.info(f"テキスト検索で{len(text_results)}件の結果を取得")
                # 各結果のスコアをログ出力
                for i, result in enumerate(text_results):
                    logger.info(f"  結果{i+1}: {result.get('title', 'N/A')} (スコア: {result.get('score', 0)})")
            else:
                logger.info("テキスト検索でも結果が見つかりませんでした")
        
        # 結果をスコア順でソート
        results = sorted(all_results, key=lambda x: x.get('score', 0), reverse=True)
        logger.info(f"ソート後の全結果数: {len(results)}")
        
        # 結果のフィルタリングと改善（厳密版）
        filtered_results = []
        seen_titles = set()
        
        # クエリ解析結果は既に取得済み
        
        for i, result in enumerate(results):
            logger.info(f"フィルタリング処理中: 結果{i+1} - {result.get('title', 'N/A')} (スコア: {result.get('score', 0)})")
            
            # 重複タイトルの除去
            title = result.get('title', '')
            if title in seen_titles:
                logger.info(f"  重複のためスキップ: {title}")
                continue
            seen_titles.add(title)
            
            # スコア閾値をクエリ解析に基づいて動的に設定（ドア関連は非常に緩く）
            if 'ドア' in query_analysis.get('main_keywords', []) or '窓' in query_analysis.get('main_keywords', []) or '開閉' in query_analysis.get('main_keywords', []):
                min_score_threshold = 10  # ドア関連は閾値を非常に下げる
            else:
                min_score_threshold = 50 if query_analysis['is_specific_problem'] else 40
            
            # 低スコア結果の除外
            if result.get('score', 0) < min_score_threshold:
                logger.info(f"  スコア不足のためスキップ: {result.get('score', 0)} < {min_score_threshold}")
                continue
            
            # 内容の長さチェック（ドア関連は非常に緩く）
            content = result.get('content', '')
            if 'ドア' in query_analysis.get('main_keywords', []) or '窓' in query_analysis.get('main_keywords', []) or '開閉' in query_analysis.get('main_keywords', []):
                if len(content) < 50:  # ドア関連は50文字以上
                    logger.info(f"  内容が短すぎるためスキップ: {len(content)}文字")
                    continue
            else:
                if len(content) < 300:  # その他は300文字以上
                    continue
            
            # カテゴリの関連性チェック（ドア関連は非常に緩く）
            category = result.get('category', '').lower()
            if query_analysis['main_keywords']:
                if not any(keyword.lower() in category for keyword in query_analysis['main_keywords']):
                    # ドア関連の場合はスコアが高ければ通す
                    if 'ドア' in query_analysis.get('main_keywords', []) or '窓' in query_analysis.get('main_keywords', []) or '開閉' in query_analysis.get('main_keywords', []):
                        if result.get('score', 0) < 20:  # ドア関連は20点以上
                            logger.info(f"  カテゴリ関連性不足のためスキップ: {category}")
                            continue
                    else:
                        # カテゴリが関連していない場合は、スコアが高くない限り除外
                        if result.get('score', 0) < 80:
                            continue
            
            # ファイル名の関連性チェック（ドア関連は非常に緩く）
            filename = result.get('filename', '').lower()
            if query_analysis['main_keywords']:
                if not any(keyword.lower() in filename for keyword in query_analysis['main_keywords']):
                    # ドア関連の場合はスコアが高ければ通す
                    if 'ドア' in query_analysis.get('main_keywords', []) or '窓' in query_analysis.get('main_keywords', []) or '開閉' in query_analysis.get('main_keywords', []):
                        if result.get('score', 0) < 15:  # ドア関連は15点以上
                            logger.info(f"  ファイル名関連性不足のためスキップ: {filename}")
                            continue
                    else:
                        # ファイル名が関連していない場合は、スコアが高くない限り除外
                        if result.get('score', 0) < 70:
                            continue
            
            # 結果の改善
            if result.get('alternatives'):
                # 代替品のフィルタリング
                result['alternatives'] = [alt for alt in result['alternatives'] 
                                        if len(alt) >= 3 and not alt.startswith('Case')]
            
            if result.get('urls'):
                # URLのフィルタリング
                result['urls'] = [url for url in result['urls'] 
                                if url and not url.endswith('**') and len(url) > 10]
            
            filtered_results.append(result)
            
            # ドア関連の場合は最大3件まで返す
            if 'ドア' in query_analysis.get('main_keywords', []) or '窓' in query_analysis.get('main_keywords', []) or '開閉' in query_analysis.get('main_keywords', []):
                if len(filtered_results) >= 3:
                    break
            else:
                # 最も関連性の高いもの1つだけに制限
                break
        
        results = filtered_results
        
        if results:
            # 結果を整理して表示用にフォーマット
            formatted_results = format_search_results(results, query)
            
            return jsonify({
                'success': True,
                'results': formatted_results,
                'count': len(formatted_results),
                'query_info': {
                    'original_query': query,
                    'analysis': analyze_query(query),
                    'total_found': len(all_results),
                    'filtered_count': len(formatted_results)
                }
            })
        else:
            # 結果がない場合の一般的なアドバイス
            general_advice = get_general_repair_advice(query)
            return jsonify({
                'success': True,
                'results': [],
                'general_advice': general_advice,
                'count': 0
            })
            
    except Exception as e:
        logger.error(f"API検索エラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'検索中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/serp-search', methods=['POST'])
def serp_search_api():
    """SERP検索専用API"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('search_type', 'comprehensive')
        
        if not query:
            return jsonify({
                'success': False,
                'error': '検索キーワードが指定されていません。'
            }), 400
        
        if not serp_system:
            return jsonify({
                'success': False,
                'error': 'SERP検索システムが利用できません。'
            }), 503
        
        logger.info(f"SERP検索クエリ: {query} (タイプ: {search_type})")
        
        # SERP検索の実行
        serp_results = search_with_serp(query, search_type)
        
        if serp_results and 'results' in serp_results:
            # 結果をフォーマット
            formatted_results = []
            
            for result in serp_results['results']:
                formatted_result = {
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('snippet', ''),
                    'domain': result.get('domain', ''),
                    'relevance_score': result.get('relevance_score', 0),
                    'search_type': result.get('search_type', ''),
                    'price_info': result.get('price_info', {}),
                    'source': result.get('source', '')
                }
                formatted_results.append(formatted_result)
            
            return jsonify({
                'success': True,
                'results': formatted_results,
                'query_info': {
                    'original_query': query,
                    'search_type': search_type,
                    'intent_analysis': serp_results.get('intent_analysis', {}),
                    'total_found': len(formatted_results),
                    'search_engines_used': serp_results.get('search_engines_used', [])
                }
            })
        else:
            return jsonify({
                'success': True,
                'results': [],
                'message': '検索結果が見つかりませんでした。'
            })
            
    except Exception as e:
        logger.error(f"SERP検索APIエラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'SERP検索中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/realtime-info', methods=['POST'])
def realtime_info_api():
    """リアルタイム情報取得API"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': '検索キーワードが指定されていません。'
            }), 400
        
        if not serp_system:
            return jsonify({
                'success': False,
                'error': 'SERP検索システムが利用できません。'
            }), 503
        
        logger.info(f"リアルタイム情報検索: {query}")
        
        # リアルタイム修理情報の取得
        realtime_results = serp_system.get_realtime_repair_info(query)
        
        if realtime_results and 'results' in realtime_results:
            return jsonify({
                'success': True,
                'results': realtime_results['results'],
                'query_info': realtime_results.get('query_info', {}),
                'intent_analysis': realtime_results.get('intent_analysis', {})
            })
        else:
            return jsonify({
                'success': True,
                'results': [],
                'message': 'リアルタイム情報が見つかりませんでした。'
            })
            
    except Exception as e:
        logger.error(f"リアルタイム情報APIエラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'リアルタイム情報取得中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/parts-price', methods=['POST'])
def parts_price_api():
    """部品価格検索API"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': '検索キーワードが指定されていません。'
            }), 400
        
        if not serp_system:
            return jsonify({
                'success': False,
                'error': 'SERP検索システムが利用できません。'
            }), 503
        
        logger.info(f"部品価格検索: {query}")
        
        # 部品価格情報の取得
        price_results = serp_system.get_parts_price_info(query)
        
        if price_results and 'results' in price_results:
            return jsonify({
                'success': True,
                'results': price_results['results'],
                'query_info': price_results.get('query_info', {}),
                'intent_analysis': price_results.get('intent_analysis', {})
            })
        else:
            return jsonify({
                'success': True,
                'results': [],
                'message': '価格情報が見つかりませんでした。'
            })
            
    except Exception as e:
        logger.error(f"部品価格APIエラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'価格情報取得中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェックAPI"""
    return jsonify({
        'status': 'healthy',
        'message': '修理専門アドバイスセンター API は正常に動作しています。',
        'features': {
            'rag_system': RAG_AVAILABLE and rag_db is not None,
            'notion_integration': NOTION_AVAILABLE and notion_client is not None,
            'serp_search': SERP_AVAILABLE and serp_system is not None
        }
    })

if __name__ == '__main__':
    print("🔧 修理専門アドバイスセンター API を起動中...")
    print("📱 アクセスURL: http://localhost:5000")
    print("🔍 API エンドポイント: http://localhost:5000/api/search")
    print("💚 ヘルスチェック: http://localhost:5000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
