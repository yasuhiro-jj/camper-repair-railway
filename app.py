from flask import Flask, render_template, request, jsonify, g, session
from flask_cors import CORS
from typing import Literal
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph, MessagesState
# from langgraph.prebuilt import tools_condition  # 一時的にコメントアウト
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma

import os
import uuid

# 設定ファイルをインポート
from config import OPENAI_API_KEY, SERP_API_KEY, LANGSMITH_API_KEY

# デバッグ: APIキーの確認
print(f"DEBUG: OPENAI_API_KEY = {OPENAI_API_KEY[:20]}..." if OPENAI_API_KEY else "DEBUG: OPENAI_API_KEY = None")
print(f"DEBUG: SERP_API_KEY = {SERP_API_KEY[:20]}..." if SERP_API_KEY else "DEBUG: SERP_API_KEY = None")

# LangSmith設定（APIキーが設定されている場合のみ）
if LANGSMITH_API_KEY:
    import os
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

# === Flask アプリケーションの設定 ===
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # セッション管理用

# CORS設定を追加
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3005'])

# グローバルエラーハンドラー
@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    print(f"グローバルエラー: {str(e)}")
    print(f"詳細: {traceback.format_exc()}")
    return jsonify({
        "error": "Internal Server Error",
        "message": str(e)
    }), 500

# 会話履歴を保存する辞書
conversation_history = {}

# === 拡張RAGシステムのセットアップ ===
from enhanced_rag_system import create_enhanced_rag_system, enhanced_rag_retrieve, format_blog_links

# 拡張RAGシステムを作成（ブログURLも含む）
try:
    db = create_enhanced_rag_system()
    print("RAGシステムが正常に初期化されました")
except Exception as e:
    print(f"RAGシステム初期化エラー: {e}")
    print("テキスト検索のみで動作します")
    db = None

# OpenAIの埋め込みモデルを設定
embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# === キャンピングカー修理専用プロンプトテンプレート ===
template = """
あなたはキャンピングカーの修理専門家です。提供された文書抜粋とツールを活用して質問に答えてください。

【重要】必ず以下の手順を実行してください：
1. まず"search_blog_articles"ツールを使用して関連ブログ記事を検索してください
2. その後、提供された文書抜粋を参照して回答してください

利用可能なツール：
- "search_blog_articles"ツール：関連ブログ記事を検索（エアコン、バッテリー、修理方法など）
- "search_ff_heater_products"ツール：FFヒーターの商品データと価格情報を検索
- "search"ツール：一般的な修理情報を検索

文書抜粋：{document_snippet}

質問：{question}

以下の形式で自然な会話の流れで回答してください：

【状況確認】
まず、{question}について詳しくお聞かせください。どのような症状が現れていますか？

【修理アドバイス】
• 最初の対処法（具体的な手順）
• 次の手順（段階的なアプローチ）
• 注意点（安全に作業するためのポイント）
• 必要な工具・部品（準備すべきもの）

【追加の質問】
他に気になる症状や、この対処法で解決しない場合は、以下の点について教えてください：
• エンジンの状態はどうですか？
• 電気系統に異常はありますか？
• 最近のメンテナンス状況は？

【次のステップ】
この対処法を試してみて、結果を教えてください。うまくいかない場合は、別のアプローチをご提案します。

💬 追加の質問
文章が途中で切れる場合がありますので、必要に応じてもう一度お聞きください。

他に何かご質問ありましたら、引き続きチャットボットに聞いてみてください。

📞 お問い合わせ
直接スタッフにお尋ねをご希望の方は、岡山キャンピングカー修理サポートセンターまでご連絡ください。

【岡山キャンピングカー修理サポートセンター】
・電話番号：086-206-6622
・ホームページ：https://camper-repair.net/blog/
・営業時間：平日 9:00〜18:00 | 土日祝 10:00〜17:00
・緊急時は24時間対応（要相談）

対応サービス：
- キャンピングカーの修理・メンテナンス
- トイレ関連のトラブル対応
- 水回り設備の設置・交換
- 診断・見積り（無料）
- 即日対応可能

🔗 関連ブログ
より詳しい情報は修理ブログ一覧をご覧ください。

【必須】エアコン、バッテリー、修理方法などの質問には、必ず最初に"search_blog_articles"ツールを使用して関連ブログ記事を検索してください。

答え：
"""

# === 高度なSERP検索システムの統合 ===
from serp_search_system import get_serp_search_system

# === ツールの設定 ===
@tool
def search(query: str):
    """キャンピングカー修理に関するリアルタイム情報を検索します。"""
    try:
        # 高度なSERP検索システムを使用
        serp_system = get_serp_search_system()
        search_results = serp_system.search(query, ['repair_info', 'parts_price', 'general_info'])
        
        if search_results and 'results' in search_results and search_results['results']:
            # 実際の検索結果をフォーマット
            formatted_results = []
            
            # 意図分析の表示
            if 'intent_analysis' in search_results:
                intent = search_results['intent_analysis']
                formatted_results.append(f"🔍 検索意図: {intent['type']} (信頼度: {intent['confidence']:.1f})")
            
            # 検索結果の表示（上位5件）
            for i, result in enumerate(search_results['results'][:5]):
                title = result.get('title', 'N/A')
                url = result.get('url', '')
                snippet = result.get('snippet', '')
                relevance = result.get('relevance_score', 0)
                
                # 価格情報がある場合
                price_info = result.get('price_info', {})
                price_text = ""
                if price_info.get('price'):
                    price_text = f" 💰 {price_info['price']}円"
                
                formatted_results.append(
                    f"📄 {i+1}. {title[:60]}...{price_text}\n"
                    f"   🔗 {url}\n"
                    f"   📝 {snippet[:100]}...\n"
                    f"   📊 関連度: {relevance:.2f}"
                )
            
            # 使用された検索エンジンの表示
            if 'search_engines_used' in search_results:
                engines = ', '.join(search_results['search_engines_used'])
                formatted_results.append(f"🌐 使用検索エンジン: {engines}")
            
            g.search_results = formatted_results
            return formatted_results
        else:
            # フォールバック: 基本的な検索リンク
            fallback_results = [
                f"🔍 検索結果が見つかりませんでした。以下のリンクをご参考ください:",
                f"📱 Google検索: キャンピングカー {query} 修理方法",
                f"🎥 YouTube動画: キャンピングカー {query} 修理手順",
                f"🛒 Amazon商品: キャンピングカー修理部品",
                f"📚 専門サイト: キャンピングカー修理専門情報"
            ]
            g.search_results = fallback_results
            return fallback_results
            
    except Exception as e:
        # エラー時のフォールバック
        error_results = [
            f"⚠️ 検索エラーが発生しました: {str(e)}",
            f"📱 Google検索: キャンピングカー {query} 修理方法",
            f"🎥 YouTube動画: キャンピングカー {query} 修理手順",
            f"🛒 Amazon商品: キャンピングカー修理部品",
            f"📚 専門サイト: キャンピングカー修理専門情報"
        ]
        g.search_results = error_results
        return error_results

@tool
def search_realtime_info(query: str):
    """リアルタイム修理情報を検索します。"""
    try:
        serp_system = get_serp_search_system()
        results = serp_system.get_realtime_repair_info(query)
        
        if results and 'results' in results and results['results']:
            formatted_results = ["🔧 リアルタイム修理情報:"]
            for i, result in enumerate(results['results'][:3]):
                title = result.get('title', 'N/A')
                url = result.get('url', '')
                formatted_results.append(f"📄 {i+1}. {title[:80]}...")
                formatted_results.append(f"   🔗 {url}")
            return formatted_results
        else:
            return [f"リアルタイム情報が見つかりませんでした: {query}"]
    except Exception as e:
        return [f"リアルタイム検索エラー: {str(e)}"]

@tool
def search_parts_price(query: str):
    """部品価格情報を検索します。"""
    try:
        serp_system = get_serp_search_system()
        results = serp_system.get_parts_price_info(query)
        
        if results and 'results' in results and results['results']:
            formatted_results = ["💰 部品価格情報:"]
            for i, result in enumerate(results['results'][:3]):
                title = result.get('title', 'N/A')
                url = result.get('url', '')
                price_info = result.get('price_info', {})
                price_text = f" - {price_info.get('price', 'N/A')}円" if price_info.get('price') else ""
                formatted_results.append(f"🛒 {i+1}. {title[:60]}...{price_text}")
                formatted_results.append(f"   🔗 {url}")
            return formatted_results
        else:
            return [f"価格情報が見つかりませんでした: {query}"]
    except Exception as e:
        return [f"価格検索エラー: {str(e)}"]

@tool
def search_blog_articles(query: str):
    """関連ブログ記事を検索します。"""
    try:
        # test_rag.pyから関数をインポート
        from test_rag import get_relevant_blog_links
        
        # 関連ブログ記事を取得
        relevant_blogs = get_relevant_blog_links(query)
        
        if relevant_blogs:
            formatted_results = ["📚 関連ブログ記事:"]
            for i, blog in enumerate(relevant_blogs, 1):
                formatted_results.append(f"🔗 {i}. {blog['title']}")
                formatted_results.append(f"   URL: {blog['url']}")
            return formatted_results
        else:
            return [f"関連ブログ記事が見つかりませんでした: {query}"]
    except Exception as e:
        return [f"ブログ記事検索エラー: {str(e)}"]

@tool
def search_ff_heater_products(query: str):
    """FFヒーターの商品データと価格情報を検索します。"""
    try:
        # FFヒーター関連のキーワードをチェック
        ff_keywords = ["ffヒーター", "ff", "ヒーター", "暖房", "エバスポッチャー", "ベバスト", "ミクニ", "lvyuan", "交換", "本体", "価格", "費用"]
        query_lower = query.lower()
        
        if not any(keyword in query_lower for keyword in ff_keywords):
            return [f"FFヒーター関連の検索ではありません: {query}"]
        
        # FFヒーター商品データを返す
        product_data = [
            "🔥 FFヒーター商品データ・価格情報",
            "",
            "【主要メーカー・製品一覧】",
            "",
            "【ベバスト（Eberspächer）】",
            "• エアトロニック D2：約15万円（2kW、12V）",
            "• エアトロニック D4：約18万円（4kW、12V）",
            "• エアトロニック D5：約22万円（5kW、12V）",
            "• エアトロニック D8：約28万円（8kW、12V）",
            "",
            "【ミクニ（Mikuni）】",
            "• MY-22：約12万円（2.2kW、12V）",
            "• MY-34：約15万円（3.4kW、12V）",
            "• MY-44：約18万円（4.4kW、12V）",
            "• MY-66：約25万円（6.6kW、12V）",
            "",
            "【LVYUAN（中国製）】",
            "• LVYUAN 2kW：約6万円（2kW、12V）",
            "• LVYUAN 3kW：約8万円（3kW、12V）",
            "• LVYUAN 5kW：約12万円（5kW、12V）",
            "",
            "【交換費用目安】",
            "• 小型車（2-3kW）：工賃 3-5万円",
            "• 中型車（4-5kW）：工賃 5-8万円",
            "• 大型車（6-8kW）：工賃 8-12万円",
            "",
            "【おすすめ商品（2024年最新）】",
            "• コストパフォーマンス重視：LVYUAN 3kW（本体8万円 + 工賃5万円 = 総額13万円）",
            "• 高品質・長期使用重視：ベバスト D4（本体18万円 + 工賃6万円 = 総額24万円）",
            "• 大型車・高性能：ベバスト D8（本体28万円 + 工賃10万円 = 総額38万円）"
        ]
        
        return product_data
        
    except Exception as e:
        return [f"FFヒーター商品検索エラー: {str(e)}"]

tools = [search, search_realtime_info, search_parts_price, search_blog_articles, search_ff_heater_products]

# === モデルのセットアップ ===
model = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4o-mini").bind_tools(tools)

# === 条件判定 ===
def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"
    
    return END

# === モデルの応答生成関数 ===
def call_model(state: MessagesState):
    messages = state['messages']
    try:
        response = model.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        # エラーが発生した場合のフォールバック
        from langchain_core.messages import AIMessage
        error_message = f"申し訳ございませんが、エラーが発生しました: {str(e)}"
        return {"messages": [AIMessage(content=error_message)]}

# === ツール実行関数 ===
def call_tools(state: MessagesState):
    messages = state['messages']
    last_message = messages[-1]
    
    # ツールを実行
    tool_calls = last_message.tool_calls
    results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        if tool_name == 'search':
            result = search.invoke(tool_args)
            results.append(result)
        elif tool_name == 'search_realtime_info':
            result = search_realtime_info.invoke(tool_args)
            results.append(result)
        elif tool_name == 'search_parts_price':
            result = search_parts_price.invoke(tool_args)
            results.append(result)
        elif tool_name == 'search_blog_articles':
            result = search_blog_articles.invoke(tool_args)
            results.append(result)
            
            # ブログ記事検索結果をg.blog_linksに保存
            try:
                from test_rag import get_relevant_blog_links
                blog_links = get_relevant_blog_links(tool_args['query'])
                g.blog_links = blog_links
                print(f"DEBUG: ブログ記事検索実行 - クエリ: {tool_args['query']}")
                print(f"DEBUG: 検索結果: {len(blog_links)}件")
                for blog in blog_links:
                    print(f"DEBUG: - {blog['title']}")
            except Exception as e:
                print(f"ブログ記事取得エラー: {e}")
                g.blog_links = []
        elif tool_name == 'search_ff_heater_products':
            result = search_ff_heater_products.invoke(tool_args)
            results.append(result)
            print(f"DEBUG: FFヒーター商品検索実行 - クエリ: {tool_args['query']}")
            print(f"DEBUG: 検索結果: {len(result)}行")
    
    # ツール実行結果をメッセージに追加
    from langchain_core.messages import ToolMessage
    tool_messages = []
    for i, result in enumerate(results):
        tool_messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_calls[i]['id']
        ))
    
    return {"messages": tool_messages}

# === 拡張RAG用ロジック ===
def rag_retrieve(question: str):
    # 拡張RAGシステムを使用してブログURLも含めて検索
    results = enhanced_rag_retrieve(question, db, max_results=5)
    
    # マニュアル内容とブログリンクを組み合わせ
    manual_content = results["manual_content"]
    blog_links = results["blog_links"]
    
    # グローバル変数にブログリンクを保存（後で使用）
    g.blog_links = blog_links
    
    # マニュアル内容のみを返す（ブログリンクは後でAIの回答内に組み込む）
    return manual_content

# === ワークフローの構築 ===
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tools)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", 'agent')
checkpointer = MemorySaver()
app_flow = workflow.compile(checkpointer=checkpointer)

# === メッセージの前処理 ===
def preprocess_message(question: str, conversation_id: str):
    document_snippet = rag_retrieve(question)
    content = template.format(document_snippet=document_snippet, question=question)
    
    # 会話履歴を取得
    history = conversation_history.get(conversation_id, [])
    
    # 新しいメッセージを追加
    messages = history + [HumanMessage(content=content)]
    
    return messages

# === Flaskルート設定 ===
@app.route("/")
def index():
    # セッションに会話IDがなければ生成
    if 'conversation_id' not in session:
        session['conversation_id'] = str(uuid.uuid4())
    return render_template("index.html")

@app.route("/start_conversation", methods=["POST"])
def start_conversation():
    """新しい会話を開始"""
    conversation_id = str(uuid.uuid4())
    session['conversation_id'] = conversation_id
    conversation_history[conversation_id] = []
    return jsonify({"conversation_id": conversation_id})

@app.route("/ask", methods=["POST"])
def ask():
    try:
        question = request.form["question"]
        conversation_id = session.get('conversation_id', str(uuid.uuid4()))
        g.search_results = []
        
        inputs = preprocess_message(question, conversation_id)
        thread = {"configurable": {"thread_id": conversation_id}}

        response = ""
        for event in app_flow.stream({"messages": inputs}, thread, stream_mode="values"):
            if "messages" in event and event["messages"]:
                response = event["messages"][-1].content

        # ブログリンクを取得
        blog_links = getattr(g, "blog_links", [])
        
        # ブログリンクが取得できていない場合は、直接検索を実行
        if not blog_links:
            try:
                from test_rag import get_relevant_blog_links
                blog_links = get_relevant_blog_links(question)
                g.blog_links = blog_links
                print(f"DEBUG: フォールバック検索実行 - クエリ: {question}")
                print(f"DEBUG: 検索結果: {len(blog_links)}件")
            except Exception as e:
                print(f"フォールバック検索エラー: {e}")
                blog_links = []
        
        # AIの回答に直接関連ブログを組み込む
        if blog_links:
            blog_section = "\n\n🔗 関連ブログ\n"
            for blog in blog_links[:3]:  # 最大3件
                blog_section += f"• {blog['title']}: {blog['url']}\n"
            response += blog_section
        else:
            # デフォルトの関連ブログセクション
            response += "\n\n🔗 関連ブログ\n"
            response += "• バッテリー・バッテリーの故障と修理方法: https://camper-repair.net/blog/repair1/\n"
            response += "• 基本修理・キャンピングカー修理の基本: https://camper-repair.net/blog/risk1/\n"
            response += "• 定期点検・定期点検とメンテナンス: https://camper-repair.net/battery-selection/\n"

        # 会話履歴を更新
        if conversation_id not in conversation_history:
            conversation_history[conversation_id] = []
        
        # ユーザーの質問とAIの回答を履歴に追加
        conversation_history[conversation_id].extend([
            HumanMessage(content=question),
            AIMessage(content=response)
        ])

        return jsonify({
            "answer": response, 
            "links": "",  # 空文字列（関連ブログは回答内に組み込まれている）
            "blog_links": blog_links[:3] if blog_links else []
        })
    
    except Exception as e:
        import traceback
        error_message = f"エラーが発生しました: {str(e)}"
        print(f"詳細エラー: {traceback.format_exc()}")
        return jsonify({
            "answer": error_message, 
            "links": "エラーによりリンクを取得できませんでした",
            "blog_links": []
        }), 500

@app.route("/repair_advice_center.html")
def repair_advice_center():
    """修理アドバイスセンターのHTMLページ"""
    return render_template("repair_advice_center.html")

@app.route("/unified_chatbot.html")
def unified_chatbot():
    """統合チャットボットのHTMLページ"""
    return render_template("unified_chatbot.html")

@app.route("/api/health")
def health_check():
    """ヘルスチェック"""
    return jsonify({
        "status": "healthy",
        "rag_available": db is not None,
        "openai_available": OPENAI_API_KEY is not None
    })

@app.route("/api/repair_costs", methods=["GET"])
def get_repair_costs():
    """修理費用データベースのJSONデータを返す"""
    try:
        import json
        
        # JSONファイルを読み込み
        with open('repair_costs_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "修理費用データベースが見つかりません"}), 404
    except Exception as e:
        return jsonify({"error": f"データベース読み込みエラー: {str(e)}"}), 500

@app.route("/api/search", methods=["POST"])
def search_repair_advice():
    """修理アドバイス検索API（HTML用）"""
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
        if db:
            try:
                rag_results = enhanced_rag_retrieve(query, db, max_results=5)
                print(f"✅ RAG検索完了")
                print(f"📊 検索結果詳細:")
                print(f"  - manual_content: {len(rag_results.get('manual_content', ''))}文字")
                print(f"  - text_file_content: {len(rag_results.get('text_file_content', ''))}文字")
                print(f"  - blog_links: {len(rag_results.get('blog_links', []))}件")
                
                # テキストファイル内容のデバッグ
                if rag_results.get('text_file_content'):
                    content = rag_results['text_file_content']
                    print(f"📄 テキストファイル内容（最初の200文字）: {content[:200]}...")
                    
                    # 費用目安情報の抽出テスト（カテゴリーマネージャーを使用）
                    if category_manager:
                        cost_info = category_manager.extract_section_from_content(content, "cost_section")
                        if cost_info:
                            print(f"💰 費用目安情報抽出成功: {cost_info[:100]}...")
                        else:
                            print("❌ 費用目安情報の抽出に失敗")
                else:
                    print("❌ テキストファイル内容が取得できませんでした")
            except Exception as e:
                print(f"❌ RAG検索エラー: {e}")
        
        # 結果をフォーマット
        advice = format_repair_advice_for_html(rag_results, query)
        
        return jsonify(advice)
        
    except Exception as e:
        print(f"❌ API エラー: {e}")
        return jsonify({
            "success": False,
            "error": f"検索中にエラーが発生しました: {str(e)}"
        })

@app.route("/api/search_text_files", methods=["POST"])
def search_text_files_api():
    """テキストファイル検索API（HTML用）"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                "success": False,
                "error": "検索クエリが空です"
            })
        
        print(f"📄 テキストファイル検索クエリ: {query}")
        
        # テキストファイル検索
        from enhanced_knowledge_base_app import search_text_files
        results = search_text_files(query)
        
        if results:
            print(f"✅ テキストファイル検索成功: {len(results)}件")
            return jsonify({
                "success": True,
                "results": results,
                "query": query,
                "source": "text_files"
            })
        else:
            print("⚠️ テキストファイル検索結果なし")
            return jsonify({
                "success": False,
                "error": "該当するテキストファイルが見つかりませんでした",
                "query": query,
                "source": "text_files"
            })
        
    except Exception as e:
        print(f"❌ テキストファイル検索エラー: {e}")
        return jsonify({
            "success": False,
            "error": f"テキストファイル検索中にエラーが発生しました: {str(e)}",
            "query": query,
            "source": "text_files"
        })

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """カテゴリ定義を返すAPI（HTML用）"""
    try:
        print("📋 カテゴリ定義API呼び出し")
        
        # カテゴリーマネージャーから全カテゴリ情報を取得
        categories = category_manager.get_all_categories()
        
        if categories:
            print(f"✅ カテゴリ定義取得成功: {len(categories)}件")
            return jsonify({
                "success": True,
                "categories": categories,
                "source": "category_definitions"
            })
        else:
            print("⚠️ カテゴリ定義が取得できませんでした")
            return jsonify({
                "success": False,
                "error": "カテゴリ定義が見つかりませんでした",
                "source": "category_definitions"
            })
        
    except Exception as e:
        print(f"❌ カテゴリ定義取得エラー: {e}")
        return jsonify({
            "success": False,
            "error": f"カテゴリ定義取得中にエラーが発生しました: {str(e)}",
            "source": "category_definitions"
        })

# === 新しいデータ駆動型カテゴリーマネージャー ===
from repair_category_manager import RepairCategoryManager

# カテゴリーマネージャーを初期化
category_manager = RepairCategoryManager()

def format_repair_advice_for_html(rag_results, query):
    """HTML用に修理アドバイスをフォーマット（データ駆動型）"""
    advice = {
        "query": query,
        "success": True,
        "results": []
    }

    print(f"🔍 データ駆動型クエリ分析開始: {query}")
    
    # カテゴリー特定
    category = category_manager.identify_category(query)
    
    if category:
        print(f"✅ {category}関連と判定されました")
        icon = category_manager.get_category_icon(category)
        
        # 修理費用目安を取得
        repair_costs = category_manager.get_repair_costs(category)
        if repair_costs:
            advice["results"].append({
                "title": f"{icon} {category}修理費用目安",
                "category": f"{category}修理費用",
                "content": repair_costs,
                "repair_costs": repair_costs,
                "costs": repair_costs,
                "source": f"{category.lower()}_direct",
                "relevance": "high"
            })

        # 修理手順の取得（JSONファイルを優先）
        repair_steps = None
        repair_steps_source = ""
        
        # まずJSONファイルから取得を試行
        json_steps = category_manager.get_repair_steps_from_json(category)
        if json_steps:
            repair_steps = json_steps
            repair_steps_source = "json"
            print(f"✅ JSONから修理手順を取得: {len(json_steps)}文字")
        else:
            # 専用ファイルから取得を試行
            repair_steps_content = category_manager.get_content_from_file(category, "repair_steps")
            if repair_steps_content:
                repair_steps = category_manager.extract_section_from_content(
                    repair_steps_content, "repair_steps_section")
                if repair_steps:
                    repair_steps_source = "file"
                    print(f"✅ 専用ファイルから修理手順を取得: {len(repair_steps)}文字")
        
        # 修理手順と注意事項の取得
        steps_array = []
        warnings_array = []
        
        # 修理手順の取得（JSONファイルを優先）
        if repair_steps:
            steps_array = [step.strip() for step in repair_steps.split('\n') if step.strip()]
            print(f"✅ 修理手順を取得: {len(steps_array)}件")
        else:
            print("❌ 修理手順の取得に失敗")

        # 注意事項の取得（JSONファイルを優先）
        warnings = None
        warnings_source = ""
        
        # まずJSONファイルから取得を試行
        json_warnings = category_manager.get_warnings_from_json(category)
        if json_warnings:
            warnings = json_warnings
            warnings_source = "json"
            warnings_array = [w.strip() for w in warnings.split('\n') if w.strip()]
            print(f"✅ JSONから注意事項を取得: {len(warnings_array)}件")
        else:
            # 専用ファイルから取得を試行
            warnings_content = category_manager.get_content_from_file(category, "warnings")
            if warnings_content:
                warnings = category_manager.extract_section_from_content(
                    warnings_content, "warnings_section")
                if warnings:
                    warnings_source = "file"
                    warnings_array = [w.strip() for w in warnings.split('\n') if w.strip()]
                    print(f"✅ 専用ファイルから注意事項を取得: {len(warnings_array)}件")

        # 統合された結果を追加（修理手順と注意事項を含む）
        if steps_array or warnings_array or repair_costs:
            title = f"🔧 {category}修理アドバイス"
            advice["results"].append({
                "title": title,
                "category": category,
                "content": f"{category}の修理に関する詳細情報",
                "repair_steps": steps_array,
                "warnings": warnings_array,
                "costs": repair_costs,
                "source": f"{category.lower()}_comprehensive",
                "relevance": "high"
            })
            print(f"✅ 統合された修理アドバイスを追加: 手順{len(steps_array)}件, 注意事項{len(warnings_array)}件")

    # RAGからの情報抽出（既存のロジックを維持）
    if rag_results:
        content = rag_results.get("text_file_content", "")
        if content.strip() and category:
            cost_info = category_manager.extract_section_from_content(content, "cost_section")
            if cost_info:
                advice["results"].append({
                    "title": "💰 修理費用目安（ファイルから抽出）",
                    "category": "費用情報",
                    "content": cost_info,
                    "repair_costs": cost_info,
                    "costs": cost_info,
                    "source": "cost_info",
                    "relevance": "high"
                })

        # マニュアル情報とブログリンク（既存のロジックを維持）
        manual = rag_results.get("manual_content", "")
        if manual.strip():
            advice["results"].append({
                "title": "📖 修理マニュアルからの情報",
                "category": "マニュアル",
                "content": manual[:1000] + "..." if len(manual) > 1000 else manual,
                "source": "manual",
                "relevance": "high"
            })

        blog_links = rag_results.get("blog_links", [])[:3]
        if blog_links:
            blog_content = "関連ブログ記事:\n" + "\n".join(
                [f"• {b['title']}: {b['url']}" for b in blog_links])
            advice["results"].append({
                "title": "🔗 関連ブログ記事",
                "category": "ブログ",
                "content": blog_content,
                "source": "blog",
                "relevance": "medium"
            })

    # 結果がなければフォールバック
    if not advice["results"]:
        repair_center = category_manager.get_repair_center_info()
        fallback_content = f"""
「{query}」に関する情報が見つかりませんでした。

以下の方法で情報を探してみてください：

1. 別のキーワードで検索（より具体的な症状・部品名・問題内容）
2. 推奨キーワード:
   - バッテリー、充電、電圧
   - トイレ、水、ポンプ
   - エアコン、冷房、暖房
   - 雨漏り、水漏れ、シーリング
3. 専門店への相談:
   - {repair_center.get('name', 'キャンピングカー修理専門店')}
   - 電話: {repair_center.get('phone', 'お問い合わせください')}
   - 営業時間: {repair_center.get('hours', '営業時間にお問い合わせください')}
        """.strip()

        advice["results"].append({
            "title": "❌ 該当する情報が見つかりませんでした",
            "category": "エラー",
            "content": fallback_content,
            "source": "fallback",
            "relevance": "low"
        })

    return advice

# === Flaskの起動 ===
if __name__ == "__main__":
    print("🚀 Flaskアプリケーションを起動中...")
    print("🌐 アクセスURL: http://localhost:5001")
    print("💡 検索機能テスト: http://localhost:5001/repair_advice_center.html")
    app.run(debug=True, host='127.0.0.1', port=5001, threaded=True)