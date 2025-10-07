#!/usr/bin/env python3
"""
修理アドバイスセンター用のAPIサーバー
RAGシステム、Notionデータベース、テキストファイルから情報を取得
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 拡張RAGシステムのインポート
try:
    from enhanced_rag_system import create_enhanced_rag_system, enhanced_rag_retrieve
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: RAGシステムが利用できません: {e}")
    RAG_AVAILABLE = False

# Notionクライアントのインポート
try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    print("Warning: Notionクライアントが利用できません")
    NOTION_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# グローバル変数
rag_db = None
notion_client = None

def initialize_rag_system():
    """RAGシステムの初期化"""
    global rag_db
    if RAG_AVAILABLE and not rag_db:
        try:
            # OpenAI APIキーの確認
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key or openai_api_key == "your_openai_api_key_here":
                print("⚠️ OpenAI APIキーが設定されていません。RAGシステムは無効です。")
                rag_db = None
                return
            
            rag_db = create_enhanced_rag_system()
            print("✅ RAGシステムが初期化されました")
        except Exception as e:
            print(f"❌ RAGシステムの初期化に失敗: {e}")
            rag_db = None

def initialize_notion_client():
    """Notionクライアントの初期化"""
    global notion_client
    if NOTION_AVAILABLE and not notion_client:
        try:
            api_key = os.getenv("NOTION_API_KEY")
            if api_key:
                notion_client = Client(auth=api_key)
                print("✅ Notionクライアントが初期化されました")
            else:
                print("❌ NOTION_API_KEYが設定されていません")
        except Exception as e:
            print(f"❌ Notionクライアントの初期化に失敗: {e}")
            notion_client = None

def search_notion_repair_cases(query: str) -> List[Dict]:
    """Notionから修理ケースを検索"""
    if not notion_client:
        return []
    
    try:
        case_db_id = os.getenv("CASE_DB_ID")
        if not case_db_id:
            return []
        
        # Notionから修理ケースを取得
        response = notion_client.databases.query(
            database_id=case_db_id,
            filter={
                "or": [
                    {
                        "property": "症状",
                        "rich_text": {
                            "contains": query
                        }
                    },
                    {
                        "property": "原因",
                        "rich_text": {
                            "contains": query
                        }
                    },
                    {
                        "property": "解決策",
                        "rich_text": {
                            "contains": query
                        }
                    }
                ]
            }
        )
        
        cases = response.get("results", [])
        repair_cases = []
        
        for case in cases:
            properties = case.get("properties", {})
            
            # プロパティの取得
            symptoms = get_notion_text(properties.get("症状", {}))
            causes = get_notion_text(properties.get("原因", {}))
            solutions = get_notion_text(properties.get("解決策", {}))
            costs = get_notion_text(properties.get("費用目安", {}))
            tools = get_notion_text(properties.get("必要な工具", {}))
            parts = get_notion_text(properties.get("必要な部品", {}))
            
            repair_case = {
                "id": case["id"],
                "symptoms": symptoms,
                "causes": causes,
                "solutions": solutions,
                "costs": costs,
                "tools": tools,
                "parts": parts,
                "source": "notion"
            }
            repair_cases.append(repair_case)
        
        return repair_cases
        
    except Exception as e:
        print(f"❌ Notion検索エラー: {e}")
        return []

def get_notion_text(property_obj):
    """Notionプロパティからテキストを取得"""
    if not property_obj:
        return ""
    
    if property_obj.get("type") == "rich_text":
        rich_text = property_obj.get("rich_text", [])
        return "".join([text.get("plain_text", "") for text in rich_text])
    elif property_obj.get("type") == "title":
        title = property_obj.get("title", [])
        return "".join([text.get("plain_text", "") for text in title])
    elif property_obj.get("type") == "select":
        select = property_obj.get("select")
        return select.get("name", "") if select else ""
    elif property_obj.get("type") == "multi_select":
        multi_select = property_obj.get("multi_select", [])
        return ", ".join([item.get("name", "") for item in multi_select])
    
    return ""

def search_text_files(query: str) -> List[Dict]:
    """テキストファイルから関連情報を検索（改良版）"""
    results = []
    
    # テキストファイルのリスト
    txt_files = [
        "バッテリー.txt", "サブバッテリー詳細.txt", "トイレ.txt", 
        "雨漏り.txt", "エアコン.txt", "冷蔵庫.txt", "ガスコンロ.txt",
        "ソーラーパネル.txt", "インバーター.txt", "電装系.txt",
        "FFヒーター.txt", "ウインドウ.txt", "ドア・窓の開閉不良.txt",
        "ヒューズ切れ・リレー不良.txt", "ベンチレーター付きトイレファンの故障.txt",
        "ルーフベント　換気扇.txt", "外部電源.txt", "室内LED.txt",
        "家具.txt", "排水タンク.txt", "水道ポンプ.txt", "異音.txt",
        "車体外装の破損.txt", "キャンピングカー　タイヤ　.txt"
    ]
    
    # クエリの関連キーワードを抽出（拡張版）
    query_lower = query.lower()
    related_keywords = []
    
    # より包括的なキーワードマッピング
    keyword_mappings = {
        # バッテリー関連
        "バッテリー": ["バッテリー", "充電", "電圧", "上がり", "始動", "エンジン", "電源", "電力", "放電"],
        "充電": ["バッテリー", "充電", "電圧", "上がり", "始動", "エンジン", "電源", "電力", "放電"],
        "電圧": ["バッテリー", "充電", "電圧", "上がり", "始動", "エンジン", "電源", "電力", "放電"],
        "始動": ["バッテリー", "充電", "電圧", "上がり", "始動", "エンジン", "電源", "電力", "放電"],
        
        # トイレ関連
        "トイレ": ["トイレ", "水", "流れ", "ポンプ", "カセット", "排水", "水漏れ"],
        "水": ["トイレ", "水", "流れ", "ポンプ", "カセット", "排水", "水漏れ", "水道"],
        "ポンプ": ["トイレ", "水", "流れ", "ポンプ", "カセット", "排水", "水漏れ", "水道"],
        
        # エアコン関連
        "エアコン": ["エアコン", "冷房", "暖房", "冷えない", "フィルター", "空調", "温度"],
        "冷房": ["エアコン", "冷房", "暖房", "冷えない", "フィルター", "空調", "温度"],
        "暖房": ["エアコン", "冷房", "暖房", "冷えない", "フィルター", "空調", "温度", "ヒーター"],
        
        # 雨漏り関連
        "雨漏り": ["雨漏り", "水漏れ", "シーリング", "防水", "屋根", "天井"],
        "水漏れ": ["雨漏り", "水漏れ", "シーリング", "防水", "屋根", "天井"],
        
        # 電装系関連
        "電装": ["電装", "電気", "配線", "ヒューズ", "リレー", "スイッチ", "コンセント"],
        "ヒューズ": ["電装", "電気", "配線", "ヒューズ", "リレー", "スイッチ", "コンセント"],
        "配線": ["電装", "電気", "配線", "ヒューズ", "リレー", "スイッチ", "コンセント"],
        
        # タイヤ関連
        "タイヤ": ["タイヤ", "ホイール", "パンク", "空気圧", "交換", "摩耗"],
        "パンク": ["タイヤ", "ホイール", "パンク", "空気圧", "交換", "摩耗"],
        
        # ドア・窓関連
        "ドア": ["ドア", "窓", "開閉", "閉まらない", "開かない", "鍵", "ロック"],
        "窓": ["ドア", "窓", "開閉", "閉まらない", "開かない", "鍵", "ロック"],
        
        # 冷蔵庫関連
        "冷蔵庫": ["冷蔵庫", "冷凍", "冷却", "温度", "電源", "モーター"],
        "冷凍": ["冷蔵庫", "冷凍", "冷却", "温度", "電源", "モーター"],
        
        # ガスコンロ関連
        "ガス": ["ガス", "コンロ", "火", "点火", "バーナー", "ガス漏れ"],
        "コンロ": ["ガス", "コンロ", "火", "点火", "バーナー", "ガス漏れ"],
        
        # ソーラーパネル関連
        "ソーラー": ["ソーラー", "パネル", "太陽光", "発電", "充電", "バッテリー"],
        "パネル": ["ソーラー", "パネル", "太陽光", "発電", "充電", "バッテリー"],
        
        # インバーター関連
        "インバーター": ["インバーター", "変換", "AC", "DC", "電源", "出力"],
        
        # ヒーター関連
        "ヒーター": ["ヒーター", "暖房", "FF", "暖かくない", "温度", "暖房"],
        "暖房": ["ヒーター", "暖房", "FF", "暖かくない", "温度", "暖房"],
        
        # 換気関連
        "換気": ["換気", "ファン", "ベンチレーター", "ルーフベント", "空気", "風"],
        "ファン": ["換気", "ファン", "ベンチレーター", "ルーフベント", "空気", "風"],
        
        # 照明関連
        "照明": ["照明", "LED", "ライト", "明かり", "電球", "点灯"],
        "LED": ["照明", "LED", "ライト", "明かり", "電球", "点灯"],
        
        # 家具関連
        "家具": ["家具", "テーブル", "椅子", "ベッド", "収納", "固定"],
        
        # 異音関連
        "異音": ["異音", "音", "うるさい", "振動", "ガタガタ", "キーキー"],
        "音": ["異音", "音", "うるさい", "振動", "ガタガタ", "キーキー"],
        
        # 外装関連
        "外装": ["外装", "ボディ", "傷", "破損", "錆", "塗装"],
        "ボディ": ["外装", "ボディ", "傷", "破損", "錆", "塗装"]
    }
    
    # クエリから関連キーワードを抽出
    for word in query_lower.split():
        if word in keyword_mappings:
            related_keywords.extend(keyword_mappings[word])
    
    # 重複を除去
    related_keywords = list(set(related_keywords))
    
    print(f"🔍 検索キーワード: {query}")
    print(f"🔗 関連キーワード: {related_keywords}")
    
    for filename in txt_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content_lower = content.lower()
                is_relevant = False
                match_type = ""
                
                # 直接的なマッチ
                if query_lower in content_lower:
                    is_relevant = True
                    match_type = "direct"
                
                # 関連キーワードでのマッチ
                if not is_relevant and related_keywords:
                    for keyword in related_keywords:
                        if keyword.lower() in content_lower:
                            is_relevant = True
                            match_type = "related"
                            break
                
                # ファイル名でのマッチ
                if not is_relevant:
                    filename_lower = filename.lower()
                    for keyword in related_keywords:
                        if keyword.lower() in filename_lower:
                            is_relevant = True
                            match_type = "filename"
                            break
                
                # 部分マッチング（より柔軟な検索）
                if not is_relevant:
                    query_words = query_lower.split()
                    for word in query_words:
                        if len(word) > 2 and word in content_lower:
                            is_relevant = True
                            match_type = "partial"
                            break
                
                if is_relevant:
                    # 関連する部分を抽出（改良版）
                    lines = content.split('\n')
                    relevant_lines = []
                    
                    # クエリが含まれる行を探す
                    for i, line in enumerate(lines):
                        line_lower = line.lower()
                        if (query_lower in line_lower or 
                            any(keyword.lower() in line_lower for keyword in related_keywords)):
                            # 前後の行も含める
                            start = max(0, i - 3)
                            end = min(len(lines), i + 4)
                            relevant_lines.extend(lines[start:end])
                    
                    # 重複を除去
                    relevant_lines = list(dict.fromkeys(relevant_lines))
                    
                    if relevant_lines:
                        results.append({
                            "filename": filename,
                            "content": '\n'.join(relevant_lines[:20]),  # 最大20行
                            "source": "text_file",
                            "relevance": "high" if match_type == "direct" else "medium",
                            "match_type": match_type
                        })
                        print(f"✅ マッチ発見 ({filename}): {match_type}")
                        
            except Exception as e:
                print(f"❌ ファイル読み込みエラー ({filename}): {e}")
    
    print(f"📊 検索結果: {len(results)}件")
    return results

def extract_repair_costs_from_content(content: str) -> str:
    """テキストファイルから修理費用を抽出"""
    lines = content.split('\n')
    costs = []
    in_cost_section = False
    
    print(f"🔍 修理費用抽出開始: {len(lines)}行")
    
    for line in lines:
        line = line.strip()
        
        # 修理費用セクションの開始を検出
        if '## 修理費用目安' in line or '修理費用目安' in line:
            in_cost_section = True
            print(f"✅ 修理費用セクション開始: {line}")
            continue
        
        # セクション終了の検出
        if in_cost_section and line.startswith('##') and '修理費用目安' not in line:
            print(f"🔚 修理費用セクション終了: {line}")
            break
        
        # 修理費用項目の抽出
        if in_cost_section and line.startswith('**') and '円' in line:
            print(f"💰 修理費用項目発見: {line}")
            # **項目名**: 金額 の形式から項目名と金額を抽出
            if '**:' in line:
                parts = line.split('**:')
                if len(parts) == 2:
                    item_name = parts[0].replace('**', '').strip()
                    cost_range = parts[1].strip()
                    cost_item = f"• {item_name}: {cost_range}"
                    costs.append(cost_item)
                    print(f"✅ 抽出完了: {cost_item}")
            # その他の形式も対応
            elif '**' in line and '円' in line:
                # **項目名** 金額 の形式
                line_clean = line.replace('**', '').strip()
                if '円' in line_clean:
                    cost_item = f"• {line_clean}"
                    costs.append(cost_item)
                    print(f"✅ 抽出完了: {cost_item}")
        
        # エアコン.txtの形式に対応：空行をスキップして次の項目を探す
        if in_cost_section and not line and len(costs) > 0:
            continue
    
    print(f"📊 抽出結果: {len(costs)}件")
    if costs:
        result = '\n'.join(costs)
        print(f"📋 最終結果:\n{result}")
        return result
    
    # フォールバック：修理費用セクションが見つからない場合でも、費用情報を探す
    print("🔍 フォールバック検索を開始...")
    for line in lines:
        line = line.strip()
        if '円' in line and any(keyword in line for keyword in ['交換', '修理', '補充', '清掃', '除去', '再整備']):
            print(f"💰 フォールバック項目発見: {line}")
            if line.startswith('**') and '**:' in line:
                parts = line.split('**:')
                if len(parts) == 2:
                    item_name = parts[0].replace('**', '').strip()
                    cost_range = parts[1].strip()
                    cost_item = f"• {item_name}: {cost_range}"
                    costs.append(cost_item)
            elif line.startswith('**') and '円' in line:
                line_clean = line.replace('**', '').strip()
                cost_item = f"• {line_clean}"
                costs.append(cost_item)
    
    if costs:
        result = '\n'.join(costs)
        print(f"📋 フォールバック結果:\n{result}")
        return result
    
    return ""

def extract_repair_steps_from_content(content: str) -> str:
    """テキストファイルから修理手順を抽出"""
    import re
    
    print(f"🔧 修理手順抽出開始")
    
    # 修理手順セクションを検索（複数のパターンを試す）
    patterns = [
        r'## 修理手順\s*\n(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'修理手順\s*\n(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'## 修理手順(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'修理手順(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'手順\s*\n(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'## 手順\s*\n(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'詳細修理手順\s*\n(.*?)(?=\n##|\n⚠️|\n\*\*|$)',
        r'## 詳細修理手順\s*\n(.*?)(?=\n##|\n⚠️|\n\*\*|$)'
    ]
    
    for i, pattern in enumerate(patterns):
        print(f"  パターン {i+1} を試行中...")
        steps_match = re.search(pattern, content, re.DOTALL)
        if steps_match:
            print(f"  ✅ パターン {i+1} でマッチしました")
            steps_section = steps_match.group(1).strip()
            print(f"  抽出されたセクション: {steps_section[:200]}...")
            
            # 手順情報を整理
            steps_lines = [line.strip() for line in steps_section.split('\n') if line.strip()]
            print(f"  手順行数: {len(steps_lines)}")
            
            if steps_lines:
                result = '\n'.join(steps_lines)
                print(f"  ✅ 修理手順抽出成功: {result[:100]}...")
                return result
            else:
                print(f"  ❌ 手順行が見つかりませんでした")
        else:
            print(f"  ❌ パターン {i+1} でマッチしませんでした")
    
    # フォールバック: 番号付きリストや箇条書きを検索
    print(f"  🔄 フォールバック検索を実行...")
    all_lines = content.split('\n')
    steps_lines = []
    
    for line in all_lines:
        line = line.strip()
        # 番号付きリスト（1. 2. 3. など）
        if re.match(r'^\d+\.', line):
            steps_lines.append(line)
        # 箇条書き（• - * など）
        elif re.match(r'^[•\-\*]\s', line):
            steps_lines.append(line)
        # 「手順」「ステップ」を含む行
        elif '手順' in line or 'ステップ' in line:
            steps_lines.append(line)
    
    if steps_lines:
        print(f"  ✅ フォールバックで {len(steps_lines)} 行の手順情報を発見")
        result = '\n'.join(steps_lines)
        print(f"  結果: {result[:100]}...")
        return result
    
    print(f"  ❌ 修理手順が見つかりませんでした")
    return ""

def extract_warnings_from_content(content: str) -> str:
    """テキストファイルから注意事項を抽出"""
    import re
    
    print(f"⚠️ 注意事項抽出開始")
    
    # 注意事項セクションを検索（複数のパターンを試す）
    patterns = [
        r'⚠️ 注意事項\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'注意事項\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'## 注意事項\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'⚠️\s*(.*?)(?=\n##|\n\*\*|$)',
        r'注意\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'## 注意\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'安全上の注意事項\s*\n(.*?)(?=\n##|\n\*\*|$)',
        r'## 安全上の注意事項\s*\n(.*?)(?=\n##|\n\*\*|$)'
    ]
    
    for i, pattern in enumerate(patterns):
        print(f"  パターン {i+1} を試行中...")
        warnings_match = re.search(pattern, content, re.DOTALL)
        if warnings_match:
            print(f"  ✅ パターン {i+1} でマッチしました")
            warnings_section = warnings_match.group(1).strip()
            print(f"  抽出されたセクション: {warnings_section[:200]}...")
            
            # 注意事項情報を整理
            warnings_lines = [line.strip() for line in warnings_section.split('\n') if line.strip()]
            print(f"  注意事項行数: {len(warnings_lines)}")
            
            if warnings_lines:
                result = '\n'.join(warnings_lines)
                print(f"  ✅ 注意事項抽出成功: {result[:100]}...")
                return result
            else:
                print(f"  ❌ 注意事項行が見つかりませんでした")
        else:
            print(f"  ❌ パターン {i+1} でマッチしませんでした")
    
    # フォールバック: ⚠️ マークや「注意」を含む行を検索
    print(f"  🔄 フォールバック検索を実行...")
    all_lines = content.split('\n')
    warnings_lines = []
    
    for line in all_lines:
        line = line.strip()
        # ⚠️ マークを含む行
        if '⚠️' in line or '注意' in line or '警告' in line or '危険' in line:
            warnings_lines.append(line)
    
    if warnings_lines:
        print(f"  ✅ フォールバックで {len(warnings_lines)} 行の注意事項を発見")
        result = '\n'.join(warnings_lines)
        print(f"  結果: {result[:100]}...")
        return result
    
    print(f"  ❌ 注意事項が見つかりませんでした")
    return ""

def get_fallback_suggestions(query: str) -> List[Dict]:
    """検索結果が空の場合のフォールバック提案を生成"""
    suggestions = []
    query_lower = query.lower()
    
    # 一般的な修理カテゴリの提案
    common_categories = {
        "バッテリー": {
            "title": "🔋 バッテリー関連の修理",
            "content": "バッテリーの充電不良、電圧不足、始動不良などの問題について",
            "keywords": ["バッテリー", "充電", "電圧", "始動", "エンジン"]
        },
        "エアコン": {
            "title": "❄️ エアコン・空調関連の修理",
            "content": "エアコンの冷房・暖房不良、フィルター清掃、温度調整などの問題について",
            "keywords": ["エアコン", "冷房", "暖房", "空調", "温度"]
        },
        "トイレ": {
            "title": "🚽 トイレ・水回り関連の修理",
            "content": "トイレの水漏れ、ポンプ不良、排水問題などの修理について",
            "keywords": ["トイレ", "水", "ポンプ", "排水", "水漏れ"]
        },
        "電装系": {
            "title": "⚡ 電装系・電気関連の修理",
            "content": "ヒューズ切れ、配線不良、スイッチ故障などの電気系統の問題について",
            "keywords": ["電装", "電気", "ヒューズ", "配線", "スイッチ"]
        },
        "雨漏り": {
            "title": "🌧️ 雨漏り・防水関連の修理",
            "content": "屋根の雨漏り、シーリング不良、防水処理などの問題について",
            "keywords": ["雨漏り", "水漏れ", "シーリング", "防水", "屋根"]
        },
        "タイヤ": {
            "title": "🛞 タイヤ・ホイール関連の修理",
            "content": "タイヤのパンク、空気圧調整、ホイール交換などの問題について",
            "keywords": ["タイヤ", "ホイール", "パンク", "空気圧", "交換"]
        }
    }
    
    # クエリに基づいて関連カテゴリを提案
    for category, info in common_categories.items():
        if any(keyword in query_lower for keyword in info["keywords"]):
            suggestions.append({
                "title": info["title"],
                "category": "関連カテゴリ",
                "content": info["content"],
                "source": "suggestion",
                "relevance": "high"
            })
    
    # 一般的な修理アドバイス
    general_advice = {
        "title": "🔧 一般的な修理アドバイス",
        "category": "修理アドバイス",
        "content": """キャンピングカーの修理でよくある問題と対処法：

1. **バッテリー関連**
   - 充電不良：充電器の確認、バッテリー端子の清掃
   - 電圧不足：バッテリーの交換、充電システムの点検

2. **エアコン関連**
   - 冷房不良：フィルター清掃、冷媒の確認
   - 暖房不良：ヒーターの点検、フィルター交換

3. **水回り関連**
   - 水漏れ：パイプ接続部の確認、シーリングの補修
   - ポンプ不良：ポンプの点検、フィルター清掃

4. **電装系関連**
   - ヒューズ切れ：ヒューズボックスの確認、適切な容量のヒューズ使用
   - 配線不良：接続部の確認、絶縁テープでの補修""",
        "source": "general_advice",
        "relevance": "medium"
    }
    
    suggestions.append(general_advice)
    
    return suggestions

def format_repair_advice(rag_results: Dict, notion_cases: List[Dict], text_results: List[Dict], query: str) -> Dict:
    """修理アドバイスをフォーマット（改良版）"""
    
    # 統合された結果を作成
    advice = {
        "query": query,
        "success": True,
        "results": []
    }
    
    # RAG結果の処理
    if rag_results and rag_results.get("text_file_content"):
        rag_content = rag_results["text_file_content"]
        if rag_content.strip():
            # 修理費用を抽出
            repair_costs = extract_repair_costs_from_content(rag_content)
            # 修理手順を抽出
            repair_steps = extract_repair_steps_from_content(rag_content)
            # 注意事項を抽出
            warnings = extract_warnings_from_content(rag_content)
            
            result_item = {
                "title": "📄 RAG検索結果",
                "category": "RAG検索",
                "content": rag_content[:1000] + "..." if len(rag_content) > 1000 else rag_content,
                "source": "rag_text",
                "relevance": "high"
            }
            
            # 修理手順がある場合は追加
            if repair_steps:
                result_item["repair_steps"] = repair_steps
                print(f"🔧 RAG結果に修理手順を追加: {repair_steps[:100]}...")
            else:
                print("⚠️ RAG結果から修理手順を抽出できませんでした")
            
            # 注意事項がある場合は追加
            if warnings:
                result_item["warnings"] = warnings
                print(f"⚠️ RAG結果に注意事項を追加: {warnings[:100]}...")
            else:
                print("⚠️ RAG結果から注意事項を抽出できませんでした")
            
            # 修理費用がある場合は追加
            if repair_costs:
                result_item["repair_costs"] = repair_costs
                result_item["costs"] = repair_costs  # 従来のフィールドも追加
                print(f"💰 RAG結果に修理費用を追加: {repair_costs[:100]}...")
            else:
                print("⚠️ RAG結果から修理費用を抽出できませんでした")
            
            advice["results"].append(result_item)
    
    # Notion結果の処理
    for case in notion_cases[:3]:  # 最大3件
        if case.get("symptoms") or case.get("solutions"):
            advice["results"].append({
                "title": f"🔧 修理ケース: {case.get('symptoms', '症状不明')[:50]}",
                "category": "修理ケース",
                "content": f"症状: {case.get('symptoms', '')}\n原因: {case.get('causes', '')}\n解決策: {case.get('solutions', '')}",
                "costs": case.get("costs", ""),
                "tools": case.get("tools", ""),
                "parts": case.get("parts", ""),
                "source": "notion",
                "relevance": "high"
            })
    
    # テキストファイル結果の処理
    for text_result in text_results[:3]:  # 最大3件
        # 修理費用を抽出
        repair_costs = extract_repair_costs_from_content(text_result["content"])
        # 修理手順を抽出
        repair_steps = extract_repair_steps_from_content(text_result["content"])
        # 注意事項を抽出
        warnings = extract_warnings_from_content(text_result["content"])
        
        result_item = {
            "title": f"📋 {text_result['filename']}",
            "category": "テキストファイル",
            "content": text_result["content"][:800] + "..." if len(text_result["content"]) > 800 else text_result["content"],
            "source": "text_file",
            "relevance": text_result.get("relevance", "medium")
        }
        
        # 修理手順がある場合は追加
        if repair_steps:
            result_item["repair_steps"] = repair_steps
            print(f"🔧 テキストファイル結果に修理手順を追加 ({text_result['filename']}): {repair_steps[:100]}...")
        else:
            print(f"⚠️ テキストファイル結果から修理手順を抽出できませんでした ({text_result['filename']})")
        
        # 注意事項がある場合は追加
        if warnings:
            result_item["warnings"] = warnings
            print(f"⚠️ テキストファイル結果に注意事項を追加 ({text_result['filename']}): {warnings[:100]}...")
        else:
            print(f"⚠️ テキストファイル結果から注意事項を抽出できませんでした ({text_result['filename']})")
        
        # 修理費用がある場合は追加
        if repair_costs:
            result_item["repair_costs"] = repair_costs
            result_item["costs"] = repair_costs  # 従来のフィールドも追加
            print(f"💰 テキストファイル結果に修理費用を追加 ({text_result['filename']}): {repair_costs[:100]}...")
        else:
            print(f"⚠️ テキストファイル結果から修理費用を抽出できませんでした ({text_result['filename']})")
        
        advice["results"].append(result_item)
    
    # ブログリンクの追加
    if rag_results and rag_results.get("blog_links"):
        blog_links = rag_results["blog_links"][:3]  # 最大3件
        if blog_links:
            blog_content = "関連ブログ記事:\n"
            for blog in blog_links:
                blog_content += f"• {blog['title']}: {blog['url']}\n"
            
            advice["results"].append({
                "title": "🔗 関連ブログ記事",
                "category": "ブログ",
                "content": blog_content,
                "source": "blog",
                "relevance": "medium"
            })
    
    # 結果がない場合はフォールバック提案を追加
    if not advice["results"]:
        print("⚠️ 検索結果が空のため、フォールバック提案を生成します")
        fallback_suggestions = get_fallback_suggestions(query)
        advice["results"] = fallback_suggestions
        advice["fallback"] = True  # フォールバック使用フラグ
    
    return advice

@app.route('/')
def index():
    """メインページ"""
    return render_template('repair_advice_center.html')

@app.route('/api/health')
def health_check():
    """ヘルスチェック"""
    return jsonify({
        "status": "healthy",
        "rag_available": RAG_AVAILABLE and rag_db is not None,
        "notion_available": NOTION_AVAILABLE and notion_client is not None
    })

@app.route('/api/search', methods=['POST'])
def search_repair_advice():
    """修理アドバイス検索API"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                "success": False,
                "error": "検索クエリが空です"
            })
        
        print(f"🔍 検索クエリ: {query}")
        
        # RAGシステムでの検索
        rag_results = None
        if rag_db:
            try:
                rag_results = enhanced_rag_retrieve(query, rag_db, max_results=5)
                print(f"✅ RAG検索完了: {len(rag_results.get('text_file_content', ''))} 文字")
            except Exception as e:
                print(f"❌ RAG検索エラー: {e}")
        
        # Notionでの検索
        notion_cases = []
        if notion_client:
            try:
                notion_cases = search_notion_repair_cases(query)
                print(f"✅ Notion検索完了: {len(notion_cases)} 件")
            except Exception as e:
                print(f"❌ Notion検索エラー: {e}")
        
        # テキストファイルでの検索
        text_results = []
        try:
            text_results = search_text_files(query)
            print(f"✅ テキストファイル検索完了: {len(text_results)} 件")
        except Exception as e:
            print(f"❌ テキストファイル検索エラー: {e}")
        
        # 結果をフォーマット
        advice = format_repair_advice(rag_results, notion_cases, text_results, query)
        
        return jsonify(advice)
        
    except Exception as e:
        print(f"❌ API エラー: {e}")
        return jsonify({
            "success": False,
            "error": f"検索中にエラーが発生しました: {str(e)}"
        })

@app.route('/api/notion/status')
def notion_status():
    """Notion接続状況の確認"""
    if not NOTION_AVAILABLE:
        return jsonify({
            "available": False,
            "error": "Notionクライアントがインストールされていません"
        })
    
    if not notion_client:
        return jsonify({
            "available": False,
            "error": "Notionクライアントが初期化されていません"
        })
    
    try:
        # 簡単な接続テスト
        case_db_id = os.getenv("CASE_DB_ID")
        if case_db_id:
            response = notion_client.databases.query(database_id=case_db_id, page_size=1)
            return jsonify({
                "available": True,
                "case_db_connected": True,
                "case_count": response.get("results", [])
            })
        else:
            return jsonify({
                "available": True,
                "error": "CASE_DB_IDが設定されていません"
            })
    except Exception as e:
        return jsonify({
            "available": False,
            "error": f"Notion接続エラー: {str(e)}"
        })

if __name__ == '__main__':
    print("🚀 修理アドバイスAPIサーバーを起動中...")
    
    # システムの初期化
    initialize_rag_system()
    initialize_notion_client()
    
    # サーバー起動
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🌐 サーバー起動: http://localhost:{port}")
    print(f"📊 RAGシステム: {'✅ 利用可能' if rag_db else '❌ 利用不可'}")
    print(f"📋 Notion: {'✅ 利用可能' if notion_client else '❌ 利用不可'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
