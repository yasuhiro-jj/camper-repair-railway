import streamlit as st
import os
import uuid
import re
import json
import time
import glob

# Notionクライアントのインポート
try:
    from notion_client import Client
except ImportError:
    st.error("notion-client モジュールが見つかりません。requirements.txtに notion-client==2.2.1 を追加してください。")
    Client = None

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage

# Windows互換性のため、個別にインポート
try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
except ModuleNotFoundError as e:
    if "pwd" in str(e):
        import sys
        import platform
        if platform.system() == "Windows":
            from langchain_community.document_loaders.pdf import PyPDFLoader
            from langchain_community.document_loaders.text import TextLoader
    else:
        raise e

# ChromaDBを完全に無効化
Chroma = None
create_enhanced_rag_system = None
enhanced_rag_retrieve = None
format_blog_links = None

# config.pyの内容を直接含める
import os
from dotenv import load_dotenv

# .envファイルを読み込み（存在する場合）
if os.path.exists('.env'):
    try:
        load_dotenv()
    except UnicodeDecodeError:
        print("Warning: .envファイルのエンコーディングエラーを無視して続行します")
    except Exception as e:
        print(f"Warning: .envファイルの読み込みエラーを無視して続行します: {e}")
else:
    print("Info: .envファイルが見つかりません。環境変数を設定してください。")

# APIキーの設定（環境変数から取得）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "default")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

# LangChain Tracing設定
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT

# LangSmith設定（APIキーが設定されている場合のみ）
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT
    print("Info: LangSmith設定が有効になりました")
else:
    print("Warning: LANGSMITH_API_KEYが設定されていません。LangSmith機能は無効です。")

# === 診断データ（ハードコード版） ===
DIAGNOSTIC_DATA = {
    "diagnostic_nodes": {
        "start_battery": {
            "question": "バッテリーに関する問題ですか？",
            "category": "バッテリー",
            "is_start": True,
            "is_end": False,
            "next_nodes": ["battery_dead", "battery_weak"],
            "result": ""
        },
        "battery_dead": {
            "question": "エンジンが全く始動しませんか？",
            "category": "バッテリー",
            "is_start": False,
            "is_end": False,
            "next_nodes": ["battery_completely_dead", "battery_partial"],
            "result": ""
        },
        "battery_completely_dead": {
            "question": "バッテリーが完全に上がっています。ブースターケーブルをお持ちですか？",
            "category": "バッテリー",
            "is_start": False,
            "is_end": True,
            "next_nodes": [],
            "result": "バッテリー完全放電の診断結果：\n\n1. ブースターケーブルで応急処置\n2. バッテリーの充電確認\n3. 必要に応じてバッテリー交換\n\n推奨：専門店での点検をお勧めします。"
        },
        "battery_partial": {
            "question": "エンジンは始動するが、すぐに止まりますか？",
            "category": "バッテリー",
            "is_start": False,
            "is_end": True,
            "next_nodes": [],
            "result": "バッテリー部分放電の診断結果：\n\n1. バッテリー端子の清掃\n2. 充電システムの確認\n3. オルタネーターの点検\n\n推奨：充電システムの専門点検が必要です。"
        },
        "battery_weak": {
            "question": "バッテリーの充電が弱いですか？",
            "category": "バッテリー",
            "is_start": False,
            "is_end": True,
            "next_nodes": [],
            "result": "バッテリー劣化の診断結果：\n\n1. バッテリーの寿命確認\n2. 充電器での充電\n3. 必要に応じてバッテリー交換\n\n推奨：バッテリーの交換時期かもしれません。"
        },
        "start_water": {
            "question": "水道・給水に関する問題ですか？",
            "category": "水道",
            "is_start": True,
            "is_end": False,
            "next_nodes": ["water_pump", "water_leak"],
            "result": ""
        },
        "water_pump": {
            "question": "水道ポンプが動きませんか？",
            "category": "水道",
            "is_start": False,
            "is_end": True,
            "next_nodes": [],
            "result": "水道ポンプ故障の診断結果：\n\n1. ヒューズの確認\n2. 配線の点検\n3. ポンプ本体の確認\n4. 必要に応じてポンプ交換\n\n推奨：電気系統の専門点検が必要です。"
        },
        "water_leak": {
            "question": "水漏れが発生していますか？",
            "category": "水道",
            "is_start": False,
            "is_end": True,
            "next_nodes": [],
            "result": "水漏れの診断結果：\n\n1. 漏れ箇所の特定\n2. パッキンの確認\n3. 配管の点検\n4. 必要に応じて部品交換\n\n推奨：早急な修理が必要です。"
        },
        "start_gas": {
            "question": "ガス・コンロに関する問題ですか？",
            "category": "ガス",
            "is_start": True,
            "is_end": False,
            "next_nodes": ["gas_no_fire", "gas_weak_fire"],
            "result": ""
        },
        "gas_no_fire": {
            "question": "ガスコンロに火がつきませんか？",
            "category": "ガス",
            "is_start": False,
            "is_end": True,
            "next_nodes": [],
            "result": "ガスコンロ点火不良の診断結果：\n\n1. ガスボンベの残量確認\n2. ガス栓の確認\n3. 点火装置の点検\n4. 必要に応じて部品交換\n\n推奨：ガス漏れの危険性があるため専門点検をお勧めします。"
        },
        "gas_weak_fire": {
            "question": "火が弱いですか？",
            "category": "ガス",
            "is_start": False,
            "is_end": True,
            "next_nodes": [],
            "result": "ガス火力不足の診断結果：\n\n1. ガス圧の確認\n2. バーナーの清掃\n3. ガス栓の調整\n4. 必要に応じて部品交換\n\n推奨：ガス圧の専門調整が必要です。"
        }
    },
    "start_nodes": {
        "バッテリー": "start_battery",
        "水道": "start_water",
        "ガス": "start_gas"
    }
}

# === シンプルなAI相談機能 ===
def get_relevant_blog_links(query):
    """クエリに基づいて関連ブログを返す"""
    # キーワードベースの簡単なマッチング
    query_lower = query.lower()
    
    blog_links = [
        {
            "title": "バッテリー・バッテリーの故障と修理方法",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["バッテリー", "充電", "電圧", "上がり", "始動"]
        },
        {
            "title": "基本修理・キャンピングカー修理の基本",
            "url": "https://camper-repair.net/blog/risk1/",
            "keywords": ["修理", "基本", "手順", "工具", "部品"]
        },
        {
            "title": "定期点検・定期点検とメンテナンス",
            "url": "https://camper-repair.net/battery-selection/",
            "keywords": ["点検", "メンテナンス", "定期", "予防", "保守"]
        },
        {
            "title": "水道ポンプの故障と修理",
            "url": "https://camper-repair.net/blog/water-pump/",
            "keywords": ["水道", "ポンプ", "水", "給水", "配管"]
        },
        {
            "title": "ガスコンロの点火不良と対処法",
            "url": "https://camper-repair.net/blog/gas-stove/",
            "keywords": ["ガス", "コンロ", "火", "点火", "バーナー"]
        },
        {
            "title": "冷蔵庫の故障診断と修理",
            "url": "https://camper-repair.net/blog/refrigerator/",
            "keywords": ["冷蔵庫", "冷凍", "温度", "冷却", "冷え"]
        }
    ]
    
    # 関連度スコアを計算
    relevant_blogs = []
    for blog in blog_links:
        score = 0
        for keyword in blog["keywords"]:
            if keyword in query_lower:
                score += 1
        
        if score > 0:
            relevant_blogs.append((blog, score))
    
    # スコアでソート
    relevant_blogs.sort(key=lambda x: x[1], reverse=True)
    
    # 上位3件を返す
    return [blog for blog, score in relevant_blogs[:3]]

def generate_ai_response_with_rag(prompt):
    """AIの回答を生成（シンプル版）"""
    try:
        # OpenAI APIキーの確認
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            st.error("OpenAI APIキーが設定されていません")
            return
        
        # LLMの初期化
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        
        # 関連ブログを取得
        blog_links = get_relevant_blog_links(prompt)
        
        # システムプロンプト
        system_prompt = f"""あなたはキャンピングカーの修理・メンテナンスの専門家です。
以下の点に注意して回答してください：

1. 安全第一：危険な作業は避け、専門家への相談を推奨
2. 具体的な手順：段階的な修理手順を説明
3. 必要な工具・部品：具体的な工具名や部品名を提示
4. 予防メンテナンス：再発防止のためのアドバイス
5. 専門家の判断：複雑な問題は専門店への相談を推奨

以下の形式で自然な会話の流れで回答してください：

【状況確認】
まず、{prompt}について詳しくお聞かせください。どのような症状が現れていますか？

【具体的な対処法】
以下の手順を順番に試してみてください：

**1. 確認作業**
• 具体的な確認項目
• 安全確認のポイント

**2. 応急処置**
• 即座にできる対処法
• 必要な工具や部品

**3. 修理手順**
• 段階的な修理手順
• 各ステップでの注意点

**4. テスト・確認**
• 修理後の確認方法
• 動作確認のポイント

【注意点】
• 安全に作業するための重要なポイント
• 危険な作業の回避方法
• 専門家に相談すべき状況

【予防策】
• 再発防止のためのメンテナンス
• 定期点検のポイント
• 日常的な注意事項

【次のステップ】
この対処法を試してみて、結果を教えてください。うまくいかない場合は、別のアプローチをご提案します。

💬 追加の質問
文章が途中で切れる場合がありますので、必要に応じてもう一度お聞きください。

他に何かご質問ありましたら、引き続きチャットボットに聞いてみてください。

📞 お問い合わせ
直接スタッフにお尋ねをご希望の方は、お問い合わせフォームまたはお電話（086-206-6622）で受付けております。

【営業時間】年中無休（9:00～21:00）
※不在時は折り返しお電話差し上げます。

ユーザーの質問に基づいて、上記の形式で回答してください。"""

        # メッセージの作成
        messages = [
            HumanMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # AIの回答を生成
        with st.spinner("AIが回答を生成中..."):
            response = llm.invoke(messages)
            
        # 関連ブログを回答に追加
        ai_response = response.content
        if blog_links:
            ai_response += "\n\n🔗 関連ブログ\n"
            for blog in blog_links:
                ai_response += f"• {blog['title']}: {blog['url']}\n"
        else:
            # デフォルトの関連ブログ
            ai_response += "\n\n🔗 関連ブログ\n"
            ai_response += "• バッテリー・バッテリーの故障と修理方法: https://camper-repair.net/blog/repair1/\n"
            ai_response += "• 基本修理・キャンピングカー修理の基本: https://camper-repair.net/blog/risk1/\n"
            ai_response += "• 定期点検・定期点検とメンテナンス: https://camper-repair.net/battery-selection/\n"
        
        # 回答をセッションに追加
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # 関連ブログの情報を保存
        st.session_state.last_search_results = {
            "manual_content": "",
            "blog_links": blog_links
        }
        
    except Exception as e:
        st.error(f"AI回答生成エラー: {e}")
        # エラーが発生した場合のフォールバック
        fallback_response = f"""申し訳ございません。一時的なエラーが発生しました。

{prompt}について、基本的なアドバイスをお答えします：

【基本的な対処法】
1. 安全確認を最優先に行ってください
2. 専門的な作業は専門店に相談することをお勧めします
3. 応急処置が必要な場合は、安全な方法で行ってください

📞 お問い合わせ
直接スタッフにお尋ねをご希望の方は、お問い合わせフォームまたはお電話（086-206-6622）で受付けております。

【営業時間】年中無休（9:00～21:00）
※不在時は折り返しお電話差し上げます。

🔗 関連ブログ
• バッテリー・バッテリーの故障と修理方法: https://camper-repair.net/blog/repair1/
• 基本修理・キャンピングカー修理の基本: https://camper-repair.net/blog/risk1/
• 定期点検・定期点検とメンテナンス: https://camper-repair.net/battery-selection/"""
        
        st.session_state.messages.append({"role": "assistant", "content": fallback_response})

def show_relevant_documents():
    """関連ブログを表示"""
    if "last_search_results" in st.session_state:
        search_results = st.session_state.last_search_results
        blog_links = search_results.get("blog_links", [])
        
        if blog_links:
            st.markdown("### 📚 関連ブログ記事")
            with st.expander("🔗 詳細を見る"):
                for i, blog in enumerate(blog_links, 1):
                    st.markdown(f"**{i}. {blog['title']}**")
                    st.markdown(f"リンク: {blog['url']}")
                    st.markdown("---")

# === メインアプリケーション ===
def main():
    st.set_page_config(
        page_title="キャンピングカー修理専門 AIチャット",
        page_icon="🔧",
        layout="wide"
    )

    # カスタムCSS
    st.markdown("""
    <style>
    /* 全体のスタイル */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        text-align: center;
        padding: 30px 20px;
        background: rgba(255, 255, 255, 0.95);
        color: #2c3e50;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-header h1 {
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        font-size: 1.1em;
        color: #6c757d;
        margin: 0;
        font-weight: 400;
    }
    
    .feature-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .feature-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .feature-banner h3 {
        font-size: 1.5em;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .feature-list {
        background: rgba(255, 255, 255, 0.9);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        backdrop-filter: blur(10px);
    }
    
    .feature-list h4 {
        color: #2c3e50;
        font-size: 1.3em;
        margin-bottom: 15px;
        font-weight: 600;
    }
    
    .feature-list ul {
        list-style: none;
        padding: 0;
    }
    
    .feature-list li {
        padding: 8px 0;
        color: #495057;
        font-weight: 500;
        position: relative;
        padding-left: 25px;
    }
    
    .feature-list li::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: #28a745;
        font-weight: bold;
    }
    
    .quick-question {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 12px 18px;
        margin: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .quick-question:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f4fd 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    /* タブのスタイル改善 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        color: #6c757d;
        font-weight: 600;
        padding: 15px 30px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        border-radius: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transform: translateY(-1px);
    }
    
    .stTabs [aria-selected="true"]:before {
        opacity: 1;
    }
    
    .stTabs [aria-selected="false"]:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        color: #667eea;
        transform: translateY(-1px);
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.15);
    }
    
    /* レスポンシブデザイン */
    @media (max-width: 768px) {
        .main-header {
            padding: 20px 15px;
        }
        
        .main-header h1 {
            font-size: 2em;
        }
        
        .feature-banner {
            padding: 20px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 12px 20px;
            font-size: 0.9em;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <h1>🔧 キャンピングカー修理専門 AIチャット</h1>
        <p>経験豊富なAIがキャンピングカーの修理について詳しくお答えします</p>
    </div>
    """, unsafe_allow_html=True)

    # 2つのタブを作成
    tab1, tab2 = st.tabs(["💬 AIチャット相談", "🔍 対話式症状診断"])

    with tab1:
        # AIチャット相談の説明バナー
        st.markdown("""
        <div class="feature-banner">
            <h3>💬 AIチャット相談</h3>
            <p>経験豊富なAIがキャンピングカーの修理について詳しくお答えします。自由に質問してください。</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 機能説明
        st.markdown("""
        <div class="feature-list">
            <h4>🎯 この機能でできること</h4>
            <ul>
                <li>🔧 修理方法の詳細な説明</li>
                <li>🛠️ 工具や部品の選び方</li>
                <li>⚠️ 安全な作業手順の案内</li>
                <li>🔗 定期メンテナンスのアドバイス</li>
                <li>🔍 トラブルシューティングのヒント</li>
                <li>📚 関連ブログ記事の自動表示</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # よくある質問ボタン
        st.markdown("### 💡 よくある質問 (クリックで質問)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔋 バッテリー上がり", key="battery_question"):
                question = "バッテリーが上がってエンジンが始動しない時の対処法を教えてください。"
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant", avatar="https://camper-repair.net/blog/wp-content/uploads/2025/05/dummy_staff_01-150x138-1.png"):
                    generate_ai_response_with_rag(question)
                st.rerun()
            
            if st.button("💧 水道ポンプ", key="water_pump_question"):
                question = "水道ポンプが動かない時の対処法と修理手順を教えてください。"
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant", avatar="https://camper-repair.net/blog/wp-content/uploads/2025/05/dummy_staff_01-150x138-1.png"):
                    generate_ai_response_with_rag(question)
                st.rerun()
        
        with col2:
            if st.button("🔥 ガスコンロ", key="gas_stove_question"):
                question = "ガスコンロに火がつかない時の対処法と修理手順を教えてください。"
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant", avatar="https://camper-repair.net/blog/wp-content/uploads/2025/05/dummy_staff_01-150x138-1.png"):
                    generate_ai_response_with_rag(question)
                st.rerun()
            
            if st.button("❄️ 冷蔵庫", key="refrigerator_question"):
                question = "冷蔵庫が冷えない時の対処法と修理手順を教えてください。"
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant", avatar="https://camper-repair.net/blog/wp-content/uploads/2025/05/dummy_staff_01-150x138-1.png"):
                    generate_ai_response_with_rag(question)
                st.rerun()
        
        with col3:
            if st.button("📋 定期点検", key="maintenance_question"):
                question = "キャンピングカーの定期点検項目とメンテナンス手順を教えてください。"
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant", avatar="https://camper-repair.net/blog/wp-content/uploads/2025/05/dummy_staff_01-150x138-1.png"):
                    generate_ai_response_with_rag(question)
                st.rerun()
            
            if st.button("🆕 新しい会話", key="new_conversation"):
                st.session_state.messages = []
                if "last_search_results" in st.session_state:
                    del st.session_state.last_search_results
                st.rerun()
        
        # セッション状態の初期化
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # チャット履歴の表示
        for message in st.session_state.messages:
            avatar = "https://camper-repair.net/blog/wp-content/uploads/2025/05/dummy_staff_01-150x138-1.png" if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # ユーザー入力
        if prompt := st.chat_input("キャンピングカーの修理について質問してください..."):
            # ユーザーメッセージを追加
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)

            # AIの回答を生成（RAG機能付き）
            with st.chat_message("assistant", avatar="https://camper-repair.net/blog/wp-content/uploads/2025/05/dummy_staff_01-150x138-1.png"):
                generate_ai_response_with_rag(prompt)

        # 関連ドキュメントの表示
        show_relevant_documents()

    with tab2:
        # 症状診断の説明
        st.markdown("""
        <div class="feature-banner">
            <h3>🔍 対話式症状診断</h3>
            <p>症状を選択して、段階的に診断を行い、最適な対処法をご案内します。</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ハードコード版の診断
        st.info("現在は基本的な診断機能のみ利用可能です。")
        st.markdown("### 📋 利用可能な診断カテゴリ")
        st.markdown("- 🔋 バッテリー関連")
        st.markdown("- 💧 水道・給水関連")
        st.markdown("- 🔥 ガス・コンロ関連")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"アプリケーションエラー: {e}")
        st.info("ページを再読み込みしてください。")
