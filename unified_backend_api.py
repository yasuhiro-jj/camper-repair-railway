#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合バックエンドAPI - 最強チャットボット用
Flask + RAG + SERP + Notion + AI の全機能を統合
"""

from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
import asyncio
import aiohttp
import json
import os
import glob
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# APIレスポンス共通ユーティリティ
try:
    from utils.api_response import (
        success_response,
        error_response,
        validation_error_response,
        not_found_response,
        service_unavailable_response
    )
    API_RESPONSE_AVAILABLE = True
except ImportError:
    API_RESPONSE_AVAILABLE = False
    print("⚠️ APIレスポンスユーティリティが利用できません。デフォルトのエラーハンドリングを使用します。")

# 既存のモジュールをインポート
from config import OPENAI_API_KEY, SERP_API_KEY, LANGSMITH_API_KEY
from enhanced_rag_system import create_enhanced_rag_system, enhanced_rag_retrieve, create_notion_based_rag_system
from serp_search_system import get_serp_search_system
from repair_category_manager import RepairCategoryManager
from save_to_notion import save_chat_log_to_notion

# フェーズ2-1: エラーハンドリングとログ分析
try:
    from utils.response_logger import response_logger
    from utils.error_handler import error_handler
    PHASE2_LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ フェーズ2-1モジュールが利用できません: {e}")
    PHASE2_LOGGING_AVAILABLE = False
    # ダミーオブジェクトを作成
    class DummyLogger:
        def log_response_quality(self, *args, **kwargs): pass
        def log_error(self, *args, **kwargs): pass
        def log_performance(self, *args, **kwargs): pass
    class DummyErrorHandler:
        @staticmethod
        def handle_openai_error(*args, **kwargs): return ("エラー", False)
        @staticmethod
        def handle_notion_error(*args, **kwargs): return {"error": "エラー", "message": "エラー"}
        @staticmethod
        def handle_rag_error(*args, **kwargs): return {"error": "エラー", "message": "エラー"}
        @staticmethod
        def handle_serp_error(*args, **kwargs): return {"error": "エラー", "message": "エラー"}
    response_logger = DummyLogger()
    error_handler = DummyErrorHandler()

# フェーズ1で追加: Factory ManagerとBuilder Manager
try:
    from data_access.factory_manager import FactoryManager
    from data_access.builder_manager import BuilderManager
    PHASE1_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ フェーズ1モジュールが利用できません: {e}")
    PHASE1_AVAILABLE = False

# Notion関連のインポート
try:
    from data_access.notion_client import notion_client
    NOTION_AVAILABLE = True
    print("✅ Notionクライアントが利用可能です")
except ImportError:
    NOTION_AVAILABLE = False
    print("⚠️ Notionクライアントが利用できません")

# === Flask アプリケーションの設定 ===
app = Flask(__name__)
# CORS設定
# - ローカル開発用: localhost 系
# - 本番フロントエンド: Vercel のドメイン
CORS(
    app,
    origins=[
        "http://localhost:8501",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5002",
        "https://camper-repair-railway-upoj.vercel.app",
    ],
    supports_credentials=True,
)

# Swagger UI用のエンドポイント
@app.route("/api/docs")
def swagger_ui():
    """Swagger UIを表示"""
    try:
        import yaml
        with open('openapi.yaml', 'r', encoding='utf-8') as f:
            openapi_spec = yaml.safe_load(f)
        
        # OpenAPI仕様書をJSON形式で提供
        swagger_html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Camper Repair System API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "/api/docs/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                validatorUrl: null
            }});
        }};
    </script>
</body>
</html>
"""
        return swagger_html
    except Exception as e:
        return f"<html><body><h1>Swagger UI読み込みエラー</h1><p>{str(e)}</p></body></html>", 500

@app.route("/api/docs/openapi.json")
def openapi_json():
    """OpenAPI仕様書をJSON形式で提供"""
    try:
        import yaml
        with open('openapi.yaml', 'r', encoding='utf-8') as f:
            openapi_spec = yaml.safe_load(f)
        return jsonify(openapi_spec)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# グローバル変数
db = None
category_manager = None
serp_system = None
notion_client_instance = None
factory_manager = None
builder_manager = None

# キャッシュシステム
cache = {}
CACHE_EXPIRY_SECONDS = 300  # 5分

# ソース別の重み係数（優先度: NOTION > RAG > SERP）
SOURCE_WEIGHTS = {
    "notion": 1.0,
    "rag": 0.7,
    "serp": 0.4
}

# シノニム辞書（同義語マッピング）
SYNONYM_DICT = {
    "電圧低下": ["電圧降下", "電圧ダウン", "電圧減少"],
    "電圧が低い": ["電圧不足", "電圧低下", "電圧降下"],
    "炎が弱い": ["火が弱い", "火力不足", "燃焼不良"],
    "水圧が弱い": ["水圧不足", "水圧低下", "水の出が悪い"],
    "異音": ["変な音", "うるさい音", "カタカタ音", "キーキー音"],
    "バッテリーが上がる": ["バッテリー上がり", "充電不足", "電圧低下"],
    "エンジンがかからない": ["エンジン始動不良", "始動しない", "かからない"],
    "エアコンが効かない": ["冷房不良", "暖房不良", "温度調整不良"],
    "ガス臭": ["ガス漏れ", "ガス漏れ臭", "プロパン臭"],
    "過負荷": ["オーバーロード", "負荷過多", "容量超過"],
    "劣化": ["老朽化", "経年劣化", "寿命"],
    "詰まる": ["閉塞", "ブロック", "流れない"]
}

# セーフティキーワード（警告が必要な危険な症状）
SAFETY_KEYWORDS = {
    "ガス": ["ガス臭", "ガス漏れ", "プロパン臭", "LPG臭"],
    "高電圧": ["火花", "ショート", "感電", "漏電"],
    "火災": ["煙", "焦げ臭", "発熱", "過熱"],
    "一酸化炭素": ["CO", "頭痛", "めまい", "吐き気"]
}

def initialize_services():
    """サービス初期化"""
    global db, category_manager, serp_system, notion_client_instance, factory_manager, builder_manager
    
    try:
        # RAGシステムの初期化（Notion統合版）
        # 環境変数でテキストファイルも含めるか設定可能
        use_text_files = os.getenv("USE_TEXT_FILES", "true").lower() == "true"
        
        # テキストファイルの自動検出
        if use_text_files:
            txt_files = glob.glob("*.txt")
            if txt_files:
                print(f"📁 検出されたテキストファイル: {len(txt_files)}件")
                for txt_file in txt_files:
                    print(f"  - {txt_file}")
            else:
                print("⚠️ テキストファイルが見つかりません")
        
        print(f"🔄 RAGシステムをバックグラウンドで初期化します... (テキストファイル使用: {use_text_files})")
        
        # RAGシステムの初期化を非同期で試行（起動時間を短縮）
        # Note: 実際のRAG検索は最初のリクエスト時に遅延ロードされます
        db = None  # 初期はNoneにして高速起動
        
        # バックグラウンドで初期化（非ブロッキング）
        import threading
        def init_rag_background():
            global db
            try:
                print("🔄 バックグラウンドでRAGシステム初期化中...")
                db_temp = create_notion_based_rag_system(use_text_files=use_text_files)
                if db_temp:
                    db = db_temp
                    print("✅ Notion統合RAGシステム初期化完了（バックグラウンド）")
                else:
                    print("⚠️ Notion統合RAGシステムの初期化に失敗しました")
                    # フォールバック処理
                    print("🔄 従来のRAGシステムで再試行中...")
                    db_temp = create_enhanced_rag_system()
                    if db_temp:
                        db = db_temp
                        print("✅ 従来のRAGシステムで初期化完了（バックグラウンド）")
                    else:
                        print("❌ 従来のRAGシステムの初期化にも失敗しました")
            except Exception as e:
                print(f"⚠️ RAGシステムの初期化エラー: {e}")
        
        # バックグラウンドスレッドで初期化
        init_thread = threading.Thread(target=init_rag_background, daemon=True)
        init_thread.start()
        print("⚡ RAGシステムの初期化をバックグラウンドで開始しました（高速起動）")
        
        # カテゴリーマネージャーの初期化
        category_manager = RepairCategoryManager()
        print("✅ カテゴリーマネージャー初期化完了")
        
        # SERPシステムの初期化
        serp_system = get_serp_search_system()
        print("✅ SERPシステム初期化完了")
        
        # Notionクライアントの初期化
        if NOTION_AVAILABLE:
            try:
                print("🔄 Notionクライアント初期化を開始...")
                notion_client_instance = notion_client
                
                # APIキーの確認
                api_key = notion_client_instance.api_key
                if not api_key:
                    print("❌ Notion APIキーが設定されていません")
                    notion_client_instance = None
                else:
                    print(f"✅ Notion APIキー確認済み: {api_key[:10]}...")
                
                # クライアント初期化（診断データのテスト読み込みは削除してパフォーマンス改善）
                result = notion_client_instance.initialize_client()
                if result:
                    print("✅ Notionクライアント初期化完了（遅延ロード有効）")
                else:
                    print("⚠️ Notionクライアント初期化に失敗")
                    notion_client_instance = None
            except Exception as e:
                print(f"❌ Notionクライアント初期化エラー: {e}")
                import traceback
                traceback.print_exc()
                notion_client_instance = None
        else:
            notion_client_instance = None
            print("⚠️ Notionクライアントが利用できません")
        
        # フェーズ1: Factory ManagerとBuilder Managerの初期化
        if PHASE1_AVAILABLE:
            try:
                print("🔄 Factory ManagerとBuilder Managerを初期化中...")
                factory_manager = FactoryManager()
                builder_manager = BuilderManager()
                print("✅ Factory ManagerとBuilder Manager初期化完了")
            except Exception as e:
                print(f"⚠️ Factory Manager/Builder Manager初期化エラー: {e}")
                factory_manager = None
                builder_manager = None
        else:
            factory_manager = None
            builder_manager = None
            print("⚠️ Factory ManagerとBuilder Managerが利用できません")
        
        return True
    except Exception as e:
        print(f"❌ サービス初期化エラー: {e}")
        return False

# === 統合API エンドポイント ===

@app.route("/", methods=["GET"])
def root():
    """ルートエンドポイント - フロントエンドHTMLを返す"""
    try:
        from flask import render_template
        return render_template('unified_chatbot.html')
    except Exception as e:
        return jsonify({
            "message": "最強キャンピングカー修理チャットボット API",
            "version": "1.0",
            "endpoints": [
                "/api/unified/health",
                "/api/unified/chat",
                "/api/unified/search",
                "/api/unified/diagnostic",
                "/api/unified/repair_guide",
                "/start_conversation",
                "/ask"
            ],
            "error": f"テンプレート読み込みエラー: {str(e)}"
        })

@app.route("/unified_chatbot.html", methods=["GET"])
def unified_chatbot():
    """統合チャットボットHTMLを返す"""
    try:
        from flask import render_template
        return render_template('unified_chatbot.html')
    except Exception as e:
        return jsonify({
            "message": "統合チャットボット",
            "error": f"テンプレート読み込みエラー: {str(e)}"
        }), 500

@app.route("/start_conversation", methods=["POST"])
def start_conversation():
    """新しい会話を開始"""
    try:
        import uuid
        conversation_id = str(uuid.uuid4())
        
        # 会話履歴の初期化（必要に応じて）
        # conversation_history[conversation_id] = []
        
        return jsonify({
            "conversation_id": conversation_id,
            "message": "新しい会話を開始しました",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"会話開始エラー: {str(e)}"}), 500

@app.route("/ask", methods=["POST"])
def ask():
    """質問に回答するエンドポイント（フロントエンド互換用）"""
    try:
        # フォームデータとJSONの両方に対応
        session_id = ""
        raw_message = ''
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json() or {}
            question = data.get('question', '')
            raw_message = data.get('raw_message', '')
            session_id = data.get('conversation_id') or data.get('session_id') or ''
        else:
            question = request.form.get('question', '')
            raw_message = request.form.get('raw_message', '')
            session_id = request.form.get('conversation_id') or request.form.get('session_id') or ''
        
        if not question:
            return jsonify({"error": "質問が入力されていません"}), 400
        
        try:
            # 意図分析
            intent = analyze_intent(question)
            
            # 基本的なチャット処理
            result = process_chat_mode(question, intent, include_serp=True)
            
            # フロントエンドの期待する形式に変換
            answer = result.get("response", "回答を生成できませんでした")
            if isinstance(answer, dict):
                answer = str(answer)

            # 会話ログ保存
            try:
                bot_text = answer
                category = intent.get("category") if isinstance(intent, dict) else None
                subcategory = None

                urgency_value = None
                try:
                    urgency_label = (intent.get("urgency") if isinstance(intent, dict) else None) or ""
                    mapping = {"low": 2, "medium": 3, "high": 5}
                    if isinstance(urgency_label, str):
                        urgency_value = mapping.get(urgency_label.lower())
                except Exception:
                    urgency_value = None

                kw_list = []
                try:
                    if isinstance(intent, dict) and isinstance(intent.get("keywords"), list):
                        kw_list = [str(x) for x in intent.get("keywords")[:10]]
                except Exception:
                    kw_list = []

                tool_used = "chat"
                try:
                    if isinstance(result, dict):
                        if result.get("notion_results") and (
                            len(result["notion_results"].get("repair_cases", []))
                            + len(result["notion_results"].get("diagnostic_nodes", []))
                        ) > 0:
                            tool_used = "notion"
                        elif result.get("rag_results") and len(result["rag_results"].get("documents", [])) > 0:
                            tool_used = "rag"
                        elif result.get("serp_results") and len(result["serp_results"].get("results", [])) > 0:
                            tool_used = "serp"
                except Exception:
                    pass

                print("🔍 Notion保存処理を開始します...")
                user_message_for_log = raw_message or question
                print(f"   - user_msg: {user_message_for_log[:50]}...")
                print(f"   - session_id: {session_id}")
                print(f"   - category: {category}")
                print(f"   - tool_used: {tool_used}")

                saved, error_msg = save_chat_log_to_notion(
                    user_msg=user_message_for_log,
                    bot_msg=bot_text,
                    session_id=session_id or "",
                    category=category,
                    subcategory=subcategory,
                    urgency=urgency_value,
                    keywords=kw_list,
                    tool_used=tool_used,
                )
                if saved:
                    print("✅ Notion保存成功")
                else:
                    print(f"⚠️ Notion保存失敗: {error_msg}")
            except Exception as log_error:
                print(f"⚠️ Notion保存処理でエラー: {log_error}")
                import traceback
                traceback.print_exc()

            return jsonify({
                "answer": answer,
                "sources": result.get("rag_results", {}),
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                "answer": f"回答生成中にエラーが発生しました: {str(e)}",
                "sources": {},
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        return jsonify({"error": f"質問処理エラー: {str(e)}"}), 500

@app.route("/repair_advice_simple.html", methods=["GET"])
def repair_advice_simple():
    """修理アドバイスセンター（シンプル版）HTMLを返す"""
    try:
        with open('repair_advice_simple.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>ページが見つかりません: {str(e)}</h1>", 404

@app.route("/repair_advice_center.html", methods=["GET"])
def repair_advice_center():
    """修理アドバイスセンターHTMLを返す"""
    try:
        from flask import render_template
        return render_template('repair_advice_center.html')
    except Exception as e:
        # テンプレートが見つからない場合は、検索機能付きのHTMLを返す
        return f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🔧 修理アドバイスセンター</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                    backdrop-filter: blur(10px);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #667eea;
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }}
                .back-btn {{
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-size: 1rem;
                    font-weight: bold;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    margin-bottom: 20px;
                }}
                .back-btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                }}
                .search-container {{
                    background: #f8f9fa;
                    border-radius: 15px;
                    padding: 30px;
                    margin-bottom: 30px;
                }}
                .search-input {{
                    width: 100%;
                    padding: 15px 20px;
                    border: 2px solid #667eea;
                    border-radius: 25px;
                    font-size: 1rem;
                    outline: none;
                    margin-bottom: 15px;
                }}
                .search-input:focus {{
                    border-color: #764ba2;
                    box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
                }}
                .search-btn {{
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 25px;
                    font-size: 1rem;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                .search-btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                }}
                .search-btn:disabled {{
                    opacity: 0.6;
                    cursor: not-allowed;
                    transform: none;
                }}
                .results-container {{
                    background: white;
                    border-radius: 15px;
                    padding: 20px;
                    margin-top: 20px;
                    display: none;
                }}
                .result-item {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid #667eea;
                }}
                .result-title {{
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 8px;
                }}
                .result-content {{
                    color: #666;
                    line-height: 1.6;
                }}
                .loading {{
                    text-align: center;
                    color: #667eea;
                    font-style: italic;
                    display: none;
                }}
                .quick-search {{
                    display: flex;
                    gap: 10px;
                    margin-top: 15px;
                    flex-wrap: wrap;
                }}
                .quick-btn {{
                    background: rgba(102, 126, 234, 0.1);
                    color: #667eea;
                    border: 1px solid #667eea;
                    padding: 8px 16px;
                    border-radius: 15px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    font-size: 0.9rem;
                }}
                .quick-btn:hover {{
                    background: #667eea;
                    color: white;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/" class="back-btn">← チャットボットに戻る</a>
                <div class="header">
                    <h1>🔧 修理アドバイスセンター</h1>
                    <p>詳細な修理情報と価格データを提供します</p>
                </div>
                
                <div class="search-container">
                    <h2>🔍 修理情報検索</h2>
                    <input type="text" id="searchInput" class="search-input" placeholder="修理したい部品や症状を入力してください..." onkeypress="handleKeyPress(event)">
                    <button class="search-btn" onclick="searchRepairInfo()" id="searchBtn">検索</button>
                    
                    <div class="quick-search">
                        <button class="quick-btn" onclick="quickSearch('バッテリー')">バッテリー</button>
                        <button class="quick-btn" onclick="quickSearch('エアコン')">エアコン</button>
                        <button class="quick-btn" onclick="quickSearch('トイレ')">トイレ</button>
                        <button class="quick-btn" onclick="quickSearch('FFヒーター')">FFヒーター</button>
                        <button class="quick-btn" onclick="quickSearch('水道ポンプ')">水道ポンプ</button>
                        <button class="quick-btn" onclick="quickSearch('インバーター')">インバーター</button>
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    🔍 検索中...
                </div>
                
                <div class="results-container" id="resultsContainer">
                    <h3>📋 検索結果</h3>
                    <div id="resultsContent"></div>
                </div>
            </div>
            
            <script>
                async function searchRepairInfo() {{
                    const query = document.getElementById('searchInput').value.trim();
                    console.log('🔍 検索開始:', query);
                    
                    if (!query) {{
                        console.log('❌ クエリが空です');
                        return;
                    }}
                    
                    const searchBtn = document.getElementById('searchBtn');
                    const loading = document.getElementById('loading');
                    const resultsContainer = document.getElementById('resultsContainer');
                    const resultsContent = document.getElementById('resultsContent');
                    
                    console.log('🔄 UI更新中...');
                    searchBtn.disabled = true;
                    searchBtn.textContent = '検索中...';
                    loading.style.display = 'block';
                    resultsContainer.style.display = 'none';
                    
                    try {{
                        console.log('📡 APIリクエスト送信中...');
                        const response = await fetch('/api/repair_advice/search', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{ query: query }})
                        }});
                        
                        console.log('📥 レスポンス受信:', response.status, response.statusText);
                        
                        if (response.ok) {{
                            const data = await response.json();
                            console.log('✅ データ取得成功:', data);
                            displayResults(data);
                        }} else {{
                            const error = await response.json();
                            console.log('❌ エラーレスポンス:', error);
                            resultsContent.innerHTML = '<div class="result-item"><div class="result-title">❌ エラー</div><div class="result-content">' + error.error + '</div></div>';
                            resultsContainer.style.display = 'block';
                        }}
                    }} catch (error) {{
                        console.log('💥 接続エラー:', error);
                        resultsContent.innerHTML = '<div class="result-item"><div class="result-title">❌ 接続エラー</div><div class="result-content">サーバーに接続できませんでした: ' + error.message + '</div></div>';
                        resultsContainer.style.display = 'block';
                    }} finally {{
                        console.log('🏁 検索完了');
                        searchBtn.disabled = false;
                        searchBtn.textContent = '検索';
                        loading.style.display = 'none';
                    }}
                }}
                
                function displayResults(data) {{
                    const resultsContent = document.getElementById('resultsContent');
                    const resultsContainer = document.getElementById('resultsContainer');
                    
                    if (!data.results || data.results.length === 0) {{
                        resultsContent.innerHTML = '<div class="result-item"><div class="result-title">🔍 結果なし</div><div class="result-content">該当する修理情報が見つかりませんでした。</div></div>';
                    }} else {{
                        let html = '';
                        data.results.forEach(result => {{
                            html += '<div class="result-item">';
                            html += '<div class="result-title">' + result.title + '</div>';
                            html += '<div class="result-content">' + result.content + '</div>';
                            if (result.url) {{
                                html += '<div style="margin-top: 10px;"><a href="' + result.url + '" target="_blank" style="color: #667eea; text-decoration: underline;">詳細を見る</a></div>';
                            }}
                            html += '</div>';
                        }});
                        resultsContent.innerHTML = html;
                    }}
                    
                    resultsContainer.style.display = 'block';
                }}
                
                function quickSearch(query) {{
                    document.getElementById('searchInput').value = query;
                    searchRepairInfo();
                }}
                
                function handleKeyPress(event) {{
                    if (event.key === 'Enter') {{
                        searchRepairInfo();
                    }}
                }}
            </script>
        </body>
        </html>
        """, 200

def format_text_content(text: str, query: str) -> str:
    """テキストコンテンツを読みやすく整形する"""
    try:
        formatted_lines = []
        
        # パイプ(|)で区切られた長い文字列を検出して構造化
        if '|' in text and len(text) > 100 and text.count('|') > 3:
            # パイプ区切りのテキストを構造化
            text = format_pipe_separated_text(text)
        
        # 見出しと本文を分離
        lines = text.split('\n')
        current_section = ""
        in_conversation = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 会話形式の検出（**ユーザー** または **スタッフ**）
            if line.startswith('**ユーザー**'):
                in_conversation = True
                formatted_lines.append(f"\n💬 **ユーザー:**")
                continue
            elif line.startswith('**スタッフ**'):
                formatted_lines.append(f"\n👨‍🔧 **スタッフ:**")
                continue
            
            # 区切り線
            if line.startswith('---') or line == '---':
                formatted_lines.append(f"\n{'─' * 40}\n")
                continue
            
            # 見出し（### で始まる）
            if line.startswith('###'):
                title = line.replace('###', '').strip()
                formatted_lines.append(f"\n### 📋 {title}\n")
                current_section = title
                in_conversation = False
            
            # 見出し（## で始まる）
            elif line.startswith('##'):
                title = line.replace('##', '').strip()
                # Caseパターンを特別処理
                if '【Case' in title or 'Case' in title:
                    formatted_lines.append(f"\n## 📌 {title}\n")
                else:
                    formatted_lines.append(f"\n## 🔧 {title}\n")
                current_section = title
                in_conversation = False
            
            # 見出し（# で始まる）
            elif line.startswith('#'):
                title = line.replace('#', '').strip()
                formatted_lines.append(f"\n# 🚀 {title}\n")
                current_section = title
                in_conversation = False
            
            # 番号付きリスト（1. で始まる）
            elif len(line) > 2 and line[0].isdigit() and '. ' in line[0:5]:
                # ステップ番号を抽出
                parts = line.split('.', 1)
                if len(parts) == 2:
                    num = parts[0].strip()
                    content = parts[1].strip()
                    
                    # 太字部分（**で囲まれた部分）を強調
                    if '**' in content:
                        # **text** を維持
                        pass
                    
                    formatted_lines.append(f"  {num}️⃣ {content}")
            
            # 箇条書き（- で始まる）
            elif line.startswith('-'):
                content = line[1:].strip()
                
                # アイコンを自動追加
                if '電圧' in content or 'テスター' in content or '測定' in content:
                    icon = '⚡'
                elif '費用' in content or '円' in content or '料金' in content or '価格' in content:
                    icon = '💰'
                elif '工具' in content or 'スパナ' in content or 'レンチ' in content:
                    icon = '🔧'
                elif '部品' in content or '交換' in content or 'パーツ' in content:
                    icon = '🔩'
                elif '注意' in content or '警告' in content or '危険' in content:
                    icon = '⚠️'
                elif '時間' in content or '日数' in content:
                    icon = '⏱️'
                elif '難易度' in content or 'レベル' in content:
                    icon = '⚙️'
                elif '水' in content or '液' in content or '漏れ' in content:
                    icon = '💧'
                elif '臭い' in content or 'ニオイ' in content:
                    icon = '👃'
                else:
                    icon = '▪️'
                
                formatted_lines.append(f"    {icon} {content}")
            
            # 会話形式の内容
            elif in_conversation:
                # インデントして表示
                formatted_lines.append(f"  ↪ {line}")
            
            # 通常のテキスト
            else:
                # 重要なキーワードを強調
                if any(keyword in line for keyword in ['重要', '注意', '警告', '必須', '危険']):
                    formatted_lines.append(f"\n⚠️ **{line}**\n")
                elif any(keyword in line for keyword in ['推奨', 'おすすめ', 'ポイント', 'ヒント']):
                    formatted_lines.append(f"\n💡 {line}\n")
                elif any(keyword in line for keyword in ['症状', '問題', 'トラブル']):
                    formatted_lines.append(f"\n🔍 {line}")
                elif any(keyword in line for keyword in ['原因', '理由']):
                    formatted_lines.append(f"\n🎯 {line}")
                elif any(keyword in line for keyword in ['対処', '解決', '修理']):
                    formatted_lines.append(f"\n✅ {line}")
                else:
                    # 長い文章は改行を追加
                    if len(line) > 50:
                        formatted_lines.append(f"\n{line}\n")
                    else:
                        formatted_lines.append(f"{line}")
        
        # 整形されたテキストを結合
        formatted_text = '\n'.join(formatted_lines)
        
        # 連続する空行を削除
        while '\n\n\n' in formatted_text:
            formatted_text = formatted_text.replace('\n\n\n', '\n\n')
        
        # 長すぎる場合は要約
        if len(formatted_text) > 2000:
            # 最初の重要な部分を保持
            formatted_text = formatted_text[:2000] + "\n\n...(以下省略)\n\n💡 **より詳しい情報が必要な場合は、専門業者にご相談ください**"
        
        return formatted_text
        
    except Exception as e:
        print(f"⚠️ テキスト整形エラー: {e}")
        import traceback
        traceback.print_exc()
        # エラーの場合は元のテキストを返す（最大500文字）
        return text[:500] + "..." if len(text) > 500 else text

def format_pipe_separated_text(text: str) -> str:
    """パイプ(|)で区切られたテキストを構造化された形式に変換"""
    try:
        # デバッグ: 元のテキストの一部を表示
        print(f"🔍 パイプ区切りテキスト処理開始: {len(text)}文字")
        print(f"   最初の200文字: {text[:200]}")
        
        # 「内容:」以降の部分を優先的に使用（process_general_contentで生成された形式の場合）
        if '内容:' in text:
            content_start = text.find('内容:')
            if content_start >= 0:
                # 「内容:」以降の部分を取得
                actual_content = text[content_start + 3:].strip()  # 「内容:」の3文字をスキップ
                print(f"  ✅ '内容:'セクションを検出: {len(actual_content)}文字")
                print(f"     最初の300文字: {actual_content[:300]}")
                
                # 実際の内容が元のテキストファイルの構造を保持している場合は、そのまま使用
                if '\n' in actual_content and ('###' in actual_content or '##' in actual_content):
                    print(f"  ✅ 構造化されたコンテンツを検出（パイプ区切りではなく構造化済み）")
                    print(f"     構造化済みコンテンツの最初の300文字: {actual_content[:300]}")
                    return actual_content
                
                # パイプ区切りテキストの場合は処理を続行
                print(f"  📝 パイプ区切りテキストとして処理を続行")
                text = actual_content
        
        # パイプで分割
        parts = [p.strip() for p in text.split('|') if p.strip()]
        
        print(f"📊 パイプ分割結果: {len(parts)}個の要素")
        print(f"   最初の10要素: {parts[:10]}")
        
        if not parts:
            return text
        
        formatted_parts = []
        current_case = None
        current_section = None  # 現在のセクション（症状、原因、対処法など）
        section_content = []  # セクションの内容を一時保存
        
        # セクションタイトル
        section_keywords = ['症状', '原因', '対処法', '修理手順', '費用目安', '工具', '部品', '注意事項', '連絡先']
        
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            
            # 見出しパターンの検出（▲ **見出し: ...）
            if part.startswith('▲') or part.startswith('**見出し'):
                # 前のセクションの内容を出力
                if current_section and section_content:
                    formatted_parts.append(f"\n### {current_section}\n")
                    formatted_parts.extend(section_content)
                    section_content = []
                    current_section = None
                
                # 見出しのマークアップを削除
                clean_part = part.replace('▲', '').replace('**', '').replace('見出し:', '').strip()
                if clean_part:
                    formatted_parts.append(f"\n## {clean_part}\n")
                continue
            
            # Caseパターンの検出（【Case XX-X】）
            if '【Case' in part or ('Case' in part and '【' not in part):
                # 前のセクションの内容を出力
                if current_section and section_content:
                    formatted_parts.append(f"\n### {current_section}\n")
                    formatted_parts.extend(section_content)
                    section_content = []
                    current_section = None
                
                # Case番号を抽出
                case_match = None
                if '【Case' in part:
                    case_match = part[part.find('【Case'):part.find('】')+1] if '】' in part else None
                elif 'Case' in part:
                    import re
                    case_match = re.search(r'Case\s*[A-Z0-9-]+', part)
                    if case_match:
                        case_match = case_match.group(0)
                
                if case_match:
                    current_case = case_match
                    # Caseの後の説明を抽出
                    case_desc = part.replace(case_match, '').strip()
                    if case_desc:
                        formatted_parts.append(f"\n## {case_match} {case_desc}\n")
                    else:
                        formatted_parts.append(f"\n## {case_match}\n")
                else:
                    formatted_parts.append(f"\n## {part}\n")
                continue
            
            # セクションタイトル（症状、原因、対処法など）
            is_section_title = False
            matched_keyword = None
            
            # セクションタイトルかどうかを判定（完全一致または単独）
            for keyword in section_keywords:
                if part == keyword or part.strip() == keyword:
                    is_section_title = True
                    matched_keyword = keyword
                    break
            
            if is_section_title:
                # 前のセクションの内容を出力
                if current_section and section_content:
                    formatted_parts.append(f"\n### {current_section}\n")
                    formatted_parts.extend(section_content)
                    section_content = []
                
                # 新しいセクションを開始
                current_section = matched_keyword
                print(f"  ✅ セクション開始: {current_section}")
                continue
            
            # セクションタイトルを含む場合（例：「症状 | 冷風が出ない」）
            for keyword in section_keywords:
                if keyword in part and '|' in part:
                    # セクションタイトルと内容を分離
                    sub_parts = [p.strip() for p in part.split('|') if p.strip()]
                    for sub_part in sub_parts:
                        if sub_part == keyword:
                            # 前のセクションの内容を出力
                            if current_section and section_content:
                                formatted_parts.append(f"\n### {current_section}\n")
                                formatted_parts.extend(section_content)
                                section_content = []
                            current_section = keyword
                        elif sub_part and current_section:
                            # セクションの内容として追加
                            icon = get_icon_for_content(sub_part)
                            section_content.append(f"- {icon} {sub_part}")
                    break
            
            # 次の要素がセクションタイトルかどうかを確認
            next_is_section = False
            if i + 1 < len(parts):
                next_part = parts[i + 1].strip()
                for keyword in section_keywords:
                    if next_part == keyword:
                        next_is_section = True
                        break
            
            # 次の要素がCaseかどうかを確認
            next_is_case = False
            if i + 1 < len(parts):
                next_part = parts[i + 1].strip()
                if '【Case' in next_part or ('Case' in next_part and '【' not in next_part):
                    next_is_case = True
            
            # 現在のセクションの内容として追加
            if current_section:
                # セクションタイトルでもCaseでもない場合は内容として追加
                icon = get_icon_for_content(part)
                section_content.append(f"- {icon} {part}")
                print(f"  📝 セクション '{current_section}' に追加: {part[:50]}...")
            else:
                # セクションが設定されていない場合は通常の項目として追加
                icon = get_icon_for_content(part)
                formatted_parts.append(f"- {icon} {part}")
        
        # 最後のセクションの内容を出力
        if current_section and section_content:
            formatted_parts.append(f"\n### {current_section}\n")
            formatted_parts.extend(section_content)
            print(f"  ✅ 最後のセクション '{current_section}' を出力: {len(section_content)}項目")
        
        # 構造化されたテキストを結合
        result = '\n'.join(formatted_parts)
        
        # 連続する空行を削除
        while '\n\n\n' in result:
            result = result.replace('\n\n\n', '\n\n')
        
        print(f"✅ パイプ区切りテキスト処理完了: {len(result)}文字")
        return result
        
    except Exception as e:
        print(f"⚠️ パイプ区切りテキスト整形エラー: {e}")
        import traceback
        traceback.print_exc()
        return text

def get_icon_for_content(content: str) -> str:
    """コンテンツに応じたアイコンを返す"""
    if '費用' in content or '円' in content or '料金' in content or '価格' in content or '診断料' in content:
        return "💰"
    elif '症状' in content or '問題' in content:
        return "🔍"
    elif '原因' in content:
        return "🎯"
    elif '対処' in content or '修理' in content or '解決' in content:
        return "✅"
    elif '工具' in content or '部品' in content or '材料' in content:
        return "🔧"
    elif '注意' in content or '警告' in content:
        return "⚠️"
    elif '連絡' in content or '電話' in content or '住所' in content:
        return "📞"
    elif '電圧' in content or 'テスター' in content or '測定' in content or 'バッテリー' in content:
        return "⚡"
    elif '水' in content or '液' in content or '漏れ' in content:
        return "💧"
    else:
        return "▪️"

@app.route("/api/repair_advice/search", methods=["POST"])
def repair_advice_search():
    """修理アドバイスセンター用検索API"""
    try:
        print(f"🔍 検索API呼び出し: {request.method} {request.url}")
        
        # リクエストデータの取得と検証
        try:
            data = request.get_json()
            if not data:
                print("❌ リクエストデータが空です")
                return jsonify({"error": "リクエストデータが空です"}), 400
        except Exception as e:
            print(f"❌ JSONパースエラー: {e}")
            return jsonify({"error": "無効なJSONデータです"}), 400
        
        print(f"📝 リクエストデータ: {data}")
        query = data.get('query', '').strip()
        print(f"🔎 検索クエリ: '{query}'")
        
        if not query:
            print("❌ クエリが空です")
            return jsonify({"error": "検索クエリが空です"}), 400
        
        # 統合検索を実行
        search_results = []
        
        # 1. RAG検索
        print(f"🔍 RAG検索チェック: db={db is not None}")
        if db:
            try:
                print(f"🔍 RAG検索実行中...クエリ='{query}'")
                rag_results = enhanced_rag_retrieve(query, db, max_results=3)
                print(f"📊 RAG検索完了。結果の型: {type(rag_results)}")
                print(f"📊 RAG結果のキー: {list(rag_results.keys()) if isinstance(rag_results, dict) else 'dict以外'}")
                
                # テキストファイルコンテンツがある場合（優先的に使用）
                text_content = rag_results.get('text_file_content', '')
                print(f"📄 text_file_content: {len(text_content) if text_content else 0}文字")
                if text_content and len(text_content) > 10:
                    # パイプ区切りテキストの検出と構造化
                    if '|' in text_content and len(text_content) > 100 and text_content.count('|') > 3:
                        print(f"  🔍 パイプ区切りテキストを検出: {text_content.count('|')}個のパイプ")
                        try:
                            # まずパイプ区切りテキストを構造化
                            text_content = format_pipe_separated_text(text_content)
                            print(f"  ✅ パイプ区切りテキスト処理完了: {len(text_content)}文字")
                        except Exception as e:
                            print(f"  ⚠️ パイプ区切りテキスト処理エラー: {e}")
                            import traceback
                            traceback.print_exc()
                            # エラーが発生しても処理を続行
                    
                    # テキストを読みやすく整形
                    try:
                        formatted_content = format_text_content(text_content, query)
                        print(f"  ✅ テキスト整形完了: {len(formatted_content)}文字")
                    except Exception as e:
                        print(f"  ⚠️ テキスト整形エラー: {e}")
                        import traceback
                        traceback.print_exc()
                        # エラーが発生した場合は元のテキストを使用
                        formatted_content = text_content[:2000] + "..." if len(text_content) > 2000 else text_content
                    
                    search_results.append({
                        "title": f"📄 {query}の詳細情報",
                        "content": formatted_content,
                        "source": "技術資料（テキスト）",
                        "category": "詳細情報",
                        "url": None,
                        "relevance": "high"
                    })
                    print(f"  ✅ テキストコンテンツを追加（整形済み）")
                
                # マニュアルコンテンツがある場合（text_file_contentがない場合のみ使用）
                manual_content = rag_results.get('manual_content', '')
                print(f"📚 manual_content: {len(manual_content) if manual_content else 0}文字")
                if manual_content and len(manual_content) > 10 and not text_content:
                    # まずパイプ区切りテキストを整形
                    if '|' in manual_content and len(manual_content) > 100 and manual_content.count('|') > 3:
                        manual_content = format_pipe_separated_text(manual_content)
                    
                    # 次にテキストコンテンツを整形
                    formatted_manual_content = format_text_content(manual_content, query)
                    
                    # 費用情報を抽出
                    cost_info = ""
                    if "費用" in formatted_manual_content or "料金" in formatted_manual_content or "価格" in formatted_manual_content:
                        # 費用関連の部分を抽出
                        lines = formatted_manual_content.split('\n')
                        for line in lines:
                            if any(keyword in line for keyword in ["費用", "料金", "価格", "円"]):
                                cost_info += line + "\n"
                    
                    # 費用情報を含むコンテンツを構築
                    full_content = formatted_manual_content[:1500] + "\n\n...(以下省略)" if len(formatted_manual_content) > 1500 else formatted_manual_content
                    if cost_info:
                        full_content = f"### 💰 費用情報\n\n{cost_info}\n\n---\n\n" + full_content
                    
                    # LLMを使って人間的な回答を生成
                    try:
                        from langchain_openai import ChatOpenAI
                        from langchain_core.messages import HumanMessage, SystemMessage
                        
                        # LLMの初期化
                        llm = ChatOpenAI(
                            model="gpt-3.5-turbo",
                            temperature=0.7,
                            openai_api_key=os.getenv("OPENAI_API_KEY")
                        )
                        
                        # システムプロンプト
                        system_prompt = """あなたはキャンピングカーの修理専門家です。
知識ベースから取得した修理情報を基に、ユーザーにとって分かりやすく、実用的な修理アドバイスを提供してください。

以下の情報を含めて、人間らしい口調で回答してください：
- 具体的な症状の説明
- 段階的な修理手順
- 必要な工具や部品
- 費用の目安
- 難易度と時間の目安
- 安全上の注意点

専門的でありながら、初心者にも理解しやすい説明を心がけてください。"""
                        
                        # ユーザープロンプト
                        user_prompt = f"""以下の知識ベース情報を基に、「{query}」についての修理アドバイスを生成してください：

{full_content}

上記の情報を参考に、実用的で分かりやすい修理ガイドを作成してください。"""
                        
                        # LLMに送信
                        messages = [
                            SystemMessage(content=system_prompt),
                            HumanMessage(content=user_prompt)
                        ]
                        
                        response = llm.invoke(messages)
                        human_content = response.content
                        
                        # レスポンスの検証
                        if not human_content or len(human_content.strip()) < 10:
                            raise Exception("AI生成された回答が短すぎます")
                        
                        search_results.append({
                            "title": f"📚 {query}の修理情報（AI生成）",
                            "content": human_content,
                            "source": "知識ベース（RAG）+ AI生成",
                            "category": "修理情報",
                            "url": None,
                            "relevance": "high"
                        })
                        print(f"  ✅ AI生成回答完了: {len(human_content)}文字")
                        
                    except Exception as e:
                        print(f"⚠️ AI生成エラー: {e}")
                        # フォールバック: 整形済みの情報をそのまま使用
                        search_results.append({
                            "title": f"📚 {query}の修理情報（RAG）",
                            "content": full_content,
                            "source": "知識ベース（RAG）",
                            "category": "修理情報",
                            "url": None,
                            "relevance": "high"
                        })
                        print(f"  ✅ マニュアルコンテンツを追加（整形済み・費用情報含む）")
                
                # ブログリンクがある場合
                blog_links = rag_results.get('blog_links', [])
                print(f"🔗 blog_links: {len(blog_links) if blog_links else 0}件")
                if blog_links and isinstance(blog_links, list):
                    for i, blog in enumerate(blog_links[:2]):
                        print(f"  ブログ{i+1}: {blog.get('title', 'N/A')}")
                        search_results.append({
                            "title": f"🔗 {blog.get('title', 'ブログ記事')}",
                            "content": f"関連ブログ: {blog.get('title', 'タイトルなし')}",
                            "source": "ブログ",
                            "category": "関連情報",
                            "url": blog.get('url'),
                            "relevance": "medium"
                        })
                        print(f"  ✅ ブログリンク{i+1}を追加")
                
                print(f"📊 RAG検索後の結果数: {len(search_results)}")
                
            except Exception as e:
                print(f"❌ RAG検索エラー: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ RAGシステムが初期化されていません")
            print("🔍 Notionデータベースを直接検索します...")
            
            # Notionデータベースを直接検索（RAGが失敗した場合のフォールバック）
            if NOTION_AVAILABLE and notion_client_instance:
                try:
                    print("🔍 Notionデータベースを直接検索中...")
                    repair_cases = notion_client_instance.load_repair_cases()
                    if repair_cases:
                        print(f"📊 修理ケース数: {len(repair_cases)}件")
                        
                        # クエリに関連する修理ケースを検索
                        query_lower = query.lower()
                        for case in repair_cases[:5]:  # 最初の5件をチェック
                            case_text = f"{case.get('title', '')} {case.get('category', '')} {case.get('solution', '')}".lower()
                            if any(keyword in case_text for keyword in query_lower.split()):
                                # 具体的な修理情報を構築
                                content_parts = []
                                
                                if case.get('title'):
                                    content_parts.append(f"🔧 ケースID: {case['title']}")
                                
                                if case.get('category'):
                                    content_parts.append(f"📂 カテゴリ: {case['category']}")
                                
                                if case.get('symptoms'):
                                    symptoms = case['symptoms']
                                    if isinstance(symptoms, list):
                                        symptoms_str = ', '.join(str(s) for s in symptoms if s)
                                    else:
                                        symptoms_str = str(symptoms)
                                    content_parts.append(f"🔍 症状: {symptoms_str}")
                                
                                if case.get('solution'):
                                    solution_text = case.get('solution')
                                    # パイプ区切りテキストの整形
                                    if '|' in solution_text and len(solution_text) > 50:
                                        solution_text = format_pipe_separated_text(solution_text)
                                    content_parts.append(f"🛠️ 解決方法:\n{solution_text}")
                                
                                if case.get('cost'):
                                    content_parts.append(f"💰 費用目安: {case['cost']}円")
                                
                                if case.get('difficulty'):
                                    content_parts.append(f"⚙️ 難易度: {case['difficulty']}")
                                
                                if case.get('time_estimate'):
                                    content_parts.append(f"⏱️ 推定時間: {case['time_estimate']}")
                                
                                # 整形されたコンテンツを結合して整形
                                formatted_case_content = '\n\n'.join(content_parts)
                                formatted_case_content = format_text_content(formatted_case_content, query)
                                
                                # LLMを使って人間的な回答を生成
                                try:
                                    from langchain_openai import ChatOpenAI
                                    from langchain_core.messages import HumanMessage, SystemMessage
                                    
                                    # LLMの初期化
                                    llm = ChatOpenAI(
                                        model="gpt-3.5-turbo",
                                        temperature=0.7,
                                        openai_api_key=os.getenv("OPENAI_API_KEY")
                                    )
                                    
                                    # システムプロンプト
                                    system_prompt = """あなたはキャンピングカーの修理専門家です。
Notionデータベースから取得した修理ケース情報を基に、ユーザーにとって分かりやすく、実用的な修理アドバイスを提供してください。

以下の情報を含めて、人間らしい口調で回答してください：
- 具体的な症状の説明
- 段階的な修理手順
- 必要な工具や部品
- 費用の目安
- 難易度と時間の目安
- 安全上の注意点

専門的でありながら、初心者にも理解しやすい説明を心がけてください。"""
                                    
                                    # ユーザープロンプト
                                    user_prompt = f"""以下の修理ケース情報を基に、「{query}」についての修理アドバイスを生成してください：

{formatted_case_content}

上記の情報を参考に、実用的で分かりやすい修理ガイドを作成してください。"""
                                    
                                    # LLMに送信
                                    messages = [
                                        SystemMessage(content=system_prompt),
                                        HumanMessage(content=user_prompt)
                                    ]
                                    
                                    response = llm.invoke(messages)
                                    human_content = response.content
                                    
                                    # レスポンスの検証
                                    if not human_content or len(human_content.strip()) < 10:
                                        raise Exception("AI生成された回答が短すぎます")
                                    
                                    search_results.append({
                                        'title': f'🔧 {case.get("title", "修理ケース")} - 専門家アドバイス',
                                        'content': human_content,
                                        'source': 'Notionデータベース + AI生成',
                                        'category': case.get('category', '修理ケース'),
                                        'url': case.get('url', ''),
                                        'relevance': 'high'
                                    })
                                    
                                    print(f"✅ AI生成回答完了: {len(human_content)}文字")
                                    
                                except Exception as e:
                                    print(f"⚠️ AI生成エラー: {e}")
                                    # フォールバック: 整形済みの情報をそのまま使用
                                    search_results.append({
                                        'title': f'🔧 {case.get("title", "修理ケース")}',
                                        'content': formatted_case_content,
                                        'source': 'Notionデータベース',
                                        'category': case.get('category', '修理ケース'),
                                        'url': case.get('url', ''),
                                        'relevance': 'high'
                                    })
                                
                                print(f"✅ Notion修理ケース検索結果: {len(search_results)}件")
                                break  # 最初の一致するケースのみ追加
                    
                except Exception as e:
                    print(f"⚠️ Notion直接検索エラー: {e}")
                    import traceback
                    traceback.print_exc()
        
        # 2. ハイブリッド検索（RAG + Notion + テキストファイル）
        if db:
            print("🔄 ハイブリッド検索を実行中...")
            try:
                # RAG検索を実行
                rag_results = enhanced_rag_retrieve(query, db, max_results=5)
                if rag_results:
                    for result in rag_results:
                        # ソースタイプに応じて処理
                        source_type = result.metadata.get("source_type", "unknown")
                        
                        if source_type == "notion_knowledge_base":
                            search_results.append({
                                'title': f'📚 {result.metadata.get("title", "ナレッジベース")}',
                                'content': result.page_content,
                                'source': 'Notionナレッジベース',
                                'category': result.metadata.get("category", "ナレッジベース"),
                                'url': result.metadata.get("url", ''),
                                'relevance': 'high'
                            })
                        elif source_type == "notion_repair_case":
                            search_results.append({
                                'title': f'🔧 {result.metadata.get("title", "修理ケース")}',
                                'content': result.page_content,
                                'source': 'Notion修理ケース',
                                'category': result.metadata.get("category", "修理ケース"),
                                'url': result.metadata.get("url", ''),
                                'relevance': 'high'
                            })
                        elif source_type == "text_file":
                            search_results.append({
                                'title': f'📄 {result.metadata.get("title", "テキストファイル")}',
                                'content': result.page_content,
                                'source': 'テキストファイル',
                                'category': result.metadata.get("category", "テキストファイル"),
                                'url': result.metadata.get("url", ''),
                                'relevance': 'medium'
                            })
                        else:
                            search_results.append({
                                'title': f'🔍 {result.metadata.get("title", "検索結果")}',
                                'content': result.page_content,
                                'source': 'RAG検索',
                                'category': result.metadata.get("category", "検索結果"),
                                'url': result.metadata.get("url", ''),
                                'relevance': 'medium'
                            })
                    
                    print(f"✅ ハイブリッド検索完了: {len(search_results)}件の結果")
                else:
                    print("⚠️ ハイブリッド検索結果が空です")
            except Exception as e:
                print(f"⚠️ ハイブリッド検索エラー: {e}")
                import traceback
                traceback.print_exc()
        
        # 3. Notion検索（フォールバック）
        if not search_results and NOTION_AVAILABLE and notion_client_instance:
            try:
                print("🔍 Notion検索実行中...")
                notion_results = notion_client_instance.search_database(query)
                print(f"📊 Notion検索結果: {len(notion_results) if notion_results else 0}件")
                
                if notion_results:
                    for result in notion_results[:2]:  # 最大2件に制限
                        title = result.get('title', '修理ケース')
                        result_type = result.get('type', 'ケース')
                        symptoms = result.get('symptoms', '')
                        solution = result.get('solution', '')
                        cost_estimate = result.get('cost_estimate', '')
                        difficulty = result.get('difficulty', '')
                        estimated_time = result.get('estimated_time', '')
                        
                        # 費用情報を含むコンテンツを構築
                        full_content = f"🔧 {title}\n"
                        full_content += f"📂 カテゴリ: {result_type}\n"
                        
                        if symptoms:
                            full_content += f"🔍 症状: {symptoms}\n"
                        
                        if solution:
                            full_content += f"🛠️ 解決方法: {solution}\n"
                        
                        if cost_estimate:
                            full_content += f"💰 費用目安: {cost_estimate}\n"
                        
                        if difficulty:
                            full_content += f"⚙️ 難易度: {difficulty}\n"
                        
                        if estimated_time:
                            full_content += f"⏱️ 推定時間: {estimated_time}\n"
                        
                        search_results.append({
                            "title": f"🔧 {title}",
                            "content": full_content,
                            "source": "Notionデータベース",
                            "category": result_type,
                            "url": None,
                            "relevance": "high"
                        })
            except Exception as e:
                print(f"Notion検索エラー: {e}")
                import traceback
                traceback.print_exc()
        
        # 4. SERP検索（価格情報）- 既存結果が少ない場合のみ実行
        if serp_system and len(search_results) < 3:
            try:
                print("🔍 SERP検索実行中...")
                serp_results = serp_system.search(f"{query} キャンピングカー 修理 価格")
                if serp_results and 'results' in serp_results:
                    print(f"📊 SERP検索結果: {len(serp_results['results'])}件")
                    for result in serp_results['results'][:2]:
                        title = result.get('title', '価格情報')
                        snippet = result.get('snippet', '価格情報が利用できません')
                        search_results.append({
                            "title": f"💰 {title}",
                            "content": snippet[:400] + "..." if len(snippet) > 400 else snippet,
                            "source": "価格検索",
                            "category": "価格情報",
                            "url": result.get('url'),
                            "relevance": "medium"
                        })
            except Exception as e:
                print(f"SERP検索エラー: {e}")
        
        # 結果が空の場合は、一般的なアドバイスを提供
        if not search_results:
            print("⚠️ 検索結果が空 - 一般アドバイスを追加")
            search_results.append({
                "title": f"🔍 {query}の修理について",
                "content": f"{query}に関する修理情報:\n\n1. まずは該当部品の状態を確認してください\n2. 電源やバッテリーの接続を確認\n3. 異音や異臭がないか注意深く観察\n4. 詳細な診断には専門業者への相談をお勧めします\n\n具体的な症状を教えていただければ、より詳細なアドバイスが可能です。",
                "source": "一般アドバイス",
                "category": "基本情報",
                "url": None,
                "relevance": "medium"
            })
        
        print(f"✅ 検索完了: {len(search_results)}件の結果")
        
        # Chat logをNotionに保存
        try:
            # 検索結果を整形して回答文字列を作成
            bot_response_parts = []
            for i, result in enumerate(search_results[:3], 1):  # 最初の3件のみ使用
                title = result.get('title', '')
                content = result.get('content', '')
                if title and content:
                    bot_response_parts.append(f"{title}\n{content}")
                elif content:
                    bot_response_parts.append(content)
                elif title:
                    bot_response_parts.append(title)
            
            # 回答が空の場合はフォールバックメッセージを使用
            if bot_response_parts:
                bot_response = "\n\n---\n\n".join(bot_response_parts)
            else:
                bot_response = f"{query}に関する検索結果が見つかりませんでした。"
            
            # session_idをリクエストから取得（なければデフォルト値）
            session_id = data.get('session_id', 'repair_advice_center')
            
            # categoryを最初の検索結果から取得
            category = None
            if search_results:
                category = search_results[0].get('category', '修理アドバイス')
            else:
                category = '修理アドバイス'
            
            # keywordsをクエリから抽出（簡単な実装）
            keywords = [word.strip() for word in query.split() if len(word.strip()) > 1][:5]
            
            # Chat logを保存（回答が空でない場合のみ）
            if bot_response and bot_response.strip():
                saved, error_msg = save_chat_log_to_notion(
                    user_msg=query,
                    bot_msg=bot_response,
                    session_id=session_id,
                    category=category,
                    subcategory="修理アドバイスセンター",
                    keywords=keywords if keywords else None,
                    tool_used="repair_advice_search"
                )
                
                if saved:
                    print(f"✅ Chat logをNotionに保存しました: session_id={session_id}, category={category}")
                else:
                    print(f"⚠️ Chat logの保存に失敗しました: {error_msg}")
            else:
                print(f"⚠️ Chat logをスキップしました: 回答が空です")
        except Exception as e:
            # Chat logの保存に失敗してもAPIは正常に動作するようにする
            print(f"⚠️ Chat log保存エラー（処理は継続）: {e}")
            import traceback
            traceback.print_exc()
        
        response_data = {
            "query": query,
            "results": search_results,
            "total": len(search_results)
        }
        print(f"📤 レスポンス送信: {response_data}")
        
        # レスポンスの検証
        try:
            # JSON形式で返すことを確認
            response_json = jsonify(response_data)
            print(f"✅ JSONレスポンス生成成功: {len(str(response_json.data))}文字")
            return response_json
        except Exception as e:
            print(f"❌ JSONレスポンス生成エラー: {e}")
            return jsonify({
                "error": "レスポンス生成エラー",
                "query": query,
                "results": [],
                "total": 0
            }), 500
        
    except Exception as e:
        print(f"❌ 検索エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"検索エラー: {str(e)}"}), 500

@app.route("/api/test", methods=["GET"])
def test_api():
    """テスト用API"""
    return jsonify({
        "status": "OK",
        "message": "API is working",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/unified/health", methods=["GET"])
def unified_health_check():
    """統合ヘルスチェック（軽量版）"""
    # RAGシステムがまだ初期化中でも「起動中」として返す
    rag_status = "initializing" if db is None else "ready"
    
    services_status = {
        "rag_system": rag_status,
        "category_manager": category_manager is not None,
        "serp_system": serp_system is not None,
        "notion_client": notion_client_instance is not None,
        "openai_api": OPENAI_API_KEY is not None,
        "serp_api": SERP_API_KEY is not None
    }
    
    # RAGが初期化中でも基本サービスは動作
    basic_healthy = (
        category_manager is not None and 
        notion_client_instance is not None and 
        OPENAI_API_KEY is not None
    )
    
    return jsonify({
        "status": "healthy" if basic_healthy else "degraded",
        "rag_status": rag_status,
        "services": services_status,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/debug/notion", methods=["GET"])
def debug_notion():
    """Notionデータベース接続デバッグエンドポイント"""
    try:
        if not NOTION_AVAILABLE:
            return jsonify({
                "status": "error",
                "message": "Notionクライアントが利用できません"
            })
        
        # 環境変数の確認
        env_vars = {
            "NOTION_API_KEY": "設定済み" if os.getenv("NOTION_API_KEY") else "未設定",
            "NODE_DB_ID": os.getenv("NODE_DB_ID", "未設定"),
            "CASE_DB_ID": os.getenv("CASE_DB_ID", "未設定"),
            "ITEM_DB_ID": os.getenv("ITEM_DB_ID", "未設定"),
            "KNOWLEDGE_BASE_DB_ID": os.getenv("KNOWLEDGE_BASE_DB_ID", "未設定")
        }
        
        # Notionクライアントの接続テスト
        connection_results = {}
        
        if notion_client_instance:
            try:
                # ナレッジベースDBの接続テスト
                kb_db_id = os.getenv("KNOWLEDGE_BASE_DB_ID")
                if kb_db_id:
                    try:
                        response = notion_client_instance.client.databases.query(database_id=kb_db_id, page_size=1)
                        connection_results["knowledge_base"] = {
                            "status": "success",
                            "count": len(response.get("results", []))
                        }
                    except Exception as e:
                        connection_results["knowledge_base"] = {
                            "status": "error",
                            "message": str(e)
                        }
                else:
                    connection_results["knowledge_base"] = {
                        "status": "error",
                        "message": "KNOWLEDGE_BASE_DB_IDが設定されていません"
                    }
            except Exception as e:
                connection_results["notion_client"] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return jsonify({
            "status": "success",
            "environment_variables": env_vars,
            "connection_results": connection_results,
            "notion_available": NOTION_AVAILABLE
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route("/api/test/notion-save", methods=["POST"])
def test_notion_save_endpoint():
    """Notion保存機能のテスト用エンドポイント（軽量版）"""
    try:
        data = request.get_json() or {}
        user_msg = data.get("message", "テストメッセージ")
        session_id = data.get("session_id", "test-session")
        
        print("🔍 テストエンドポイント: Notion保存処理を開始します...")
        
        # 環境変数の確認
        import os
        notion_api_key = os.getenv("NOTION_API_KEY")
        notion_log_db_id = os.getenv("NOTION_LOG_DB_ID")
        
        print(f"   環境変数確認:")
        print(f"   - NOTION_API_KEY: {'設定済み' if notion_api_key else '❌ 未設定'}")
        print(f"   - NOTION_LOG_DB_ID: {'設定済み' if notion_log_db_id else '❌ 未設定'}")
        
        if not notion_api_key or not notion_log_db_id:
            return jsonify({
                "status": "error",
                "message": "環境変数が未設定です",
                "details": {
                    "NOTION_API_KEY": "設定済み" if notion_api_key else "❌ 未設定",
                    "NOTION_LOG_DB_ID": "設定済み" if notion_log_db_id else "❌ 未設定"
                },
                "saved": False
            }), 500
        
        # 保存処理を直接実行
        print(f"   - 保存処理開始: user_msg={user_msg[:50]}...")
        print(f"   - session_id={session_id}")
        
        saved, error_msg = save_chat_log_to_notion(
            user_msg=user_msg,
            bot_msg="これはテスト用の応答です。",
            session_id=session_id,
            category="テスト",
            urgency=3,
            keywords=["テスト"],
            tool_used="test",
        )
        
        print(f"   - 保存結果: saved={saved}, error_msg={error_msg[:200] if error_msg else 'なし'}")
        
        if saved:
            return jsonify({
                "status": "success",
                "message": "Notion保存成功",
                "saved": True
            })
        else:
            # エラーメッセージを詳細に返す
            error_response = {
                "status": "error",
                "message": "Notion保存失敗（詳細はサーバーログを確認）",
                "error_details": error_msg or "エラー詳細が取得できませんでした",
                "saved": False
            }
            print(f"❌ エラーレスポンス: {error_response}")
            return jsonify(error_response), 500
            
    except Exception as e:
        print(f"❌ テストエンドポイントエラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }), 500

@app.route("/api/unified/chat", methods=["POST"])
def unified_chat():
    """
    統合チャットAPI（タイムアウト対応）
    
    ユーザーからのメッセージを受け取り、AIが回答を生成します。
    RAG検索、Notion検索、SERP検索を統合して、最適な回答を提供します。
    
    Request Body:
        {
            "message": "エアコンが効かない",
            "mode": "chat" | "diagnostic" | "repair_search" | "cost_estimate",
            "include_serp": true,
            "session_id": "optional-session-id"
        }
    
    Returns:
        {
            "response": "AIの回答テキスト",
            "rag_results": {...},
            "notion_results": {...},
            "serp_results": {...}
        }
    
    Raises:
        400: メッセージが空の場合
        500: サーバーエラー
        504: タイムアウトエラー
    """
    import time
    import concurrent.futures
    
    endpoint_start_time = time.time()
    endpoint_timeout = 50  # エンドポイント全体のタイムアウト（秒）
    
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        mode = data.get("mode", "chat")
        include_serp = data.get("include_serp", True)
        session_id = data.get("session_id", "")
        
        if not message:
            return jsonify({"error": "メッセージが空です"}), 400
        
        print(f"🚀 /api/unified/chat リクエスト開始: message='{message[:50]}...', mode={mode}")
        
        # タイムアウト付きで処理を実行
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                def process_request():
                    # 意図分析
                    intent_start = time.time()
                    intent = analyze_intent(message)
                    intent_time = time.time() - intent_start
                    print(f"✅ 意図分析完了: {intent_time:.2f}秒")
                    
                    # モード別処理
                    process_start = time.time()
                    if mode == "diagnostic":
                        result = process_diagnostic_mode(message, intent)
                    elif mode == "repair_search":
                        result = process_repair_search_mode(message, intent)
                    elif mode == "cost_estimate":
                        result = process_cost_estimate_mode(message, intent)
                    else:  # chat
                        result = process_chat_mode(message, intent, include_serp)
                    process_time = time.time() - process_start
                    print(f"✅ モード別処理完了: {process_time:.2f}秒")
                    
                    return result
                
                future = executor.submit(process_request)
                result = future.result(timeout=endpoint_timeout)
                
        except concurrent.futures.TimeoutError:
            elapsed_time = time.time() - endpoint_start_time
            print(f"❌ /api/unified/chat タイムアウト: {elapsed_time:.2f}秒（制限: {endpoint_timeout}秒）")
            return jsonify({
                "error": f"リクエストがタイムアウトしました（{endpoint_timeout}秒以内に完了しませんでした）",
                "timeout": True,
                "elapsed_time": f"{elapsed_time:.2f}s"
            }), 504
        
        # 返答テキストの抽出（Notion保存用）
        print(f"🔍 会話ログ保存準備中... (session_id: {session_id})")
        try:
            bot_text = None
            if isinstance(result, dict):
                if isinstance(result.get("response"), str):
                    bot_text = result.get("response")
                elif isinstance(result.get("message"), str):
                    bot_text = result.get("message")
            if not bot_text:
                import json as _json
                bot_text = _json.dumps(result, ensure_ascii=False)[:1900]
            print(f"   - bot_text長さ: {len(bot_text) if bot_text else 0}文字")

            # カテゴリは意図分析の結果を利用
            category = None
            if isinstance(intent, dict):
                category = intent.get("category")

            # サブカテゴリ（現状なし）：将来拡張のため None
            subcategory = None

            # 緊急度マッピング（low/medium/high → 数値）
            urgency_value = None
            try:
                urgency_label = (intent.get("urgency") if isinstance(intent, dict) else None) or ""
                mapping = {"low": 2, "medium": 3, "high": 5}
                if isinstance(urgency_label, str):
                    urgency_value = mapping.get(urgency_label.lower())
            except Exception:
                urgency_value = None

            # キーワード（意図分析の結果）
            kw_list = []
            try:
                if isinstance(intent, dict) and isinstance(intent.get("keywords"), list):
                    kw_list = [str(x) for x in intent.get("keywords")[:10]]
            except Exception:
                kw_list = []

            # 使用ツール（NOTION/RAG/SERP の優先判定）
            tool_used = "chat"
            try:
                if isinstance(result, dict):
                    # 優先度: notion > rag > serp
                    if result.get("notion_results") and (
                        len(result["notion_results"].get("repair_cases", []))
                        + len(result["notion_results"].get("diagnostic_nodes", []))
                    ) > 0:
                        tool_used = "notion"
                    elif result.get("rag_results") and len(result["rag_results"].get("documents", [])) > 0:
                        tool_used = "rag"
                    elif result.get("serp_results") and len(result["serp_results"].get("results", [])) > 0:
                        tool_used = "serp"
                    elif isinstance(result.get("type"), str):
                        if "notion" in result["type"]:
                            tool_used = "notion"
                        elif "diagnostic" in result["type"]:
                            tool_used = "diagnostic"
            except Exception:
                pass

            # Notion に会話ログ保存（失敗しても処理継続）
            print("🔍 Notion保存処理を開始します...")
            print(f"   - user_msg: {message[:50]}...")
            print(f"   - session_id: {session_id}")
            print(f"   - category: {category}")
            print(f"   - tool_used: {tool_used}")
            print(f"   - bot_text: {len(bot_text) if bot_text else 0}文字")
            
            saved, error_msg = save_chat_log_to_notion(
                user_msg=message,
                bot_msg=bot_text,
                session_id=session_id,
                category=category,
                subcategory=subcategory,
                urgency=urgency_value,
                keywords=kw_list,
                tool_used=tool_used,
            )
            if saved:
                print("✅ Notion保存成功")
            else:
                print(f"⚠️ Notion保存失敗: {error_msg}")
        except Exception as e:
            # ログ保存の失敗はAPI応答に影響させない
            print(f"⚠️ Notion保存処理でエラー: {e}")
            import traceback
            traceback.print_exc()

        # 処理時間のログ
        total_elapsed = time.time() - endpoint_start_time
        print(f"✅ /api/unified/chat 完了: 合計処理時間 {total_elapsed:.2f}秒")
        
        # レスポンスに処理時間を追加
        if isinstance(result, dict):
            result["processing_time"] = f"{total_elapsed:.2f}s"
        
        return jsonify(result)
        
    except Exception as e:
        elapsed_time = time.time() - endpoint_start_time
        print(f"❌ /api/unified/chat エラー: {str(e)} (処理時間: {elapsed_time:.2f}秒)")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"チャット処理エラー: {str(e)}",
            "processing_time": f"{elapsed_time:.2f}s"
        }), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    """チャットAPI（フロントエンド互換用）"""
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        conversation_id = data.get("conversation_id", "")
        
        if not message:
            return jsonify({"error": "メッセージが空です"}), 400
        
        # /api/unified/chatの処理を再利用
        # 意図分析
        intent = analyze_intent(message)
        
        # チャットモードで処理
        result = process_chat_mode(message, intent, include_serp=True)
        
        # レスポンス形式をフロントエンドの期待形式に変換
        response_text = result.get("response", "")
        
        # ブログリンクを抽出（RAG結果から）
        blog_links = []
        try:
            rag_results = result.get("rag_results", {})
            if rag_results and isinstance(rag_results, dict):
                blog_links = rag_results.get("blog_links", [])
        except Exception:
            pass
        
        # 返答テキストの抽出（Notion保存用）
        bot_text = response_text
        if not bot_text:
            import json as _json
            bot_text = _json.dumps(result, ensure_ascii=False)[:1900]

        # カテゴリは意図分析の結果を利用
        category = None
        if isinstance(intent, dict):
            category = intent.get("category")

        # サブカテゴリ（現状なし）
        subcategory = None

        # 緊急度マッピング
        urgency_value = None
        try:
            urgency_label = (intent.get("urgency") if isinstance(intent, dict) else None) or ""
            mapping = {"low": 2, "medium": 3, "high": 5}
            if isinstance(urgency_label, str):
                urgency_value = mapping.get(urgency_label.lower())
        except Exception:
            urgency_value = None

        # キーワード
        kw_list = []
        try:
            if isinstance(intent, dict) and isinstance(intent.get("keywords"), list):
                kw_list = [str(x) for x in intent.get("keywords")[:10]]
        except Exception:
            kw_list = []

        # 使用ツール判定
        tool_used = "chat"
        try:
            if isinstance(result, dict):
                if result.get("notion_results") and (
                    len(result["notion_results"].get("repair_cases", []))
                    + len(result["notion_results"].get("diagnostic_nodes", []))
                ) > 0:
                    tool_used = "notion"
                elif result.get("rag_results") and len(result["rag_results"].get("documents", [])) > 0:
                    tool_used = "rag"
                elif result.get("serp_results") and len(result["serp_results"].get("results", [])) > 0:
                    tool_used = "serp"
        except Exception:
            pass

        # Notion に会話ログ保存（失敗しても処理継続）
        print("🔍 Notion保存処理を開始します...")
        print(f"   - user_msg: {message[:50]}...")
        print(f"   - conversation_id: {conversation_id}")
        print(f"   - category: {category}")
        print(f"   - tool_used: {tool_used}")
        
        saved, error_msg = save_chat_log_to_notion(
            user_msg=message,
            bot_msg=bot_text,
            session_id=conversation_id,
            category=category,
            subcategory=subcategory,
            urgency=urgency_value,
            keywords=kw_list,
            tool_used=tool_used,
        )
        if saved:
            print("✅ Notion保存成功")
        else:
            print(f"⚠️ Notion保存失敗: {error_msg}")
            
        # フロントエンドの期待形式で返す
        return jsonify({
            "response": response_text,
            "blog_links": blog_links[:3] if blog_links else []
        })
        
    except Exception as e:
        print(f"❌ /api/chat エラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"チャット処理エラー: {str(e)}"}), 500

@app.route("/api/unified/search", methods=["POST"])
def unified_search():
    """統合検索API（並列検索で高速化）"""
    try:
        import concurrent.futures
        import time
        
        data = request.get_json()
        query = data.get("query", "").strip()
        search_types = data.get("types", ["rag", "serp", "categories"])
        
        if not query:
            return jsonify({"error": "検索クエリが空です"}), 400
        
        start_time = time.time()
        results = {}
        
        # 並列検索の実装
        def search_rag_unified():
            if "rag" in search_types and db:
                try:
                    return enhanced_rag_retrieve(query, db, max_results=5)
                except Exception as e:
                    return {"error": str(e)}
            return {}
        
        def search_serp_unified():
            if "serp" in search_types and serp_system:
                try:
                    return serp_system.search(query, ['repair_info', 'parts_price', 'general_info'])
                except Exception as e:
                    return {"error": str(e)}
            return {}
        
        def search_categories_unified():
            if "categories" in search_types and category_manager:
                try:
                    category = category_manager.identify_category(query)
                    if category:
                        return {
                            "category": category,
                            "icon": category_manager.get_category_icon(category),
                            "repair_costs": category_manager.get_repair_costs(category),
                            "repair_steps": category_manager.get_repair_steps_from_json(category),
                            "warnings": category_manager.get_warnings_from_json(category)
                        }
                except Exception as e:
                    return {"error": str(e)}
            return {}
        
        # 並列実行（最大2秒でタイムアウト）
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_rag = executor.submit(search_rag_unified) if "rag" in search_types else None
            future_serp = executor.submit(search_serp_unified) if "serp" in search_types else None
            future_categories = executor.submit(search_categories_unified) if "categories" in search_types else None
            
            if future_rag:
                try:
                    results["rag"] = future_rag.result(timeout=2.0)
                except concurrent.futures.TimeoutError:
                    results["rag"] = {"error": "検索タイムアウト"}
            
            if future_serp:
                try:
                    results["serp"] = future_serp.result(timeout=2.0)
                except concurrent.futures.TimeoutError:
                    results["serp"] = {"error": "検索タイムアウト"}
            
            if future_categories:
                try:
                    results["categories"] = future_categories.result(timeout=1.0)
                except concurrent.futures.TimeoutError:
                    results["categories"] = {"error": "検索タイムアウト"}
        
        search_time = time.time() - start_time
        print(f"⚡ 統合検索完了: {search_time:.2f}秒")
        
        return jsonify({
            "query": query,
            "results": results,
            "search_time": f"{search_time:.2f}s",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"検索エラー: {str(e)}"}), 500

@app.route("/api/unified/diagnostic", methods=["POST"])
def unified_diagnostic():
    """統合診断API"""
    try:
        data = request.get_json()
        symptoms = data.get("symptoms", [])
        additional_info = data.get("additional_info", "")
        
        if not symptoms:
            return jsonify({"error": "症状が指定されていません"}), 400
        
        # 診断処理
        diagnostic_result = process_diagnostic(symptoms, additional_info)
        
        return jsonify(diagnostic_result)
        
    except Exception as e:
        return jsonify({"error": f"診断エラー: {str(e)}"}), 500

@app.route("/api/unified/debug", methods=["GET"])
def debug_info():
    """デバッグ情報API"""
    try:
        # 環境変数をチェック
        notion_api_key = os.getenv("NOTION_API_KEY")
        notion_token = os.getenv("NOTION_TOKEN")
        node_db_id = os.getenv("NODE_DB_ID")
        case_db_id = os.getenv("CASE_DB_ID")
        item_db_id = os.getenv("ITEM_DB_ID")
        openai_api_key = os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY
        
        # .envファイルの存在確認
        env_exists = os.path.exists('.env')
        
        # サービス状態をチェック
        services_status = {
            "rag_system": db is not None,
            "category_manager": category_manager is not None,
            "serp_system": serp_system is not None,
            "notion_client": notion_client_instance is not None,
            "notion_available": NOTION_AVAILABLE,
            "openai_api": openai_api_key is not None,
            "serp_api": SERP_API_KEY is not None
        }
        
        debug_info = {
            "environment_variables": {
                "NOTION_API_KEY": "✅ 設定済み" if notion_api_key else "❌ 未設定",
                "NOTION_TOKEN": "✅ 設定済み" if notion_token else "❌ 未設定",
                "NODE_DB_ID": "✅ 設定済み" if node_db_id else "❌ 未設定",
                "CASE_DB_ID": "✅ 設定済み" if case_db_id else "❌ 未設定",
                "ITEM_DB_ID": "✅ 設定済み" if item_db_id else "❌ 未設定",
                "OPENAI_API_KEY": "✅ 設定済み" if openai_api_key else "❌ 未設定"
            },
            "api_keys": {
                "notion_api_key": f"{notion_api_key[:10]}...{notion_api_key[-4:] if notion_api_key and len(notion_api_key) > 14 else ''}" if notion_api_key else None,
                "notion_token": f"{notion_token[:10]}...{notion_token[-4:] if notion_token and len(notion_token) > 14 else ''}" if notion_token else None,
                "openai_api_key": f"{openai_api_key[:10]}...{openai_api_key[-4:] if openai_api_key and len(openai_api_key) > 14 else ''}" if openai_api_key else None,
                "openai_api_key_full_preview": f"{openai_api_key[:20]}...{openai_api_key[-10:] if openai_api_key and len(openai_api_key) > 30 else ''}" if openai_api_key else None
            },
            "database_ids": {
                "node_db_id": node_db_id,
                "case_db_id": case_db_id,
                "item_db_id": item_db_id
            },
            "file_checks": {
                "env_file_exists": "✅ 存在" if env_exists else "❌ 存在しない"
            },
            "services_status": services_status,
            "diagnostic_data_available": load_notion_diagnostic_data() is not None,
            "repair_cases_available": len(load_notion_repair_cases()) > 0 if notion_client_instance else False,
            "openai_info": {
                "key_source": "config.py" if OPENAI_API_KEY else ("環境変数" if openai_api_key else "未設定"),
                "key_length": len(openai_api_key) if openai_api_key else 0,
                "key_prefix": openai_api_key[:7] if openai_api_key else None
            }
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({"error": f"デバッグ情報取得エラー: {str(e)}"}), 500

@app.route("/api/unified/repair_guide", methods=["POST"])
def unified_repair_guide():
    """統合修理ガイドAPI"""
    try:
        data = request.get_json()
        problem = data.get("problem", "").strip()
        category = data.get("category", "")
        
        if not problem:
            return jsonify({"error": "問題が指定されていません"}), 400
        
        # カテゴリの自動特定
        if not category and category_manager:
            category = category_manager.identify_category(problem)
        
        # 修理ガイドの生成
        repair_guide = generate_repair_guide(problem, category)
        
        return jsonify(repair_guide)
        
    except Exception as e:
        return jsonify({"error": f"修理ガイド生成エラー: {str(e)}"}), 500

# === 新しいAPI エンドポイント ===

@app.route("/api/route", methods=["POST"])
def api_route():
    """ルーティングエンジンAPI"""
    try:
        data = request.get_json()
        current_node_id = data.get("currentNodeId", "").strip()
        user_answer = data.get("userAnswer", "").strip()
        
        if not current_node_id:
            return jsonify({"error": "currentNodeIdが必要です"}), 400
        
        # 診断データを取得（キャッシュ付き）
        diagnostic_data = load_notion_diagnostic_data_cached()
        if not diagnostic_data:
            return jsonify({"error": "診断データが利用できません"}), 500
        
        # ルーティング実行
        context = {"nodes": diagnostic_data.get("nodes", [])}
        result = route_next_node(current_node_id, user_answer, context)
        
        # ログ記録
        log_routing_decision({
            "current_node_id": current_node_id,
            "user_answer": user_answer,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"ルーティングエラー: {str(e)}"}), 500

@app.route("/api/nodes", methods=["GET"])
def api_nodes():
    """診断ノード取得API"""
    try:
        category = request.args.get("category", "")
        updated_since = request.args.get("updatedSince", "")
        
        # 診断データを取得（キャッシュ付き）
        diagnostic_data = load_notion_diagnostic_data_cached(category=category, updated_since=updated_since)
        if not diagnostic_data:
            return jsonify({"error": "診断データが利用できません"}), 500
        
        nodes = diagnostic_data.get("nodes", [])
        
        # カテゴリフィルタリング
        if category:
            nodes = [node for node in nodes if node.get("category", "").lower() == category.lower()]
        
        # 更新日時フィルタリング（簡易実装）
        if updated_since:
            # 実際の実装では、Notionの更新日時をチェック
            pass
        
        return jsonify(nodes)
        
    except Exception as e:
        return jsonify({"error": f"ノード取得エラー: {str(e)}"}), 500

@app.route("/api/cases", methods=["GET"])
def api_cases():
    """修理ケース取得API"""
    try:
        category = request.args.get("category", "")
        
        # 修理ケースを取得（キャッシュ付き）
        repair_cases = load_notion_repair_cases_cached(category=category)
        
        # カテゴリフィルタリング
        if category:
            repair_cases = [case for case in repair_cases if case.get("category", "").lower() == category.lower()]
        
        return jsonify(repair_cases)
        
    except Exception as e:
        return jsonify({"error": f"修理ケース取得エラー: {str(e)}"}), 500

@app.route("/api/kb", methods=["GET"])
def api_kb():
    """知識ベース取得API"""
    try:
        category = request.args.get("category", "")
        
        # 知識ベースデータを取得（簡易実装）
        # 実際の実装では、Notionの知識ベースページから取得
        knowledge_items = []
        
        # カテゴリフィルタリング
        if category:
            knowledge_items = [item for item in knowledge_items if item.get("category", "").lower() == category.lower()]
        
        return jsonify(knowledge_items)
        
    except Exception as e:
        return jsonify({"error": f"知識ベース取得エラー: {str(e)}"}), 500

# === 内部処理関数 ===

def analyze_intent(message: str) -> Dict[str, Any]:
    """意図分析"""
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4o-mini")
        
        prompt = f"""
        キャンピングカーの修理に関する質問の意図を分析してください。
        
        質問: {message}
        
        以下の形式でJSONを返してください:
        {{
            "intent": "diagnostic|repair_search|general_chat|parts_inquiry|cost_estimate",
            "confidence": 0.0-1.0,
            "category": "バッテリー|トイレ|エアコン|雨漏り|その他",
            "urgency": "low|medium|high",
            "keywords": ["キーワード1", "キーワード2"]
        }}
        """
        
        response = llm.invoke(prompt)
        intent_data = json.loads(response.content)
        
        return intent_data
        
    except Exception as e:
        return {
            "intent": "general_chat",
            "confidence": 0.5,
            "category": "その他",
            "urgency": "medium",
            "keywords": []
        }

def expand_keywords_with_synonyms(keywords: List[str]) -> List[str]:
    """シノニム辞書を使ってキーワードを拡張"""
    expanded_keywords = set(keywords)
    
    for keyword in keywords:
        # シノニム辞書から同義語を追加
        for base_word, synonyms in SYNONYM_DICT.items():
            if keyword in base_word or base_word in keyword:
                expanded_keywords.update(synonyms)
            for synonym in synonyms:
                if keyword in synonym or synonym in keyword:
                    expanded_keywords.add(base_word)
                    expanded_keywords.update(synonyms)
    
    return list(expanded_keywords)

def extract_snippets_from_notion_data(item: Dict[str, Any], max_length: int = 200) -> Dict[str, str]:
    """Notionデータから優先順位でスニペットを抽出"""
    snippets = {}
    
    # 優先順位: 修理手順 > 診断結果 > 質問内容 > 解決方法
    if item.get("repair_steps"):
        snippets["repair_steps"] = item["repair_steps"][:max_length] + "..." if len(item["repair_steps"]) > max_length else item["repair_steps"]
    
    if item.get("diagnosis_result"):
        snippets["diagnosis_result"] = item["diagnosis_result"][:max_length] + "..." if len(item["diagnosis_result"]) > max_length else item["diagnosis_result"]
    
    if item.get("question"):
        snippets["question"] = item["question"][:150] + "..." if len(item["question"]) > 150 else item["question"]
    
    if item.get("solution"):
        snippets["solution"] = item["solution"][:max_length] + "..." if len(item["solution"]) > max_length else item["solution"]
    
    return snippets

def check_safety_keywords(message: str) -> List[str]:
    """セーフティキーワードをチェックして警告リストを返す"""
    detected_warnings = []
    message_lower = message.lower()
    
    for category, keywords in SAFETY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                detected_warnings.append(f"{category}: {keyword}")
    
    return detected_warnings

def search_notion_knowledge(message: str, include_cache: bool = True) -> Dict[str, Any]:
    """Notionから関連知識を検索（シノニム辞書対応）"""
    try:
        global notion_client_instance
        
        if not notion_client_instance:
            return {"error": "Notion client not available"}
        
        # 修理ケースを検索
        if include_cache:
            repair_cases = load_notion_repair_cases_cached()
        else:
            repair_cases = load_notion_repair_cases()
        
        related_cases = []
        
        # メッセージからキーワードを抽出し、シノニムで拡張
        keywords = message.lower().split()
        expanded_keywords = expand_keywords_with_synonyms(keywords)
        
        for case in repair_cases:
            case_text = f"{case.get('title', '')} {case.get('category', '')} {case.get('solution', '')}".lower()
            if any(keyword.lower() in case_text for keyword in expanded_keywords):
                snippets = extract_snippets_from_notion_data(case)
                related_cases.append({
                    "title": case.get("title", ""),
                    "category": case.get("category", ""),
                    "solution": case.get("solution", "")[:200] + "..." if len(case.get("solution", "")) > 200 else case.get("solution", ""),
                    "url": case.get("url", ""),
                    "snippets": snippets,
                    "matched_keywords": [kw for kw in expanded_keywords if kw.lower() in case_text]
                })
        
        # 診断ノードを検索
        if include_cache:
            diagnostic_nodes = load_notion_diagnostic_data_cached()
        else:
            diagnostic_nodes = load_notion_diagnostic_data()
        
        related_nodes = []
        
        for node in diagnostic_nodes:
            node_text = f"{node.get('title', '')} {node.get('category', '')} {node.get('question', '')} {node.get('diagnosis_result', '')}".lower()
            if any(keyword.lower() in node_text for keyword in expanded_keywords):
                snippets = extract_snippets_from_notion_data(node)
                related_nodes.append({
                    "title": node.get("title", ""),
                    "category": node.get("category", ""),
                    "question": node.get("question", "")[:150] + "..." if len(node.get("question", "")) > 150 else node.get("question", ""),
                    "diagnosis_result": node.get("diagnosis_result", "")[:150] + "..." if len(node.get("diagnosis_result", "")) > 150 else node.get("diagnosis_result", ""),
                    "url": node.get("url", ""),
                    "snippets": snippets,
                    "matched_keywords": [kw for kw in expanded_keywords if kw.lower() in node_text]
                })
        
        # セーフティキーワードチェック
        safety_warnings = check_safety_keywords(message)
        
        return {
            "repair_cases": related_cases[:3],  # 最大3件
            "diagnostic_nodes": related_nodes[:3],  # 最大3件
            "total_cases_found": len(related_cases),
            "total_nodes_found": len(related_nodes),
            "safety_warnings": safety_warnings,
            "expanded_keywords": expanded_keywords
        }
        
    except Exception as e:
        return {"error": f"Notion search error: {str(e)}"}

def log_source_citations(message: str, rag_results: Dict, serp_results: Dict, notion_results: Dict, intent: Dict) -> Dict[str, Any]:
    """ソース別引用情報をログに記録"""
    try:
        citations = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "intent": intent,
            "sources": {
                "notion": {
                    "weight": SOURCE_WEIGHTS["notion"],
                    "items_cited": len(notion_results.get("repair_cases", [])) + len(notion_results.get("diagnostic_nodes", [])),
                    "safety_warnings": notion_results.get("safety_warnings", [])
                },
                "rag": {
                    "weight": SOURCE_WEIGHTS["rag"],
                    "items_cited": len(rag_results.get("documents", [])),
                },
                "serp": {
                    "weight": SOURCE_WEIGHTS["serp"],
                    "items_cited": len(serp_results.get("results", []))
                }
            }
        }
        
        # ログファイルに記録（JSONL形式）
        log_entry = json.dumps(citations, ensure_ascii=False)
        with open("routing_logs.jsonl", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        
        return citations
        
    except Exception as e:
        print(f"⚠️ ログ記録エラー: {e}")
        return {}

def process_chat_mode(message: str, intent: Dict[str, Any], include_serp: bool = True, include_cache: bool = True) -> Dict[str, Any]:
    """チャットモード処理（並列検索で高速化）"""
    try:
        import concurrent.futures
        import time
        
        start_time = time.time()
        
        # 並列検索の実装
        rag_results = {}
        serp_results = {}
        notion_results = {}
        
        def search_rag():
            """RAG検索（強化版・タイムアウト付き）"""
            rag_start_time = time.time()
            try:
                if db:
                    # フェーズ2-4: 強化版RAG検索を使用
                    try:
                        from utils.rag_search_enhanced import enhanced_rag_retrieve_v2
                        
                        # カテゴリを取得
                        category = intent.get('category') if isinstance(intent, dict) else None
                        
                        # 強化版RAG検索を実行
                        result_v2 = enhanced_rag_retrieve_v2(
                            query=message,
                            db=db,
                            max_results=5,
                            relevance_threshold=0.65,
                            use_query_expansion=True,
                            category=category
                        )
                        
                        # 結果を旧形式に変換（後方互換性）
                        if result_v2 and 'results' in result_v2:
                            duration = time.time() - rag_start_time
                            response_logger.log_performance("RAG検索(強化版)", duration, True, {
                                "total_found": result_v2.get('total_found', 0),
                                "returned": result_v2.get('returned', 0),
                                "queries_used": len(result_v2.get('queries_used', []))
                            })
                            
                            print(f"✅ 強化版RAG検索完了: {result_v2.get('returned', 0)}件")
                            return {'search_results': result_v2['results']}
                    
                    except ImportError:
                        print("⚠️ 強化版RAG検索モジュールが見つかりません。標準版を使用します。")
                    
                    # フォールバック: 標準版RAG検索
                    result = enhanced_rag_retrieve(message, db, max_results=5)
                    duration = time.time() - rag_start_time
                    response_logger.log_performance("RAG検索", duration, True)
                    return result
            except Exception as e:
                duration = time.time() - rag_start_time
                error_info = error_handler.handle_rag_error(e, message)
                response_logger.log_performance("RAG検索", duration, False, {"error": str(e)})
                print(f"⚠️ RAG検索エラー: {e}")
            return {}
        
        def search_serp():
            """SERP検索（強化版・タイムアウト付き・条件付き実行）"""
            serp_start_time = time.time()
            try:
                if include_serp and serp_system:
                    # フェーズ2-4: 強化版SERP検索を使用
                    try:
                        from utils.serp_query_optimizer import serp_query_optimizer, serp_result_filter
                        
                        # SERP検索が必要か判定（拡張版）
                        should_search = serp_query_optimizer.should_use_serp(message, intent)
                        
                        if should_search:
                            # クエリ最適化
                            search_params = serp_query_optimizer.get_search_parameters(message)
                            optimized_query = search_params['optimized_query']
                            
                            print(f"🌐 SERP検索実行")
                            print(f"  元のクエリ: {message}")
                            print(f"  最適化: {optimized_query}")
                            print(f"  意図: {search_params['intent']}")
                            
                            # SERP検索実行
                            result = serp_system.search(optimized_query, ['repair_info', 'parts_price', 'general_info'])
                            
                            # 結果をフィルタリングしてスコアリング
                            if result and 'results' in result:
                                filtered_results = serp_result_filter.filter_and_score_results(
                                    results=result['results'],
                                    query=message,
                                    min_relevance=0.6,
                                    max_results=5
                                )
                                
                                result['results'] = filtered_results
                                result['filtered_count'] = len(filtered_results)
                                result['optimized_query'] = optimized_query
                                
                                print(f"✅ SERP検索完了: {len(filtered_results)}件（フィルタリング後）")
                            
                            duration = time.time() - serp_start_time
                            response_logger.log_performance("SERP検索(強化版)", duration, True, {
                                "optimized_query": optimized_query,
                                "intent": search_params['intent'],
                                "filtered_count": len(filtered_results) if result and 'results' in result else 0
                            })
                            
                            return result
                        else:
                            print("⚡ SERP検索スキップ（不要）")
                    
                    except ImportError:
                        print("⚠️ 強化版SERP検索モジュールが見つかりません。標準版を使用します。")
                        
                        # フォールバック: 標準版SERP検索
                        price_keywords = ['価格', '値段', '費用', 'いくら', 'コスト', '料金']
                        latest_keywords = ['最新', '新しい', '最近', '今', '現在']
                        
                        needs_serp = any(keyword in message for keyword in price_keywords + latest_keywords)
                        
                        if needs_serp:
                            print("🌐 SERP検索実行（価格/最新情報）")
                            result = serp_system.search(message, ['repair_info', 'parts_price', 'general_info'])
                            duration = time.time() - serp_start_time
                            response_logger.log_performance("SERP検索", duration, True)
                            return result
                        else:
                            print("⚡ SERP検索スキップ（不要）")
            
            except Exception as e:
                duration = time.time() - serp_start_time
                error_info = error_handler.handle_serp_error(e, message)
                response_logger.log_performance("SERP検索", duration, False, {"error": str(e)})
                print(f"⚠️ SERP検索エラー: {e}")
            return {}
        
        def search_notion():
            """Notion検索（強化版・タイムアウト付き）"""
            notion_start_time = time.time()
            try:
                if NOTION_AVAILABLE and notion_client_instance:
                    # フェーズ2-4: 強化版Notion検索を使用
                    try:
                        from utils.notion_search_enhanced import NotionSearchEnhanced
                        
                        # 強化版Notion検索インスタンスを作成
                        enhanced_search = NotionSearchEnhanced(notion_client_instance.client)
                        
                        # カテゴリを取得
                        category = intent.get('category') if isinstance(intent, dict) else None
                        
                        # 検索対象のデータベース
                        databases = {
                            '修理ケースDB': os.getenv('NOTION_CASE_DB_ID', '').replace('-', ''),
                            '診断フローDB': os.getenv('NODE_DB_ID', '').replace('-', ''),
                            '部品・工具DB': os.getenv('ITEM_DB_ID', '').replace('-', '')
                        }
                        
                        # 空のデータベースIDを除外
                        databases = {k: v for k, v in databases.items() if v}
                        
                        if databases:
                            print(f"🔍 強化版Notion検索実行")
                            print(f"  データベース数: {len(databases)}")
                            
                            # 強化版Notion検索を実行
                            result_v2 = enhanced_search.search_notion_databases(
                                query=message,
                                databases=databases,
                                max_results_per_db=5,
                                min_relevance=0.6,
                                use_relations=True
                            )
                            
                            # 結果を旧形式に変換（後方互換性）
                            if result_v2:
                                duration = time.time() - notion_start_time
                                response_logger.log_performance("Notion検索(強化版)", duration, True, {
                                    "total_results": result_v2['metadata'].get('total_results', 0),
                                    "keywords": result_v2['metadata'].get('keywords', []),
                                    "databases": len(databases)
                                })
                                
                                print(f"✅ 強化版Notion検索完了: {result_v2['metadata']['total_results']}件")
                                
                                # 旧形式に変換
                                return {
                                    'repair_cases': result_v2.get('cases', [])[:3],
                                    'diagnostic_nodes': result_v2.get('nodes', [])[:3],
                                    'items': result_v2.get('items', [])[:3],
                                    'factories': result_v2.get('factories', [])[:3],
                                    'builders': result_v2.get('builders', [])[:3],
                                    'total_cases_found': len(result_v2.get('cases', [])),
                                    'total_nodes_found': len(result_v2.get('nodes', [])),
                                    'metadata': result_v2['metadata']
                                }
                    
                    except ImportError:
                        print("⚠️ 強化版Notion検索モジュールが見つかりません。標準版を使用します。")
                    
                    # フォールバック: 標準版Notion検索
                    result = search_notion_knowledge(message, include_cache=include_cache)
                    duration = time.time() - notion_start_time
                    response_logger.log_performance("Notion検索", duration, True)
                    return result
            except Exception as e:
                duration = time.time() - notion_start_time
                error_info = error_handler.handle_notion_error(e, "Notion検索")
                response_logger.log_performance("Notion検索", duration, False, {"error": str(e)})
                print(f"⚠️ Notion検索エラー: {e}")
            return {}
        
        # 並列実行（最大3秒でタイムアウト）
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_rag = executor.submit(search_rag)
            future_serp = executor.submit(search_serp) if include_serp else None
            future_notion = executor.submit(search_notion)
            
            try:
                # RAG検索（最優先、2秒でタイムアウト）
                rag_results = future_rag.result(timeout=2.0)
            except concurrent.futures.TimeoutError:
                print("⚠️ RAG検索タイムアウト（2秒）")
                rag_results = {}
            
            try:
                # SERP検索（3秒でタイムアウト）
                if future_serp:
                    serp_results = future_serp.result(timeout=3.0)
            except concurrent.futures.TimeoutError:
                print("⚠️ SERP検索タイムアウト（3秒）")
                serp_results = {}
            
            try:
                # Notion検索（2秒でタイムアウト）
                notion_results = future_notion.result(timeout=2.0)
            except concurrent.futures.TimeoutError:
                print("⚠️ Notion検索タイムアウト（2秒）")
                notion_results = {}
        
        search_time = time.time() - start_time
        print(f"⚡ 並列検索完了: {search_time:.2f}秒")
        
        # フェーズ2-4: 統合検索最適化（タイムアウト付き）
        integration_metadata = None
        ab_test_variant = None
        integration_timeout = 5  # 統合検索最適化のタイムアウト（秒）
        print("🔄 統合検索最適化を開始...")
        try:
            print("📦 utils.search_integrationモジュールをインポート中...")
            from utils.search_integration import search_integration
            print("✅ インポート成功")
            
            # タイムアウト付きで統合検索最適化を実行
            integration_start_time = time.time()
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    def run_integration():
                        # A/Bテストフレームワークをインポート（オプション）
                        ab_test_variant_local = None
                        try:
                            from utils.ab_test_framework import ab_test_framework
                            # ユーザーIDを生成（メッセージのハッシュから）
                            # 実際の実装では、session_idやuser_idを引数として渡すことを推奨
                            user_id = f"user_{hash(message) % 10000}"
                            
                            # バリアントを割り当て
                            ab_test_variant_local = ab_test_framework.assign_variant(user_id, message)
                            print(f"🧪 A/Bテストバリアント: {ab_test_variant_local}")
                        except ImportError:
                            print("⚠️ A/Bテストフレームワークが利用できません（オプション）")
                        except Exception as e:
                            print(f"⚠️ A/Bテスト初期化エラー: {e}")
                        
                        # 動的な重み付けを計算
                        print(f"📊 動的重み付けを計算中... (message='{message[:50]}...', intent={intent.get('intent')})")
                        dynamic_weights = search_integration.calculate_dynamic_weights(message, intent)
                        print(f"✅ 動的重み付け: {dynamic_weights}")
                        
                        # 結果をマージと重複排除（A/Bテストバリアントに応じて調整）
                        print("🔗 検索結果をマージ中...")
                        merge_start_time = time.time()
                        integrated_results = search_integration.merge_search_results(
                            rag_results=rag_results,
                            serp_results=serp_results,
                            notion_results=notion_results,
                            weights=dynamic_weights,
                            max_results=10
                        )
                        merge_time = time.time() - merge_start_time
                        print(f"✅ マージ完了: {len(integrated_results)}件 ({merge_time:.2f}秒)")
                        
                        return integrated_results, ab_test_variant_local, dynamic_weights, merge_time
                    
                    future = executor.submit(run_integration)
                    integrated_results, ab_test_variant, dynamic_weights, merge_time = future.result(timeout=integration_timeout)
                    
            except concurrent.futures.TimeoutError:
                integration_duration = time.time() - integration_start_time
                print(f"⚠️ 統合検索最適化タイムアウト: {integration_duration:.2f}秒（制限: {integration_timeout}秒）")
                # タイムアウト時は統合検索最適化をスキップして、通常の検索結果を使用
                integrated_results = []
                dynamic_weights = {'rag': 0.5, 'serp': 0.3, 'notion': 0.7}
                merge_time = 0
                ab_test_variant = None
            
            response_time = time.time() - integration_start_time
            
            # A/Bテストの追跡（統合検索最適化が成功した場合のみ）
            if ab_test_variant and integrated_results:
                try:
                    from utils.ab_test_framework import ab_test_framework
                    user_id = f"user_{hash(message) % 10000}"
                    ab_test_framework.track_query(
                        user_id=user_id,
                        query=message,
                        variant=ab_test_variant,
                        results_count=len(integrated_results),
                        response_time=response_time,
                        metadata={
                            'intent': intent.get('intent'),
                            'source_distribution': search_integration.get_source_distribution(integrated_results)
                        }
                    )
                except Exception as e:
                    print(f"⚠️ A/Bテスト追跡エラー: {e}")
            
            # ソース別の分布を取得（統合検索最適化が成功した場合のみ）
            if integrated_results:
                print("📈 ソース分布を計算中...")
                distribution = search_integration.get_source_distribution(integrated_results)
                print(f"✅ ソース分布: RAG={distribution['rag']}件, SERP={distribution['serp']}件, Notion={distribution['notion']}件")
            else:
                # タイムアウト時はデフォルトの分布を使用
                distribution = {'rag': 0, 'serp': 0, 'notion': 0}
            
            # 統合結果をメタデータに追加
            integration_metadata = {
                'dynamic_weights': dynamic_weights,
                'integrated_results_count': len(integrated_results),
                'source_distribution': distribution,
                'ab_test_variant': ab_test_variant,
                'response_time': response_time
            }
            print("✅ 統合検索最適化: 正常に動作")
        
        except ImportError as e:
            print(f"❌ 統合検索モジュールのインポートエラー: {e}")
            print(f"❌ インポートエラー詳細: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            integration_metadata = None
        except Exception as e:
            print(f"❌ 統合検索最適化エラー: {e}")
            print(f"❌ エラータイプ: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            integration_metadata = None
            # エラー時も統合検索最適化をスキップして続行
            integrated_results = []
            distribution = {'rag': 0, 'serp': 0, 'notion': 0}
        
        # ソース別引用情報をログに記録
        citation_log = log_source_citations(message, rag_results, serp_results, notion_results, intent)
        
        # AI回答生成
        ai_start_time = time.time()
        ai_response = generate_ai_response(message, rag_results, serp_results, intent, notion_results)
        ai_response_time = time.time() - ai_start_time
        
        # 修理店紹介の提案が必要か判定
        should_suggest_partner = should_suggest_partner_shop(message, intent, ai_response)
        
        # 応答品質をログに記録
        response_logger.log_response_quality(
            message=message,
            response=ai_response,
            intent=intent,
            sources={
                "rag_results": rag_results,
                "serp_results": serp_results,
                "notion_results": notion_results
            },
            session_id=intent.get("session_id"),
            response_time=search_time + ai_response_time
        )
        
        # AI生成のパフォーマンスをログに記録
        response_logger.log_performance("AI生成", ai_response_time, True)
        
        # 処理時間の詳細ログ
        total_time = time.time() - start_time
        print(f"📊 処理時間サマリー:")
        print(f"   - 並列検索: {search_time:.2f}秒")
        print(f"   - AI応答生成: {ai_response_time:.2f}秒")
        print(f"   - 合計: {total_time:.2f}秒")
        
        response_data = {
            "type": "chat",
            "response": ai_response,
            "rag_results": rag_results,
            "serp_results": serp_results,
            "notion_results": notion_results,
            "intent": intent,
            "citation_log": citation_log,
            "search_time": f"{search_time:.2f}s",
            "ai_response_time": f"{ai_response_time:.2f}s",
            "total_time": f"{total_time:.2f}s"
        }
        
        # 修理店紹介の提案を追加
        if should_suggest_partner:
            response_data["suggest_partner"] = True
            response_data["partner_suggestion"] = {
                "message": "修理店を紹介しますか？",
                "category": intent.get("category", ""),
                "symptom": message[:100]  # 症状の最初の100文字
            }
        
        # 統合検索のメタデータを追加
        print(f"🔍 integration_metadata の値: {integration_metadata}")
        print(f"🔍 integration_metadata の型: {type(integration_metadata)}")
        if integration_metadata:
            print("✅ integration_metadataをresponse_dataに追加")
            response_data['integration'] = integration_metadata
        else:
            print("⚠️ integration_metadataがNoneまたは空のため、追加されません")
        
        print(f"📦 最終的なresponse_dataのキー: {list(response_data.keys())}")
        return response_data
        
    except Exception as e:
        error_str = str(e)
        session_id = intent.get("session_id") if isinstance(intent, dict) else None
        response_logger.log_error("ChatMode", error_str, {"message": message}, session_id)
        return {"error": f"チャット処理エラー: {error_str}"}

# 診断データのキャッシュ（グローバル変数）
_diagnostic_data_cache = None
_diagnostic_data_cache_time = None
_CACHE_DURATION = 300  # 5分間キャッシュ

def load_notion_diagnostic_data(force_reload: bool = False):
    """Notionから診断データを読み込み（キャッシュ付き）"""
    global notion_client_instance, _diagnostic_data_cache, _diagnostic_data_cache_time
    
    import time
    
    # キャッシュチェック
    if not force_reload and _diagnostic_data_cache is not None and _diagnostic_data_cache_time is not None:
        cache_age = time.time() - _diagnostic_data_cache_time
        if cache_age < _CACHE_DURATION:
            print(f"✅ キャッシュから診断データを取得（有効期限: {int(_CACHE_DURATION - cache_age)}秒）")
            return _diagnostic_data_cache
    
    if not notion_client_instance:
        print("⚠️ Notionクライアントが初期化されていません")
        return None
    
    try:
        print("🔄 Notionから診断データを読み込み中...")
        diagnostic_data = notion_client_instance.load_diagnostic_data()
        if diagnostic_data:
            # キャッシュに保存
            _diagnostic_data_cache = diagnostic_data
            _diagnostic_data_cache_time = time.time()
            print(f"✅ 診断データ読み込み成功: {len(diagnostic_data.get('nodes', []))}件のノード（キャッシュに保存）")
        else:
            print("⚠️ 診断データが空です")
        return diagnostic_data
    except Exception as e:
        print(f"⚠️ Notion診断データ読み込みエラー: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_notion_repair_cases():
    """Notionから修理ケースデータを読み込み"""
    global notion_client_instance
    
    if not notion_client_instance:
        return []
    
    try:
        repair_cases = notion_client_instance.load_repair_cases()
        return repair_cases if repair_cases else []
    except Exception as e:
        print(f"⚠️ Notion修理ケース読み込みエラー: {e}")
        return []

def score_candidate(text: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
    """候補ノードのスコアリング"""
    keywords = candidate.get("keywords", [])
    weight = candidate.get("weight", 1.0)
    
    # キーワード一致によるスコア計算
    hits = [k for k in keywords if k.lower() in text.lower()]
    score = len(hits) * weight
    
    # 簡易ペア加点（名詞×症状ペア）
    noun_symptom_pairs = [
        ["水圧", "弱い"], ["炎", "弱い"], ["電圧", "低い"],
        ["音", "大きい"], ["温度", "高い"], ["振動", "激しい"],
        ["エンジン", "かからない"], ["バッテリー", "上がらない"],
        ["エアコン", "効かない"], ["トイレ", "詰まる"]
    ]
    
    for noun, symptom in noun_symptom_pairs:
        if noun in text and symptom in text:
            score += 0.3
    
    return {"score": score, "hits": hits}

def route_next_node(current_node_id: str, user_answer: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """ルーティングエンジン - 次のノードを決定"""
    try:
        nodes = context.get("nodes", [])
        current_node = None
        
        # 現在のノードを検索
        for node in nodes:
            if node.get("id") == current_node_id:
                current_node = node
                break
        
        if not current_node:
            return {
                "ask": "診断ノードが見つかりません。症状をもう少し詳しく教えてください。",
                "decision_detail": {"reason": "node_not_found"}
            }
        
        # routing_configを取得
        routing_config = current_node.get("routing_config", {})
        if not routing_config or "next_nodes_map" not in routing_config:
            return {
                "ask": "症状をもう少し詳しく教えてください。",
                "decision_detail": {"reason": "no_routing_config"}
            }
        
        text = user_answer.lower() if user_answer else ""
        next_nodes_map = routing_config["next_nodes_map"]
        threshold = routing_config.get("threshold", 1.5)
        
        # 安全ワード判定（最優先）
        safety_words = routing_config.get("safety_words", [])
        if safety_words:
            for safety_word in safety_words:
                if safety_word.lower() in text:
                    # 安全ノードを検索
                    safety_candidate = None
                    for candidate in next_nodes_map:
                        if candidate.get("safety", False):
                            safety_candidate = candidate
                            break
                    
                    if safety_candidate:
                        return {
                            "nextNodeId": safety_candidate["id"],
                            "decision_detail": {
                                "safety_triggered": True,
                                "matched_keywords": [safety_word],
                                "reason": "safety_word_detected"
                            }
                        }
        
        # スコアリング実行
        scored_candidates = []
        for candidate in next_nodes_map:
            result = score_candidate(text, candidate)
            scored_candidates.append({
                **candidate,
                "score": result["score"],
                "hits": result["hits"]
            })
        
        # スコア順にソート
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        if not scored_candidates:
            return {
                "ask": "症状をもう少し詳しく教えてください。",
                "decision_detail": {"reason": "no_candidates"}
            }
        
        best = scored_candidates[0]
        second = scored_candidates[1] if len(scored_candidates) > 1 else {"score": 0}
        
        # 閾値チェック
        if best["score"] >= threshold and (best["score"] - second["score"]) >= 0.2:
            return {
                "nextNodeId": best["id"],
                "decision_detail": {
                    "matched_keywords": best["hits"],
                    "score": best["score"],
                    "threshold": threshold,
                    "reason": "threshold_met"
                }
            }
        
        # 確認質問を生成
        best_label = best.get("label", "A")
        second_label = second.get("label", "B")
        ask = f"「{best_label}」と「{second_label}」のどちらが近いですか？"
        
        return {
            "ask": ask,
            "decision_detail": {
                "scores": scored_candidates[:3],
                "reason": "clarification_needed"
            }
        }
        
    except Exception as e:
        return {
            "ask": "診断中にエラーが発生しました。もう一度お試しください。",
            "decision_detail": {"reason": "error", "error": str(e)}
        }

def run_notion_diagnostic_flow(message: str, symptoms: List[str]) -> Dict[str, Any]:
    """Notion診断フローを実行"""
    try:
        # Notion診断データを取得
        diagnostic_data = load_notion_diagnostic_data()
        if not diagnostic_data:
            return {"error": "Notion診断データが利用できません"}
        
        # 開始ノードから診断フローを開始
        start_nodes = diagnostic_data.get("start_nodes", [])
        if not start_nodes:
            return {"error": "開始ノードが見つかりません"}
        
        # 症状に最も関連する開始ノードを選択
        best_start_node = None
        best_match_score = 0
        
        for node in start_nodes:
            node_symptoms = node.get("symptoms", [])
            if node_symptoms:
                # 症状の一致度を計算
                match_count = sum(1 for symptom in symptoms if any(symptom.lower() in node_symptom.lower() for node_symptom in node_symptoms))
                match_score = match_count / len(node_symptoms) if node_symptoms else 0
                
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_start_node = node
        
        if not best_start_node:
            best_start_node = start_nodes[0]  # デフォルトで最初のノード
        
        # 診断フローの実行
        current_node = best_start_node
        diagnostic_path = [current_node]
        
        # 関連する修理ケースを取得
        repair_cases = load_notion_repair_cases()
        related_cases = []
        
        if repair_cases and current_node.get("related_cases"):
            for related_case_id in current_node["related_cases"]:
                for case in repair_cases:
                    if case.get("id") == related_case_id:
                        related_cases.append(case)
                        break
        
        return {
            "type": "notion_diagnostic",
            "current_node": current_node,
            "diagnostic_path": diagnostic_path,
            "related_cases": related_cases,
            "confidence": best_match_score,
            "message": f"診断フローを開始しました: {current_node.get('title', 'Unknown')}",
            "routing_available": bool(current_node.get("routing_config"))
        }
        
    except Exception as e:
        return {"error": f"Notion診断フローエラー: {str(e)}"}

def process_diagnostic_mode(message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
    """診断モード処理"""
    try:
        # 症状の抽出
        symptoms = extract_symptoms(message)
        
        # Notion診断フローを試行
        notion_result = run_notion_diagnostic_flow(message, symptoms)
        
        # Notion診断が成功した場合はそれを使用
        if not notion_result.get("error"):
            return notion_result
        
        # Notion診断が失敗した場合は従来のAI診断を使用
        diagnostic_result = process_diagnostic(symptoms, message)
        
        return {
            "type": "ai_diagnostic",
            "symptoms": symptoms,
            "diagnosis": diagnostic_result,
            "intent": intent,
            "fallback": True
        }
        
    except Exception as e:
        return {"error": f"診断処理エラー: {str(e)}"}

def process_repair_search_mode(message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
    """修理検索モード処理"""
    try:
        # カテゴリ特定
        category = None
        if category_manager:
            category = category_manager.identify_category(message)
        
        # 修理情報の取得
        repair_info = {}
        if category:
            repair_info = {
                "category": category,
                "icon": category_manager.get_category_icon(category),
                "repair_costs": category_manager.get_repair_costs(category),
                "repair_steps": category_manager.get_repair_steps_from_json(category),
                "warnings": category_manager.get_warnings_from_json(category)
            }
        
        # RAG検索
        rag_results = {}
        if db:
            rag_results = enhanced_rag_retrieve(message, db, max_results=3)
        
        return {
            "type": "repair_search",
            "repair_info": repair_info,
            "rag_results": rag_results,
            "intent": intent
        }
        
    except Exception as e:
        return {"error": f"修理検索エラー: {str(e)}"}

def process_cost_estimate_mode(message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
    """費用見積もりモード処理"""
    try:
        # カテゴリ特定
        category = None
        if category_manager:
            category = category_manager.identify_category(message)
        
        # 費用情報の取得
        cost_info = {}
        if category:
            cost_info = category_manager.get_repair_costs(category)
        
        # SERP検索（価格情報）
        price_results = {}
        if serp_system:
            price_results = serp_system.get_parts_price_info(message)
        
        return {
            "type": "cost_estimate",
            "category": category,
            "cost_info": cost_info,
            "price_results": price_results,
            "intent": intent
        }
        
    except Exception as e:
        return {"error": f"費用見積もりエラー: {str(e)}"}

def generate_safety_warning(safety_warnings: List[str]) -> str:
    """セーフティ警告文を生成"""
    if not safety_warnings:
        return ""
    
    warning_text = "🚨 **緊急警告**\n\n"
    warning_text += "以下の危険な症状が検出されました。直ちに安全対策を講じてください:\n\n"
    
    for warning in safety_warnings:
        category, keyword = warning.split(": ", 1)
        if category == "ガス":
            warning_text += f"⚠️ **ガス関連**: {keyword} - 直ちに換気を行い、火気を避けてください\n"
        elif category == "高電圧":
            warning_text += f"⚠️ **電気関連**: {keyword} - 電源を切り、感電を避けてください\n"
        elif category == "火災":
            warning_text += f"⚠️ **火災関連**: {keyword} - 直ちに消火活動を行い、安全な場所に避難してください\n"
        elif category == "一酸化炭素":
            warning_text += f"⚠️ **一酸化炭素**: {keyword} - 直ちに換気を行い、新鮮な空気を確保してください\n"
    
    warning_text += "\n**緊急時は消防署（119）またはガス会社に連絡してください。**\n\n"
    warning_text += "---\n\n"
    
    return warning_text

def generate_ai_response(message: str, rag_results: Dict, serp_results: Dict, intent: Dict, notion_results: Dict = None) -> str:
    """AI回答生成（セーフティ警告・重みづけ対応・タイムアウト対応）"""
    import time
    import concurrent.futures
    max_retries = 3
    retry_delay = 2  # 秒
    ai_timeout = 30  # AI応答生成のタイムアウト（秒）
    
    for attempt in range(max_retries):
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage
            
            # APIキーの確認
            api_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
            if not api_key:
                return """⚠️ **OpenAI APIキーが設定されていません**

**対処方法：**
1. `.env`ファイルに`OPENAI_API_KEY`を設定してください
2. Railwayの環境変数に`OPENAI_API_KEY`を設定してください
3. サーバーを再起動してください

詳細は管理者にお問い合わせください。"""
            
            llm = ChatOpenAI(
                api_key=api_key, 
                model_name="gpt-4o-mini",
                temperature=0,  # 決定的な出力で形式を固定
                timeout=ai_timeout  # タイムアウトを設定（秒）
            )
            
            # セーフティ警告の生成
            safety_warning = ""
            if notion_results and notion_results.get("safety_warnings"):
                safety_warning = generate_safety_warning(notion_results["safety_warnings"])
            
            # コンテキストの構築
            context = build_context(rag_results, serp_results, intent)
            
            # Notion検索結果の処理（重みづけとスニペット優先）
            notion_context = ""
            if notion_results and not notion_results.get("error"):
                # スニペット要約を先頭に配置
                notion_summary = ""
                if notion_results.get("repair_cases") or notion_results.get("diagnostic_nodes"):
                    notion_summary = "📋 **Notionデータベースからの関連情報:**\n\n"
                    
                    # 修理ケースのスニペット要約
                    if notion_results.get("repair_cases"):
                        for i, case in enumerate(notion_results["repair_cases"], 1):
                            notion_summary += f"🔧 **{case['title']}** ({case['category']})\n"
                            if case.get("snippets", {}).get("repair_steps"):
                                notion_summary += f"   修理手順: {case['snippets']['repair_steps']}\n"
                            elif case.get("snippets", {}).get("solution"):
                                notion_summary += f"   解決方法: {case['snippets']['solution']}\n"
                            notion_summary += f"   マッチキーワード: {', '.join(case.get('matched_keywords', [])[:3])}\n\n"
                    
                    # 診断ノードのスニペット要約
                    if notion_results.get("diagnostic_nodes"):
                        for i, node in enumerate(notion_results["diagnostic_nodes"], 1):
                            notion_summary += f"🔍 **{node['title']}** ({node['category']})\n"
                            if node.get("snippets", {}).get("diagnosis_result"):
                                notion_summary += f"   診断結果: {node['snippets']['diagnosis_result']}\n"
                            elif node.get("snippets", {}).get("question"):
                                notion_summary += f"   質問: {node['snippets']['question']}\n"
                            notion_summary += f"   マッチキーワード: {', '.join(node.get('matched_keywords', [])[:3])}\n\n"
                
                notion_context = notion_summary
            
            # 重みづけ情報をプロンプトに追加
            weight_info = f"""
            情報ソースの重みづけ:
            - Notionデータベース: {SOURCE_WEIGHTS['notion']} (最優先)
            - RAG検索: {SOURCE_WEIGHTS['rag']} (補完)
            - SERP検索: {SOURCE_WEIGHTS['serp']} (参考)
            """
            
            # フェーズ2: 6要素形式のプロンプトテンプレート（Few-shot Example版）
            # システムメッセージで形式を厳格に指定 + 具体例を提示
            system_message = SystemMessage(content="""あなたはキャンピングカー修理専門AIです。

回答は必ず以下の6要素形式で構成してください。他の形式は一切使用しないでください。

【正しい形式の例】

質問: バッテリーが上がりました

【① 共感リアクション】
お困りの状況、よく分かります。バッテリー上がりは突然起こると本当に困りますよね。

【② 要点】
この症状は、バッテリーの寿命またはオルタネーター故障が原因の可能性が高いです。キャンピングカーのサブバッテリーは特に放電しやすいため、定期的な充電が必要です。

【③ 手順】
1. まず、バッテリー電圧をテスターで確認してください（正常値: 12.5V以上）
2. 次に、ブースターケーブルでジャンプスタートを試してください
3. エンジンがかかったら30分以上走行して充電してください
4. それでも充電されない場合は、オルタネーターの点検が必要です

【④ 次アクション】
- バッテリーが3年以上使用している場合は交換を推奨
- 専門業者に診断を依頼する
- 最寄りの工場を検索する

【⑤ 工賃目安】
- 診断料: 2,000円〜3,000円
- バッテリー交換: 15,000円〜35,000円（バッテリー代込み）
- オルタネーター交換: 50,000円〜80,000円

【⑥ 作業時間】
- 診断: 30分
- バッテリー交換: 1時間
- オルタネーター交換: 2〜3時間

【絶対に使用禁止の形式】
❌ ### 1. 【状況確認】
❌ ### 2. 【診断結果】
❌ ### 3. 【修理手順】

これらの番号付き形式は使用しないでください。必ず【①】【②】【③】【④】【⑤】【⑥】のマーカーを使用してください。""")
            
            # ユーザーメッセージ（簡潔版）
            user_prompt = f"""ユーザーの質問: {message}

カテゴリ: {intent.get('category', '不明')}
緊急度: {intent.get('urgency', '不明')}

{notion_context if notion_context else ''}

上記の6要素形式で専門的な修理アドバイスを生成してください。"""
            
            user_message = HumanMessage(content=user_prompt)
            
            # システムメッセージとユーザーメッセージを使用
            messages = [system_message, user_message]
            
            # タイムアウト付きでAI応答を生成
            ai_start_time = time.time()
            try:
                # ThreadPoolExecutorでタイムアウトを制御
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(llm.invoke, messages)
                    response = future.result(timeout=ai_timeout)
                
                ai_duration = time.time() - ai_start_time
                print(f"✅ AI応答生成完了: {ai_duration:.2f}秒")
                
                # セーフティ警告を回答の先頭に挿入
                if safety_warning:
                    return safety_warning + response.content
                else:
                    return response.content
                    
            except concurrent.futures.TimeoutError:
                ai_duration = time.time() - ai_start_time
                print(f"⚠️ AI応答生成タイムアウト: {ai_duration:.2f}秒（制限: {ai_timeout}秒）")
                raise TimeoutError(f"AI応答生成がタイムアウトしました（{ai_timeout}秒以内に完了しませんでした）")
            
        except TimeoutError as e:
            # タイムアウトエラーの場合はリトライしない
            print(f"❌ AI回答生成タイムアウト (試行 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                print(f"⚠️ {wait_time}秒後にリトライします (試行 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                return "⚠️ AI回答生成がタイムアウトしました。時間をおいて再度お試しください。"
        except Exception as e:
            # フェーズ2-1: 強化されたエラーハンドリングを使用
            error_message, should_retry = error_handler.handle_openai_error(e, attempt, max_retries)
            
            print(f"❌ AI回答生成エラー (試行 {attempt + 1}/{max_retries}): {str(e)}")
            import traceback
            traceback.print_exc()
            
            # リトライ可能な場合はリトライ
            if should_retry and attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                print(f"⚠️ {wait_time}秒後にリトライします (試行 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                return error_message
    
    return "⚠️ AI回答生成に失敗しました。時間をおいて再度お試しください。"

def should_suggest_partner_shop(message: str, intent: Dict[str, Any], ai_response: str) -> bool:
    """修理店紹介の提案が必要かどうかを判定"""
    try:
        # 修理関連のキーワードをチェック
        repair_keywords = [
            "修理", "故障", "不調", "異常", "問題", "トラブル", "症状",
            "直したい", "直して", "交換", "点検", "メンテナンス",
            "エアコン", "バッテリー", "トイレ", "水回り", "ガス", "電気",
            "エンジン", "エンジンがかからない", "始動しない"
        ]
        
        # 専門業者への相談を推奨するキーワード
        professional_keywords = [
            "専門", "業者", "工場", "修理店", "ショップ", "プロ",
            "相談", "見積もり", "診断", "点検"
        ]
        
        # メッセージに修理関連のキーワードが含まれているか
        message_lower = message.lower()
        has_repair_keyword = any(keyword in message_lower for keyword in repair_keywords)
        
        # 意図に修理カテゴリが含まれているか
        category = intent.get("category", "").lower() if isinstance(intent, dict) else ""
        has_repair_category = category and category not in ["不明", "その他", "general"]
        
        # AI応答に専門業者への相談が推奨されているか
        response_lower = ai_response.lower()
        suggests_professional = any(keyword in response_lower for keyword in professional_keywords)
        
        # 提案条件：
        # 1. 修理関連のキーワードまたはカテゴリがある
        # 2. AI応答が専門業者への相談を推奨している、または緊急度が高い
        urgency = intent.get("urgency", "").lower() if isinstance(intent, dict) else ""
        is_urgent = urgency in ["high", "緊急", "高"]
        
        should_suggest = (has_repair_keyword or has_repair_category) and (suggests_professional or is_urgent)
        
        if should_suggest:
            print(f"✅ 修理店紹介の提案を追加: カテゴリ={category}, 緊急度={urgency}")
        
        return should_suggest
        
    except Exception as e:
        print(f"⚠️ 修理店紹介提案判定エラー: {e}")
        # エラー時は安全のため提案しない
        return False

def build_context(rag_results: Dict, serp_results: Dict, intent: Dict) -> str:
    """コンテキスト構築"""
    context_parts = []
    
    # RAG結果の追加
    if rag_results.get("manual_content"):
        context_parts.append("📚 マニュアル情報:")
        context_parts.append(rag_results["manual_content"][:500] + "...")
    
    if rag_results.get("text_file_content"):
        context_parts.append("📄 テキストファイル情報:")
        context_parts.append(rag_results["text_file_content"][:500] + "...")
    
    # SERP結果の追加
    if serp_results.get("results"):
        context_parts.append("🌐 リアルタイム情報:")
        for result in serp_results["results"][:3]:
            context_parts.append(f"- {result.get('title', 'N/A')}: {result.get('snippet', 'N/A')[:200]}...")
    
    return "\n".join(context_parts)

def extract_symptoms(message: str) -> List[str]:
    """症状の抽出"""
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4o-mini")
        
        prompt = f"""
        キャンピングカーの症状を抽出してください。
        
        メッセージ: {message}
        
        以下の形式でJSONを返してください:
        {{
            "symptoms": ["症状1", "症状2", "症状3"]
        }}
        """
        
        response = llm.invoke(prompt)
        result = json.loads(response.content)
        return result.get("symptoms", [])
        
    except Exception as e:
        return [message]

def process_diagnostic(symptoms: List[str], additional_info: str) -> Dict[str, Any]:
    """診断処理"""
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4o-mini")
        
        prompt = f"""
        キャンピングカーの症状から原因を診断してください。
        
        症状: {', '.join(symptoms)}
        追加情報: {additional_info}
        
        以下の形式でJSONを返してください:
        {{
            "possible_causes": ["原因1", "原因2", "原因3"],
            "confidence": 0.0-1.0,
            "recommended_actions": ["対処法1", "対処法2"],
            "urgency": "low|medium|high"
        }}
        """
        
        response = llm.invoke(prompt)
        return json.loads(response.content)
        
    except Exception as e:
        return {
            "possible_causes": ["診断エラー"],
            "confidence": 0.0,
            "recommended_actions": ["専門家に相談してください"],
            "urgency": "high"
        }

def generate_repair_guide(problem: str, category: str) -> Dict[str, Any]:
    """修理ガイド生成"""
    try:
        guide = {
            "problem": problem,
            "category": category,
            "steps": [],
            "tools_needed": [],
            "parts_needed": [],
            "warnings": [],
            "estimated_time": "",
            "difficulty": ""
        }
        
        if category_manager and category:
            guide["repair_costs"] = category_manager.get_repair_costs(category)
            guide["repair_steps"] = category_manager.get_repair_steps_from_json(category)
            guide["warnings"] = category_manager.get_warnings_from_json(category)
        
        return guide
        
    except Exception as e:
        return {"error": f"修理ガイド生成エラー: {str(e)}"}

def get_cache_key(cache_type: str, **kwargs) -> str:
    """キャッシュキーを生成"""
    key_parts = [cache_type]
    for k, v in sorted(kwargs.items()):
        if v:
            key_parts.append(f"{k}:{v}")
    return ":".join(key_parts)

def get_from_cache(key: str) -> Optional[Any]:
    """キャッシュからデータを取得"""
    global cache
    
    if key not in cache:
        return None
    
    entry = cache[key]
    if datetime.now().timestamp() > entry["expires_at"]:
        del cache[key]
        return None
    
    return entry["data"]

def set_cache(key: str, data: Any, ttl: int = CACHE_EXPIRY_SECONDS):
    """キャッシュにデータを保存"""
    global cache
    
    cache[key] = {
        "data": data,
        "expires_at": datetime.now().timestamp() + ttl
    }

def load_notion_diagnostic_data_cached(category: str = "", updated_since: str = ""):
    """キャッシュ付き診断データ取得"""
    cache_key = get_cache_key("DIAG", category=category, updated_since=updated_since)
    
    # キャッシュから取得を試行
    cached_data = get_from_cache(cache_key)
    if cached_data is not None:
        print(f"📦 キャッシュから診断データを取得: {cache_key}")
        return cached_data
    
    # キャッシュにない場合は取得して保存
    try:
        data = load_notion_diagnostic_data()
        if data:
            set_cache(cache_key, data)
            print(f"💾 診断データをキャッシュに保存: {cache_key}")
        return data
    except Exception as e:
        print(f"⚠️ 診断データ取得エラー: {e}")
        return None

def load_notion_repair_cases_cached(category: str = ""):
    """キャッシュ付き修理ケース取得"""
    cache_key = get_cache_key("CASE", category=category)
    
    # キャッシュから取得を試行
    cached_data = get_from_cache(cache_key)
    if cached_data is not None:
        print(f"📦 キャッシュから修理ケースを取得: {cache_key}")
        return cached_data
    
    # キャッシュにない場合は取得して保存
    try:
        data = load_notion_repair_cases()
        if data:
            set_cache(cache_key, data)
            print(f"💾 修理ケースをキャッシュに保存: {cache_key}")
        return data
    except Exception as e:
        print(f"⚠️ 修理ケース取得エラー: {e}")
        return []

def log_routing_decision(decision_data: Dict[str, Any]):
    """ルーティング決定のログ記録"""
    try:
        import uuid
        run_id = str(uuid.uuid4())[:8]
        
        log_entry = {
            "run_id": run_id,
            "timestamp": decision_data.get("timestamp"),
            "current_node_id": decision_data.get("current_node_id"),
            "user_answer": decision_data.get("user_answer"),
            "result": decision_data.get("result")
        }
        
        # ログファイルに記録（簡易実装）
        log_file = "routing_logs.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        print(f"📝 ルーティングログ記録: {run_id}")
        
    except Exception as e:
        print(f"⚠️ ログ記録エラー: {e}")

# === 診断フロー専用API エンドポイント ===

# 診断セッション管理用のグローバル変数（本番環境ではRedis等を使用）
DIAGNOSTIC_SESSIONS = {}
DIAGNOSTIC_NODE_CACHE = {}
CACHE_LAST_FETCHED = 0

@app.route("/chat/diagnose/start", methods=["POST"])
def diagnose_start():
    """診断セッション開始API"""
    try:
        # リクエストデータの取得と検証
        try:
            data = request.get_json()
            if not data:
                data = {}
        except Exception as e:
            print(f"❌ リクエストデータ取得エラー: {e}")
            return jsonify({"error": "無効なリクエストデータ", "status": "error"}), 400
        
        category = data.get("category", "general")
        
        print(f"🔍 診断セッション開始: category={category}")
        
        # Notion診断データを取得（ルーティング機能付き）
        print("📊 診断データ取得開始（ルーティング機能付き）...")
        diagnostic_data = notion_client_instance.get_diagnostic_data_with_routing(category)
        
        print(f"📊 診断データ結果: {type(diagnostic_data)}, 内容: {diagnostic_data is not None}")
        
        if not diagnostic_data:
            print("❌ 診断データが利用できません - フォールバック診断を試行")
            import uuid
            # フォールバック診断セッションを保存
            fallback_session_id = str(uuid.uuid4())
            DIAGNOSTIC_SESSIONS[fallback_session_id] = {
                "current_node": "fallback_start",
                "history": ["fallback_start"],
                "answers": [],
                "created_at": datetime.now().isoformat(),
                "category": category,
                "fallback": True
            }
            print(f"✅ フォールバック診断セッション作成: {fallback_session_id}")
            
            response_data = {
                "session_id": fallback_session_id,
                "node_id": "fallback_start",
                "question": "症状を詳しく教えてください（例：バッテリーが上がらない、エアコンが効かない）",
                "options": [
                    {"text": "バッテリー関連の症状", "value": "battery"},
                    {"text": "エアコン・冷暖房の症状", "value": "aircon"},
                    {"text": "トイレ・水回りの症状", "value": "toilet"},
                    {"text": "その他の症状", "value": "other"}
                ],
                "safety": {"urgent": False, "notes": ""},
                "fallback": True,
                "status": "success"
            }
            
            print(f"📤 フォールバック診断レスポンス送信: {response_data}")
            
            # レスポンスをJSON形式で返す
            try:
                response = jsonify(response_data)
                response.headers['Content-Type'] = 'application/json'
                return response
            except Exception as json_error:
                print(f"❌ JSON生成エラー: {json_error}")
                return jsonify({"error": "JSONレスポンス生成エラー"}), 500
        
        # 新しいルーティングシステムを使用
        print("🔄 Notionルーティングシステムを開始...")
        user_input = data.get("user_input", "")
        
        # ルーティング実行
        routing_result = notion_client_instance.run_diagnostic_routing(user_input, diagnostic_data)
        
        if routing_result.get("end", False):
            # 診断完了
            print("✅ Notionルーティング診断完了")
            return jsonify({
                "is_terminated": True,
                "confidence": 0.9,
                "summary": {
                    "title": "Notion診断結果",
                    "details": routing_result.get("text", "診断完了"),
                    "next_steps": "詳細な診断が完了しました"
                },
                "related_cases": [],
                "required_parts": [],
                "notion_routing": True
            })
        else:
            # 継続診断（質問がある場合）
            print("🔄 Notionルーティング継続診断")
            # 継続診断の実装は後で追加
            pass
        
        # 開始ノードを検索
        start_node = None
        for node in diagnostic_data.get("nodes", []):
            if node.get("is_start", False):
                if category == "general" or node.get("category", "").lower() == category.lower():
                    start_node = node
                    break
        
        if not start_node:
            return jsonify({"error": "開始ノードが見つかりません"}), 404
        
        # セッションIDを生成
        import uuid
        session_id = str(uuid.uuid4())
        
        # セッション情報を保存
        DIAGNOSTIC_SESSIONS[session_id] = {
            "current_node": start_node["id"],
            "history": [start_node["id"]],
            "answers": [],
            "created_at": datetime.now().isoformat(),
            "category": category
        }
        
        print(f"✅ 診断セッション開始: session_id={session_id}, node_id={start_node['id']}")
        
        return jsonify({
            "session_id": session_id,
            "node_id": start_node["id"],
            "question": start_node.get("question", "症状を詳しく教えてください"),
            "options": get_diagnostic_options(start_node),
            "safety": {
                "urgent": start_node.get("emergency", False),
                "notes": start_node.get("warnings", "")
            }
        })
        
    except Exception as e:
        print(f"❌ 診断セッション開始エラー: {e}")
        import traceback
        traceback.print_exc()
        
        # エラーレスポンスをJSON形式で返す
        error_response = {
            "error": f"診断セッション開始エラー: {str(e)}",
            "status": "error",
            "fallback_available": True
        }
        response = jsonify(error_response)
        response.headers['Content-Type'] = 'application/json'
        return response, 500

@app.route("/chat/diagnose/answer", methods=["POST"])
def diagnose_answer():
    """診断回答処理API"""
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        node_id = data.get("node_id")
        answer_text = data.get("answer_text", "")
        
        if not session_id or not node_id:
            return jsonify({"error": "session_idとnode_idが必要です"}), 400
        
        print(f"🔍 診断回答処理: session_id={session_id}, node_id={node_id}, answer={answer_text}")
        
        # フォールバック診断の処理
        if node_id == "fallback_start":
            return handle_fallback_diagnosis(answer_text, session_id)
        
        # セッションの存在確認
        if session_id not in DIAGNOSTIC_SESSIONS:
            return jsonify({"error": "セッションが見つかりません"}), 404
        
        session = DIAGNOSTIC_SESSIONS[session_id]
        
        # 診断データを取得
        diagnostic_data = load_notion_diagnostic_data_cached()
        if not diagnostic_data:
            return jsonify({"error": "診断データが利用できません"}), 500
        
        # 現在のノードを取得
        current_node = None
        for node in diagnostic_data.get("nodes", []):
            if node["id"] == node_id:
                current_node = node
                break
        
        if not current_node:
            return jsonify({"error": "診断ノードが見つかりません"}), 404
        
        # 回答をセッションに記録
        session["answers"].append({
            "node_id": node_id,
            "answer": answer_text,
            "timestamp": datetime.now().isoformat()
        })
        
        # 次のノードを決定
        next_node_id = determine_next_node(current_node, answer_text, diagnostic_data)
        
        if next_node_id:
            # 次のノードを取得
            next_node = None
            for node in diagnostic_data.get("nodes", []):
                if node["id"] == next_node_id:
                    next_node = node
                    break
            
            if next_node:
                # セッションを更新
                session["current_node"] = next_node_id
                session["history"].append(next_node_id)
                
                return jsonify({
                    "node_id": next_node_id,
                    "question": next_node.get("question", "症状を詳しく教えてください"),
                    "options": get_diagnostic_options(next_node),
                    "safety": {
                        "urgent": next_node.get("emergency", False),
                        "notes": next_node.get("warnings", "")
                    },
                    "is_terminated": False
                })
        
        # 診断終了処理
        return generate_diagnostic_result(session, current_node, diagnostic_data)
        
    except Exception as e:
        print(f"❌ 診断回答処理エラー: {e}")
        import traceback
        traceback.print_exc()
        
        # エラーレスポンスをJSON形式で返す
        error_response = {
            "error": f"診断回答処理エラー: {str(e)}",
            "status": "error",
            "is_terminated": True
        }
        response = jsonify(error_response)
        response.headers['Content-Type'] = 'application/json'
        return response, 500

def get_diagnostic_options(node):
    """診断ノードから選択肢を取得"""
    options = []
    
    # routing_configから選択肢を取得
    routing_config = node.get("routing_config")
    if routing_config and isinstance(routing_config, dict):
        next_nodes_map = routing_config.get("next_nodes_map", [])
        for option in next_nodes_map:
            options.append({
                "text": option.get("label", "選択肢"),
                "value": option.get("id", "")
            })
    
    # 次のノードから選択肢を取得（フォールバック）
    if not options:
        next_nodes = node.get("next_nodes", [])
        for next_node_id in next_nodes:
            options.append({
                "text": f"選択肢 {len(options) + 1}",
                "value": next_node_id
            })
    
    return options

def determine_next_node(current_node, answer_text, diagnostic_data):
    """次のノードを決定するルーティングエンジン"""
    try:
        # routing_configを優先
        routing_config = current_node.get("routing_config")
        if routing_config and isinstance(routing_config, dict):
            return route_by_config(answer_text, routing_config, diagnostic_data)
        
        # フォールバック: 次のノードの最初を選択
        next_nodes = current_node.get("next_nodes", [])
        if next_nodes:
            return next_nodes[0]
        
        return None
        
    except Exception as e:
        print(f"⚠️ ルーティングエラー: {e}")
        return None

def route_by_config(answer_text, config, diagnostic_data):
    """routing_configに基づくルーティング"""
    try:
        next_nodes_map = config.get("next_nodes_map", [])
        threshold = config.get("threshold", 1.0)
        
        # キーワードマッチングでスコアリング
        scored_options = []
        for option in next_nodes_map:
            keywords = option.get("keywords", [])
            weight = option.get("weight", 1.0)
            
            score = score_keywords(answer_text, keywords) * weight
            scored_options.append({
                "id": option.get("id"),
                "score": score,
                "fallback": option.get("fallback", False)
            })
        
        # スコア順にソート
        scored_options.sort(key=lambda x: x["score"], reverse=True)
        
        # 閾値を超えた最初のオプションを選択
        if scored_options and scored_options[0]["score"] >= threshold:
            return scored_options[0]["id"]
        
        # フォールバックオプションを検索
        fallback_option = next((opt for opt in scored_options if opt["fallback"]), None)
        if fallback_option:
            return fallback_option["id"]
        
        return None
        
    except Exception as e:
        print(f"⚠️ ルーティング設定エラー: {e}")
        return None

def score_keywords(text, keywords):
    """キーワードマッチングによるスコアリング"""
    if not keywords:
        return 0.0
    
    text_lower = text.lower()
    hits = sum(1 for keyword in keywords if keyword.lower() in text_lower)
    return hits / len(keywords)

def generate_diagnostic_result(session, current_node, diagnostic_data):
    """診断結果を生成"""
    try:
        # 診断結果の基本情報
        result = {
            "is_terminated": True,
            "confidence": 0.8,  # 簡易実装
            "summary": {
                "title": current_node.get("diagnosis_result", "診断結果"),
                "details": current_node.get("diagnosis_result", ""),
                "next_steps": "専門業者への相談をお勧めします"
            },
            "related_cases": [],
            "required_parts": []
        }
        
        # 関連ケースを取得
        related_cases = get_related_cases(current_node, diagnostic_data)
        result["related_cases"] = related_cases
        
        # 必要な部品を取得
        required_parts = get_required_parts(current_node, diagnostic_data)
        result["required_parts"] = required_parts
        
        print(f"✅ 診断結果生成完了: {len(related_cases)}件のケース, {len(required_parts)}件の部品")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ 診断結果生成エラー: {e}")
        return jsonify({"error": f"診断結果生成エラー: {str(e)}"}), 500

def get_related_cases(node, diagnostic_data):
    """関連する修理ケースを取得"""
    try:
        related_cases = []
        
        # ノードに関連付けられたケースを取得
        case_relations = node.get("related_cases", [])
        for case_id in case_relations:
            # 実際の実装では、Notionデータベースからケースを取得
            related_cases.append({
                "case_id": case_id,
                "title": f"修理ケース {case_id}",
                "description": "詳細な修理手順が含まれています",
                "url": f"https://notion.so/{case_id}"
            })
        
        return related_cases
        
    except Exception as e:
        print(f"⚠️ 関連ケース取得エラー: {e}")
        return []

def get_required_parts(node, diagnostic_data):
    """必要な部品・工具を取得"""
    try:
        required_parts = []
        
        # ノードに関連付けられた部品を取得
        item_relations = node.get("related_items", [])
        for item_id in item_relations:
            # 実際の実装では、Notionデータベースから部品情報を取得
            required_parts.append({
                "item_id": item_id,
                "name": f"部品 {item_id}",
                "description": "修理に必要な部品です",
                "price": "¥3,000-5,000"
            })
        
        return required_parts
        
    except Exception as e:
        print(f"⚠️ 必要部品取得エラー: {e}")
        return []

def handle_fallback_diagnosis(answer_text, session_id):
    """フォールバック診断の処理"""
    try:
        import uuid
        
        # 簡単なキーワードベースの診断
        answer_lower = answer_text.lower()
        
        if "バッテリー" in answer_lower or "battery" in answer_lower:
            category = "バッテリー"
            diagnosis = "バッテリー関連の症状が検出されました。"
            solutions = [
                "バッテリー端子の清掃",
                "電圧の確認",
                "充電システムの点検"
            ]
        elif "エアコン" in answer_lower or "aircon" in answer_lower:
            category = "エアコン"
            diagnosis = "エアコン関連の症状が検出されました。"
            solutions = [
                "フィルターの清掃",
                "冷媒ガスの確認",
                "室外機の点検"
            ]
        elif "トイレ" in answer_lower or "toilet" in answer_lower:
            category = "トイレ"
            diagnosis = "トイレ関連の症状が検出されました。"
            solutions = [
                "排水ポンプの確認",
                "配管の点検",
                "水タンクの清掃"
            ]
        else:
            category = "その他"
            diagnosis = "一般的な症状が検出されました。"
            solutions = [
                "基本点検の実施",
                "専門業者への相談",
                "マニュアルの確認"
            ]
        
        # 診断結果を返す
        result = {
            "is_terminated": True,
            "confidence": 0.7,
            "summary": {
                "title": f"{category}の診断結果",
                "details": diagnosis,
                "next_steps": "詳細な診断には専門業者への相談をお勧めします"
            },
            "related_cases": [
                {
                    "case_id": f"fallback_{category}",
                    "title": f"{category}の一般的な対処法",
                    "description": "基本的な修理手順と注意事項",
                    "url": None
                }
            ],
            "required_parts": [
                {
                    "item_id": f"part_{category}",
                    "name": f"{category}関連部品",
                    "description": "修理に必要な基本部品",
                    "price": "¥5,000-10,000"
                }
            ],
            "fallback": True,
            "solutions": solutions
        }
        
        # レスポンスをJSON形式で返す
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    except Exception as e:
        print(f"❌ フォールバック診断エラー: {e}")
        import traceback
        traceback.print_exc()
        
        # エラーレスポンスをJSON形式で返す
        error_response = {
            "error": f"フォールバック診断エラー: {str(e)}",
            "status": "error",
            "is_terminated": True
        }
        response = jsonify(error_response)
        response.headers['Content-Type'] = 'application/json'
        return response, 500

# === フェーズ1: Factory & Builder API エンドポイント ===

@app.route("/api/v1/factories", methods=["GET"])
def get_factories():
    """工場一覧取得"""
    try:
        if not factory_manager:
            return jsonify({"error": "Factory Managerが利用できません"}), 503
        
        # クエリパラメータ取得
        status = request.args.get("status")
        prefecture = request.args.get("prefecture")
        specialty = request.args.get("specialty")
        limit = int(request.args.get("limit", 100))
        
        factories = factory_manager.list_factories(
            status=status,
            prefecture=prefecture,
            specialty=specialty,
            limit=limit
        )
        
        return jsonify({
            "factories": factories,
            "count": len(factories)
        })
    except Exception as e:
        print(f"❌ 工場一覧取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/factories", methods=["POST"])
def create_factory():
    """工場登録"""
    try:
        if not factory_manager:
            return jsonify({"error": "Factory Managerが利用できません"}), 503
        
        data = request.get_json()
        
        # 必須フィールドチェック
        required_fields = ["name", "prefecture", "address", "phone", "email", "specialties", "business_hours", "service_areas"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field}は必須です"}), 400
        
        factory = factory_manager.create_factory(
            name=data["name"],
            prefecture=data["prefecture"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            specialties=data["specialties"],
            business_hours=data["business_hours"],
            service_areas=data["service_areas"],
            status=data.get("status", "アクティブ"),
            total_cases=data.get("total_cases", 0),
            completed_cases=data.get("completed_cases", 0),
            avg_response_time=data.get("avg_response_time", 0),
            rating=data.get("rating", 0),
            notes=data.get("notes")
        )
        
        return jsonify(factory), 201
    except Exception as e:
        print(f"❌ 工場登録エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/factories/<factory_id>", methods=["GET"])
def get_factory_detail(factory_id):
    """工場詳細取得"""
    try:
        if not factory_manager:
            return jsonify({"error": "Factory Managerが利用できません"}), 503
        
        factory = factory_manager.get_factory(factory_id)
        if not factory:
            return jsonify({"error": "工場が見つかりません"}), 404
        
        return jsonify(factory)
    except Exception as e:
        print(f"❌ 工場取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/factories/<factory_id>", methods=["PATCH"])
def update_factory_detail(factory_id):
    """工場更新"""
    try:
        if not factory_manager:
            return jsonify({"error": "Factory Managerが利用できません"}), 503
        
        data = request.get_json()
        factory = factory_manager.update_factory(factory_id, **data)
        
        if not factory:
            return jsonify({"error": "工場が見つかりません"}), 404
        
        return jsonify(factory)
    except Exception as e:
        print(f"❌ 工場更新エラー: {e}")
        return jsonify({"error": str(e)}), 500

# ===== フェーズ2-3: 工場教育AIモード =====

@app.route("/api/factory/manual/search", methods=["POST"])
def search_manual():
    """作業マニュアルを検索（フェーズ2-3）"""
    try:
        from data_access.manual_manager import get_manual_manager
        
        manual_mgr = get_manual_manager()
        if not manual_mgr:
            return jsonify({
                "error": "マニュアル管理機能が利用できません",
                "message": "NOTION_MANUAL_DB_IDが設定されていない可能性があります"
            }), 503
        
        data = request.get_json() or {}
        query = data.get("query", "").strip()
        category = data.get("category", "")
        difficulty = data.get("difficulty", "")
        limit = int(data.get("limit", 10))
        
        if not query:
            return jsonify({"error": "検索クエリが空です"}), 400
        
        # マニュアルを検索
        manuals = manual_mgr.search_manuals(
            query=query,
            category=category if category else None,
            difficulty=difficulty if difficulty else None,
            limit=limit
        )
        
        return jsonify({
            "manuals": manuals,
            "count": len(manuals),
            "query": query,
            "filters": {
                "category": category,
                "difficulty": difficulty
            }
        })
    
    except Exception as e:
        print(f"❌ マニュアル検索エラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/factory/manual/<manual_id>", methods=["GET"])
def get_manual_detail(manual_id):
    """マニュアル詳細を取得（フェーズ2-3）"""
    try:
        from data_access.manual_manager import get_manual_manager
        
        manual_mgr = get_manual_manager()
        if not manual_mgr:
            return jsonify({"error": "マニュアル管理機能が利用できません"}), 503
        
        manual = manual_mgr.get_manual(manual_id)
        if not manual:
            return jsonify({"error": "マニュアルが見つかりません"}), 404
        
        return jsonify(manual)
    
    except Exception as e:
        print(f"❌ マニュアル取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/factory/technical/answer", methods=["POST"])
def answer_technical_question():
    """技術質問への回答を生成（フェーズ2-3）"""
    try:
        from data_access.manual_manager import get_manual_manager
        from ai_symptom_classifier import SymptomClassifier
        
        data = request.get_json() or {}
        question = data.get("question", "").strip()
        context = data.get("context", {})
        
        if not question:
            return jsonify({"error": "質問が空です"}), 400
        
        # 1. 関連マニュアルを検索
        manual_mgr = get_manual_manager()
        related_manuals = []
        if manual_mgr:
            related_manuals = manual_mgr.search_manuals(
                query=question,
                category=context.get("category"),
                limit=3
            )
        
        # 2. 過去の類似質問を検索（Notion ChatLogsから）
        similar_qa = []
        # TODO: 過去のQ&Aを検索する機能を実装
        # （実際の実装では、より高度な類似度計算を使用）
        
        # 3. AIで回答を生成
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # プロンプトを構築
            manual_context = ""
            if related_manuals:
                manual_context = "\n\n【関連マニュアル】\n"
                for i, manual in enumerate(related_manuals[:3], 1):
                    manual_context += f"{i}. {manual.get('title', '')}\n"
                    manual_context += f"   手順: {manual.get('steps', '')[:200]}...\n"
            
            prompt = f"""あなたはキャンピングカー修理の専門家です。以下の技術質問に回答してください。

【質問】
{question}

{manual_context}

【回答要件】
1. 専門的で正確な回答
2. 具体的な手順や方法を含める
3. 安全注意事項があれば明記
4. 必要に応じて工具や部品の情報を含める

【回答】
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはキャンピングカー修理の技術エキスパートです。工場の技術者からの質問に専門的で実践的な回答を提供してください。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content.strip()
            
            # 4. カテゴリを分類
            classifier = SymptomClassifier()
            category_result = classifier.classify_symptom(question, use_ai=False)
            
            return jsonify({
                "answer": answer,
                "category": category_result.get("category", "一般"),
                "confidence": category_result.get("confidence", 0.5),
                "references": [
                    {
                        "type": "manual",
                        "title": manual.get("title", ""),
                        "id": manual.get("id", ""),
                        "url": manual.get("url", "")
                    }
                    for manual in related_manuals[:3]
                ],
                "similar_qa_count": len(similar_qa)
            })
        
        except Exception as e:
            print(f"❌ AI回答生成エラー: {e}")
            return jsonify({
                "error": "回答生成に失敗しました",
                "message": str(e)
            }), 500
    
    except Exception as e:
        print(f"❌ 技術質問回答エラー: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/factory/best-practices/suggest", methods=["POST"])
def suggest_best_practices():
    """ベストプラクティスを提示（フェーズ2-3）"""
    try:
        data = request.get_json() or {}
        context = data.get("context", {})
        
        category = context.get("category", "")
        difficulty = context.get("difficulty", "")
        current_step = context.get("current_step", "")
        
        # 簡易実装: マニュアルから関連情報を取得
        from data_access.manual_manager import get_manual_manager
        
        manual_mgr = get_manual_manager()
        practices = []
        
        if manual_mgr:
            # カテゴリと難易度でマニュアルを検索
            manuals = manual_mgr.search_manuals(
                query=current_step or category,
                category=category if category else None,
                difficulty=difficulty if difficulty else None,
                limit=5
            )
            
            # マニュアルからベストプラクティスを抽出
            for manual in manuals:
                practices.append({
                    "id": manual.get("id", ""),
                    "title": manual.get("title", ""),
                    "content": manual.get("steps", "")[:300] + "...",
                    "effect": f"作業時間: 約{manual.get('estimated_time', 0)}分",
                    "recommendation": "高" if manual.get("difficulty") == "初級" else "中",
                    "category": manual.get("category", ""),
                    "difficulty": manual.get("difficulty", "")
                })
        
        return jsonify({
            "practices": practices,
            "count": len(practices),
            "context": context
        })
    
    except Exception as e:
        print(f"❌ ベストプラクティス提示エラー: {e}")
        return jsonify({"error": str(e)}), 500

# ===== フェーズ2-3: 工場教育AIモード 終了 =====

# ===== フェーズ3: 工場ダッシュボードAPI（Next.js用） =====

@app.route("/admin/api/cases", methods=["GET"])
def get_admin_cases():
    """案件一覧取得API（Next.js用、認証なしで開発）"""
    try:
        from data_access.factory_dashboard_manager import FactoryDashboardManager
        
        manager = FactoryDashboardManager()
        
        status = request.args.get("status")  # フィルタ（受付/診断中/修理中/完了/キャンセル）
        limit = int(request.args.get("limit", 100))
        partner_page_id = request.args.get("partner_page_id")  # パートナー工場のNotion Page ID
        
        # パートナー工場IDが指定されている場合、その工場に紹介された案件のみ取得
        cases = manager.get_cases(
            status=status if status else None,
            limit=limit,
            partner_page_id=partner_page_id if partner_page_id else None
        )
        
        if partner_page_id:
            print(f"✅ パートナー工場専用の案件取得成功: {len(cases)}件（工場ID: {partner_page_id}）")
        else:
            print(f"✅ 全案件取得成功: {len(cases)}件")
        
        return jsonify({
            "success": True,
            "cases": cases,
            "count": len(cases),
            "partner_page_id": partner_page_id  # デバッグ用
        })
    
    except Exception as e:
        import traceback
        print(f"❌ 案件取得APIエラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/admin/api/update-status", methods=["POST"])
def update_admin_case_status():
    """ステータス更新API（Next.js用、認証なしで開発）"""
    try:
        data = request.get_json()
        page_id = data.get("page_id")
        status = data.get("status")
        
        if not page_id or not status:
            return jsonify({
                "success": False,
                "error": "page_idとstatusが必要です"
            }), 400
        
        from data_access.factory_dashboard_manager import FactoryDashboardManager
        
        manager = FactoryDashboardManager()
        success = manager.update_status(page_id, status)
        
        if success:
            return jsonify({
                "success": True,
                "message": "ステータスを更新しました"
            })
        else:
            return jsonify({
                "success": False,
                "error": "ステータス更新に失敗しました"
            }), 500
    
    except Exception as e:
        import traceback
        print(f"❌ ステータス更新APIエラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/admin/api/add-comment", methods=["POST"])
def add_admin_comment():
    """コメント追加API（Next.js用、認証なしで開発）"""
    try:
        data = request.get_json()
        page_id = data.get("page_id")
        comment = data.get("comment")
        
        if not page_id or not comment:
            return jsonify({
                "success": False,
                "error": "page_idとcommentが必要です"
            }), 400
        
        from data_access.factory_dashboard_manager import FactoryDashboardManager
        
        manager = FactoryDashboardManager()
        success = manager.add_comment(page_id, comment)
        
        if success:
            return jsonify({
                "success": True,
                "message": "コメントを追加しました"
            })
        else:
            return jsonify({
                "success": False,
                "error": "コメント追加に失敗しました"
            }), 500
    
    except Exception as e:
        import traceback
        print(f"❌ コメント追加APIエラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ===== フェーズ3: 工場ダッシュボードAPI 終了 =====

@app.route("/api/v1/factories/<factory_id>/cases", methods=["GET"])
def get_factory_cases(factory_id):
    """工場の案件一覧取得"""
    try:
        if not factory_manager:
            return jsonify({"error": "Factory Managerが利用できません"}), 503
        
        status = request.args.get("status")
        limit = int(request.args.get("limit", 100))
        
        cases = factory_manager.get_factory_cases(
            factory_id=factory_id,
            status=status,
            limit=limit
        )
        
        return jsonify({
            "factory_id": factory_id,
            "cases": cases,
            "count": len(cases)
        })
    except Exception as e:
        print(f"❌ 工場案件取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/builders", methods=["GET"])
def get_builders():
    """ビルダー一覧取得"""
    try:
        if not builder_manager:
            return jsonify({"error": "Builder Managerが利用できません"}), 503
        
        # クエリパラメータ取得
        status = request.args.get("status")
        prefecture = request.args.get("prefecture")
        limit = int(request.args.get("limit", 100))
        
        builders = builder_manager.list_builders(
            status=status,
            prefecture=prefecture,
            limit=limit
        )
        
        return jsonify({
            "builders": builders,
            "count": len(builders)
        })
    except Exception as e:
        print(f"❌ ビルダー一覧取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/builders", methods=["POST"])
def create_builder():
    """ビルダー登録"""
    try:
        if not builder_manager:
            return jsonify({"error": "Builder Managerが利用できません"}), 503
        
        data = request.get_json()
        
        # 必須フィールドチェック
        required_fields = ["name", "prefecture", "address", "phone", "email", "contact_person"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field}は必須です"}), 400
        
        builder = builder_manager.create_builder(
            name=data["name"],
            prefecture=data["prefecture"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            contact_person=data["contact_person"],
            line_account=data.get("line_account"),
            status=data.get("status", "アクティブ"),
            total_referrals=data.get("total_referrals", 0),
            total_deals=data.get("total_deals", 0),
            monthly_fee=data.get("monthly_fee", 0),
            contract_start_date=data.get("contract_start_date"),
            notes=data.get("notes")
        )
        
        return jsonify(builder), 201
    except Exception as e:
        print(f"❌ ビルダー登録エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/builders/<builder_id>", methods=["GET"])
def get_builder_detail(builder_id):
    """ビルダー詳細取得"""
    try:
        if not builder_manager:
            return jsonify({"error": "Builder Managerが利用できません"}), 503
        
        builder = builder_manager.get_builder(builder_id)
        if not builder:
            return jsonify({"error": "ビルダーが見つかりません"}), 404
        
        return jsonify(builder)
    except Exception as e:
        print(f"❌ ビルダー取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/builders/<builder_id>", methods=["PATCH"])
def update_builder_detail(builder_id):
    """ビルダー更新"""
    try:
        if not builder_manager:
            return jsonify({"error": "Builder Managerが利用できません"}), 503
        
        data = request.get_json()
        builder = builder_manager.update_builder(builder_id, **data)
        
        if not builder:
            return jsonify({"error": "ビルダーが見つかりません"}), 404
        
        return jsonify(builder)
    except Exception as e:
        print(f"❌ ビルダー更新エラー: {e}")
        return jsonify({"error": str(e)}), 500

# === 評価システムAPI ===
@app.route("/api/v1/reviews", methods=["POST"])
def create_review():
    """
    評価を作成
    
    Request Body:
    {
        "deal_id": "DEAL-20241103-001",
        "partner_page_id": "notion-page-id",
        "customer_name": "田中太郎",
        "star_rating": 5,
        "comment": "とても丁寧に対応していただきました",
        "anonymous": false
    }
    
    Returns:
    {
        "success": true,
        "review": {
            "review_id": "REVIEW-20241103-001",
            "star_rating": 5,
            "comment": "...",
            ...
        }
    }
    """
    try:
        from data_access.review_manager import ReviewManager
        
        data = request.get_json()
        deal_id = data.get("deal_id")
        partner_page_id = data.get("partner_page_id")
        customer_name = data.get("customer_name")
        star_rating = data.get("star_rating")
        comment = data.get("comment", "")
        anonymous = data.get("anonymous", False)
        
        if not all([deal_id, partner_page_id, customer_name, star_rating]):
            return jsonify({
                "success": False,
                "error": "deal_id, partner_page_id, customer_name, star_ratingは必須です"
            }), 400
        
        if not (1 <= star_rating <= 5):
            return jsonify({
                "success": False,
                "error": "star_ratingは1〜5の範囲で指定してください"
            }), 400
        
        review_manager = ReviewManager()
        review = review_manager.create_review(
            deal_id=deal_id,
            partner_page_id=partner_page_id,
            customer_name=customer_name,
            star_rating=star_rating,
            comment=comment,
            anonymous=anonymous
        )
        
        if not review:
            return jsonify({
                "success": False,
                "error": "評価の作成に失敗しました"
            }), 500
        
        return jsonify({
            "success": True,
            "review": review
        })
    
    except Exception as e:
        import traceback
        print(f"❌ 評価作成エラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/reviews", methods=["GET"])
def get_reviews():
    """
    評価一覧を取得
    
    Query Parameters:
    - partner_page_id: パートナー工場のNotion Page ID（フィルタ用）
    - status: 承認ステータス（pending / approved / rejected）
    - limit: 取得件数（デフォルト: 20）
    
    Returns:
    {
        "success": true,
        "reviews": [...],
        "count": 10
    }
    """
    try:
        from data_access.review_manager import ReviewManager
        
        partner_page_id = request.args.get("partner_page_id")
        status = request.args.get("status")
        limit = int(request.args.get("limit", 20))
        
        review_manager = ReviewManager()
        reviews = review_manager.get_reviews(
            partner_page_id=partner_page_id,
            status=status,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "reviews": reviews,
            "count": len(reviews)
        })
    
    except Exception as e:
        import traceback
        print(f"❌ 評価取得エラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/reviews/<review_id>/status", methods=["PATCH"])
def update_review_status(review_id):
    """
    評価の承認ステータスを更新（運営側用）
    
    Request Body:
    {
        "status": "approved",  # approved / rejected
        "admin_comment": "承認しました"  # オプション
    }
    
    Returns:
    {
        "success": true
    }
    """
    try:
        from data_access.review_manager import ReviewManager
        
        data = request.get_json()
        status = data.get("status")
        admin_comment = data.get("admin_comment")
        
        if status not in ["approved", "rejected"]:
            return jsonify({
                "success": False,
                "error": "statusはapprovedまたはrejectedを指定してください"
            }), 400
        
        review_manager = ReviewManager()
        success = review_manager.update_review_status(
            review_id=review_id,
            status=status,
            admin_comment=admin_comment
        )
        
        if not success:
            return jsonify({
                "success": False,
                "error": "評価ステータスの更新に失敗しました"
            }), 500
        
        return jsonify({
            "success": True
        })
    
    except Exception as e:
        import traceback
        print(f"❌ 評価ステータス更新エラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# === フェーズ4-1: 工場ネットワーク機能の拡張 ===
@app.route("/api/v1/factories/match", methods=["POST"])
def match_factory_to_case():
    """
    案件に最適な工場をマッチング（フェーズ4-1）
    
    案件情報（カテゴリ、症状、顧客所在地）に基づいて、
    最適な工場をAIでマッチングします。
    マッチングスコアは以下の要素で計算されます：
    - カテゴリマッチング（専門分野との一致度）
    - 地域マッチング（対応エリアとの一致度）
    - キャパシティマッチング（混雑状況）
    - 評価スコア（過去の実績）
    
    Request Body:
        {
            "case": {
                "category": "エアコン",           # 症状カテゴリ
                "user_message": "エアコンが効かない",  # ユーザーメッセージ
                "customer_location": "東京都"    # 顧客所在地
            },
            "max_results": 5  # 返す工場の最大数（デフォルト: 5）
        }
    
    Returns:
        {
            "success": true,
            "matched_factories": [
                {
                    "factory_id": "FACTORY-001",
                    "name": "工場名",
                    "matching_score": 0.85,  # 総合マッチングスコア（0-1）
                    "score_details": {
                        "category_match": 0.9,    # カテゴリマッチングスコア
                        "location_match": 0.8,    # 地域マッチングスコア
                        "capacity_match": 0.9,    # キャパシティスコア
                        "rating_score": 0.8       # 評価スコア
                    }
                }
            ],
            "count": 5
        }
    
    Raises:
        400: case情報が不足している場合
        500: サーバーエラー
    """
    try:
        from data_access.factory_matching import FactoryMatchingEngine
        
        data = request.get_json()
        case = data.get("case", {})
        max_results = int(data.get("max_results", 5))
        
        if not case:
            return jsonify({
                "success": False,
                "error": "case情報が必要です"
            }), 400
        
        matching_engine = FactoryMatchingEngine()
        matched_factories = matching_engine.match_factory_to_case(
            case=case,
            max_results=max_results
        )
        
        return jsonify({
            "success": True,
            "matched_factories": matched_factories,
            "count": len(matched_factories)
        })
        
    except Exception as e:
        import traceback
        print(f"❌ 工場マッチングエラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/cases/<case_id>/auto-assign", methods=["POST"])
def auto_assign_case_to_factory(case_id):
    """
    案件を自動的に最適な工場に割り当て（フェーズ4-1）
    
    Request Body:
    {
        "case": {
            "category": "エアコン",
            "user_message": "エアコンが効かない",
            "customer_location": "東京都"
        }
    }
    
    Returns:
    {
        "success": true,
        "assigned_factory": {
            "factory_id": "FACTORY-001",
            "name": "工場名",
            "matching_score": 0.85
        }
    }
    """
    try:
        from data_access.factory_matching import FactoryMatchingEngine
        
        data = request.get_json()
        case = data.get("case", {})
        
        if not case:
            return jsonify({
                "success": False,
                "error": "case情報が必要です"
            }), 400
        
        matching_engine = FactoryMatchingEngine()
        assigned_factory = matching_engine.auto_assign_case(
            case_id=case_id,
            case=case
        )
        
        if assigned_factory:
            return jsonify({
                "success": True,
                "assigned_factory": assigned_factory
            })
        else:
            return jsonify({
                "success": False,
                "error": "マッチする工場が見つかりませんでした"
            }), 404
        
    except Exception as e:
        import traceback
        print(f"❌ 案件自動割り当てエラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# === フェーズ4-2: ビルダー（販売店）連携機能 ===
@app.route("/api/v1/partner-shops", methods=["GET"])
def get_partner_shops():
    """パートナー修理店一覧取得"""
    try:
        from data_access.partner_shop_manager import PartnerShopManager
        
        manager = PartnerShopManager()
        
        status = request.args.get("status")
        prefecture = request.args.get("prefecture")
        specialty = request.args.get("specialty")
        limit = int(request.args.get("limit", 100))
        
        shops = manager.list_shops(
            status=status,
            prefecture=prefecture,
            specialty=specialty,
            limit=limit
        )
        
        return jsonify({
            "shops": shops,
            "count": len(shops)
        })
    except Exception as e:
        print(f"❌ パートナー修理店一覧取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/partner-shops/<shop_id>", methods=["GET"])
def get_partner_shop_detail(shop_id):
    """パートナー修理店詳細取得"""
    try:
        from data_access.partner_shop_manager import PartnerShopManager
        
        manager = PartnerShopManager()
        shop = manager.get_shop(shop_id)
        
        if not shop:
            return jsonify({"error": "パートナー修理店が見つかりません"}), 404
        
        return jsonify(shop)
    except Exception as e:
        print(f"❌ パートナー修理店取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/deals", methods=["POST"])
def create_deal():
    """商談作成（問い合わせフォーム送信）"""
    try:
        from data_access.deal_manager import DealManager
        
        data = request.get_json()
        
        # 必須項目チェック
        required_fields = [
            "customer_name", "phone", "prefecture",
            "symptom_category", "symptom_detail", "partner_page_id"
        ]
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"{field}は必須です"
                }), 400
        
        deal_manager = DealManager()
        deal = deal_manager.create_inquiry(
            customer_name=data["customer_name"],
            phone=data["phone"],
            prefecture=data["prefecture"],
            symptom_category=data["symptom_category"],
            symptom_detail=data["symptom_detail"],
            partner_page_id=data["partner_page_id"],
            email=data.get("email"),
            notification_method=data.get("notification_method"),
            line_user_id=data.get("line_user_id")
        )
        
        # 通知機能（メール + LINE）
        try:
            from notification.email_sender import EmailSender
            from notification.line_notifier import LineNotifier
            from data_access.partner_shop_manager import PartnerShopManager
            
            email_sender = EmailSender()
            line_notifier = LineNotifier()
            
            # 修理店情報を取得
            partner_manager = PartnerShopManager()
            partner_shop = partner_manager.get_shop_by_page_id(data["partner_page_id"])
            
            if partner_shop:
                customer_info = {
                    "name": data["customer_name"],
                    "phone": data["phone"],
                    "prefecture": data["prefecture"],
                    "email": data.get("email", ""),
                    "category": data["symptom_category"],
                    "detail": data["symptom_detail"]
                }
                partner_name = partner_shop.get("name", "修理店様")
                
                # 通知方法を取得（デフォルトはメール）
                notification_method = data.get("notification_method", "email")
                
                # メール通知機能（メールを選択した場合）
                if notification_method == "email" and email_sender.enabled:
                    # 修理店にメール通知
                    if partner_shop.get("email"):
                        email_sender.send_to_partner(
                            partner_email=partner_shop["email"],
                            partner_name=partner_name,
                            customer_info=customer_info
                        )
                    
                    # 顧客に確認メール（メールアドレスが入力されている場合）
                    if data.get("email"):
                        email_sender.send_to_customer(
                            customer_email=data["email"],
                            customer_name=data["customer_name"],
                            partner_name=partner_name
                        )
                        
                        # 自動返信メールを送信（システムフロー図のステップ0に対応）
                        email_sender.send_auto_reply_to_customer(
                            customer_email=data["email"],
                            customer_name=data["customer_name"]
                        )
                elif notification_method == "email" and not email_sender.enabled:
                    print("⚠️ SMTP設定が不完全です。メール送信をスキップします。")
                
                # LINE通知機能（LINEを選択した場合）
                if notification_method == "line" and line_notifier.enabled and partner_shop.get("line_notification"):
                    line_user_id = partner_shop.get("line_user_id")
                    
                    # LINEユーザーIDが設定されていない場合、Webhook URLから抽出を試みる
                    if not line_user_id:
                        line_webhook_url = partner_shop.get("line_webhook_url")
                        if line_webhook_url:
                            # Webhook URLからユーザーIDを抽出する試み（カスタムWebhookの場合は別途実装が必要）
                            print("⚠️ LINEユーザーIDが設定されていません。Webhook URLから抽出を試みます。")
                    
                    # 修理店にLINE通知
                    if line_user_id:
                        line_result = line_notifier.send_to_partner(
                            line_user_id=line_user_id,
                            partner_name=partner_name,
                            customer_info=customer_info
                        )
                        if line_result.get("success"):
                            print(f"✅ LINE通知送信成功: {partner_name}")
                        else:
                            print(f"⚠️ LINE通知送信失敗: {line_result.get('error')}")
                    else:
                        print("⚠️ LINEユーザーIDが設定されていません。LINE通知をスキップします。")
                elif notification_method == "line" and partner_shop.get("line_notification") and not line_notifier.enabled:
                    print("⚠️ LINE_CHANNEL_ACCESS_TOKENが設定されていません。LINE通知をスキップします。")
                
                # 顧客へのLINE通知（顧客がLINE Loginでログインしている場合、かつLINE通知を希望している場合）
                if notification_method == "line" and line_notifier.enabled and data.get("line_user_id"):
                    customer_line_result = line_notifier.send_to_customer(
                        line_user_id=data["line_user_id"],
                        customer_name=data["customer_name"],
                        partner_name=partner_name,
                        deal_id=deal.get("deal_id")
                    )
                    if customer_line_result.get("success"):
                        print(f"✅ 顧客へのLINE通知送信成功: {data['customer_name']}")
                    else:
                        print(f"⚠️ 顧客へのLINE通知送信失敗: {customer_line_result.get('error')}")
                    
        except Exception as notification_error:
            # 通知エラーはログに記録するが、商談作成は成功とする
            print(f"⚠️ 通知エラー（商談は正常に作成されました）: {notification_error}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            "success": True,
            "deal": deal,
            "message": "問い合わせを受け付けました"
        })
        
    except Exception as e:
        import traceback
        print(f"❌ 商談作成エラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/deals", methods=["GET"])
def get_deals():
    """商談一覧取得"""
    try:
        from data_access.deal_manager import DealManager
        
        deal_manager = DealManager()
        
        status = request.args.get("status")
        partner_page_id = request.args.get("partner_page_id")
        limit = int(request.args.get("limit", 100))
        
        deals = deal_manager.list_deals(
            status=status,
            partner_page_id=partner_page_id,
            limit=limit
        )
        
        return jsonify({
            "deals": deals,
            "count": len(deals)
        })
    except Exception as e:
        print(f"❌ 商談一覧取得エラー: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/deals/<deal_id>/status", methods=["PATCH"])
def update_deal_status(deal_id):
    """商談ステータス更新"""
    try:
        from data_access.deal_manager import DealManager
        from data_access.partner_shop_manager import PartnerShopManager
        from notification.email_sender import EmailSender
        from notification.line_notifier import LineNotifier
        
        data = request.get_json()
        status = data.get("status")
        notes = data.get("notes")  # 備考（オプション）
        
        if not status:
            return jsonify({
                "success": False,
                "error": "statusが必要です"
            }), 400
        
        deal_manager = DealManager()
        updated_deal = deal_manager.update_deal_status(deal_id, status)
        
        if not updated_deal:
            return jsonify({
                "success": False,
                "error": "商談が見つかりません"
            }), 404
        
        # ステータス更新通知を送信
        try:
            email_sender = EmailSender()
            line_notifier = LineNotifier()
            
            # 商談情報を取得
            deal = deal_manager.get_deal(deal_id)
            if deal:
                notification_method = deal.get("notification_method", "email")
                customer_name = deal.get("customer_name", "")
                customer_email = deal.get("email")
                line_user_id = deal.get("line_user_id")
                
                # 修理店情報を取得
                partner_page_ids = deal.get("partner_page_ids", [])
                partner_name = "修理店"
                if partner_page_ids:
                    partner_manager = PartnerShopManager()
                    partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                    if partner_shop:
                        partner_name = partner_shop.get("name", "修理店")
                
                # メール通知（メールを選択した場合）
                if notification_method == "email" and email_sender.enabled and customer_email:
                    email_sender.send_status_update_to_customer(
                        customer_email=customer_email,
                        customer_name=customer_name,
                        partner_name=partner_name,
                        status=status,
                        deal_id=deal_id,
                        notes=notes
                    )
                
                # LINE通知（LINEを選択した場合）
                if notification_method == "line" and line_notifier.enabled and line_user_id:
                    line_notifier.send_status_update_notification(
                        line_user_id=line_user_id,
                        customer_name=customer_name,
                        partner_name=partner_name,
                        status=status,
                        deal_id=deal_id,
                        notes=notes
                    )
                    
        except Exception as notification_error:
            # 通知エラーはログに記録するが、ステータス更新は成功とする
            print(f"⚠️ ステータス更新通知エラー（ステータス更新は正常に完了しました）: {notification_error}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            "success": True,
            "deal": updated_deal
        })
        
    except Exception as e:
        print(f"❌ 商談ステータス更新エラー: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/deals/<deal_id>/customer-notes", methods=["POST"])
def add_customer_note(deal_id):
    """お客様からの備考追加"""
    try:
        from data_access.deal_manager import DealManager
        from data_access.partner_shop_manager import PartnerShopManager
        from notification.email_sender import EmailSender
        from notification.line_notifier import LineNotifier
        
        data = request.get_json()
        customer_note = data.get("note") or data.get("customer_note")
        
        if not customer_note:
            return jsonify({
                "success": False,
                "error": "note（備考）が必要です"
            }), 400
        
        deal_manager = DealManager()
        updated_deal = deal_manager.add_customer_note(deal_id, customer_note)
        
        if not updated_deal:
            return jsonify({
                "success": False,
                "error": "商談が見つかりません"
            }), 404
        
        # 工場側への自動通知
        try:
            email_sender = EmailSender()
            line_notifier = LineNotifier()
            
            # 商談情報を取得
            deal = deal_manager.get_deal(deal_id)
            if deal:
                customer_name = deal.get("customer_name", "")
                customer_phone = deal.get("phone", "")
                
                # 修理店情報を取得
                partner_page_ids = deal.get("partner_page_ids", [])
                if partner_page_ids:
                    partner_manager = PartnerShopManager()
                    partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                    
                    if partner_shop:
                        partner_name = partner_shop.get("name", "修理店")
                        partner_email = partner_shop.get("email")
                        partner_line_user_id = partner_shop.get("line_user_id")
                        
                        # 工場側にメール通知
                        if email_sender.enabled and partner_email:
                            subject = "【お客様からのメッセージ】岡山キャンピングカー修理サポートセンター"
                            body = f"""
{partner_name} 様

お世話になっております。
岡山キャンピングカー修理サポートセンターです。

お客様からメッセージが届きました。

【商談ID】
{deal_id}

【お客様情報】
お名前: {customer_name}
電話番号: {customer_phone}

【お客様からのメッセージ】
{customer_note}

Notionダッシュボードで詳細を確認してください。

---
岡山キャンピングカー修理サポートセンター
https://camper-repair.net/
"""
                            email_sender._send_email(partner_email, subject, body)
                        
                        # 工場側にLINE通知
                        if line_notifier.enabled and partner_shop.get("line_notification") and partner_line_user_id:
                            message = f"""📝 お客様からメッセージが届きました

【商談ID】
{deal_id}

【お客様】
{customer_name}様

【メッセージ】
{customer_note}

Notionダッシュボードで詳細を確認してください。
"""
                            line_notifier._send_notification(partner_line_user_id, message)
                            
        except Exception as notification_error:
            # 通知エラーはログに記録するが、備考追加は成功とする
            print(f"⚠️ 工場側通知エラー（備考追加は正常に完了しました）: {notification_error}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            "success": True,
            "deal": updated_deal,
            "message": "メッセージを送信しました。修理店より連絡がありますので、しばらくお待ちください。"
        })
        
    except Exception as e:
        print(f"❌ お客様備考追加エラー: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/deals/<deal_id>/progress-report", methods=["POST"])
def add_progress_report(deal_id):
    """工場側からの経過報告送信"""
    try:
        from data_access.deal_manager import DealManager
        from data_access.partner_shop_manager import PartnerShopManager
        from notification.email_sender import EmailSender
        from notification.line_notifier import LineNotifier
        
        data = request.get_json()
        progress_message = data.get("message") or data.get("progress_message")
        
        if not progress_message:
            return jsonify({
                "success": False,
                "error": "message（経過報告内容）が必要です"
            }), 400
        
        deal_manager = DealManager()
        
        # 経過報告を追加（最大2回まで）
        try:
            updated_deal = deal_manager.add_progress_report(deal_id, progress_message, max_reports=2)
        except ValueError as ve:
            # 最大回数に達した場合
            return jsonify({
                "success": False,
                "error": str(ve)
            }), 400
        
        if not updated_deal:
            return jsonify({
                "success": False,
                "error": "商談が見つかりません"
            }), 404
        
        # お客様への自動通知
        try:
            email_sender = EmailSender()
            line_notifier = LineNotifier()
            
            # 商談情報を取得
            deal = deal_manager.get_deal(deal_id)
            if deal:
                notification_method = deal.get("notification_method", "email")
                customer_name = deal.get("customer_name", "")
                customer_email = deal.get("email")
                line_user_id = deal.get("line_user_id")
                
                # 修理店情報を取得
                partner_page_ids = deal.get("partner_page_ids", [])
                partner_name = "修理店"
                if partner_page_ids:
                    partner_manager = PartnerShopManager()
                    partner_shop = partner_manager.get_shop_by_page_id(partner_page_ids[0])
                    if partner_shop:
                        partner_name = partner_shop.get("name", "修理店")
                
                # 現在の報告回数を取得
                report_count = updated_deal.get("progress_report_count", 0)
                
                # メール通知（メールを選択した場合）
                if notification_method == "email" and email_sender.enabled and customer_email:
                    email_sender.send_progress_report_to_customer(
                        customer_email=customer_email,
                        customer_name=customer_name,
                        partner_name=partner_name,
                        progress_message=progress_message,
                        report_count=report_count,
                        deal_id=deal_id
                    )
                
                # LINE通知（LINEを選択した場合）
                if notification_method == "line" and line_notifier.enabled and line_user_id:
                    line_notifier.send_progress_report_notification(
                        line_user_id=line_user_id,
                        customer_name=customer_name,
                        partner_name=partner_name,
                        progress_message=progress_message,
                        report_count=report_count,
                        deal_id=deal_id
                    )
                    
        except Exception as notification_error:
            # 通知エラーはログに記録するが、経過報告追加は成功とする
            print(f"⚠️ 経過報告通知エラー（経過報告追加は正常に完了しました）: {notification_error}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            "success": True,
            "deal": updated_deal,
            "message": f"経過報告を送信しました（{updated_deal.get('progress_report_count', 0)}/2回）"
        })
        
    except Exception as e:
        print(f"❌ 経過報告追加エラー: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/deals/by-page-id/<page_id>", methods=["GET"])
def get_deal_by_page_id(page_id):
    """Page IDから商談IDを取得"""
    try:
        from data_access.deal_manager import DealManager
        
        deal_manager = DealManager()
        
        # すべての商談を検索してpage_idでフィルタ
        deals = deal_manager.list_deals(limit=1000)
        deal = next((d for d in deals if d.get("page_id") == page_id), None)
        
        if not deal:
            return jsonify({
                "success": False,
                "error": "商談が見つかりません"
            }), 404
        
        return jsonify({
            "success": True,
            "deal_id": deal.get("deal_id"),
            "deal_data": deal
        })
        
    except Exception as e:
        print(f"❌ 商談取得エラー: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/v1/deals/<deal_id>/amount", methods=["PATCH"])
def update_deal_amount(deal_id):
    """成約金額更新"""
    try:
        from data_access.deal_manager import DealManager
        
        data = request.get_json()
        deal_amount = data.get("deal_amount")
        commission_rate = data.get("commission_rate")
        
        if deal_amount is None:
            return jsonify({
                "success": False,
                "error": "deal_amountが必要です"
            }), 400
        
        deal_manager = DealManager()
        updated_deal = deal_manager.update_deal_amount(
            deal_id=deal_id,
            deal_amount=deal_amount,
            commission_rate=commission_rate
        )
        
        if not updated_deal:
            return jsonify({
                "success": False,
                "error": "商談が見つかりません"
            }), 404
        
        return jsonify({
            "success": True,
            "deal": updated_deal
        })
        
    except Exception as e:
        print(f"❌ 成約金額更新エラー: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# === 管理者画面API ===
@app.route("/reload_data", methods=["POST"])
def reload_data():
    """データベース再構築"""
    try:
        print("🔄 データベース再構築を開始します...")
        
        # RAGシステムを再構築
        global db
        use_text_files = os.getenv("USE_TEXT_FILES", "true").lower() == "true"
        
        # 既存のDBをクリア
        db = None
        
        # 新しいRAGシステムを作成
        db = create_notion_based_rag_system(use_text_files=use_text_files)
        
        if db:
            print("✅ データベース再構築が完了しました")
            return jsonify({
                "success": True,
                "message": "データベースを再構築しました"
            })
        else:
            return jsonify({
                "success": False,
                "error": "データベースの再構築に失敗しました"
            }), 500
            
    except Exception as e:
        import traceback
        print(f"❌ データベース再構築エラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/admin/files", methods=["GET"])
def get_admin_files():
    """ファイル一覧取得"""
    try:
        # テキストファイルを検索
        txt_files = glob.glob("*.txt")
        files = []
        
        for txt_file in txt_files:
            try:
                file_size = os.path.getsize(txt_file)
                # ファイルサイズを読みやすい形式に変換
                if file_size < 1024:
                    size_str = f"{file_size}B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f}KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f}MB"
                
                files.append({
                    "name": txt_file,
                    "size": size_str
                })
            except Exception as e:
                print(f"⚠️ ファイル情報取得エラー ({txt_file}): {e}")
        
        return jsonify({
            "files": files,
            "count": len(files)
        })
    except Exception as e:
        print(f"❌ ファイル一覧取得エラー: {e}")
        return jsonify({
            "files": [],
            "count": 0,
            "error": str(e)
        }), 500

# === フェーズ4-4: AI工賃推定 ===
@app.route("/api/v1/cost-estimation", methods=["POST"])
def estimate_repair_cost():
    """
    AI工賃推定（フェーズ4-4）
    
    Request Body:
    {
        "symptoms": "エアコンが効かない",
        "category": "エアコン",
        "vehicle_info": "トヨタ ハイエース 2020年式"
    }
    
    Returns:
    {
        "success": true,
        "estimation": {
            "estimated_work_hours": 2.5,
            "difficulty": "中級",
            "labor_cost_min": 15000,
            "labor_cost_max": 25000,
            "parts_cost_min": 5000,
            "parts_cost_max": 15000,
            "diagnosis_fee": 4000,
            "total_cost_min": 20000,
            "total_cost_max": 40000,
            "reasoning": "推定理由の説明",
            "similar_cases_count": 3
        }
    }
    """
    try:
        from data_access.cost_estimation import CostEstimationEngine
        
        data = request.get_json()
        symptoms = data.get("symptoms", "")
        category = data.get("category")
        vehicle_info = data.get("vehicle_info")
        
        if not symptoms:
            return jsonify({
                "success": False,
                "error": "symptoms（症状）が必要です"
            }), 400
        
        estimation_engine = CostEstimationEngine()
        estimation = estimation_engine.estimate_cost(
            symptoms=symptoms,
            category=category,
            vehicle_info=vehicle_info
        )
        
        return jsonify({
            "success": True,
            "estimation": estimation
        })
        
    except Exception as e:
        import traceback
        print(f"❌ 工賃推定エラー: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/admin/system-info", methods=["GET"])
def get_system_info():
    """システム情報取得"""
    try:
        # データベース状態を確認
        db_status = "正常" if db else "未初期化"
        
        # ドキュメント数を取得（RAGシステムから）
        doc_count = 0
        if db:
            try:
                # ChromaDBの場合、コレクションから取得
                if hasattr(db, 'get') and hasattr(db, '_collection'):
                    # コレクションの件数を取得
                    try:
                        collection = db._collection
                        if hasattr(collection, 'count'):
                            doc_count = collection.count()
                    except:
                        pass
            except Exception as e:
                print(f"⚠️ ドキュメント数取得エラー: {e}")
        
        # テキストファイル数も追加
        txt_files = glob.glob("*.txt")
        doc_count += len(txt_files)
        
        return jsonify({
            "dbStatus": db_status,
            "docCount": doc_count
        })
    except Exception as e:
        print(f"❌ システム情報取得エラー: {e}")
        return jsonify({
            "dbStatus": "エラー",
            "docCount": 0,
            "error": str(e)
        }), 500

# === アプリケーション起動 ===
# Railway環境でも初期化処理を実行
print("🚀 統合バックエンドAPIを起動中...")
print("📋 初期化プロセス開始...")

# サービス初期化（エラーハンドリング付き）
try:
    if initialize_services():
        print("✅ 全サービスが正常に初期化されました")
        print("🌐 アクセスURL: http://localhost:5002")
        print("📚 API ドキュメント (Swagger UI): http://localhost:5002/api/docs")
        print("📋 OpenAPI仕様書 (JSON): http://localhost:5002/api/docs/openapi.json")
        print("🔧 修理アドバイスセンター: http://localhost:5002/repair_advice_center.html")
        print("🔍 テストエンドポイント: http://localhost:5002/api/test")
    else:
        print("⚠️ 一部のサービス初期化に失敗しましたが、アプリケーションは起動します")
except Exception as e:
    print(f"❌ サービス初期化エラー: {e}")
    import traceback
    traceback.print_exc()
    print("⚠️ エラーが発生しましたが、アプリケーションは起動します")

if __name__ == "__main__":
    print("🚀 統合バックエンドAPIを起動中...")
    print("📋 初期化プロセス開始...")
    
    # サービス初期化
    if initialize_services():
        print("✅ 全サービスが正常に初期化されました")
        print("🌐 アクセスURL: http://localhost:5002")
        print("📚 API ドキュメント (Swagger UI): http://localhost:5002/api/docs")
        print("📋 OpenAPI仕様書 (JSON): http://localhost:5002/api/docs/openapi.json")
        print("🔧 修理アドバイスセンター: http://localhost:5002/repair_advice_center.html")
        print("🔍 テストエンドポイント: http://localhost:5002/api/test")
        print("🔍 診断フローAPI: http://localhost:5002/chat/diagnose/start")
        print("=" * 50)
        print("🚀 サーバーを起動中...")
        print("=" * 50)
        
        try:
            # Railway対応: 環境変数からポートを取得
            port = int(os.environ.get('PORT', 5002))
            host = os.environ.get('HOST', '0.0.0.0')
            debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
            
            app.run(debug=debug, host=host, port=port, threaded=True)
        except Exception as e:
            print(f"❌ サーバー起動エラー: {e}")
            print("🔧 対処法:")
            print("1. ポート5002が使用中でないか確認してください")
            print("2. ファイアウォール設定を確認してください")
            print("3. 管理者権限で実行してください")
    else:
        print("❌ サービス初期化に失敗しました")
        print("🔧 確認事項:")
        print("1. 環境変数が正しく設定されているか")
        print("2. 必要なライブラリがインストールされているか")
        print("3. APIキーが有効か")
        print("4. データベースファイルが存在するか")
