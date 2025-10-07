#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最強キャンピングカー修理チャットボット - 統合アプリケーション
Streamlit + Flask + RAG + SERP + Notion の全機能を統合
"""

import streamlit as st
import requests
import json
import os
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp

# 設定ファイルをインポート
from config import OPENAI_API_KEY, SERP_API_KEY, LANGSMITH_API_KEY

# === 統合チャットボットクラス ===
class UnifiedChatbot:
    def __init__(self):
        self.flask_base_url = "http://localhost:5001"
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
        self.diagnostic_data = None
        self.repair_cases = []
        
    async def initialize(self):
        """初期化処理"""
        try:
            # Flaskアプリのヘルスチェック
            await self.check_flask_connection()
            
            # 診断データの読み込み
            self.diagnostic_data = await self.load_diagnostic_data()
            
            # 修理ケースの読み込み
            self.repair_cases = await self.load_repair_cases()
            
            return True
        except Exception as e:
            st.error(f"初期化エラー: {e}")
            return False
    
    async def check_flask_connection(self):
        """Flaskアプリとの接続確認"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.flask_base_url}/api/health", timeout=5) as response:
                    if response.status == 200:
                        st.success("✅ Flaskアプリとの接続確認完了")
                        return True
                    else:
                        st.warning("⚠️ Flaskアプリが起動していません")
                        return False
        except Exception as e:
            st.error(f"❌ Flaskアプリ接続エラー: {e}")
            st.info("Flaskアプリを起動してください: python app.py")
            return False
    
    async def load_diagnostic_data(self):
        """診断データの読み込み"""
        try:
            # Notionから診断データを取得（Streamlitの機能を活用）
            from notion_client import Client
            
            client = Client(auth=os.getenv("NOTION_API_KEY"))
            node_db_id = os.getenv("NODE_DB_ID")
            
            if not node_db_id:
                return None
                
            response = client.databases.query(database_id=node_db_id)
            nodes = response.get("results", [])
            
            return {
                "nodes": nodes,
                "loaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            st.warning(f"診断データの読み込みに失敗: {e}")
            return None
    
    async def load_repair_cases(self):
        """修理ケースの読み込み"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.flask_base_url}/api/categories", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("categories", [])
                    else:
                        return []
        except Exception as e:
            st.warning(f"修理ケースの読み込みに失敗: {e}")
            return []
    
    async def process_message(self, user_message: str, mode: str = "chat") -> Dict[str, Any]:
        """メッセージ処理（統合機能）"""
        try:
            # 1. 意図分析
            intent = await self.analyze_intent(user_message)
            
            # 2. モード別処理
            if mode == "diagnostic":
                return await self.process_diagnostic(user_message, intent)
            elif mode == "repair_search":
                return await self.process_repair_search(user_message, intent)
            else:  # chat
                return await self.process_chat(user_message, intent)
                
        except Exception as e:
            return {
                "error": f"処理エラー: {e}",
                "type": "error"
            }
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """意図分析（AI駆動）"""
        try:
            # OpenAI APIを使用した意図分析
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
    
    async def process_diagnostic(self, message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """診断処理"""
        try:
            # 診断フローの実行
            if self.diagnostic_data:
                # Notionデータを使用した診断
                return await self.run_diagnostic_flow(message, intent)
            else:
                # フォールバック: 一般的な診断
                return await self.general_diagnostic(message, intent)
                
        except Exception as e:
            return {
                "error": f"診断エラー: {e}",
                "type": "error"
            }
    
    async def process_repair_search(self, message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """修理検索処理"""
        try:
            # Flaskアプリの検索APIを使用
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.flask_base_url}/api/search",
                    json={"query": message},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "type": "repair_search",
                            "results": data.get("results", []),
                            "intent": intent
                        }
                    else:
                        return {
                            "error": "検索APIエラー",
                            "type": "error"
                        }
        except Exception as e:
            return {
                "error": f"検索エラー: {e}",
                "type": "error"
            }
    
    async def process_chat(self, message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """チャット処理（統合AI）"""
        try:
            # 1. RAG検索
            rag_results = await self.rag_search(message)
            
            # 2. SERP検索
            serp_results = await self.serp_search(message)
            
            # 3. AI回答生成
            ai_response = await self.generate_ai_response(message, rag_results, serp_results, intent)
            
            return {
                "type": "chat",
                "response": ai_response,
                "rag_results": rag_results,
                "serp_results": serp_results,
                "intent": intent
            }
            
        except Exception as e:
            return {
                "error": f"チャットエラー: {e}",
                "type": "error"
            }
    
    async def rag_search(self, query: str) -> Dict[str, Any]:
        """RAG検索"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.flask_base_url}/api/search_text_files",
                    json={"query": query},
                    timeout=20
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"results": []}
        except Exception as e:
            return {"results": [], "error": str(e)}
    
    async def serp_search(self, query: str) -> Dict[str, Any]:
        """SERP検索"""
        try:
            # FlaskアプリのSERP検索機能を使用
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.flask_base_url}/api/search",
                    json={"query": query, "include_serp": True},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"results": []}
        except Exception as e:
            return {"results": [], "error": str(e)}
    
    async def generate_ai_response(self, message: str, rag_results: Dict, serp_results: Dict, intent: Dict) -> str:
        """AI回答生成（統合）"""
        try:
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4o-mini")
            
            # コンテキストの構築
            context = self.build_context(rag_results, serp_results, intent)
            
            prompt = f"""
            あなたは最強のキャンピングカー修理専門AIです。
            以下の情報を統合して、最高品質の回答を生成してください。
            
            ユーザーの質問: {message}
            
            意図分析: {json.dumps(intent, ensure_ascii=False, indent=2)}
            
            検索結果:
            RAG検索: {json.dumps(rag_results, ensure_ascii=False, indent=2)}
            SERP検索: {json.dumps(serp_results, ensure_ascii=False, indent=2)}
            
            回答形式:
            1. 【状況確認】- 症状の詳細確認
            2. 【診断結果】- 原因の特定
            3. 【修理手順】- 段階的な修理方法
            4. 【費用目安】- 修理費用の概算
            5. 【推奨部品】- 必要な部品・工具
            6. 【注意事項】- 安全な作業のポイント
            7. 【関連情報】- 追加の参考資料
            
            専門的で実用的な回答を生成してください。
            """
            
            response = llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            return f"AI回答生成エラー: {e}"
    
    def build_context(self, rag_results: Dict, serp_results: Dict, intent: Dict) -> str:
        """コンテキスト構築"""
        context_parts = []
        
        # RAG結果の追加
        if rag_results.get("results"):
            context_parts.append("📚 マニュアル情報:")
            for result in rag_results["results"][:3]:
                context_parts.append(f"- {result.get('title', 'N/A')}: {result.get('content', 'N/A')[:200]}...")
        
        # SERP結果の追加
        if serp_results.get("results"):
            context_parts.append("🌐 リアルタイム情報:")
            for result in serp_results["results"][:3]:
                context_parts.append(f"- {result.get('title', 'N/A')}: {result.get('snippet', 'N/A')[:200]}...")
        
        return "\n".join(context_parts)

# === Streamlit UI ===
def main():
    st.set_page_config(
        page_title="🔧 最強キャンピングカー修理チャットボット",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # カスタムCSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .message-user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .message-ai {
        background: white;
        color: #333;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
        border: 2px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #28a745; }
    .status-offline { background-color: #dc3545; }
    .status-warning { background-color: #ffc107; }
    </style>
    """, unsafe_allow_html=True)
    
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <h1>🔧 最強キャンピングカー修理チャットボット</h1>
        <p>AI診断 + RAG検索 + リアルタイム情報 + 専門知識 = 最強の修理支援</p>
    </div>
    """, unsafe_allow_html=True)
    
    # サイドバー
    with st.sidebar:
        st.markdown("### 🔧 システム状態")
        
        # 接続状態の表示
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Flask API**")
            flask_status = st.empty()
        with col2:
            st.markdown("**AI エンジン**")
            ai_status = st.empty()
        
        st.markdown("### 🎯 チャットモード")
        chat_mode = st.selectbox(
            "モードを選択",
            ["🤖 統合チャット", "🔍 症状診断", "🛠️ 修理検索", "💰 費用相談"]
        )
        
        st.markdown("### ⚙️ 設定")
        show_debug = st.checkbox("デバッグ情報を表示")
        auto_search = st.checkbox("自動検索を有効化")
        
        if st.button("🔄 システム再起動"):
            st.rerun()
    
    # メインコンテンツ
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = UnifiedChatbot()
        st.session_state.messages = []
        st.session_state.initialized = False
    
    # 初期化
    if not st.session_state.initialized:
        with st.spinner("🔧 システムを初期化中..."):
            if asyncio.run(st.session_state.chatbot.initialize()):
                st.session_state.initialized = True
                st.success("✅ システム初期化完了")
            else:
                st.error("❌ システム初期化に失敗")
                st.stop()
    
    # チャット履歴の表示
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message-user">
                    <strong>あなた:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-ai">
                    <strong>🔧 AI修理専門家:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # メッセージ入力
    user_input = st.chat_input("修理について質問してください...")
    
    if user_input:
        # ユーザーメッセージを追加
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # AI処理
        with st.spinner("🔧 AIが回答を生成中..."):
            try:
                # モード別処理
                if chat_mode == "🔍 症状診断":
                    result = asyncio.run(st.session_state.chatbot.process_message(user_input, "diagnostic"))
                elif chat_mode == "🛠️ 修理検索":
                    result = asyncio.run(st.session_state.chatbot.process_message(user_input, "repair_search"))
                else:
                    result = asyncio.run(st.session_state.chatbot.process_message(user_input, "chat"))
                
                # 結果の表示
                if result.get("error"):
                    ai_response = f"❌ エラー: {result['error']}"
                else:
                    ai_response = result.get("response", "回答を生成できませんでした")
                
                # AIメッセージを追加
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # デバッグ情報の表示
                if show_debug:
                    with st.expander("🔍 デバッグ情報"):
                        st.json(result)
                
            except Exception as e:
                st.error(f"処理エラー: {e}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"❌ エラーが発生しました: {e}"
                })
        
        st.rerun()

if __name__ == "__main__":
    main()
