from flask import Flask, render_template, request, jsonify, g, session, redirect
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
import logging

# ロギング設定
logger = logging.getLogger(__name__)

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

【重要】以下のルールに従って、必ず箇条書き形式で回答してください：

1. 出力は必ず「箇条書き（●または-）」で表現する
2. 長い文章は短く分割して1項目＝1行にまとめる
3. セクションごとに見出し（##）をつける
4. 強調は **太字** のみに限定し、絵文字は最小限にする
5. 不要な繰り返しや「Case番号」は省略する

【回答形式】

## よくある原因
- [原因1]
- [原因2]
- [原因3]
- [原因4]
- [原因5]

## 対処法
### 原因1の場合
- [手順1]
- [手順2]
- 費用目安：[金額]

### 原因2の場合
- [手順1]
- [手順2]
- 費用目安：[金額]

## 修理費用の目安
- 診断料：3,000円〜5,000円
- [部品名]交換：XX円〜XX円
- [作業名]：XX円〜XX円

## 必要な工具・部品
- [工具1]
- [工具2]
- [部品1]
- [部品2]

## 注意事項
- 作業前に必ず電源を切る
- [安全対策1]
- [安全対策2]
- 専門知識が必要な場合は専門店に相談

## 追加の確認事項
- 他に気になる症状はありますか？
- 最近のメンテナンス状況は？
- この対処法を試してみて、結果を教えてください

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

# === 拡張RAG用ロジック（Phase 3対応） ===
def rag_retrieve(question: str, return_scores: bool = False):
    """
    RAG検索（Phase 3対応：スコア返却オプション）
    
    Args:
        question: 検索クエリ
        return_scores: スコアも返すか
    
    Returns:
        str or Tuple[str, float]: マニュアル内容（スコア含む場合はタプル）
    """
    # chroma_managerを使用（Phase 3対応）
    try:
        from data_access.chroma_manager import get_chroma_manager
        chroma_manager = get_chroma_manager()
        
        if chroma_manager.db:
            results = chroma_manager.search(question, max_results=5)
            
            # スコアをグローバル変数に保存
            if results.get("scores"):
                g.rag_scores = results["scores"]
                g.rag_avg_score = sum(results["scores"]) / len(results["scores"]) if results["scores"] else 0.0
            else:
                g.rag_scores = []
                g.rag_avg_score = 0.0
            
            # ブログリンクを保存
            g.blog_links = results.get("blog_links", [])
            
            # マニュアル内容を返す
            manual_content = results.get("manual_content", "")
            return manual_content
    except Exception as e:
        print(f"⚠️ chroma_manager使用エラー（フォールバック）: {e}")
    
    # フォールバック: 既存のenhanced_rag_systemを使用
    results = enhanced_rag_retrieve(question, db, max_results=5)
    
    # マニュアル内容とブログリンクを組み合わせ
    manual_content = results["manual_content"]
    blog_links = results["blog_links"]
    
    # グローバル変数にブログリンクを保存（後で使用）
    g.blog_links = blog_links
    g.rag_scores = []
    g.rag_avg_score = 0.0
    
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

        # Notionログ保存処理を追加
        notion_saved = False
        notion_error = None
        try:
            from save_to_notion import save_chat_log_to_notion
            
            # 意図分析（IntentClassifierを使用）
            category = None
            confidence_score = 0.5
            confidence_level = "medium"
            intent_keywords = []
            try:
                from data_access.intent_classifier import IntentClassifier, get_confidence_level
                intent_classifier = IntentClassifier()
                intent_result = intent_classifier.classify(question)
                category = intent_result.get("category")
                confidence_score = intent_result.get("confidence", 0.5)
                confidence_level = get_confidence_level(confidence_score)
                intent_keywords = intent_result.get("keywords", [])
            except Exception as e:
                print(f"⚠️ 意図分類エラー（フォールバック）: {e}")
                # 簡易的なキーワード抽出
                import re
                japanese_words = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', question)
                intent_keywords = [w for w in japanese_words if len(w) >= 2][:5]
            
            # ツール使用情報の検出
            tool_used = "推論"  # デフォルト
            if blog_links:
                tool_used = "RAG"  # ブログリンクが取得された場合はRAGを使用
            
            # RAGスコアの取得（利用可能な場合）
            rag_avg_score = getattr(g, "rag_avg_score", 0.0)
            
            # キーワードの確定
            keywords = intent_keywords if intent_keywords else []
            if not keywords:
                import re
                japanese_words = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', question)
                keywords = [w for w in japanese_words if len(w) >= 2][:5]
            
            # Notionに保存
            saved, error_msg = save_chat_log_to_notion(
                user_msg=question,
                bot_msg=response,
                session_id=conversation_id,
                category=category,
                subcategory=None,
                urgency=None,
                keywords=keywords if keywords else None,
                tool_used=tool_used,
                rag_score=rag_avg_score if rag_avg_score > 0.0 else None,
                confidence=confidence_level,
                confidence_score=confidence_score,
                sources_summary=None
            )
            
            if saved:
                notion_saved = True
                print(f"✅ Notionログ保存成功: session_id={conversation_id}, category={category}, tool={tool_used}")
            else:
                notion_error = error_msg
                print(f"⚠️ Notionログ保存失敗（APIは継続）: {error_msg}")
        except Exception as e:
            notion_error = str(e)
            print(f"⚠️ Notionログ保存例外（APIは継続）: {e}")
            import traceback
            traceback.print_exc()

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

@app.route("/healthz")
def healthz():
    """シンプルなヘルスチェック（ロードマップ準拠）"""
    return jsonify({"status": "ok"}), 200

@app.route("/test_notion_save.html")
def test_notion_save():
    """Notion保存機能のテストページ"""
    try:
        with open("test_notion_save.html", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "テストページが見つかりません", 404

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    ロードマップ準拠のチャットエンドポイント（Phase 3対応）
    会話ログをNotionに100%保存 + 意図分類 & 信頼度付与
    """
    try:
        # リクエストデータの取得（JSON形式を優先、フォームデータにも対応）
        if request.is_json:
            data = request.get_json()
            message = data.get("message", "").strip()
            session_id = data.get("session_id")
        else:
            message = request.form.get("message", "").strip()
            session_id = request.form.get("session_id")
        
        if not message:
            return jsonify({
                "success": False,
                "error": "メッセージが空です"
            }), 400
        
        # セッションIDの確実な付与（ロードマップ準拠）
        if not session_id:
            session_id = session.get('conversation_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                session['conversation_id'] = session_id
        
        # Phase 3: 意図分類（先に実行）
        intent_result = None
        try:
            from data_access.intent_classifier import IntentClassifier, get_confidence_level
            intent_classifier = IntentClassifier()
            intent_result = intent_classifier.classify(message)
            category = intent_result.get("category")
            confidence_score = intent_result.get("confidence", 0.5)
            confidence_level = get_confidence_level(confidence_score)
            intent_keywords = intent_result.get("keywords", [])
        except Exception as e:
            print(f"⚠️ 意図分類エラー（フォールバック）: {e}")
            category = None
            confidence_score = 0.5
            confidence_level = "medium"
            intent_keywords = []
        
        # RAG検索（Phase 3対応：スコア取得）
        g.search_results = []
        g.rag_scores = []
        g.rag_avg_score = 0.0
        
        document_snippet = rag_retrieve(message)
        
        # RAGスコアを取得
        rag_avg_score = getattr(g, "rag_avg_score", 0.0)
        rag_scores = getattr(g, "rag_scores", [])
        
        # プロンプトテンプレートにRAG結果を組み込み
        inputs = preprocess_message(message, session_id)
        thread = {"configurable": {"thread_id": session_id}}
        
        response = ""
        tool_used_list = []
        
        # AI応答生成
        for event in app_flow.stream({"messages": inputs}, thread, stream_mode="values"):
            if "messages" in event and event["messages"]:
                last_message = event["messages"][-1]
                response = last_message.content
                
                # ツール使用の検出
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        tool_used_list.append(tool_call.get('name', 'unknown'))
        
        # ブログリンクを取得
        blog_links = getattr(g, "blog_links", [])
        if not blog_links:
            try:
                from test_rag import get_relevant_blog_links
                blog_links = get_relevant_blog_links(message)
                g.blog_links = blog_links
            except Exception as e:
                print(f"フォールバック検索エラー: {e}")
                blog_links = []
        
        # Phase 3: 返答テンプレート改善（共感リアクション+要点+手順+次アクション）
        # 既存の回答に追加情報を付与
        enhanced_response = response
        
        # 信頼度が低い場合は追加質問を促す
        if confidence_level == "low" and rag_avg_score < 0.5:
            enhanced_response += "\n\n💡 より正確な診断のため、以下の情報を教えていただけますか？\n"
            enhanced_response += "- 症状が発生した時期\n"
            enhanced_response += "- 他に気になる症状はありますか？\n"
            enhanced_response += "- 最近のメンテナンス状況\n"
        
        # ブログリンクを追加
        if blog_links:
            blog_section = "\n\n🔗 関連ブログ\n"
            for blog in blog_links[:3]:
                blog_section += f"• {blog['title']}: {blog['url']}\n"
            enhanced_response += blog_section
        
        # 参照元の要約（Phase 3対応、200文字にトリム）
        sources_summary = ""
        if document_snippet and len(document_snippet) > 50:
            # 200文字にトリム（Notionの指示に従う）
            sources_summary = document_snippet[:200].strip()
        
        # ツール使用情報の確定
        tool_used = None
        if tool_used_list:
            tool_used = "/".join(tool_used_list)
        elif rag_avg_score > 0.0:  # RAGが使用された場合
            tool_used = "RAG"
        else:
            tool_used = "推論"
        
        # 最終的なキーワード（意図分類 + 抽出キーワード）
        keywords = intent_keywords if intent_keywords else []
        if not keywords:
            import re
            japanese_words = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', message)
            keywords = [w for w in japanese_words if len(w) >= 2][:5]
        
        # Notionログ保存（Phase 3対応：スコアと信頼度を含む）
        notion_saved = False
        notion_error = None
        try:
            from save_to_notion import save_chat_log_to_notion
            
            saved, error_msg = save_chat_log_to_notion(
                user_msg=message,
                bot_msg=enhanced_response,
                session_id=session_id,
                category=category,
                subcategory=None,  # Phase 3では未実装
                urgency=None,  # Phase 3では未実装
                keywords=keywords if keywords else None,
                tool_used=tool_used,
                rag_score=rag_avg_score if rag_avg_score > 0.0 else None,  # Phase 3対応
                confidence=confidence_level,  # Phase 3対応（lower case）
                confidence_score=confidence_score,  # Phase 3対応
                sources_summary=sources_summary if sources_summary else None  # Phase 3対応（200文字にトリム済み）
            )
            
            if saved:
                notion_saved = True
                print(f"✅ Notionログ保存成功: session_id={session_id}, category={category}, tool={tool_used}")
            else:
                notion_error = error_msg
                print(f"⚠️ Notionログ保存失敗（APIは継続）: {error_msg}")
        except Exception as e:
            notion_error = str(e)
            print(f"⚠️ Notionログ保存例外（APIは継続）: {e}")
            import traceback
            traceback.print_exc()
        
        # 会話履歴を更新（既存機能維持）
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        conversation_history[session_id].extend([
            HumanMessage(content=message),
            AIMessage(content=enhanced_response)
        ])
        
        # レスポンス（Phase 3対応：信頼度・スコア・参照元を含む）
        return jsonify({
            "success": True,
            "reply": enhanced_response,
            "sources": [blog.get("url", "") for blog in blog_links[:3]] if blog_links else [],
            "score": rag_avg_score,  # Phase 3対応：RAGスコア
            "confidence": confidence_level,  # Phase 3対応：信頼度（low/medium/high）
            "confidence_score": confidence_score,  # Phase 3対応：信頼度スコア（0.0-1.0）
            "category": category,  # Phase 3対応：分類されたカテゴリ
            "sources_summary": sources_summary,  # Phase 3対応：参照元の要約
            "session_id": session_id,
            "notion_saved": notion_saved,
            "notion_error": notion_error if not notion_saved else None
        }), 200
    
    except Exception as e:
        import traceback
        error_message = f"エラーが発生しました: {str(e)}"
        print(f"詳細エラー: {traceback.format_exc()}")
        
        # エラー時でもHTTP 200を返す（ロードマップ準拠：ユーザー影響最小）
        return jsonify({
            "success": False,
            "error": error_message,
            "reply": "申し訳ございませんが、エラーが発生しました。もう一度お試しください。",
            "session_id": session.get('conversation_id', str(uuid.uuid4())),
            "notion_saved": False
        }), 200

@app.route("/api/health")
def health_check():
    """詳細なヘルスチェック（既存機能維持）"""
    return jsonify({
        "status": "healthy",
        "rag_available": db is not None,
        "openai_available": OPENAI_API_KEY is not None
    })

# ============================================
# Phase 4: 工場向けダッシュボード（Flask実装）
# ============================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """パスコード簡易ログイン（Phase 4）"""
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        admin_code = os.getenv("ADMIN_CODE", "change-me")
        
        if code == admin_code:
            session["admin_authenticated"] = True
            return redirect("/admin/dashboard")
        else:
            return render_template("admin_login.html", error="パスコードが正しくありません"), 401
    
    # GET: ログインページ表示
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    """ログアウト"""
    session.pop("admin_authenticated", None)
    return redirect("/admin/login")

@app.route("/admin/dashboard")
def admin_dashboard():
    """工場向けダッシュボード（Phase 4 - チャットログ用）"""
    # 認証チェック
    if not session.get("admin_authenticated"):
        return redirect("/admin/login")
    
    # ステータスフィルタ（クエリパラメータ）
    status_filter = request.args.get("status", "")
    
    # 案件一覧を取得（テンプレート側でJavaScriptで取得する方式）
    return render_template("factory_dashboard.html", status_filter=status_filter)

@app.route("/admin/deals-dashboard")
def deals_dashboard():
    """商談管理用工場ダッシュボード"""
    # 認証チェック
    if not session.get("admin_authenticated"):
        return redirect("/admin/login")
    
    # ステータスフィルタ（クエリパラメータ）
    status_filter = request.args.get("status", "")
    
    return render_template("deals_dashboard.html", status_filter=status_filter)

@app.route("/admin/api/cases", methods=["GET"])
def get_cases_api():
    """案件一覧取得API（Phase 4）"""
    # 認証チェック
    if not session.get("admin_authenticated"):
        return jsonify({"error": "認証が必要です"}), 401
    
    try:
        from data_access.factory_dashboard_manager import FactoryDashboardManager
        
        manager = FactoryDashboardManager()
        
        status = request.args.get("status")  # フィルタ（受付/診断中/修理中/完了/キャンセル）
        limit = int(request.args.get("limit", 100))
        
        cases = manager.get_cases(status=status if status else None, limit=limit)
        
        return jsonify({
            "success": True,
            "cases": cases,
            "count": len(cases)
        })
    
    except Exception as e:
        import traceback
        logger.error(f"❌ 案件取得APIエラー: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/admin/api/update-status", methods=["POST"])
def update_case_status_api():
    """ステータス更新API（Phase 4）"""
    # 認証チェック
    if not session.get("admin_authenticated"):
        return jsonify({"error": "認証が必要です"}), 401
    
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
        logger.error(f"❌ ステータス更新APIエラー: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/admin/api/add-comment", methods=["POST"])
def add_comment_api():
    """コメント追加API（Phase 4）"""
    # 認証チェック
    if not session.get("admin_authenticated"):
        return jsonify({"error": "認証が必要です"}), 401
    
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
        logger.error(f"❌ コメント追加APIエラー: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/admin/api/update-image-url", methods=["POST"])
def update_image_url_api():
    """画像URL更新API（Phase 4）"""
    # 認証チェック
    if not session.get("admin_authenticated"):
        return jsonify({"error": "認証が必要です"}), 401
    
    try:
        data = request.get_json()
        page_id = data.get("page_id")
        image_url = data.get("image_url")
        
        if not page_id or not image_url:
            return jsonify({
                "success": False,
                "error": "page_idとimage_urlが必要です"
            }), 400
        
        from data_access.factory_dashboard_manager import FactoryDashboardManager
        
        manager = FactoryDashboardManager()
        success = manager.update_image_url(page_id, image_url)
        
        if success:
            return jsonify({
                "success": True,
                "message": "画像URLを更新しました"
            })
        else:
            return jsonify({
                "success": False,
                "error": "画像URL更新に失敗しました"
            }), 500
    
    except Exception as e:
        import traceback
        logger.error(f"❌ 画像URL更新APIエラー: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/rag/rebuild", methods=["POST"])
def rag_rebuild():
    """
    RAGシステムを再構築（Phase 3対応）
    Notion/テキストから同期＆ベクトル化（手動トリガー）
    """
    try:
        # 管理者認証（簡易版）
        admin_code = request.headers.get("X-Admin-Code") or request.form.get("admin_code")
        expected_code = os.getenv("ADMIN_CODE", "change-me")
        
        if admin_code != expected_code:
            return jsonify({
                "success": False,
                "error": "管理者認証が必要です"
            }), 401
        
        # ソースの指定（デフォルト: "notion"）
        source = request.form.get("source", "notion")
        
        # chroma_managerを使用して再構築
        try:
            from data_access.chroma_manager import get_chroma_manager
            chroma_manager = get_chroma_manager()
            
            success = chroma_manager.rebuild(source=source)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": f"RAGシステムを再構築しました（ソース: {source}）",
                    "source": source
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "RAGシステムの再構築に失敗しました"
                }), 500
        except Exception as e:
            import traceback
            error_msg = f"RAG再構築エラー: {str(e)}"
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            return jsonify({
                "success": False,
                "error": error_msg
            }), 500
    
    except Exception as e:
        import traceback
        error_msg = f"エラーが発生しました: {str(e)}"
        print(f"詳細エラー: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

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