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

from langchain_chroma import Chroma
from enhanced_rag_system import create_enhanced_rag_system, enhanced_rag_retrieve, format_blog_links
import config

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

# === RAG機能付きAI相談機能 ===
def initialize_database():
    """データベースを初期化（拡張RAGシステム使用）"""
    try:
        # OpenAI APIキーの確認
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key or openai_api_key == "your_openai_api_key_here":
            st.warning("⚠️ OPENAI_API_KEYが正しく設定されていません")
            st.info("💡 .envファイルに有効なOPENAI_API_KEYを設定してください")
            st.info("🔧 現在はフォールバックモードで動作します")
            return "fallback_mode"
        
        st.info("🔄 データベースを初期化中...")
        
        # 拡張RAGシステムを作成（ブログURLも含む）
        db = create_enhanced_rag_system()
        
        st.success("✅ データベースの初期化が完了しました")
        return db
        
    except Exception as e:
        st.error(f"❌ データベース初期化エラー: {e}")
        st.error(f"エラーの詳細: {type(e).__name__}")
        st.info("🔧 フォールバックモードに切り替えます")
        return "fallback_mode"

def search_relevant_documents(db, query, k=5):
    """関連ドキュメントを検索（拡張RAG使用）"""
    try:
        if not db:
            st.warning("⚠️ データベースが初期化されていません")
            return {"manual_content": "", "blog_links": []}
        
        # フォールバックモードの場合
        if db == "fallback_mode":
            return search_fallback_mode(query)
        
        # デバッグ情報を表示
        st.info(f"🔍 検索クエリ: '{query}'")
        
        # 拡張RAG検索（ブログURLも含む）
        results = enhanced_rag_retrieve(query, db, max_results=k)
        
        # 検索結果の詳細を表示
        manual_content = results.get("manual_content", "")
        blog_links = results.get("blog_links", [])
        
        st.success(f"✅ 検索完了: マニュアル内容 {len(manual_content)}文字, ブログ記事 {len(blog_links)}件")
        
        return results
        
    except Exception as e:
        st.error(f"❌ ドキュメント検索エラー: {e}")
        st.error(f"エラーの詳細: {type(e).__name__}")
        st.info("🔧 フォールバックモードに切り替えます")
        return search_fallback_mode(query)

def search_fallback_mode(query):
    """フォールバックモードでの検索（キーワードマッチング）"""
    try:
        st.info("🔧 フォールバックモードで検索中...")
        
        # キーワードベースの検索
        query_lower = query.lower()
        
        # ブログデータ（ハードコード版）
        blog_documents = [
            {
                "title": "サブバッテリー完全ガイド",
                "content": "サブバッテリー、ディープサイクル、リチウムイオン、鉛バッテリー、容量選定、寿命、充電方法、バッテリー管理、放電深度、残量計、運用時間、バッテリー並列、直列接続、温度管理、メンテナンス、取り付け方法、電圧監視、車両改造、保安基準、交換目安",
                "url": "https://camper-repair.net/blog/risk1/",
                "tags": ["サブバッテリー", "完全ガイド", "容量選定", "寿命"]
            },
            {
                "title": "サブバッテリーの種類と選び方",
                "content": "サブバッテリー、鉛、AGM、リチウムイオン、ニッケル水素、価格比較、容量計算、用途別選択、重量、サイズ、対応機器、充電サイクル、長所短所、放電深度、温度特性、耐久性、購入時注意、メーカー比較、口コミ、トラブル事例",
                "url": "https://camper-repair.net/blog/repair1/",
                "tags": ["サブバッテリー", "種類", "選び方", "容量計算"]
            },
            {
                "title": "サブバッテリー容量計算のコツ",
                "content": "サブバッテリー、容量計算、使用家電、消費電力、連続運用、充電サイクル、同時使用、最大負荷、予備容量、計算例、バッテリー増設、残量管理、省エネ運用、電装計画、充電速度、容量オーバー、失敗例、運用体験、節電グッズ、バッテリー保護",
                "url": "https://camper-repair.net/battery-selection/",
                "tags": ["サブバッテリー", "容量計算", "消費電力", "運用時間"]
            },
            {
                "title": "水道ポンプの故障と修理方法",
                "content": "水道ポンプ、故障、修理、水圧不足、異音、動作不良、ヒューズ、配線、ポンプ本体、交換、メンテナンス、清掃、フィルター、水漏れ、電気系統、DC12V、AC100V、ポンプ容量、設置方法、トラブルシューティング",
                "url": "https://camper-repair.net/blog/repair1/",
                "tags": ["水道ポンプ", "故障", "修理", "水圧不足"]
            },
            {
                "title": "ガスコンロの点火不良と対処法",
                "content": "ガスコンロ、点火不良、火がつかない、ガスボンベ、ガス栓、点火装置、バーナー、清掃、調整、ガス圧、安全装置、ガス漏れ、点検方法、修理手順、部品交換、メンテナンス、トラブル事例",
                "url": "https://camper-repair.net/blog/risk1/",
                "tags": ["ガスコンロ", "点火不良", "ガスボンベ", "点火装置"]
            },
            {
                "title": "冷蔵庫の冷却不良と修理方法",
                "content": "冷蔵庫、冷却不良、冷えない、温度調整、電源、ヒューズ、コンプレッサー、冷媒、フィルター、清掃、メンテナンス、設置環境、通気性、温度設定、故障診断、修理手順、交換部品",
                "url": "https://camper-repair.net/battery-selection/",
                "tags": ["冷蔵庫", "冷却不良", "温度調整", "コンプレッサー"]
            }
        ]
        
        # キーワードマッチング
        matched_blogs = []
        for blog in blog_documents:
            score = 0
            content_lower = (blog["content"] + " " + blog["title"]).lower()
            
            # キーワードマッチング
            keywords = ["バッテリー", "サブバッテリー", "水道", "ポンプ", "ガス", "コンロ", "冷蔵庫", "冷却", "点火", "故障", "修理", "調子", "悪い", "動かない", "つかない", "冷えない"]
            for keyword in keywords:
                if keyword in query_lower and keyword in content_lower:
                    score += 2
                elif keyword in content_lower:
                    score += 1
            
            if score > 0:
                matched_blogs.append((blog, score))
        
        # スコアでソート
        matched_blogs.sort(key=lambda x: x[1], reverse=True)
        
        # 結果を返す
        blog_links = [blog for blog, score in matched_blogs[:3]]
        
        st.success(f"✅ フォールバック検索完了: 関連記事 {len(blog_links)}件")
        
        return {
            "manual_content": "フォールバックモード: キーワードマッチングによる検索結果",
            "blog_links": blog_links
        }
        
    except Exception as e:
        st.error(f"❌ フォールバック検索エラー: {e}")
        return {"manual_content": "", "blog_links": []}

def integrate_notion_data_to_rag(notion_data):
    """NotionデータをRAGシステムに統合"""
    try:
        if not notion_data:
            return
        
        # NotionデータをRAG用のドキュメントに変換
        notion_documents = []
        
        # 診断ノードをドキュメントに変換
        for node_id, node_data in notion_data.get("diagnostic_nodes", {}).items():
            doc_content = f"""
診断ノードID: {node_id}
カテゴリ: {node_data.get('category', '')}
質問: {node_data.get('question', '')}
診断結果: {node_data.get('result', '')}
開始フラグ: {node_data.get('is_start', False)}
終端フラグ: {node_data.get('is_end', False)}
次のノード: {', '.join(node_data.get('next_nodes', []))}
"""
            
            notion_doc = {
                "page_content": doc_content,
                "metadata": {
                    "source_type": "notion_diagnostic",
                    "node_id": node_id,
                    "category": node_data.get('category', ''),
                    "title": f"診断ノード: {node_id}",
                    "url": f"notion://diagnostic/{node_id}"
                }
            }
            notion_documents.append(notion_doc)
        
        # セッション状態に保存
        st.session_state.notion_documents = notion_documents
        
        st.info(f"✅ NotionデータをRAGに統合: {len(notion_documents)}件の診断ノード")
        
    except Exception as e:
        st.error(f"❌ NotionデータのRAG統合エラー: {e}")

def search_notion_data(query):
    """Notionデータから関連情報を検索"""
    try:
        if "notion_documents" not in st.session_state:
            return []
        
        notion_docs = st.session_state.notion_documents
        query_lower = query.lower()
        
        # キーワードマッチングで関連ドキュメントを検索
        relevant_docs = []
        for doc in notion_docs:
            content_lower = doc["page_content"].lower()
            metadata = doc["metadata"]
            
            # カテゴリ、質問、結果でマッチング
            if (query_lower in content_lower or 
                query_lower in metadata.get("category", "").lower() or
                query_lower in metadata.get("title", "").lower()):
                
                relevant_docs.append({
                    "content": doc["page_content"],
                    "metadata": metadata,
                    "relevance_score": calculate_relevance_score(query_lower, content_lower)
                })
        
        # 関連度でソート
        relevant_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return relevant_docs[:3]  # 上位3件を返す
        
    except Exception as e:
        st.error(f"❌ Notionデータ検索エラー: {e}")
        return []

def calculate_relevance_score(query, content):
    """関連度スコアを計算"""
    score = 0
    query_words = query.split()
    
    for word in query_words:
        if word in content:
            score += 1
        if word in content and len(word) > 3:  # 長い単語は重み付け
            score += 0.5
    
    return score

def generate_fallback_response(prompt):
    """フォールバックモードでの簡易回答生成"""
    try:
        st.info("🔧 フォールバックモードで回答を生成中...")
        
        # キーワードベースの回答生成
        prompt_lower = prompt.lower()
        
        # 検索結果を取得
        search_results = search_fallback_mode(prompt)
        blog_links = search_results.get("blog_links", [])
        
        # Notionデータも検索
        notion_results = search_notion_data(prompt)
        if notion_results:
            st.info(f"📊 Notionデータから {len(notion_results)}件の関連情報を発見")
        
        # 基本的な回答テンプレート
        if "バッテリー" in prompt_lower or "サブバッテリー" in prompt_lower:
            response = """**バッテリー関連の問題について**

【状況確認】
バッテリーの調子が悪いとのことですね。まず、どのような症状が現れていますか？

【基本的な対処法】
**1. 確認作業**
• バッテリーの電圧測定（12V以上が正常）
• 端子の接続状態確認
• バッテリー液の量と比重確認

**2. 応急処置**
• 端子の清掃と締め直し
• 充電器での充電
• ブースターケーブルでの応急充電

**3. 修理手順**
• バッテリーの交換
• 充電システムの点検
• 配線の確認と修理

**4. テスト・確認**
• 電圧の再測定
• 負荷テストの実施
• 充電状態の確認

【注意点】
• バッテリー液は危険です。手袋と保護メガネを着用
• 充電中は換気を十分に行う
• 専門知識が必要な場合は専門店に相談

【予防策】
• 定期的な電圧チェック
• 端子の清掃と保護
• 適切な充電管理

【次のステップ】
上記の対処法を試してみて、結果を教えてください。うまくいかない場合は、別のアプローチをご提案します。"""
        
        elif "水道" in prompt_lower or "ポンプ" in prompt_lower:
            response = """**水道ポンプ関連の問題について**

【状況確認】
水道ポンプが動かないとのことですね。どのような症状が現れていますか？

【基本的な対処法】
**1. 確認作業**
• 電源の確認（ヒューズ、配線）
• 水の供給状況確認
• ポンプの動作音確認

**2. 応急処置**
• ヒューズの交換
• 配線の接続確認
• ポンプの清掃

**3. 修理手順**
• ポンプ本体の分解点検
• 部品の交換
• 配線の修理

**4. テスト・確認**
• 動作テストの実施
• 水圧の確認
• 異音の確認

【注意点】
• 電気系統の作業は感電の危険があります
• 水漏れの可能性があるため注意
• 専門知識が必要な場合は専門店に相談

【予防策】
• 定期的な清掃とメンテナンス
• フィルターの交換
• 適切な使用環境の維持"""
        
        elif "ガス" in prompt_lower or "コンロ" in prompt_lower:
            response = """**ガスコンロ関連の問題について**

【状況確認】
ガスコンロに火がつかないとのことですね。どのような症状が現れていますか？

【基本的な対処法】
**1. 確認作業**
• ガスボンベの残量確認
• ガス栓の開閉確認
• 点火装置の動作確認

**2. 応急処置**
• バーナーの清掃
• 点火装置の清掃
• ガス栓の調整

**3. 修理手順**
• 点火装置の交換
• バーナーの交換
• ガス系統の点検

**4. テスト・確認**
• 点火テストの実施
• 火の強さの確認
• ガス漏れの確認

【注意点】
• ガス漏れの危険性があります
• 火気厳禁の環境で作業
• 専門知識が必要な場合は専門店に相談

【予防策】
• 定期的な清掃とメンテナンス
• ガスボンベの適切な管理
• 安全装置の点検"""
        
        elif "冷蔵庫" in prompt_lower:
            response = """**冷蔵庫関連の問題について**

【状況確認】
冷蔵庫が冷えないとのことですね。どのような症状が現れていますか？

【基本的な対処法】
**1. 確認作業**
• 電源の確認
• 温度設定の確認
• 通気性の確認

**2. 応急処置**
• フィルターの清掃
• 通気口の清掃
• 温度設定の調整

**3. 修理手順**
• コンプレッサーの点検
• 冷媒の確認
• 電気系統の点検

**4. テスト・確認**
• 温度測定の実施
• 動作音の確認
• 冷却性能の確認

【注意点】
• 冷媒は危険な物質です
• 電気系統の作業は感電の危険があります
• 専門知識が必要な場合は専門店に相談

【予防策】
• 定期的な清掃とメンテナンス
• 適切な設置環境の維持
• 温度設定の最適化"""
        
        else:
            response = f"""**{prompt}について**

【状況確認】
ご質問いただいた内容について、詳しくお聞かせください。

【基本的な対処法】
**1. 確認作業**
• 症状の詳細確認
• 安全確認の実施
• 周辺環境の確認

**2. 応急処置**
• 安全な応急処置の実施
• 必要な工具の準備
• 作業環境の整備

**3. 修理手順**
• 段階的な修理手順の実施
• 各ステップでの注意点の確認
• 安全な作業の継続

**4. テスト・確認**
• 修理後の動作確認
• 安全性の確認
• 性能の確認

【注意点】
• 安全第一で作業を進める
• 危険な作業は避ける
• 専門知識が必要な場合は専門店に相談

【予防策】
• 定期的なメンテナンス
• 適切な使用方法の維持
• 早期発見・早期対処

【次のステップ】
上記の対処法を試してみて、結果を教えてください。うまくいかない場合は、別のアプローチをご提案します。"""
        
        # 関連ブログを追加
        if blog_links:
            response += "\n\n🔗 関連ブログ記事\n"
            for blog in blog_links[:3]:
                response += f"• **{blog['title']}**: {blog['url']}\n"
        else:
            response += "\n\n🔗 関連ブログ記事\n"
            response += "• **バッテリーの故障と修理方法**: https://camper-repair.net/blog/repair1/\n"
            response += "• **キャンピングカー修理の基本**: https://camper-repair.net/blog/risk1/\n"
            response += "• **定期点検とメンテナンス**: https://camper-repair.net/battery-selection/\n"
        
        # 回答をセッションに追加
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # 関連ドキュメントの情報を保存
        st.session_state.last_search_results = search_results
        
        st.success("✅ フォールバックモードで回答を生成しました")
        
    except Exception as e:
        st.error(f"❌ フォールバック回答生成エラー: {e}")
        # 基本的なエラーメッセージ
        error_response = f"""申し訳ございませんが、現在システムに問題が発生しています。

**{prompt}** についてお答えできませんでした。

【対処法】
• しばらく時間をおいて再度お試しください
• 別のキーワードで質問してみてください
• 直接お電話（086-206-6622）でご相談ください

【営業時間】年中無休（9:00～21:00）
※不在時は折り返しお電話差し上げます。"""
        
        st.session_state.messages.append({"role": "assistant", "content": error_response})

def generate_ai_response_with_rag(prompt):
    """RAG機能付きAIの回答を生成"""
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
        
        # データベースから関連ドキュメントとブログリンクを検索
        if "database" not in st.session_state:
            st.session_state.database = initialize_database()
        
        db = st.session_state.database
        if not db:
            st.error("❌ データベースの初期化に失敗しました。AI回答を生成できません。")
            return
        
        # フォールバックモードの場合は簡易回答を生成
        if db == "fallback_mode":
            generate_fallback_response(prompt)
            return
        
        search_results = search_relevant_documents(db, prompt)
        
        # 関連ドキュメントの内容を抽出
        manual_content = search_results.get("manual_content", "")
        blog_links = search_results.get("blog_links", [])
        
        # 検索結果の詳細を表示
        if manual_content:
            st.info(f"📄 マニュアル内容: {len(manual_content)}文字")
        if blog_links:
            st.info(f"🔗 関連ブログ: {len(blog_links)}件")
        if not manual_content and not blog_links:
            st.warning("⚠️ 関連するドキュメントが見つかりませんでした")
        
        # システムプロンプト（RAG機能付き）
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

以下の関連ドキュメントの情報を参考にして、上記の形式で回答してください：

関連ドキュメント:
{manual_content}

ユーザーの質問に基づいて、上記のドキュメント情報を活用して回答してください。"""

        # メッセージの作成
        messages = [
            HumanMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # AIの回答を生成
        with st.spinner("AIが回答を生成中..."):
            response = llm.invoke(messages)
            
        # 関連ブログを回答に追加（非表示設定）
        ai_response = response.content
        # 関連ブログの表示を有効化
        if blog_links:
            ai_response += "\n\n🔗 関連ブログ記事\n"
            for blog in blog_links[:3]:  # 最大3件
                ai_response += f"• **{blog['title']}**: {blog['url']}\n"
        else:
            # デフォルトの関連ブログ
            ai_response += "\n\n🔗 関連ブログ記事\n"
            ai_response += "• **バッテリーの故障と修理方法**: https://camper-repair.net/blog/repair1/\n"
            ai_response += "• **キャンピングカー修理の基本**: https://camper-repair.net/blog/risk1/\n"
            ai_response += "• **定期点検とメンテナンス**: https://camper-repair.net/battery-selection/\n"
        
        # 回答をセッションに追加
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # 関連ドキュメントの情報を保存
        if manual_content or blog_links:
            st.session_state.last_search_results = {
                "manual_content": manual_content,
                "blog_links": blog_links
            }
        
    except Exception as e:
        st.error(f"AI回答生成エラー: {e}")

def show_relevant_documents():
    """関連ドキュメントを表示"""
    if "last_search_results" in st.session_state:
        search_results = st.session_state.last_search_results
        manual_content = search_results.get("manual_content", "")
        blog_links = search_results.get("blog_links", [])
        
        if manual_content or blog_links:
            st.markdown("### 📚 参考情報")
            
            if manual_content:
                with st.expander("📄 修理マニュアルから", expanded=False):
                    # マニュアル内容を適切に表示（長すぎる場合は省略）
                    display_content = manual_content[:1000] + "..." if len(manual_content) > 1000 else manual_content
                    st.markdown(display_content)
            
            if blog_links:
                with st.expander("🔗 関連ブログ記事", expanded=False):
                    for i, blog in enumerate(blog_links[:3], 1):
                        st.markdown(f"**{i}. {blog['title']}**")
                        st.markdown(f"🔗 [リンクを開く]({blog['url']})")
                        if 'content' in blog:
                            content_preview = blog['content'][:200] + "..." if len(blog['content']) > 200 else blog['content']
                            st.markdown(f"概要: {content_preview}")
                        st.markdown("---")
        else:
            st.info("💡 関連するドキュメントが見つかりませんでした。別のキーワードで検索してみてください。")

# === Notion連携機能 ===
def initialize_notion_client():
    """Notionクライアントを初期化"""
    if Client is None:
        st.error("❌ notion-client モジュールが利用できません")
        return None
    
    try:
        # 複数の環境変数名に対応
        api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
        if not api_key:
            st.warning("⚠️ NOTION_API_KEYまたはNOTION_TOKENが設定されていません")
            return None
        
        client = Client(auth=api_key)
        return client
    except Exception as e:
        st.error(f"❌ Notionクライアントの初期化に失敗: {e}")
        return None

def load_notion_diagnostic_data():
    """Notionから診断データを読み込み（キャッシュ対応・RAG統合）"""
    # セッション状態でキャッシュをチェック
    if "notion_diagnostic_data" in st.session_state:
        return st.session_state.notion_diagnostic_data
    
    client = initialize_notion_client()
    if not client:
        return None
    
    try:
        # 複数の環境変数名に対応
        node_db_id = os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
        if not node_db_id:
            st.error("❌ NODE_DB_IDまたはNOTION_DIAGNOSTIC_DB_IDが設定されていません")
            return None
        
        # Notionから診断ノードを取得
        response = client.databases.query(database_id=node_db_id)
        nodes = response.get("results", [])
        
        # データを変換
        diagnostic_nodes = {}
        start_nodes = {}
        
        for node in nodes:
            properties = node.get("properties", {})
            
            # ノードIDを取得
            node_id_prop = properties.get("ノードID", {})
            node_id = ""
            if node_id_prop.get("type") == "title":
                title_content = node_id_prop.get("title", [])
                if title_content:
                    node_id = title_content[0].get("plain_text", "")
            
            if not node_id:
                continue
            
            # 各プロパティを取得
            question_prop = properties.get("質問内容", {})
            question = ""
            if question_prop.get("type") == "rich_text":
                rich_text_content = question_prop.get("rich_text", [])
                if rich_text_content:
                    question = rich_text_content[0].get("plain_text", "")
            
            result_prop = properties.get("診断結果", {})
            result = ""
            if result_prop.get("type") == "rich_text":
                rich_text_content = result_prop.get("rich_text", [])
                if rich_text_content:
                    result = rich_text_content[0].get("plain_text", "")
            
            category_prop = properties.get("カテゴリ", {})
            category = ""
            if category_prop.get("type") == "rich_text":
                rich_text_content = category_prop.get("rich_text", [])
                if rich_text_content:
                    category = rich_text_content[0].get("plain_text", "")
            
            is_start = properties.get("開始フラグ", {}).get("checkbox", False)
            is_end = properties.get("終端フラグ", {}).get("checkbox", False)
            
            next_nodes_prop = properties.get("次のノード", {})
            next_nodes = []
            if next_nodes_prop.get("type") == "rich_text":
                rich_text_content = next_nodes_prop.get("rich_text", [])
                if rich_text_content:
                    next_nodes_text = rich_text_content[0].get("plain_text", "")
                    next_nodes = [node.strip() for node in next_nodes_text.split(",") if node.strip()]
            
            # 修理ケースの関連付けを取得
            repair_cases_relation = properties.get("修理ケース", {})
            related_repair_cases = []
            if repair_cases_relation.get("type") == "relation":
                relation_data = repair_cases_relation.get("relation", [])
                for relation in relation_data:
                    related_repair_cases.append(relation.get("id", ""))
            
            # ノードデータを作成
            node_data = {
                "question": question,
                "category": category,
                "is_start": is_start,
                "is_end": is_end,
                "next_nodes": next_nodes,
                "result": result,
                "related_repair_cases": related_repair_cases
            }
            
            diagnostic_nodes[node_id] = node_data
            
            # 開始ノードを記録
            if is_start:
                start_nodes[category] = node_id
        
        # セッション状態にキャッシュ
        result_data = {
            "diagnostic_nodes": diagnostic_nodes,
            "start_nodes": start_nodes
        }
        st.session_state.notion_diagnostic_data = result_data
        
        # RAGシステムにNotionデータを統合
        integrate_notion_data_to_rag(result_data)
        
        return result_data
        
    except Exception as e:
        st.error(f"❌ Notionからの診断データ読み込みに失敗: {e}")
        return None

def load_notion_repair_cases():
    """Notionから修理ケースデータを読み込み（キャッシュ対応）"""
    # セッション状態でキャッシュをチェック
    if "notion_repair_cases" in st.session_state:
        return st.session_state.notion_repair_cases
    
    client = initialize_notion_client()
    if not client:
        return []
    
    try:
        # 複数の環境変数名に対応
        case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
        if not case_db_id:
            st.error("❌ CASE_DB_IDまたはNOTION_REPAIR_CASE_DB_IDが設定されていません")
            return []
        
        # Notionから修理ケースを取得
        response = client.databases.query(database_id=case_db_id)
        cases = response.get("results", [])
        
        repair_cases = []
        
        for case in cases:
            properties = case.get("properties", {})
            
            # ケースIDを取得
            case_id_prop = properties.get("ケースID", {})
            case_id = ""
            if case_id_prop.get("type") == "title":
                title_content = case_id_prop.get("title", [])
                if title_content:
                    case_id = title_content[0].get("plain_text", "")
            
            if not case_id:
                continue
            
            # 各プロパティを取得
            symptoms_prop = properties.get("症状", {})
            symptoms = ""
            if symptoms_prop.get("type") == "rich_text":
                rich_text_content = symptoms_prop.get("rich_text", [])
                if rich_text_content:
                    symptoms = rich_text_content[0].get("plain_text", "")
            
            repair_steps_prop = properties.get("修理手順", {})
            repair_steps = ""
            if repair_steps_prop.get("type") == "rich_text":
                rich_text_content = repair_steps_prop.get("rich_text", [])
                if rich_text_content:
                    repair_steps = rich_text_content[0].get("plain_text", "")
            
            parts_prop = properties.get("必要な部品", {})
            parts = ""
            if parts_prop.get("type") == "rich_text":
                rich_text_content = parts_prop.get("rich_text", [])
                if rich_text_content:
                    parts = rich_text_content[0].get("plain_text", "")
            
            tools_prop = properties.get("必要な工具", {})
            tools = ""
            if tools_prop.get("type") == "rich_text":
                rich_text_content = tools_prop.get("rich_text", [])
                if rich_text_content:
                    tools = rich_text_content[0].get("plain_text", "")
            
            difficulty_prop = properties.get("難易度", {})
            difficulty = ""
            if difficulty_prop.get("type") == "rich_text":
                rich_text_content = difficulty_prop.get("rich_text", [])
                if rich_text_content:
                    difficulty = rich_text_content[0].get("plain_text", "")
            
            # 診断ノードの関連付けを取得
            diagnostic_nodes_relation = properties.get("診断ノード", {})
            related_diagnostic_nodes = []
            if diagnostic_nodes_relation.get("type") == "relation":
                relation_data = diagnostic_nodes_relation.get("relation", [])
                for relation in relation_data:
                    related_diagnostic_nodes.append(relation.get("id", ""))
            
            # 必要部品の関連付けを取得
            required_parts_relation = properties.get("必要部品", {})
            related_parts = []
            if required_parts_relation.get("type") == "relation":
                relation_data = required_parts_relation.get("relation", [])
                for relation in relation_data:
                    related_parts.append(relation.get("id", ""))
            
            # ケースデータを作成
            case_data = {
                "case_id": case_id,
                "symptoms": symptoms,
                "repair_steps": repair_steps,
                "parts": parts,
                "tools": tools,
                "difficulty": difficulty,
                "related_diagnostic_nodes": related_diagnostic_nodes,
                "related_parts": related_parts
            }
            
            repair_cases.append(case_data)
        
        # セッション状態にキャッシュ
        st.session_state.notion_repair_cases = repair_cases
        
        return repair_cases
        
    except Exception as e:
        st.error(f"❌ Notionからの修理ケース読み込みに失敗: {e}")
        return []

def clear_notion_cache():
    """Notionデータのキャッシュをクリア"""
    if "notion_diagnostic_data" in st.session_state:
        del st.session_state.notion_diagnostic_data
    if "notion_repair_cases" in st.session_state:
        del st.session_state.notion_repair_cases
    if "notion_diagnostic_current_node" in st.session_state:
        del st.session_state.notion_diagnostic_current_node
    if "notion_diagnostic_history" in st.session_state:
        del st.session_state.notion_diagnostic_history

# === 対話式症状診断機能（Notion連携版） ===
def run_notion_diagnostic_flow(diagnostic_data, current_node_id=None):
    """Notionデータを使用した診断フローを実行"""
    if not diagnostic_data:
        st.error("Notion診断データが読み込めませんでした。")
        return

    diagnostic_nodes = diagnostic_data["diagnostic_nodes"]
    start_nodes = diagnostic_data["start_nodes"]

    # セッション状態の初期化
    if "notion_diagnostic_current_node" not in st.session_state:
        st.session_state.notion_diagnostic_current_node = None
        st.session_state.notion_diagnostic_history = []

    # 開始ノードの選択
    if st.session_state.notion_diagnostic_current_node is None:
        st.markdown("**症状のカテゴリを選択してください：**")
        
        # 利用可能なカテゴリを表示
        available_categories = list(start_nodes.keys())
        
        if not available_categories:
            st.warning("⚠️ 利用可能な診断カテゴリがありません")
            return
        
        selected_category = st.selectbox(
            "カテゴリを選択",
            available_categories,
            key="notion_category_select"
        )
        
        if st.button("診断開始", key="notion_start_diagnosis"):
            start_node_id = start_nodes[selected_category]
            st.session_state.notion_diagnostic_current_node = start_node_id
            st.session_state.notion_diagnostic_history = [start_node_id]
            st.rerun()
        
        return

    # 現在のノードを取得
    current_node = diagnostic_nodes.get(st.session_state.notion_diagnostic_current_node)
    if not current_node:
        st.error("診断ノードが見つかりませんでした。")
        return

    # 質問の表示
    question = current_node.get("question", "")
    if question:
        st.markdown(f"### ❓ {question}")
    
    # 終端ノードの場合
    if current_node.get("is_end", False):
        result = current_node.get("result", "")
        if result:
            st.markdown("### 📋 診断結果")
            st.markdown(result)
        
        # 関連する修理ケースを表示
        st.markdown("### 📋 関連する修理ケース")
        repair_cases = load_notion_repair_cases()
        
        if repair_cases:
            # リレーションに基づく関連ケースフィルタリング（優先）
            current_node_id = st.session_state.notion_diagnostic_current_node
            related_cases = []
            
            # 1. リレーションに基づく関連ケースを検索
            for case in repair_cases:
                related_nodes = case.get("related_diagnostic_nodes", [])
                if current_node_id in related_nodes:
                    related_cases.append((case, 10))  # 最高スコア
            
            # 2. リレーションが見つからない場合、キーワードマッチング
            if not related_cases:
                category = current_node.get("category", "").lower()
                question = current_node.get("question", "").lower()
                result = current_node.get("result", "").lower()
                
                for case in repair_cases:
                    symptoms = case.get("symptoms", "").lower()
                    repair_steps = case.get("repair_steps", "").lower()
                    
                    # 複数の条件でマッチング
                    score = 0
                    
                    # カテゴリマッチング
                    if category and category in symptoms:
                        score += 3
                    if category and category in repair_steps:
                        score += 2
                    
                    # キーワードマッチング
                    keywords = ["インバーター", "バッテリー", "電圧", "充電", "配線"]
                    for keyword in keywords:
                        if keyword in symptoms and (keyword in question or keyword in result):
                            score += 2
                        if keyword in repair_steps and (keyword in question or keyword in result):
                            score += 1
                    
                    # 症状の類似性チェック
                    if any(word in symptoms for word in ["電圧", "不足", "弱い", "重い"]) and any(word in result for word in ["電圧", "不足", "弱い", "重い"]):
                        score += 2
                    
                    if score >= 2:  # スコアが2以上の場合に関連ケースとして追加
                        related_cases.append((case, score))
            
            # スコアでソート
            related_cases.sort(key=lambda x: x[1], reverse=True)
            
            if related_cases:
                st.success(f"🔧 {len(related_cases)}件の関連ケースが見つかりました")
                for case, score in related_cases[:3]:  # 上位3件を表示
                    with st.expander(f"🔧 {case['case_id']}: {case['symptoms'][:50]}... (関連度: {score})"):
                        st.markdown(f"**症状:** {case['symptoms']}")
                        st.markdown(f"**修理手順:** {case['repair_steps']}")
                        # 詳細な推奨製品情報を非表示
                        # st.markdown(f"**必要な部品:** {case['parts']}")
                        # st.markdown(f"**必要な工具:** {case['tools']}")
                        st.markdown(f"**難易度:** {case['difficulty']}")
            else:
                st.info("関連する修理ケースが見つかりませんでした。")
                st.info("💡 ヒント: Notionで診断ノードと修理ケースの関連付けを設定してください。")
        else:
            st.info("修理ケースデータを読み込めませんでした。")
        
        # 診断をリセット
        if st.button("新しい診断を開始", key="notion_reset_diagnosis"):
            st.session_state.notion_diagnostic_current_node = None
            st.session_state.notion_diagnostic_history = []
            st.rerun()
        
        return

    # 次のノードへの選択肢
    next_nodes = current_node.get("next_nodes", [])
    if len(next_nodes) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("はい", key=f"notion_yes_{current_node_id}"):
                next_node_id = next_nodes[0]
                st.session_state.notion_diagnostic_current_node = next_node_id
                st.session_state.notion_diagnostic_history.append(next_node_id)
                st.rerun()
        
        with col2:
            if st.button("いいえ", key=f"notion_no_{current_node_id}"):
                next_node_id = next_nodes[1] if len(next_nodes) > 1 else next_nodes[0]
                st.session_state.notion_diagnostic_current_node = next_node_id
                st.session_state.notion_diagnostic_history.append(next_node_id)
                st.rerun()
    elif len(next_nodes) == 1:
        if st.button("次へ", key=f"notion_next_{current_node_id}"):
            next_node_id = next_nodes[0]
            st.session_state.notion_diagnostic_current_node = next_node_id
            st.session_state.notion_diagnostic_history.append(next_node_id)
            st.rerun()

    # 診断履歴の表示
    if st.session_state.notion_diagnostic_history:
        st.markdown("---")
        st.markdown("**📝 診断履歴**")
        for i, node_id in enumerate(st.session_state.notion_diagnostic_history):
            node = diagnostic_nodes.get(node_id, {})
            question = node.get("question", "")
            if question:
                st.markdown(f"{i+1}. {question}")

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
                <li>📚 専門的な修理アドバイス</li>
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

        # 関連ドキュメントの表示（有効化）
        show_relevant_documents()

    with tab2:
        # 症状診断の説明
        st.markdown("""
        <div class="feature-banner">
            <h3>🔍 対話式症状診断</h3>
            <p>症状を選択して、段階的に診断を行い、最適な対処法をご案内します。</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Notion連携版の診断
        notion_data = load_notion_diagnostic_data()
        if notion_data:
            run_notion_diagnostic_flow(notion_data)
        else:
            st.error("Notionデータの読み込みに失敗しました。")
            st.info("環境変数の設定を確認してください。")

if __name__ == "__main__":
    main()
