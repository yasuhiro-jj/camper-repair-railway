# streamlit_app_with_notion.py
import streamlit as st
import os
import uuid
import re
import json
from notion_client import Client
import time

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

import glob
import config

# === Notion連携機能 ===
def initialize_notion_client():
    """Notionクライアントを初期化"""
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
    """Notionから診断データを読み込み（キャッシュ対応）"""
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
        
        # デバッグ情報を表示
        st.info(f"🔍 データベースID: {node_db_id}")
        
        # Notionから診断ノードを取得
        response = client.databases.query(database_id=node_db_id)
        nodes = response.get("results", [])
        
        st.info(f"📊 取得したノード数: {len(nodes)}")
        
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
        
        st.success(f"✅ 診断ノード: {len(diagnostic_nodes)}件, 開始ノード: {len(start_nodes)}件")
        
        # セッション状態にキャッシュ
        result_data = {
            "diagnostic_nodes": diagnostic_nodes,
            "start_nodes": start_nodes
        }
        st.session_state.notion_diagnostic_data = result_data
        
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
        st.markdown("###    症状診断システム（Notion連携版）")
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
            st.markdown("###    診断結果")
            st.markdown(result)
        
        # 関連する修理ケースを表示
        st.markdown("### 📋 関連する修理ケース")
        repair_cases = load_notion_repair_cases()
        
        # デバッグ情報（開発時のみ表示）
        with st.expander("🔍 デバッグ情報"):
            st.write(f"**診断カテゴリ:** {current_node.get('category', '')}")
            st.write(f"**診断結果:** {current_node.get('result', '')[:100]}...")
            st.write(f"**利用可能な修理ケース数:** {len(repair_cases)}")
            st.write(f"**現在のノードID:** {st.session_state.notion_diagnostic_current_node}")
            st.write(f"**関連修理ケース数:** {len(current_node.get('related_repair_cases', []))}")
            if repair_cases:
                st.write("**修理ケースの例:**")
                for i, case in enumerate(repair_cases[:3]):
                    st.write(f"- {case.get('case_id', '')}: {case.get('symptoms', '')[:50]}...")
                    st.write(f"  関連診断ノード: {len(case.get('related_diagnostic_nodes', []))}件")
        
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
                st.success(f"🔍 {len(related_cases)}件の関連ケースが見つかりました")
                for case, score in related_cases[:3]:  # 上位3件を表示
                    with st.expander(f"   {case['case_id']}: {case['symptoms'][:50]}... (関連度: {score})"):
                        st.markdown(f"**症状:** {case['symptoms']}")
                        st.markdown(f"**修理手順:** {case['repair_steps']}")
                        st.markdown(f"**必要な部品:** {case['parts']}")
                        st.markdown(f"**必要な工具:** {case['tools']}")
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
        page_title="キャンピングカー修理アドバイザー（Notion連携版）",
        page_icon="  ",
        layout="wide"
    )

    # ヘッダー
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
        <h1>🔧 キャンピングカー修理アドバイザー（Notion連携版）</h1>
        <p>AIを活用したキャンピングカーの修理・メンテナンス支援システム</p>
    </div>
    """, unsafe_allow_html=True)

    # データ更新ボタン
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Notionデータを再読み込み", key="reload_notion_data"):
            clear_notion_cache()
            st.success("✅ キャッシュをクリアしました。ページを再読み込みしてください。")
            st.rerun()

    # タブを作成
    tab1, tab2 = st.tabs(["🔧 症状診断", "📊 システム情報"])

    with tab1:
        st.markdown("""
        <div style="background: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h3>   症状診断システム（Notion連携版）</h3>
            <p>Notionデータベースから取得した最新の診断データを使用して、症状を段階的に診断し、最適な対処法をご案内します。</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Notion連携版の診断
        notion_data = load_notion_diagnostic_data()
        if notion_data:
            run_notion_diagnostic_flow(notion_data)
        else:
            st.error("Notionデータの読み込みに失敗しました。")
            st.info("環境変数の設定を確認してください。")

    with tab2:
        st.markdown("""
        <div style="background: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h3>📊 システム情報</h3>
            <p>システムの状態と設定情報を確認できます。</p>
        </div>
        """, unsafe_allow_html=True)
        
        # システム情報の表示
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔧 データソース情報")
            
            # Notion接続状態
            notion_client = initialize_notion_client()
            if notion_client:
                st.success("✅ Notion接続: 正常")
                
                # データベース情報
                node_db_id = os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
                case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
                item_db_id = os.getenv("ITEM_DB_ID")
                
                if node_db_id:
                    st.info(f"📋 診断フローDB: {node_db_id}")
                if case_db_id:
                    st.info(f"🔧 修理ケースDB: {case_db_id}")
                if item_db_id:
                    st.info(f"  ️ 部品・工具DB: {item_db_id}")
            else:
                st.error("❌ Notion接続: 失敗")
                st.info("環境変数 NOTION_API_KEY または NOTION_TOKEN を確認してください。")
        
        with col2:
            st.markdown("### 📈 データ統計")
            
            # Notionデータの統計
            if notion_client:
                try:
                    # 診断ノード数
                    node_db_id = os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
                    if node_db_id:
                        node_response = notion_client.databases.query(database_id=node_db_id)
                        node_count = len(node_response.get("results", []))
                        st.metric("診断ノード数", node_count)
                    
                    # 修理ケース数
                    case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
                    if case_db_id:
                        case_response = notion_client.databases.query(database_id=case_db_id)
                        case_count = len(case_response.get("results", []))
                        st.metric("修理ケース数", case_count)
                    
                    # 部品・工具数
                    item_db_id = os.getenv("ITEM_DB_ID")
                    if item_db_id:
                        item_response = notion_client.databases.query(database_id=item_db_id)
                        item_count = len(item_response.get("results", []))
                        st.metric("部品・工具数", item_count)
                        
                except Exception as e:
                    st.error(f"データ統計の取得に失敗: {e}")
            else:
                st.info("Notion接続が利用できません")

if __name__ == "__main__":
    main()