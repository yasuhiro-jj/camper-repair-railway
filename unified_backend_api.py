#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合バックエンドAPI - 最強チャットボット用
Flask + RAG + SERP + Notion + AI の全機能を統合
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import asyncio
import aiohttp
import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional

# 既存のモジュールをインポート
from config import OPENAI_API_KEY, SERP_API_KEY, LANGSMITH_API_KEY
from enhanced_rag_system import create_enhanced_rag_system, enhanced_rag_retrieve, create_notion_based_rag_system
from serp_search_system import get_serp_search_system
from repair_category_manager import RepairCategoryManager

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
CORS(app, origins=['http://localhost:8501', 'http://localhost:3000', 'http://localhost:3001', 'http://localhost:5002'])

# グローバル変数
db = None
category_manager = None
serp_system = None
notion_client_instance = None

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
    global db, category_manager, serp_system, notion_client_instance
    
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
    """質問に回答するエンドポイント"""
    try:
        # フォームデータとJSONの両方に対応
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            question = data.get('question', '')
        else:
            question = request.form.get('question', '')
        
        if not question:
            return jsonify({"error": "質問が入力されていません"}), 400
        
        # 統合チャット機能を呼び出し
        try:
            # 意図分析
            intent = analyze_intent(question)
            
            # 基本的なチャット処理
            result = process_chat_mode(question, intent, include_serp=True)
            
            # フロントエンドの期待する形式に変換
            answer = result.get("response", "回答を生成できませんでした")
            if isinstance(answer, dict):
                answer = str(answer)
            
            return jsonify({
                "answer": answer,
                "sources": result.get("rag_results", {}),
                "confidence": 0.8,  # デフォルト値
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
                
                # マニュアルコンテンツがある場合
                manual_content = rag_results.get('manual_content', '')
                print(f"📚 manual_content: {len(manual_content) if manual_content else 0}文字")
                if manual_content and len(manual_content) > 10:
                    # 費用情報を抽出
                    cost_info = ""
                    if "費用" in manual_content or "料金" in manual_content or "価格" in manual_content:
                        # 費用関連の部分を抽出
                        lines = manual_content.split('\n')
                        for line in lines:
                            if any(keyword in line for keyword in ["費用", "料金", "価格", "円"]):
                                cost_info += line + "\n"
                    
                    # 費用情報を含むコンテンツを構築
                    full_content = manual_content[:500] + "..." if len(manual_content) > 500 else manual_content
                    if cost_info:
                        full_content = f"💰 費用情報:\n{cost_info}\n\n" + full_content
                    
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
                        # フォールバック: 元の情報をそのまま使用
                        search_results.append({
                            "title": f"📚 {query}の修理情報（RAG）",
                            "content": full_content,
                            "source": "知識ベース（RAG）",
                            "category": "修理情報",
                            "url": None,
                            "relevance": "high"
                        })
                        print(f"  ✅ マニュアルコンテンツを追加（費用情報含む）")
                
                # テキストファイルコンテンツがある場合
                text_content = rag_results.get('text_file_content', '')
                print(f"📄 text_file_content: {len(text_content) if text_content else 0}文字")
                if text_content and len(text_content) > 10:
                    search_results.append({
                        "title": f"📄 {query}の詳細情報（テキスト）",
                        "content": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                        "source": "技術資料（テキスト）",
                        "category": "詳細情報",
                        "url": None,
                        "relevance": "high"
                    })
                    print(f"  ✅ テキストコンテンツを追加")
                
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
                                    content_parts.append(f"🛠️ 解決方法: {case['solution']}")
                                
                                if case.get('cost'):
                                    content_parts.append(f"💰 費用目安: {case['cost']}円")
                                
                                if case.get('difficulty'):
                                    content_parts.append(f"⚙️ 難易度: {case['difficulty']}")
                                
                                if case.get('time_estimate'):
                                    content_parts.append(f"⏱️ 推定時間: {case['time_estimate']}")
                                
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

{chr(10).join(content_parts)}

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
                                    # フォールバック: 元の情報をそのまま使用
                                    search_results.append({
                                        'title': f'🔧 {case.get("title", "修理ケース")}',
                                        'content': '\n'.join(content_parts),
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
                rag_results = enhanced_rag_retrieve(db, query, k=5)
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
                serp_results = serp_system.search(f"{query} キャンピングカー 修理 価格", num_results=2)
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

@app.route("/api/unified/chat", methods=["POST"])
def unified_chat():
    """統合チャットAPI"""
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        mode = data.get("mode", "chat")
        include_serp = data.get("include_serp", True)
        
        if not message:
            return jsonify({"error": "メッセージが空です"}), 400
        
        # 意図分析
        intent = analyze_intent(message)
        
        # モード別処理
        if mode == "diagnostic":
            result = process_diagnostic_mode(message, intent)
        elif mode == "repair_search":
            result = process_repair_search_mode(message, intent)
        elif mode == "cost_estimate":
            result = process_cost_estimate_mode(message, intent)
        else:  # chat
            result = process_chat_mode(message, intent, include_serp)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"チャット処理エラー: {str(e)}"}), 500

@app.route("/api/unified/search", methods=["POST"])
def unified_search():
    """統合検索API"""
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        search_types = data.get("types", ["rag", "serp", "categories"])
        
        if not query:
            return jsonify({"error": "検索クエリが空です"}), 400
        
        results = {}
        
        # RAG検索
        if "rag" in search_types and db:
            try:
                rag_results = enhanced_rag_retrieve(query, db, max_results=5)
                results["rag"] = rag_results
            except Exception as e:
                results["rag"] = {"error": str(e)}
        
        # SERP検索
        if "serp" in search_types and serp_system:
            try:
                serp_results = serp_system.search(query, ['repair_info', 'parts_price', 'general_info'])
                results["serp"] = serp_results
            except Exception as e:
                results["serp"] = {"error": str(e)}
        
        # カテゴリ検索
        if "categories" in search_types and category_manager:
            try:
                category = category_manager.identify_category(query)
                if category:
                    category_info = {
                        "category": category,
                        "icon": category_manager.get_category_icon(category),
                        "repair_costs": category_manager.get_repair_costs(category),
                        "repair_steps": category_manager.get_repair_steps_from_json(category),
                        "warnings": category_manager.get_warnings_from_json(category)
                    }
                    results["categories"] = category_info
            except Exception as e:
                results["categories"] = {"error": str(e)}
        
        return jsonify({
            "query": query,
            "results": results,
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
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
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
                "openai_api_key": f"{openai_api_key[:10]}...{openai_api_key[-4:] if openai_api_key and len(openai_api_key) > 14 else ''}" if openai_api_key else None
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
            "repair_cases_available": len(load_notion_repair_cases()) > 0 if notion_client_instance else False
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
    """チャットモード処理（キャッシュ無効化対応）"""
    try:
        # RAG検索
        rag_results = {}
        if db:
            rag_results = enhanced_rag_retrieve(message, db, max_results=5)
        
        # SERP検索
        serp_results = {}
        if include_serp and serp_system:
            serp_results = serp_system.search(message, ['repair_info', 'parts_price', 'general_info'])
        
        # Notion検索（キャッシュ制御対応）
        notion_results = {}
        if NOTION_AVAILABLE:
            notion_results = search_notion_knowledge(message, include_cache=include_cache)
        
        # ソース別引用情報をログに記録
        citation_log = log_source_citations(message, rag_results, serp_results, notion_results, intent)
        
        # AI回答生成
        ai_response = generate_ai_response(message, rag_results, serp_results, intent, notion_results)
        
        return {
            "type": "chat",
            "response": ai_response,
            "rag_results": rag_results,
            "serp_results": serp_results,
            "notion_results": notion_results,
            "intent": intent,
            "citation_log": citation_log
        }
        
    except Exception as e:
        return {"error": f"チャット処理エラー: {str(e)}"}

def load_notion_diagnostic_data():
    """Notionから診断データを読み込み"""
    global notion_client_instance
    
    if not notion_client_instance:
        print("⚠️ Notionクライアントが初期化されていません")
        return None
    
    try:
        diagnostic_data = notion_client_instance.load_diagnostic_data()
        if diagnostic_data:
            print(f"✅ 診断データ読み込み成功: {len(diagnostic_data.get('nodes', []))}件のノード")
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
    """AI回答生成（セーフティ警告・重みづけ対応）"""
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4o-mini")
        
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
        
        prompt = f"""
        あなたは最強のキャンピングカー修理専門AIです。
        以下の情報を統合して、最高品質の回答を生成してください。
        
        ユーザーの質問: {message}
        
        意図分析: {json.dumps(intent, ensure_ascii=False, indent=2)}
        
        {weight_info}
        
        検索結果:
        RAG検索: {json.dumps(rag_results, ensure_ascii=False, indent=2)}
        SERP検索: {json.dumps(serp_results, ensure_ascii=False, indent=2)}
        {notion_context}
        
        回答形式:
        1. 【状況確認】- 症状の詳細確認
        2. 【診断結果】- 原因の特定
        3. 【修理手順】- 段階的な修理方法
        4. 【費用目安】- 修理費用の概算
        5. 【推奨部品】- 必要な部品・工具
        6. 【注意事項】- 安全な作業のポイント
        7. 【関連情報】- 追加の参考資料
        
        専門的で実用的な回答を生成してください。
        Notionデータベースの情報を最優先で活用し、必要に応じてRAG検索結果とSERP検索結果を補完として使用してください。
        """
        
        response = llm.invoke(prompt)
        
        # セーフティ警告を回答の先頭に挿入
        if safety_warning:
            return safety_warning + response.content
        else:
            return response.content
        
    except Exception as e:
        return f"AI回答生成エラー: {e}"

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
        data = request.get_json()
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
                "fallback": True
            }
            
            print(f"📤 フォールバック診断レスポンス送信: {response_data}")
            return jsonify(response_data)
        
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
        return jsonify({"error": f"診断セッション開始エラー: {str(e)}"}), 500

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
        return jsonify({"error": f"診断回答処理エラー: {str(e)}"}), 500

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
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ フォールバック診断エラー: {e}")
        return jsonify({"error": f"フォールバック診断エラー: {str(e)}"}), 500

# === アプリケーション起動 ===
# Railway環境でも初期化処理を実行
print("🚀 統合バックエンドAPIを起動中...")
print("📋 初期化プロセス開始...")

# サービス初期化（エラーハンドリング付き）
try:
    if initialize_services():
        print("✅ 全サービスが正常に初期化されました")
        print("🌐 アクセスURL: http://localhost:5002")
        print("📚 API ドキュメント: http://localhost:5002/api/unified/health")
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
        print("📚 API ドキュメント: http://localhost:5002/api/unified/health")
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
