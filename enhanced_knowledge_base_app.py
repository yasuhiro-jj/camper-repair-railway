#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
キャンピングカー修理AIチャットアプリ（最適化版）
- 遅延インポート対応
- キャッシュシステム統合
- 非同期処理対応
"""

import os
import sys
import subprocess
import re
import hashlib
from functools import lru_cache
from typing import Optional, Dict, Any

# 遅延インポート用の関数
def get_streamlit():
    """Streamlitを遅延インポート"""
    try:
        import streamlit as st
        return st
    except ImportError:
        return None

def safe_st_call(func_name, *args, **kwargs):
    """Streamlitが利用できない場合の安全な呼び出し"""
    st = ensure_streamlit()
    if st and hasattr(st, func_name):
        return getattr(st, func_name)(*args, **kwargs)
    else:
        # Streamlitが利用できない場合はprintで代替
        if func_name in ['error', 'warning', 'info', 'success']:
            print(f"[{func_name.upper()}] {args[0] if args else ''}")
        return None

def get_langchain():
    """LangChainを遅延インポート"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage, AIMessage
        return ChatOpenAI, HumanMessage, AIMessage
    except ImportError:
        return None, None, None

def get_data_access():
    """データアクセス層を遅延インポート"""
    try:
        from data_access import NotionClient, KnowledgeBaseManager, DiagnosticDataManager
        from data_access.notion_client import notion_client
        from data_access.knowledge_base import knowledge_base_manager
        from data_access.diagnostic_data import diagnostic_data_manager
        return {
            'NotionClient': NotionClient,
            'KnowledgeBaseManager': KnowledgeBaseManager,
            'DiagnosticDataManager': DiagnosticDataManager,
            'notion_client': notion_client,
            'knowledge_base_manager': knowledge_base_manager,
            'diagnostic_data_manager': diagnostic_data_manager,
            'available': True
        }
    except ImportError:
        return {'available': False}

# グローバル変数（遅延初期化）
_data_access = None
_st = None
_langchain = None

def ensure_data_access():
    """データアクセス層を遅延初期化"""
    global _data_access
    if _data_access is None:
        _data_access = get_data_access()
    return _data_access

def ensure_streamlit():
    """Streamlitを遅延初期化"""
    global _st
    if _st is None:
        _st = get_streamlit()
    return _st

def ensure_langchain():
    """LangChainを遅延初期化"""
    global _langchain
    if _langchain is None:
        _langchain = get_langchain()
    return _langchain

# 最適化されたNotion統合をインポート
try:
    from optimized_notion_integration import get_optimized_notion_client, search_camper_repair_info
    NOTION_OPTIMIZATION_AVAILABLE = True
except ImportError:
    NOTION_OPTIMIZATION_AVAILABLE = False
    print("Warning: optimized_notion_integration module not available")

# 必要なライブラリの自動インストール
def install_required_packages():
    """必要なライブラリを自動インストール"""
    required_packages = [
        "notion-client==2.2.1",
        "python-dotenv"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("==", "").replace("-", "_"))
        except ImportError:
            # st.info(f"📦 {package}をインストール中...")  # 非表示化
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                # st.success(f"✅ {package}のインストール完了")  # 非表示化
            except subprocess.CalledProcessError:
                print(f"❌ {package}のインストールに失敗しました")
                print("💡 手動でインストールしてください: pip install notion-client==2.2.1")

# アプリ起動時にライブラリをチェック
install_required_packages()

# .envファイルの読み込みを試行
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenvがインストールされていません。環境変数を手動で設定します。")

# 環境変数の設定
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = "camper-repair-ai"

# OpenAI APIキーの安全な設定
# 1. 環境変数から取得
# 2. Streamlitシークレットから取得
# 3. どちらもない場合は設定を促す

# Streamlitのsecretsを安全に取得
st = ensure_streamlit()
if st and hasattr(st, 'secrets'):
    openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
else:
    openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    # APIキーが設定されていない場合は静かに処理を続行
    # 実際のAPI呼び出し時にエラーハンドリングを行う
    print("⚠️ OpenAI APIキーが設定されていません。チャット機能を使用するにはAPIキーを設定してください。")

# 環境変数として設定
os.environ["OPENAI_API_KEY"] = openai_api_key

# Notion APIキーの設定
if st and hasattr(st, 'secrets'):
    notion_api_key = st.secrets.get("NOTION_API_KEY") or st.secrets.get("NOTION_TOKEN") or os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
else:
    notion_api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")

# NotionDB接続の初期化（データアクセス層を使用）
def initialize_notion_client():
    """Notionクライアントを初期化（データアクセス層を使用）"""
    data_access = ensure_data_access()
    st = ensure_streamlit()
    
    if data_access['available']:
        return data_access['notion_client'].initialize_client()
    else:
        if st:
            st.error("❌ データアクセス層が利用できません")
        return None

@lru_cache(maxsize=1)
def load_notion_diagnostic_data():
    """Notionから診断データを読み込み（データアクセス層を使用）"""
    data_access = ensure_data_access()
    st = ensure_streamlit()
    
    if data_access['available']:
        return data_access['notion_client'].load_diagnostic_data()
    else:
        if st:
            st.error("❌ データアクセス層が利用できません")
        return None

def perform_detailed_notion_test():
    """詳細なNotion接続テストを実行"""
    test_results = {
        "overall_success": False,
        "databases": {},
        "success_count": 0,
        "total_count": 0
    }
    
    try:
        # クライアント初期化テスト
        client = initialize_notion_client()
        if not client:
            test_results["databases"]["クライアント初期化"] = {
                "status": "error",
                "message": "Notionクライアントの初期化に失敗",
                "solution": "APIキーの形式と権限を確認してください"
            }
            return test_results
        
        test_results["databases"]["クライアント初期化"] = {
            "status": "success",
            "message": "Notionクライアントの初期化に成功"
        }
        test_results["success_count"] += 1
        test_results["total_count"] += 1
        
        # データベースIDの取得
        if st and hasattr(st, 'secrets'):
            node_db_id = st.secrets.get("NODE_DB_ID") or st.secrets.get("NOTION_DIAGNOSTIC_DB_ID") or os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
            case_db_id = st.secrets.get("CASE_DB_ID") or st.secrets.get("NOTION_REPAIR_CASE_DB_ID") or os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
            item_db_id = st.secrets.get("ITEM_DB_ID") or os.getenv("ITEM_DB_ID")
        else:
            node_db_id = os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
            case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
            item_db_id = os.getenv("ITEM_DB_ID")
        
        # 診断フローDBテスト
        if node_db_id:
            test_results["total_count"] += 1
            try:
                response = client.databases.query(database_id=node_db_id)
                nodes = response.get("results", [])
                if nodes:
                    test_results["databases"]["診断フローDB"] = {
                        "status": "success",
                        "message": f"{len(nodes)}件のノードを取得"
                    }
                    test_results["success_count"] += 1
                else:
                    test_results["databases"]["診断フローDB"] = {
                        "status": "warning",
                        "message": "データベースにアクセス可能だが、データがありません",
                        "solution": "Notionデータベースに診断ノードを追加してください"
                    }
            except Exception as e:
                error_msg = str(e)
                if "not_found" in error_msg.lower() or "404" in error_msg:
                    solution = "データベースIDが間違っています。NotionでデータベースのIDを確認してください"
                elif "unauthorized" in error_msg.lower() or "401" in error_msg:
                    solution = "APIキーにデータベースへのアクセス権限がありません。Notion統合の設定を確認してください"
                else:
                    solution = "ネットワーク接続とAPIキーの権限を確認してください"
                
                test_results["databases"]["診断フローDB"] = {
                    "status": "error",
                    "message": f"アクセス失敗: {error_msg[:100]}",
                    "solution": solution
                }
        else:
            test_results["databases"]["診断フローDB"] = {
                "status": "error",
                "message": "データベースIDが設定されていません",
                "solution": ".streamlit/secrets.tomlにNODE_DB_IDを設定してください"
            }
        
        # 修理ケースDBテスト
        if case_db_id:
            test_results["total_count"] += 1
            try:
                response = client.databases.query(database_id=case_db_id)
                cases = response.get("results", [])
                if cases:
                    test_results["databases"]["修理ケースDB"] = {
                        "status": "success",
                        "message": f"{len(cases)}件のケースを取得"
                    }
                    test_results["success_count"] += 1
                else:
                    test_results["databases"]["修理ケースDB"] = {
                        "status": "warning",
                        "message": "データベースにアクセス可能だが、データがありません",
                        "solution": "Notionデータベースに修理ケースを追加してください"
                    }
            except Exception as e:
                error_msg = str(e)
                if "not_found" in error_msg.lower() or "404" in error_msg:
                    solution = "データベースIDが間違っています。NotionでデータベースのIDを確認してください"
                elif "unauthorized" in error_msg.lower() or "401" in error_msg:
                    solution = "APIキーにデータベースへのアクセス権限がありません。Notion統合の設定を確認してください"
                else:
                    solution = "ネットワーク接続とAPIキーの権限を確認してください"
                
                test_results["databases"]["修理ケースDB"] = {
                    "status": "error",
                    "message": f"アクセス失敗: {error_msg[:100]}",
                    "solution": solution
                }
        else:
            test_results["databases"]["修理ケースDB"] = {
                "status": "error",
                "message": "データベースIDが設定されていません",
                "solution": ".streamlit/secrets.tomlにCASE_DB_IDを設定してください"
            }
        
        # 部品・工具DBテスト
        if item_db_id:
            test_results["total_count"] += 1
            try:
                response = client.databases.query(database_id=item_db_id)
                items = response.get("results", [])
                if items:
                    test_results["databases"]["部品・工具DB"] = {
                        "status": "success",
                        "message": f"{len(items)}件のアイテムを取得"
                    }
                    test_results["success_count"] += 1
                else:
                    test_results["databases"]["部品・工具DB"] = {
                        "status": "warning",
                        "message": "データベースにアクセス可能だが、データがありません",
                        "solution": "Notionデータベースに部品・工具を追加してください"
                    }
            except Exception as e:
                error_msg = str(e)
                if "not_found" in error_msg.lower() or "404" in error_msg:
                    solution = "データベースIDが間違っています。NotionでデータベースのIDを確認してください"
                elif "unauthorized" in error_msg.lower() or "401" in error_msg:
                    solution = "APIキーにデータベースへのアクセス権限がありません。Notion統合の設定を確認してください"
                else:
                    solution = "ネットワーク接続とAPIキーの権限を確認してください"
                
                test_results["databases"]["部品・工具DB"] = {
                    "status": "error",
                    "message": f"アクセス失敗: {error_msg[:100]}",
                    "solution": solution
                }
        else:
            test_results["databases"]["部品・工具DB"] = {
                "status": "error",
                "message": "データベースIDが設定されていません",
                "solution": ".streamlit/secrets.tomlにITEM_DB_IDを設定してください"
            }
        
        # 全体の成功判定
        if test_results["success_count"] > 0:
            test_results["overall_success"] = True
        
        return test_results
        
    except Exception as e:
        test_results["databases"]["全体テスト"] = {
            "status": "error",
            "message": f"テスト実行エラー: {str(e)}",
            "solution": "システムエラーが発生しました。アプリケーションを再起動してください"
        }
        return test_results

@lru_cache(maxsize=1)
def load_notion_repair_cases():
    """Notionから修理ケースデータを読み込み（データアクセス層を使用）"""
    data_access = ensure_data_access()
    st = ensure_streamlit()
    
    if data_access['available']:
        return data_access['notion_client'].load_repair_cases()
    else:
        if st:
            st.error("❌ データアクセス層が利用できません")
        return []
    
        
        # Notionから修理ケースを取得
        response = client.databases.query(database_id=case_db_id)
        cases = response.get("results", [])
        
        repair_cases = []
        
        for case in cases:
            properties = case.get("properties", {})
            
            case_info = {
                "id": case.get("id"),
                "title": "",
                "category": "",
                "symptoms": [],
                "solution": "",
                "parts": [],
                "tools": [],
                "related_nodes": [],  # 関連する診断ノード
                "related_items": []   # 関連する部品・工具
            }
            
            # タイトルの抽出
            title_prop = properties.get("タイトル", {})
            if title_prop.get("type") == "title" and title_prop.get("title"):
                case_info["title"] = title_prop["title"][0].get("plain_text", "")
            
            # カテゴリの抽出
            category_prop = properties.get("カテゴリ", {})
            if category_prop.get("type") == "select" and category_prop.get("select"):
                case_info["category"] = category_prop["select"].get("name", "")
            
            # 症状の抽出
            symptoms_prop = properties.get("症状", {})
            if symptoms_prop.get("type") == "multi_select":
                case_info["symptoms"] = [item.get("name", "") for item in symptoms_prop.get("multi_select", [])]
            
            # 解決方法の抽出
            solution_prop = properties.get("解決方法", {})
            if solution_prop.get("type") == "rich_text" and solution_prop.get("rich_text"):
                case_info["solution"] = solution_prop["rich_text"][0].get("plain_text", "")
            
            # 必要な部品の抽出（リレーション対応）
            parts_prop = properties.get("必要な部品", {})
            if parts_prop.get("type") == "relation":
                # リレーションから部品情報を取得
                for relation in parts_prop.get("relation", []):
                    try:
                        item_response = client.pages.retrieve(page_id=relation["id"])
                        item_properties = item_response.get("properties", {})
                        
                        item_info = {
                            "id": relation["id"],
                            "name": "",
                            "category": "",
                            "price": "",
                            "supplier": ""
                        }
                        
                        # 部品名の抽出
                        name_prop = item_properties.get("名前", {})
                        if name_prop.get("type") == "title" and name_prop.get("title"):
                            item_info["name"] = name_prop["title"][0].get("plain_text", "")
                        
                        # カテゴリの抽出
                        cat_prop = item_properties.get("カテゴリ", {})
                        if cat_prop.get("type") == "select" and cat_prop.get("select"):
                            item_info["category"] = cat_prop["select"].get("name", "")
                        
                        # 価格の抽出
                        price_prop = item_properties.get("価格", {})
                        if price_prop.get("type") == "number":
                            item_info["price"] = str(price_prop.get("number", ""))
                        
                        # サプライヤーの抽出
                        supplier_prop = item_properties.get("サプライヤー", {})
                        if supplier_prop.get("type") == "rich_text" and supplier_prop.get("rich_text"):
                            item_info["supplier"] = supplier_prop["rich_text"][0].get("plain_text", "")
                        
                        case_info["related_items"].append(item_info)
                    except Exception as e:
                        st.warning(f"部品情報の取得に失敗: {e}")
            elif parts_prop.get("type") == "multi_select":
                # 従来のmulti_select形式
                case_info["parts"] = [item.get("name", "") for item in parts_prop.get("multi_select", [])]
            
            # 必要な工具の抽出（リレーション対応）
            tools_prop = properties.get("必要な工具", {})
            if tools_prop.get("type") == "relation":
                # リレーションから工具情報を取得
                for relation in tools_prop.get("relation", []):
                    try:
                        item_response = client.pages.retrieve(page_id=relation["id"])
                        item_properties = item_response.get("properties", {})
                        
                        tool_info = {
                            "id": relation["id"],
                            "name": "",
                            "category": "",
                            "price": "",
                            "supplier": ""
                        }
                        
                        # 工具名の抽出
                        name_prop = item_properties.get("名前", {})
                        if name_prop.get("type") == "title" and name_prop.get("title"):
                            tool_info["name"] = name_prop["title"][0].get("plain_text", "")
                        
                        # カテゴリの抽出
                        cat_prop = item_properties.get("カテゴリ", {})
                        if cat_prop.get("type") == "select" and cat_prop.get("select"):
                            tool_info["category"] = cat_prop["select"].get("name", "")
                        
                        # 価格の抽出
                        price_prop = item_properties.get("価格", {})
                        if price_prop.get("type") == "number":
                            tool_info["price"] = str(price_prop.get("number", ""))
                        
                        # サプライヤーの抽出
                        supplier_prop = item_properties.get("サプライヤー", {})
                        if supplier_prop.get("type") == "rich_text" and supplier_prop.get("rich_text"):
                            tool_info["supplier"] = supplier_prop["rich_text"][0].get("plain_text", "")
                        
                        case_info["related_items"].append(tool_info)
                    except Exception as e:
                        st.warning(f"工具情報の取得に失敗: {e}")
            elif tools_prop.get("type") == "multi_select":
                # 従来のmulti_select形式
                case_info["tools"] = [item.get("name", "") for item in tools_prop.get("multi_select", [])]
            
            # 関連診断ノードの抽出（リレーション対応）
            nodes_prop = properties.get("関連診断ノード", {})
            if nodes_prop.get("type") == "relation":
                for relation in nodes_prop.get("relation", []):
                    try:
                        node_response = client.pages.retrieve(page_id=relation["id"])
                        node_properties = node_response.get("properties", {})
                        
                        node_info = {
                            "id": relation["id"],
                            "title": "",
                            "category": "",
                            "symptoms": []
                        }
                        
                        # ノードタイトルの抽出
                        title_prop = node_properties.get("タイトル", {})
                        if title_prop.get("type") == "title" and title_prop.get("title"):
                            node_info["title"] = title_prop["title"][0].get("plain_text", "")
                        
                        # カテゴリの抽出
                        cat_prop = node_properties.get("カテゴリ", {})
                        if cat_prop.get("type") == "select" and cat_prop.get("select"):
                            node_info["category"] = cat_prop["select"].get("name", "")
                        
                        # 症状の抽出
                        symptoms_prop = node_properties.get("症状", {})
                        if symptoms_prop.get("type") == "multi_select":
                            node_info["symptoms"] = [item.get("name", "") for item in symptoms_prop.get("multi_select", [])]
                        
                        case_info["related_nodes"].append(node_info)
                    except Exception as e:
                        st.warning(f"診断ノード情報の取得に失敗: {e}")
            
            repair_cases.append(case_info)
        

# 知識ベースの読み込み
@lru_cache(maxsize=1)
def load_knowledge_base():
    """テキストファイルから知識ベースを読み込み（データアクセス層を使用）"""
    data_access = ensure_data_access()
    st = ensure_streamlit()
    
    if data_access['available']:
        return data_access['knowledge_base_manager'].knowledge_base
    else:
        if st:
            st.error("❌ データアクセス層が利用できません")
        return {}

def get_water_pump_info(query):
    """水道ポンプ専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    st = ensure_streamlit()
    
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_water_pump_info(query)
    else:
        if st:
            st.error("❌ データアクセス層が利用できません")
        return None

def format_response(relevant_info, query, category, icon, color, title):
    """汎用レスポンスフォーマッター"""
    if not relevant_info:
        return None
    
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid {color};">
        <h4 style="color: {color}; margin-bottom: 15px;">{icon} {title}</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーの{category}は重要な設備です。適切な点検・メンテナンスが長期間の使用には欠かせません。</p>
    </div>
    """
    
    return html_content

def format_water_pump_response(relevant_info, query):
    """水道ポンプ情報をフォーマット済みHTMLで返す"""
    return format_response(relevant_info, query, "水道ポンプシステム", "💧", "#17a2b8", "水道ポンプ・給水システム修理アドバイス")

def get_body_damage_info(query):
    """車体外装の破損専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_body_damage_info(query)
    else:
        safe_st_call('error', "❌ データアクセス層が利用できません")
        return None

def format_body_damage_response(relevant_info, query):
    """車体外装の破損情報をフォーマット済みHTMLで返す"""
    return format_response(relevant_info, query, "車体外装", "🚗", "#dc3545", "車体外装の破損・ボディ修理アドバイス")

def get_indoor_led_info(query):
    """室内LED専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_indoor_led_info(query)
    else:
        safe_st_call('error', "❌ データアクセス層が利用できません")
        return None

def format_indoor_led_response(relevant_info, query):
    """室内LED情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # 室内LED専用のHTMLフォーマット
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #ffc107;">
        <h4 style="color: #ffc107; margin-bottom: 15px;">💡 室内LED・照明システム修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーの室内LED照明は、低消費電力で明るく、バッテリーに優しい照明システムです。適切な点検・交換で快適な室内環境を維持できます。</p>
    </div>
    """
    
    return html_content

def get_external_power_info(query):
    """外部電源専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_external_power_info(query)
    else:
        safe_st_call('error', "❌ データアクセス層が利用できません")
        return None

def format_external_power_response(relevant_info, query):
    """外部電源情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # 外部電源専用のHTMLフォーマット
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #28a745;">
        <h4 style="color: #28a745; margin-bottom: 15px;">🔌 外部電源・AC入力システム修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーの外部電源システムは、AC100Vコンセントからの電源供給とバッテリー充電の要となる重要な設備です。安全な接続と適切な管理が重要です。</p>
    </div>
    """
    
    return html_content

def get_noise_info(query):
    """異音専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_noise_info(query)
    else:
        safe_st_call('error', "❌ データアクセス層が利用できません")
        return None

def format_noise_response(relevant_info, query):
    """異音情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # 異音専用のHTMLフォーマット
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #6f42c1;">
        <h4 style="color: #6f42c1; margin-bottom: 15px;">🔊 異音・騒音トラブル修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーの異音・騒音トラブルは、各部品の摩耗や緩み、オイル不足などが原因となることが多いです。適切な診断と対処で快適な走行・停車環境を維持できます。</p>
    </div>
    """
    
    return html_content

def get_tire_info(query):
    """タイヤ専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_tire_info(query)
    else:
        safe_st_call('error', "❌ データアクセス層が利用できません")
        return None

def format_tire_response(relevant_info, query):
    """タイヤ情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # タイヤ専用のHTMLフォーマット
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #6f42c1;">
        <h4 style="color: #6f42c1; margin-bottom: 15px;">🛞 タイヤ・足回りメンテナンス修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーのタイヤは、重量のある車両と長距離走行に耐える重要な部品です。定期的な点検と適切なメンテナンスで安全な走行を確保できます。</p>
    </div>
    """
    
    return html_content

def get_solar_panel_info(query):
    """ソーラーパネル専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_solar_panel_info(query)
    else:
        safe_st_call('error', "❌ データアクセス層が利用できません")
        return None

def format_solar_panel_response(relevant_info, query):
    """ソーラーパネル情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # ソーラーパネル専用のHTMLフォーマット
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #ffc107;">
        <h4 style="color: #ffc107; margin-bottom: 15px;">☀️ ソーラーパネル・発電システム修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーのソーラーパネルシステムは、走行や停車環境に左右されやすく、適切な設置・点検・修理が重要です。MPPT/PWMコントローラーとの組み合わせで効率的な発電が可能です。</p>
    </div>
    """
    
    return html_content

def get_sub_battery_info(query):
    """サブバッテリー専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_sub_battery_info(query)
    else:
        safe_st_call('error', "❌ データアクセス層が利用できません")
        return None

def format_sub_battery_response(relevant_info, query):
    """サブバッテリー情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # サブバッテリー専用のHTMLフォーマット
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #dc3545;">
        <h4 style="color: #dc3545; margin-bottom: 15px;">🔋 サブバッテリー・蓄電システム修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーのサブバッテリーは、停車時の電源供給とエンジン充電システムの中核を担う重要な設備です。適切な管理とメンテナンスで長期間の使用が可能です。</p>
    </div>
    """
    
    return html_content

def get_air_conditioner_info(query):
    """エアコン専用テキストデータから情報を取得"""
    try:
        with open("エアコン.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 既存のextract_relevant_knowledge関数を活用
        relevant_info = extract_relevant_knowledge(query, {"エアコン": content})
        
        # フォーマット済みのHTMLを返す
        return format_air_conditioner_response(relevant_info, query)
    except Exception as e:
        return None

def format_air_conditioner_response(relevant_info, query):
    """エアコン情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # エアコン専用のHTMLフォーマット
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #17a2b8;">
        <h4 style="color: #17a2b8; margin-bottom: 15px;">❄️ エアコン・冷暖房システム修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーのエアコンは、12V/24V車載クーラーから3WAY冷暖房まで様々なタイプがあります。コンプレッサーや冷媒システムの適切なメンテナンスが重要です。</p>
    </div>
    """
    
    return html_content

def get_inverter_info(query):
    """インバーター専用テキストデータから情報を取得"""
    try:
        with open("インバーター.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 既存のextract_relevant_knowledge関数を活用
        relevant_info = extract_relevant_knowledge(query, {"インバーター": content})
        
        # フォーマット済みのHTMLを返す
        return format_inverter_response(relevant_info, query)
    except Exception as e:
        return None

def format_inverter_response(relevant_info, query):
    """インバーター情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # インバーター専用のHTMLフォーマット
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #6c757d;">
        <h4 style="color: #6c757d; margin-bottom: 15px;">⚡ インバーター・電源変換装置修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーのインバーターは、DC12V/24VからAC100Vへの電源変換を行う重要な機器です。純正弦波と疑似正弦波の違いを理解し、適切な容量選択と保護回路の確認が重要です。</p>
    </div>
    """
    
    return html_content

def get_window_info(query):
    """ウインドウ専用テキストデータから情報を取得"""
    try:
        with open("ウインドウ.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 既存のextract_relevant_knowledge関数を活用
        relevant_info = extract_relevant_knowledge(query, {"ウインドウ": content})
        
        # フォーマット済みのHTMLを返す
        return format_window_response(relevant_info, query)
    except Exception as e:
        return None

def format_window_response(relevant_info, query):
    """ウインドウ情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # ウインドウ専用のHTMLフォーマット
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #28a745;">
        <h4 style="color: #28a745; margin-bottom: 15px;">🪟 ウインドウ・窓まわり修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
        <p>キャンピングカーのウインドウは、開閉機能とガラス保護が重要な要素です。適切なメンテナンスと修理で快適な居住環境と安全性を確保できます。</p>
    </div>
    """
    
    return html_content

def get_rain_leak_info(query):
    """雨漏り専用テキストデータから情報を取得"""
    try:
        with open("雨漏り.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 既存のextract_relevant_knowledge関数を活用
        relevant_info = extract_relevant_knowledge(query, {"雨漏り": content})
        
        # フォーマット済みのHTMLを返す
        return format_rain_leak_response(relevant_info, query)
    except Exception as e:
        return None

def format_rain_leak_response(relevant_info, query):
    """雨漏り情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # キーワードに基づいて動的にコンテンツを生成
    query_lower = query.lower()
    
    # キーワードマッチングによる動的コンテンツ
    matched_symptoms = []
    matched_costs = []
    matched_tools = []
    matched_steps = []
    matched_warnings = []
    
    # 症状のマッチング
    if any(word in query_lower for word in ["天井", "水滴", "落ちる"]):
        matched_symptoms.append("天井から水滴が落ちる")
    if any(word in query_lower for word in ["壁面", "染み", "水の染み"]):
        matched_symptoms.append("壁面に水の染みができる")
    if any(word in query_lower for word in ["窓枠", "窓", "ウインドウ"]):
        matched_symptoms.append("窓枠から水が浸入する")
    if any(word in query_lower for word in ["ドア", "ドア周辺"]):
        matched_symptoms.append("ドア周辺から水が入る")
    if any(word in query_lower for word in ["ルーフベント", "ベント"]):
        matched_symptoms.append("ルーフベント周辺の水漏れ")
    if any(word in query_lower for word in ["エアコン", "ダクト"]):
        matched_symptoms.append("エアコンダクト周辺の水漏れ")
    
    # 費用のマッチング
    if any(word in query_lower for word in ["シーリング", "コーキング"]):
        matched_costs.append("シーリング材交換：5,000〜15,000円")
    if any(word in query_lower for word in ["パッキン", "窓枠"]):
        matched_costs.append("窓枠パッキン交換：3,000〜8,000円")
    if any(word in query_lower for word in ["ドア", "ドアパッキン"]):
        matched_costs.append("ドアパッキン交換：5,000〜12,000円")
    if any(word in query_lower for word in ["天井", "天井修理"]):
        matched_costs.append("天井修理：20,000〜50,000円")
    if any(word in query_lower for word in ["配管", "配管修理"]):
        matched_costs.append("配管修理：8,000〜25,000円")
    if any(word in query_lower for word in ["防水", "防水処理"]):
        matched_costs.append("防水処理：15,000〜35,000円")
    
    # 工具のマッチング
    if any(word in query_lower for word in ["シーリング", "コーキング"]):
        matched_tools.append("シーリングガン、カッターナイフ、スクレーパー")
    if any(word in query_lower for word in ["パッキン", "交換"]):
        matched_tools.append("ドライバーセット、パッキン類")
    if any(word in query_lower for word in ["防水", "テープ"]):
        matched_tools.append("防水テープ、アルミテープ")
    if any(word in query_lower for word in ["清掃", "掃除"]):
        matched_tools.append("ブラシ、清掃用具")
    
    # 修理手順のマッチング
    if any(word in query_lower for word in ["診断", "確認", "点検"]):
        matched_steps.append("1. 水漏れ箇所の特定 - 水の流れを追跡、外側からの浸入経路確認")
    if any(word in query_lower for word in ["応急", "緊急", "一時"]):
        matched_steps.append("2. 応急処置 - 水の受け皿設置、タオルでの水受け、テープでの応急止水")
    if any(word in query_lower for word in ["修理", "本格", "交換"]):
        matched_steps.append("3. 本格修理 - 古いシーリング材の除去、新しいシーリング材の施工")
    if any(word in query_lower for word in ["予防", "メンテナンス", "点検"]):
        matched_steps.append("4. 予防策 - 定期的なシーリング材の点検、パッキンの劣化確認")
    
    # 注意事項のマッチング
    if any(word in query_lower for word in ["高所", "屋根", "ルーフ"]):
        matched_warnings.append("高所作業時の安全確保")
    if any(word in query_lower for word in ["電気", "電装", "配線"]):
        matched_warnings.append("電気系統への水の接触防止")
    if any(word in query_lower for word in ["工具", "道具"]):
        matched_warnings.append("適切な工具の使用")
    if any(word in query_lower for word in ["乾燥", "水拭き"]):
        matched_warnings.append("作業後の水拭きと乾燥")
    
    # HTMLコンテンツの生成
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #dc3545;">
        <h4 style="color: #dc3545; margin-bottom: 15px;">🌧️ 雨漏り・水漏れ修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
    """
    
    # マッチした症状を表示
    if matched_symptoms:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #dc3545; margin-bottom: 10px;">🔍 該当する症状</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for symptom in matched_symptoms:
            html_content += f'<li style="margin: 5px 0;">{symptom}</li>'
        html_content += "</ul></div>"
    
    # マッチした費用を表示
    if matched_costs:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #dc3545; margin-bottom: 10px;">💰 関連する修理費用目安</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for cost in matched_costs:
            html_content += f'<li style="margin: 5px 0;">{cost}</li>'
        html_content += "</ul></div>"
    
    # マッチした工具を表示
    if matched_tools:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #dc3545; margin-bottom: 10px;">🔧 必要な工具・材料</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for tool in matched_tools:
            html_content += f'<li style="margin: 5px 0;">{tool}</li>'
        html_content += "</ul></div>"
    
    # マッチした修理手順を表示
    if matched_steps:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #dc3545; margin-bottom: 10px;">📝 関連する修理手順</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for step in matched_steps:
            html_content += f'<li style="margin: 5px 0;">{step}</li>'
        html_content += "</ul></div>"
    
    # マッチした注意事項を表示
    if matched_warnings:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #dc3545; margin-bottom: 10px;">⚠️ 安全上の注意事項</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for warning in matched_warnings:
            html_content += f'<li style="margin: 5px 0;">{warning}</li>'
        html_content += "</ul></div>"
    
    html_content += "</div>"
    
    return html_content

def get_toilet_info(query):
    """トイレ専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_toilet_info(query)
    else:
        safe_st_call('error', "❌ データアクセス層が利用できません")
        return None

def format_toilet_response(relevant_info, query):
    """トイレ情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # キーワードに基づいて動的にコンテンツを生成
    query_lower = query.lower()
    
    # キーワードマッチングによる動的コンテンツ
    matched_symptoms = []
    matched_costs = []
    matched_tools = []
    matched_steps = []
    matched_warnings = []
    
    # 症状のマッチング
    if any(word in query_lower for word in ["ファン", "回らない", "作動しない"]):
        matched_symptoms.append("トイレのファンが回らない")
    if any(word in query_lower for word in ["水", "流れない", "流れが弱い"]):
        matched_symptoms.append("水が流れない・流れが弱い")
    if any(word in query_lower for word in ["フラッパー", "閉まらない"]):
        matched_symptoms.append("フラッパーが閉まらない")
    if any(word in query_lower for word in ["汚れ", "付着"]):
        matched_symptoms.append("便器に汚れが付着する")
    if any(word in query_lower for word in ["臭い", "悪臭"]):
        matched_symptoms.append("悪臭がする")
    if any(word in query_lower for word in ["ポンプ", "作動しない"]):
        matched_symptoms.append("ポンプが作動しない")
    if any(word in query_lower for word in ["シール", "パッキン", "劣化"]):
        matched_symptoms.append("シール・パッキンの劣化")
    
    # 費用のマッチング
    if any(word in query_lower for word in ["ポンプ", "交換"]):
        matched_costs.append("ポンプ交換：8,000〜15,000円")
    if any(word in query_lower for word in ["シール", "パッキン"]):
        matched_costs.append("シール・パッキン交換：3,000〜8,000円")
    if any(word in query_lower for word in ["フラッパー", "交換"]):
        matched_costs.append("フラッパー交換：5,000〜12,000円")
    if any(word in query_lower for word in ["電源", "配線"]):
        matched_costs.append("電源部修理：4,000〜10,000円")
    if any(word in query_lower for word in ["清掃", "メンテナンス"]):
        matched_costs.append("清掃・メンテナンス：2,000〜5,000円")
    if any(word in query_lower for word in ["ヒューズ", "交換"]):
        matched_costs.append("ヒューズ交換：1,000〜2,000円")
    
    # 工具のマッチング
    if any(word in query_lower for word in ["ポンプ", "交換"]):
        matched_tools.append("ドライバーセット、ポンプ、配線材料")
    if any(word in query_lower for word in ["シール", "パッキン"]):
        matched_tools.append("パッキン類、Oリング")
    if any(word in query_lower for word in ["清掃", "洗浄"]):
        matched_tools.append("トイレ用洗剤、消臭剤、清掃用具")
    if any(word in query_lower for word in ["ヒューズ", "電源"]):
        matched_tools.append("ヒューズ、配線材料、テスター")
    
    # 修理手順のマッチング
    if any(word in query_lower for word in ["診断", "確認", "点検"]):
        matched_steps.append("1. ポンプの故障診断 - 電源の確認、ポンプの作動音確認")
    if any(word in query_lower for word in ["ポンプ", "交換"]):
        matched_steps.append("2. ポンプの交換 - 古いポンプの取り外し、新しいポンプの取り付け")
    if any(word in query_lower for word in ["シール", "パッキン"]):
        matched_steps.append("3. シール・パッキンの交換 - 古いシールの除去、新しいシールの取り付け")
    if any(word in query_lower for word in ["清掃", "メンテナンス"]):
        matched_steps.append("4. 清掃・メンテナンス - 便器の清掃、配管の清掃、消臭処理")
    
    # 注意事項のマッチング
    if any(word in query_lower for word in ["汚物", "処理"]):
        matched_warnings.append("汚物の適切な処理")
    if any(word in query_lower for word in ["清掃剤", "洗剤"]):
        matched_warnings.append("清掃剤の安全な使用")
    if any(word in query_lower for word in ["電源", "電気"]):
        matched_warnings.append("電源の安全な取り扱い")
    if any(word in query_lower for word in ["換気", "通気"]):
        matched_warnings.append("換気の確保")
    
    # HTMLコンテンツの生成
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #6f42c1;">
        <h4 style="color: #6f42c1; margin-bottom: 15px;">🚽 トイレ修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
    """
    
    # マッチした症状を表示
    if matched_symptoms:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #6f42c1; margin-bottom: 10px;">🔍 該当する症状</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for symptom in matched_symptoms:
            html_content += f'<li style="margin: 5px 0;">{symptom}</li>'
        html_content += "</ul></div>"
    
    # マッチした費用を表示
    if matched_costs:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #6f42c1; margin-bottom: 10px;">💰 関連する修理費用目安</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for cost in matched_costs:
            html_content += f'<li style="margin: 5px 0;">{cost}</li>'
        html_content += "</ul></div>"
    
    # マッチした工具を表示
    if matched_tools:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #6f42c1; margin-bottom: 10px;">🔧 必要な工具・材料</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for tool in matched_tools:
            html_content += f'<li style="margin: 5px 0;">{tool}</li>'
        html_content += "</ul></div>"
    
    # マッチした修理手順を表示
    if matched_steps:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #6f42c1; margin-bottom: 10px;">📝 関連する修理手順</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for step in matched_steps:
            html_content += f'<li style="margin: 5px 0;">{step}</li>'
        html_content += "</ul></div>"
    
    # マッチした注意事項を表示
    if matched_warnings:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #6f42c1; margin-bottom: 10px;">⚠️ 安全上の注意事項</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for warning in matched_warnings:
            html_content += f'<li style="margin: 5px 0;">{warning}</li>'
        html_content += "</ul></div>"
    
    html_content += "</div>"
    
    return html_content

def get_battery_info(query):
    """バッテリー専用テキストデータから情報を取得（データアクセス層を使用）"""
    data_access = ensure_data_access()
    if data_access['available']:
        return data_access['knowledge_base_manager'].get_battery_info(query)
    else:
        safe_st_call('error', "❌ データアクセス層が利用できません")
        return None

def format_battery_response(relevant_info, query):
    """バッテリー情報をフォーマット済みHTMLで返す"""
    if not relevant_info:
        return None
    
    # キーワードに基づいて動的にコンテンツを生成
    query_lower = query.lower()
    
    # キーワードマッチングによる動的コンテンツ
    matched_symptoms = []
    matched_costs = []
    matched_tools = []
    matched_steps = []
    matched_warnings = []
    
    # 症状のマッチング
    if any(word in query_lower for word in ["充電されない", "充電され", "not charging"]):
        matched_symptoms.append("バッテリーが充電されない")
    if any(word in query_lower for word in ["充電が遅い", "遅い", "slow charge"]):
        matched_symptoms.append("充電が遅い・充電時間が長い")
    if any(word in query_lower for word in ["電圧", "低い", "low voltage"]):
        matched_symptoms.append("バッテリーの電圧が低い")
    if any(word in query_lower for word in ["放電", "すぐに", "quick discharge"]):
        matched_symptoms.append("バッテリーがすぐに放電する")
    if any(word in query_lower for word in ["端子", "腐食", "corrosion"]):
        matched_symptoms.append("バッテリー端子が腐食している")
    if any(word in query_lower for word in ["バッテリー液", "電解液", "electrolyte"]):
        matched_symptoms.append("バッテリー液が減っている")
    if any(word in query_lower for word in ["膨らん", "swelling"]):
        matched_symptoms.append("バッテリーが膨らんでいる")
    if any(word in query_lower for word in ["充電器", "charger"]):
        matched_symptoms.append("充電器が動作しない")
    
    # 費用のマッチング
    if any(word in query_lower for word in ["バッテリー", "交換"]):
        matched_costs.append("バッテリー交換：15,000〜30,000円")
    if any(word in query_lower for word in ["端子", "清掃", "交換"]):
        matched_costs.append("端子清掃・交換：3,000〜8,000円")
    if any(word in query_lower for word in ["充電器", "修理"]):
        matched_costs.append("充電器修理：8,000〜15,000円")
    if any(word in query_lower for word in ["配線", "修理"]):
        matched_costs.append("配線修理：5,000〜12,000円")
    if any(word in query_lower for word in ["バッテリー液", "補充"]):
        matched_costs.append("バッテリー液補充：1,000〜2,000円")
    if any(word in query_lower for word in ["点検", "診断"]):
        matched_costs.append("充電システム点検：3,000〜6,000円")
    if any(word in query_lower for word in ["ヒューズ", "交換"]):
        matched_costs.append("ヒューズ交換：500〜1,500円")
    
    # 工具のマッチング
    if any(word in query_lower for word in ["診断", "測定", "テスター"]):
        matched_tools.append("バッテリーテスター、電圧計")
    if any(word in query_lower for word in ["端子", "清掃", "クリーナー"]):
        matched_tools.append("端子クリーナー、清掃用具")
    if any(word in query_lower for word in ["バッテリー", "交換"]):
        matched_tools.append("ドライバーセット、端子類")
    if any(word in query_lower for word in ["バッテリー液", "補充"]):
        matched_tools.append("バッテリー液、漏斗")
    if any(word in query_lower for word in ["充電器", "修理"]):
        matched_tools.append("充電器、配線材料")
    if any(word in query_lower for word in ["ヒューズ", "リレー"]):
        matched_tools.append("ヒューズ、リレー、テスター")
    
    # 修理手順のマッチング
    if any(word in query_lower for word in ["診断", "確認", "点検"]):
        matched_steps.append("1. バッテリーの診断 - 電圧測定（12.6V以上が正常）、端子の腐食確認")
    if any(word in query_lower for word in ["端子", "清掃", "交換"]):
        matched_steps.append("2. 端子の清掃・交換 - 古い端子の取り外し、腐食部分の清掃")
    if any(word in query_lower for word in ["バッテリー", "交換"]):
        matched_steps.append("3. バッテリーの交換 - 古いバッテリーの取り外し、新しいバッテリーの取り付け")
    if any(word in query_lower for word in ["充電", "システム", "点検"]):
        matched_steps.append("4. 充電システムの点検 - 充電器の動作確認、配線の接続確認")
    
    # 注意事項のマッチング
    if any(word in query_lower for word in ["バッテリー液", "電解液"]):
        matched_warnings.append("バッテリー液は危険です。直接触れないでください")
    if any(word in query_lower for word in ["充電", "火花"]):
        matched_warnings.append("充電中の火花に注意")
    if any(word in query_lower for word in ["工具", "道具"]):
        matched_warnings.append("適切な工具の使用")
    if any(word in query_lower for word in ["換気", "通気"]):
        matched_warnings.append("換気の確保")
    
    # HTMLコンテンツの生成
    html_content = f"""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #ffc107;">
        <h4 style="color: #ffc107; margin-bottom: 15px;">🔋 バッテリー修理アドバイス</h4>
        <p><strong>検索キーワード:</strong> {query}</p>
    """
    
    # マッチした症状を表示
    if matched_symptoms:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #ffc107; margin-bottom: 10px;">🔍 該当する症状</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for symptom in matched_symptoms:
            html_content += f'<li style="margin: 5px 0;">{symptom}</li>'
        html_content += "</ul></div>"
    
    # マッチした費用を表示
    if matched_costs:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #ffc107; margin-bottom: 10px;">💰 関連する修理費用目安</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for cost in matched_costs:
            html_content += f'<li style="margin: 5px 0;">{cost}</li>'
        html_content += "</ul></div>"
    
    # マッチした工具を表示
    if matched_tools:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #ffc107; margin-bottom: 10px;">🔧 必要な工具・材料</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for tool in matched_tools:
            html_content += f'<li style="margin: 5px 0;">{tool}</li>'
        html_content += "</ul></div>"
    
    # マッチした修理手順を表示
    if matched_steps:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #ffc107; margin-bottom: 10px;">📝 関連する修理手順</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for step in matched_steps:
            html_content += f'<li style="margin: 5px 0;">{step}</li>'
        html_content += "</ul></div>"
    
    # マッチした注意事項を表示
    if matched_warnings:
        html_content += f"""
        <div style="margin: 15px 0;">
            <h5 style="color: #ffc107; margin-bottom: 10px;">⚠️ 安全上の注意事項</h5>
            <ul style="margin: 0; padding-left: 20px;">
        """
        for warning in matched_warnings:
            html_content += f'<li style="margin: 5px 0;">{warning}</li>'
        html_content += "</ul></div>"
    
    html_content += "</div>"
    
    return html_content

def extract_relevant_knowledge(query, knowledge_base):
    """クエリに関連する知識を抽出（改善版）"""
    query_lower = query.lower()
    relevant_content = []
    
    # 拡張されたキーワードマッピング（バッテリー充電問題を強化）
    keyword_mapping = {
        "インバーター": ["インバーター", "inverter", "dc-ac", "正弦波", "電源変換", "ac", "dc", "電源"],
        "バッテリー": [
            "バッテリー", "battery", "サブバッテリー", "充電", "電圧", "電圧低下", "充電器",
            "充電されない", "充電できない", "走行充電", "充電ライン", "アイソレーター", 
            "dc-dcコンバーター", "切替リレー", "リレー", "ヒューズ切れ", "充電不良",
            "電圧が上がらない", "12.5v", "12.6v", "13.5v", "満充電", "残量", "容量"
        ],
        "トイレ": ["トイレ", "toilet", "カセット", "マリン", "フラッパー", "便器", "水洗"],
        "ルーフベント": ["ルーフベント", "換気扇", "ファン", "マックスファン", "vent", "換気", "排気"],
        "水道": ["水道", "ポンプ", "給水", "水", "water", "pump", "シャワー", "蛇口"],
        "冷蔵庫": [
            "冷蔵庫", "冷凍", "コンプレッサー", "refrigerator", "冷える", "冷却",
            "3way", "3-way", "12v冷蔵庫", "24v冷蔵庫", "dometic", "waeco", "engel",
            "arb", "national luna", "ペルチェ式", "吸収式", "アンモニア臭",
            "ドアパッキン", "温度センサー", "サーミスタ", "エラーコード", "E4",
            "バッテリー消費", "消費電力", "庫内温度", "冷凍室", "野菜室",
            "ドアラッチ", "ヒューズ切れ", "電源切替", "ガスモード", "点火プラグ"
        ],
        "ガス": ["ガス", "gas", "コンロ", "ヒーター", "ff", "プロパン", "lpg"],
        "FFヒーター": [
            # 基本名称
            "FFヒーター", "ffヒーター", "FFヒータ", "ffヒータ", "FF heater", "ff heater",
            "FFヒーダー", "ffヒーダー", "FFヒーダ", "ffヒーダ",
            # 英語表記・略語
            "forced fan heater", "Forced Fan Heater", "FFH", "ffh",
            "車載ヒーター", "車載暖房", "キャンピングカーヒーター", "RVヒーター",
            # メーカー名・製品名
            "ベバスト", "webasto", "Webasto", "ウェバスト", "ウェバスト",
            "ミクニ", "mikuni", "Mikuni", "日本ミクニ",
            "LVYUAN", "lvyuan", "リョクエン", "リョクエン",
            "エバポール", "Eberspacher", "エバスポッチャー",
            "プラネー", "Planar", "プラナー",
            # 症状・トラブル
            "点火しない", "点火不良", "つかない", "点かない", "起動しない", "動かない",
            "白煙", "煙が出る", "煙がでる", "白い煙", "黒い煙", "煙突", "排気",
            "異音", "うるさい", "音が大きい", "ファン音", "燃焼音", "ポンプ音",
            "エラー", "エラーコード", "E13", "エラー表示", "リモコンエラー",
            "燃料", "燃料切れ", "燃料不足", "燃料ポンプ", "燃料フィルター",
            "燃焼", "燃焼不良", "燃焼室", "グロープラグ", "点火プラグ",
            "温度", "温風", "暖房", "暖かくならない", "温度調節",
            "電源", "電圧", "ヒューズ", "配線", "リモコン",
            "換気", "吸気", "排気", "一酸化炭素", "CO", "安全装置",
            "設置", "取り付け", "配管", "煙突設置", "DIY",
            "メンテナンス", "清掃", "分解", "オーバーホール", "点検",
            # 関連用語
            "暖房器", "強制送風", "熱交換器", "ファン", "温度制御",
            "自動停止", "安全装置", "燃料タンク", "配管工事"
        ],
        "電気": ["電気", "led", "照明", "電装", "electrical", "配線", "ヒューズ", "fuse"],
        "排水タンク": [
            "排水タンク", "グレータンク", "汚水", "排水", "drain", "tank", "グレー",
            "thetford", "dometic", "sealand", "valterra", "バルブハンドル", "Oリング",
            "レベルセンサー", "Pトラップ", "封水", "悪臭", "逆流", "凍結", "不凍剤",
            "排水ホース", "カムロック", "通気ベンチ", "バイオフィルム", "排水口キャップ"
        ],
        "電装系": [
            "電装系", "電気", "配線", "ヒューズ", "led", "照明", "electrical", "電源",
            "バッテリー", "インバーター", "victron", "samlex", "renogy", "goal zero",
            "bluetti", "調光器", "PWM", "100Vコンセント", "サブバッテリー", "残量計",
            "シャント抵抗", "DCシガーソケット", "USBポート", "5Vレギュレーター",
            "電子レンジ", "突入電流", "電圧降下", "配線太径", "外部電源", "AC入力"
        ],
        "雨漏り": ["雨漏り", "rain", "leak", "防水", "シール", "水漏れ", "水滴"],
        "異音": ["異音", "音", "騒音", "振動", "noise", "うるさい", "ガタガタ"],
        "ドア": ["ドア", "door", "窓", "window", "開閉", "開かない", "閉まらない"],
        "タイヤ": [
            "タイヤ", "tire", "パンク", "空気圧", "摩耗", "交換", "cp規格", "lt規格",
            "ミシュラン", "ブリヂストン", "ダンロップ", "ヨコハマ", "バースト", "偏摩耗",
            "亀裂", "ひび割れ", "バランス", "ローテーション", "過積載", "経年劣化",
            "ホイール", "損傷", "変形", "psi", "kpa", "kgf/cm2", "パンク保証"
        ],
        "エアコン": ["エアコン", "aircon", "冷房", "暖房", "温度", "設定"],
        "家具": [
            "家具", "テーブル", "椅子", "収納", "棚", "furniture", "ベッド", "ソファ",
            "キャビネット", "引き出し", "ダイネット", "ラッチ", "ヒンジ", "化粧板",
            "床下収納", "フロアハッチ", "スライドクローゼット", "マグネットキャッチ",
            "耐振動ラッチ", "金属ダンパー", "樹脂ブッシュ", "木工パテ", "消臭処理"
        ],
        "外装": ["外装", "塗装", "傷", "へこみ", "錆", "corrosion"],
        "排水": ["排水", "タンク", "汚水", "waste", "tank", "空にする"],
        "ソーラー": [
            "ソーラー", "solar", "パネル", "発電", "太陽光", "チャージコントローラー", "pwm", "mppt",
            "ソーラーパネル", "太陽光発電", "トイファクトリー", "京セラ", "長州産業", "kyocera", "choshu",
            "発電量", "変換効率", "バッテリー充電", "影の影響", "表面汚れ", "ひび割れ", "配線断線",
            "雷故障", "老朽化", "角度調整", "設置工事", "メンテナンス", "清掃", "診断"
        ],
        "外部電源": ["外部電源", "ac", "コンセント", "電源", "接続"],
        "室内LED": ["led", "照明", "電球", "暗い", "点かない", "light"],
        "水道ポンプ": [
            "水道ポンプ", "給水システム", "ポンプユニット", "給水設備", "配管・水回り",
            "ポンプ", "給水", "吐水", "吸水", "水圧", "流量", "故障", "モーター", "漏水",
            "water pump", "water system", "pump unit", "water supply", "plumbing",
            "water pressure", "flow rate", "motor failure", "leak", "water leak",
            "ポンプ停止", "ポンプ音", "異音", "振動", "水が出ない", "水が止まらない",
            "電圧", "ヒューズ切れ", "配線", "オーバーホール", "メンテナンス", "清掃",
            "水タンク", "給水ホース", "フィルター", "逆止弁", "圧力スイッチ",
            "プライミング", "エアロック", "キャビテーション", "過負荷", "焼損"
        ],
        "車体外装の破損": [
            "車体外装", "外装破損", "キズ", "ヘコミ", "塗装剥がれ", "FRP", "パネル交換",
            "修理費用", "車体補修", "ボディ修理", "外装パネル", "車体修理", "外装補修",
            "ボディメンテナンス", "body damage", "exterior damage", "panel repair",
            "FRP repair", "paint damage", "dent", "scratch", "crack", "fiberglass",
            "車体損傷", "外装損傷", "パネル損傷", "塗装損傷", "補修", "修復",
            "コーティング", "下地処理", "プライマー", "中塗り", "上塗り", "研磨",
            "サンドペーパー", "バフ研磨", "ポリッシュ", "ワックス", "UV劣化",
            "クラック", "ひび割れ", "剥離", "膨れ", "変色", "退色", "酸化"
        ],
        "室内LED": [
            "室内LED", "照明", "車内ライト", "電球交換", "明るさ", "消費電力", "点灯不良",
            "フリッカー", "ちらつき", "配線", "電圧", "照明システム", "室内電装",
            "車内照明", "インテリアライト", "indoor LED", "interior lighting", "lighting system",
            "LED bulb", "light replacement", "brightness", "power consumption", "flickering",
            "wiring", "voltage", "dimming", "調光", "スイッチ", "電源", "ヒューズ",
            "点滅", "暗い", "明るすぎる", "色温度", "白色", "暖色", "冷色",
            "LEDストリップ", "テープライト", "スポットライト", "ダウンライト",
            "天井照明", "読書灯", "ナイトランプ", "アンビエントライト"
        ],
        "外部電源": [
            "外部電源", "AC100V", "コンセント", "電圧", "ブレーカー", "過電流", "漏電",
            "充電", "インバーター", "電装トラブル", "AC入力", "電源システム", "外部コンセント",
            "電装設備", "external power", "AC input", "power system", "outlet", "voltage",
            "breaker", "overcurrent", "leakage", "charging", "inverter", "electrical trouble",
            "電源入力", "ACアダプター", "電源ケーブル", "接地", "アース", "感電",
            "ショート", "断線", "接触不良", "電源切替", "自動切替", "手動切替",
            "バッテリー充電", "充電器", "電源管理", "負荷管理", "電力消費", "待機電力"
        ],
        "異音": [
            "異音", "騒音", "ガタガタ音", "キュルキュル音", "ゴトゴト音", "エンジン音",
            "モーター音", "振動", "異常音", "金属音", "騒音トラブル", "機械音",
            "車内異常音", "振動・ノイズ", "noise", "vibration", "abnormal sound", "mechanical noise",
            "rattling", "squeaking", "grinding", "engine noise", "motor noise", "metal sound",
            "うるさい", "音が大きい", "音がする", "音が出る", "音が聞こえる", "音がうるさい",
            "ファン音", "ポンプ音", "コンプレッサー音", "ヒーター音", "換気扇音", "ファンベルト",
            "ベアリング", "軸受け", "オイル切れ", "グリス不足", "摩耗", "緩み",
            "共振", "ハウリング", "ピーキング", "エコー", "反響音", "室内音響"
        ],
        "タイヤ": [
            "タイヤ", "パンク", "空気圧", "摩耗", "ひび割れ", "ホイール", "スペアタイヤ",
            "ローテーション", "グリップ", "交換", "足回り", "ホイール・タイヤ", "車両走行系",
            "タイヤメンテナンス", "tire", "wheel", "puncture", "air pressure", "wear", "crack",
            "spare tire", "rotation", "grip", "replacement", "suspension", "chassis",
            "ミシュラン", "ブリヂストン", "ダンロップ", "ヨコハマ", "バースト", "偏摩耗",
            "亀裂", "バランス", "過積載", "経年劣化", "損傷", "変形", "psi", "kpa", "kgf/cm2",
            "パンク保証", "タイヤサイズ", "扁平率", "リム径", "トレッド", "サイドウォール",
            "スリップサイン", "溝深さ", "摩耗限界", "タイヤ交換", "タイヤ点検"
        ],
        "ソーラーパネル": [
            "ソーラーパネル", "太陽光", "発電", "充電", "バッテリー充電", "発電効率", "配線",
            "コントローラー", "MPPT", "PWM", "設置", "故障", "発電システム", "太陽光発電",
            "充電システム", "電装設備", "solar panel", "solar power", "solar energy", "photovoltaic",
            "PV", "generation", "charging", "battery charging", "efficiency", "wiring", "controller",
            "installation", "failure", "power system", "electrical equipment",
            "トイファクトリー", "京セラ", "長州産業", "kyocera", "choshu", "シャープ", "sharp",
            "発電量", "変換効率", "影の影響", "表面汚れ", "ひび割れ", "配線断線", "雷故障",
            "老朽化", "角度調整", "設置工事", "メンテナンス", "清掃", "診断", "太陽電池",
            "セル", "モジュール", "アレイ", "インバーター", "充電制御", "過充電保護"
        ],
        "サブバッテリー": [
            "サブバッテリー", "充電", "放電", "劣化", "電圧", "容量", "過放電", "走行充電",
            "バッテリー交換", "寿命", "走行充電システム", "電装バッテリー", "蓄電システム",
            "電源設備", "sub battery", "auxiliary battery", "secondary battery", "charging", "discharging",
            "degradation", "voltage", "capacity", "over-discharge", "engine charging", "battery replacement",
            "life span", "charging system", "electrical battery", "storage system", "power equipment",
            "アイソレーター", "切替リレー", "DC-DCコンバーター", "バッテリーマネージャー", "残量計",
            "12V", "24V", "リチウム", "鉛蓄電池", "AGM", "GEL", "リチウムイオン", "LiFePO4",
            "バッテリー液", "端子", "腐食", "ヒューズ", "配線", "充電器", "インバーター",
            "過充電", "バランス充電", "保護回路", "BMS", "バッテリーモニター"
        ],
        "エアコン": [
            "エアコン", "冷房", "暖房", "コンプレッサー", "ガス漏れ", "エアコンフィルター", "風量",
            "温度調整", "冷媒", "故障", "冷暖房システム", "車載クーラー", "室内空調",
            "クライメートコントロール", "air conditioner", "AC", "aircon", "cooling", "heating",
            "compressor", "gas leak", "filter", "air flow", "temperature control", "refrigerant",
            "failure", "HVAC", "climate control", "vehicle cooler", "interior climate",
            "12Vエアコン", "24Vエアコン", "ドメスティック", "ウェバスト", "トルネード", "dometic",
            "waeco", "ウェバスト", "webasto", "トルネード", "tornado", "車載クーラー",
            "エバポール", "エバスポッチャー", "eberspacher", "エアロ", "aero", "プラネー", "planar",
            "フロンガス", "R134a", "R410a", "R32", "ガス充填", "オイル交換", "フィルター交換",
            "コンプレッサー交換", "エバポレーター", "コンデンサー", "ドライヤー", "エキスパンションバルブ",
            "温度センサー", "サーモスタット", "リレー", "ヒューズ", "配線", "ファンモーター"
        ],
        "インバーター": [
            "インバーター", "DC-AC変換", "出力", "電圧不安定", "過負荷", "発熱", "配線", "ノイズ",
            "故障", "保護回路", "電源変換装置", "AC/DCコンバーター", "電装機器", "電力システム",
            "inverter", "DC-AC converter", "power conversion", "output", "voltage instability",
            "overload", "heat generation", "wiring", "noise", "failure", "protection circuit",
            "power conversion device", "electrical equipment", "power system",
            "12Vインバーター", "24Vインバーター", "100V出力", "正弦波", "疑似正弦波", "矩形波",
            "純正弦波", "pure sine wave", "modified sine wave", "square wave", "PWM",
            "victron", "samlex", "renogy", "goal zero", "bluetti", "jackery", "anker",
            "電圧保護", "過電流保護", "過熱保護", "低電圧保護", "高電圧保護", "短絡保護",
            "突入電流", "効率", "待機電力", "冷却ファン", "放熱", "ヒートシンク",
            "コンデンサー", "トランス", "FET", "IGBT", "制御回路", "フィードバック"
        ],
        "ウインドウ": [
            "ウインドウ", "窓", "ガラス", "開閉", "網戸", "シーリング", "レール", "破損",
            "結露", "曇り止め", "窓まわり", "開閉部品", "車体外装（窓）", "内装窓設備",
            "window", "glass", "opening", "closing", "screen", "sealing", "rail", "damage",
            "condensation", "anti-fog", "window area", "opening parts", "exterior window", "interior window",
            "サイドウインドウ", "フロントウインドウ", "リアウインドウ", "ルーフウインドウ", "スライド窓",
            "開き窓", "ポップアップ窓", "天窓", "サンルーフ", "ベンチレーション",
            "ガラス交換", "ガラス修理", "レール清掃", "レール交換", "シーリング交換",
            "網戸交換", "網戸修理", "曇り止め剤", "コーティング", "撥水加工",
            "UVカット", "遮熱フィルム", "プライバシーフィルム", "安全フィルム",
            "窓枠", "サッシ", "ヒンジ", "ハンドル", "ロック", "ストッパー",
            "雨漏り", "水漏れ", "気密性", "断熱性", "防音性"
        ],
        "雨漏り": [
            "雨漏り", "水漏れ", "浸水", "漏水", "水浸し", "水滴", "水の染み",
            "rain leak", "water leak", "leakage", "water damage", "drip",
            "天井", "壁面", "窓枠", "ドア周辺", "ルーフベント", "エアコンダクト",
            "配管", "シーリング材", "パッキン", "防水", "防水処理", "シーリング",
            "コーキング", "シリコーン", "防水テープ", "アルミテープ", "ドアパッキン",
            "窓枠パッキン", "防水シート", "ルーフ", "屋根", "継ぎ目", "隙間",
            "シーリングガン", "カッターナイフ", "スクレーパー", "ブラシ",
            "応急処置", "本格修理", "予防策", "点検", "メンテナンス"
        ],
        "トイレ詳細": [
            "トイレ", "便器", "カセット", "マリン", "フラッパー", "ポンプ",
            "toilet", "cassette", "marine", "flapper", "pump",
            "ファン", "水洗", "シール", "パッキン", "悪臭", "清掃",
            "fan", "flush", "seal", "packing", "odor", "cleaning",
            "テトフォード", "ドメスティック", "thetford", "dometic",
            "Oリング", "ヒューズ", "配線", "電源", "自動洗浄", "排水"
        ],
        "ガスコンロ": [
            "ガスコンロ", "ガス", "コンロ", "点火", "火", "燃焼", "gas", "stove",
            "ignition", "fire", "combustion", "burning",
            "プロパン", "LPG", "バルブ", "圧力", "配管", "安全装置",
            "propane", "valve", "pressure", "pipeline", "safety",
            "点火プラグ", "燃焼器", "ガス漏れ", "換気", "清掃", "メンテナンス",
            "ignition plug", "burner", "gas leak", "ventilation"
        ],
        "ルーフベント": [
            "ルーフベント", "換気扇", "ファン", "マックスファン", "vent", "fan",
            "maxxfan", "fantec", "ドメスティック", "dometic",
            "開閉", "リモコン", "モーター", "ブレード", "異音", "自動",
            "opening", "closing", "remote", "motor", "blade", "noise", "auto",
            "12V", "24V", "配線", "ヒューズ", "スイッチ", "清掃", "メンテナンス",
            "wiring", "fuse", "switch", "cleaning", "maintenance"
        ],
        "バッテリー詳細": [
            "バッテリー", "充電", "放電", "電圧", "端子", "腐食", "battery", "charge",
            "discharge", "voltage", "terminal", "corrosion",
            "ディープサイクル", "AGM", "リチウムイオン", "deep cycle", "lithium ion",
            "充電器", "チャージャー", "ソーラーチャージャー", "charger", "solar charger",
            "バッテリー液", "電解液", "electrolyte", "battery fluid",
            "ヒューズ", "リレー", "配線", "fuse", "relay", "wiring",
            "充電されない", "充電が遅い", "電圧が低い", "すぐに放電", "膨らんでいる",
            "not charging", "slow charge", "low voltage", "quick discharge", "swelling"
        ]
    }
    
    # 関連カテゴリを特定（強化されたマッチング）
    relevant_categories = []
    query_words = query_lower.split()
    
    # 1. 直接キーワードマッチング
    for category, keywords in keyword_mapping.items():
        for keyword in keywords:
            if keyword in query_lower:
                if category not in relevant_categories:
                    relevant_categories.append(category)
                break
    
    # 2. 部分マッチングと関連語検索
    for category, keywords in keyword_mapping.items():
        for word in query_words:
            for keyword in keywords:
                # 部分マッチング
                if keyword in word or word in keyword:
                    if category not in relevant_categories:
                        relevant_categories.append(category)
                
                # 関連語検索（バッテリー関連の特殊ケース）
                if category == "バッテリー":
                    battery_related = ["充電", "電圧", "上がらない", "下がる", "切れる", "空になる", "劣化"]
                    for related in battery_related:
                        if related in query_lower:
                            if category not in relevant_categories:
                                relevant_categories.append(category)
    
    # 知識ベース内の全カテゴリもチェック（フォールバック）
    for category in knowledge_base.keys():
        if category not in relevant_categories:
            # カテゴリ名自体がクエリに含まれているかチェック
            if category.lower() in query_lower:
                relevant_categories.append(category)
    
    # 関連コンテンツを抽出（強化版）
    for category in relevant_categories:
        if category in knowledge_base:
            content = knowledge_base[category]
            
            # トラブル事例を抽出
            case_pattern = r'## 【Case.*?】.*?(?=##|$)'
            cases = re.findall(case_pattern, content, re.DOTALL)
            
            for case in cases:
                # より柔軟なマッチング
                case_lower = case.lower()
                
                # 直接キーワードマッチング
                if any(keyword in case_lower for keyword in query_words):
                    relevant_content.append(f"【{category}】\n{case}")
                # 部分マッチング
                elif any(keyword in query_lower for keyword in case_lower.split()[:10]):
                    relevant_content.append(f"【{category}】\n{case}")
                # バッテリー関連の特殊マッチング
                elif category == "バッテリー" and any(term in query_lower for term in ["充電", "電圧", "上がらない", "下がる"]):
                    relevant_content.append(f"【{category}】\n{case}")
    
    # 関連コンテンツが見つからない場合は、一般的なトラブル情報を提供
    if not relevant_content:
        # 全カテゴリから一般的なトラブル情報を抽出
        for category, content in knowledge_base.items():
            case_pattern = r'## 【Case.*?】.*?(?=##|$)'
            cases = re.findall(case_pattern, content, re.DOTALL)
            if cases:
                # 最初のケースを追加
                relevant_content.append(f"【{category}】\n{cases[0]}")
                if len(relevant_content) >= 2:  # 最大2つまで
                    break
    
    return relevant_content

def extract_urls_from_text(content):
    """テキストからURLを抽出"""
    import re
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, content)
    return urls

def determine_blog_category(blog, query):
    """ブログのカテゴリーを判定"""
    query_lower = query.lower()
    title_lower = blog['title'].lower()
    url_lower = blog['url'].lower()
    keywords_lower = [kw.lower() for kw in blog['keywords']]
    
    # インバーター関連
    if any(keyword in query_lower for keyword in ['インバーター', 'inverter', 'dc-ac', '正弦波', '電源変換']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['インバーター', 'inverter', '正弦波', '矩形波', 'dc-ac']):
            return "🔌 インバーター関連"
    
    # バッテリー関連
    if any(keyword in query_lower for keyword in ['バッテリー', 'battery', '充電', '電圧']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['バッテリー', 'battery', '充電', '電圧', 'agm', 'リチウム']):
            return "🔋 バッテリー関連"
    
    # 水道ポンプ関連
    if any(keyword in query_lower for keyword in ['水道', 'ポンプ', 'water', 'pump', '給水']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['水道', 'ポンプ', 'water', 'pump', '給水']):
            return "💧 水道・ポンプ関連"
    
    # 雨漏り関連
    if any(keyword in query_lower for keyword in ['雨漏り', 'rain', 'leak', '防水', 'シール']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['雨漏り', 'rain', 'leak', '防水', 'シール']):
            return "🌧️ 雨漏り・防水関連"
    
    # 電気・電装系関連
    if any(keyword in query_lower for keyword in ['電気', '電装', 'electrical', 'led', '照明']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['電気', '電装', 'electrical', 'led', '照明']):
            return "⚡ 電気・電装系関連"
    
    # 冷蔵庫関連
    if any(keyword in query_lower for keyword in ['冷蔵庫', '冷凍', 'コンプレッサー', '3way', 'dometic', 'waeco', 'engel']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['冷蔵庫', '冷凍', 'コンプレッサー', '3way', 'dometic', 'waeco', 'engel']):
            return "❄️ 冷蔵庫・冷凍関連"
    
    # 排水タンク関連
    if any(keyword in query_lower for keyword in ['排水タンク', 'グレータンク', '汚水', 'drain', 'tank']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['排水タンク', 'グレータンク', '汚水', 'drain', 'tank']):
            return "🚿 排水タンク関連"
    
    # 電装系関連
    if any(keyword in query_lower for keyword in ['電装系', '電気', '配線', 'ヒューズ', 'led', '照明', 'electrical']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['電装系', '電気', '配線', 'ヒューズ', 'led', '照明', 'electrical']):
            return "⚡ 電装系関連"
    
    # 家具関連
    if any(keyword in query_lower for keyword in ['家具', 'furniture', 'テーブル', 'ベッド', 'ソファ', '収納', 'キャビネット']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['家具', 'furniture', 'テーブル', 'ベッド', 'ソファ', '収納', 'キャビネット']):
            return "🪑 家具・収納関連"
    
    # タイヤ関連
    if any(keyword in query_lower for keyword in ['タイヤ', 'tire', 'パンク', '空気圧', '摩耗', 'cp規格', 'lt規格']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['タイヤ', 'tire', 'パンク', '空気圧', '摩耗', 'cp規格', 'lt規格']):
            return "🛞 タイヤ・ホイール関連"
    
    # ソーラーパネル関連
    if any(keyword in query_lower for keyword in ['ソーラーパネル', 'solar', 'パネル', '発電', '太陽光', 'チャージコントローラー']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['ソーラーパネル', 'solar', 'パネル', '発電', '太陽光', 'チャージコントローラー']):
            return "☀️ ソーラーパネル・発電システム関連"
    
    # ガス関連
    if any(keyword in query_lower for keyword in ['ガス', 'gas', 'コンロ', 'ヒーター', 'ff']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['ガス', 'gas', 'コンロ', 'ヒーター', 'ff']):
            return "🔥 ガス・ヒーター関連"
    
    # FFヒーター関連（詳細検索）
    ff_heater_keywords = [
        'ffヒーター', 'ff heater', 'forced fan heater', '車載ヒーター', '車載暖房',
        'ベバスト', 'webasto', 'ミクニ', 'mikuni', 'lvyuan', 'リョクエン',
        'エバポール', 'eberspacher', 'プラネー', 'planar',
        '点火しない', '白煙', '燃焼音', 'エラーコード', '燃料ポンプ', 'グロープラグ'
    ]
    if any(keyword in query_lower for keyword in ff_heater_keywords):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ff_heater_keywords):
            return "🔥 FFヒーター関連"
    
    # トイレ関連
    if any(keyword in query_lower for keyword in ['トイレ', 'toilet', 'カセット', 'マリン']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['トイレ', 'toilet', 'カセット', 'マリン']):
            return "🚽 トイレ関連"
    
    # ルーフベント関連
    if any(keyword in query_lower for keyword in ['ルーフベント', '換気扇', 'ファン', 'vent']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['ルーフベント', '換気扇', 'ファン', 'vent']):
            return "💨 ルーフベント・換気扇関連"
    
    # 異音・騒音関連
    if any(keyword in query_lower for keyword in ['異音', '騒音', '音', '振動', 'noise']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['異音', '騒音', '音', '振動', 'noise']):
            return "🔊 異音・騒音関連"
    
    # 基本修理・メンテナンス関連
    if any(keyword in query_lower for keyword in ['修理', 'メンテナンス', 'repair', 'maintenance']):
        if any(keyword in title_lower or keyword in url_lower or keyword in keywords_lower 
               for keyword in ['修理', 'メンテナンス', 'repair', 'maintenance']):
            return "🔧 基本修理・メンテナンス関連"
    
    # デフォルトカテゴリー
    return "📚 その他関連記事"

def determine_query_category(query):
    """クエリのカテゴリーを判定"""
    query_lower = query.lower()
    
    # インバーター関連
    if any(keyword in query_lower for keyword in ['インバーター', 'inverter', 'dc-ac', '正弦波', '電源変換']):
        return "🔌 インバーター関連"
    
    # バッテリー関連
    if any(keyword in query_lower for keyword in ['バッテリー', 'battery', '充電', '電圧']):
        return "🔋 バッテリー関連"
    
    # 水道ポンプ関連
    if any(keyword in query_lower for keyword in ['水道', 'ポンプ', 'water', 'pump', '給水']):
        return "💧 水道・ポンプ関連"
    
    # 雨漏り関連
    if any(keyword in query_lower for keyword in ['雨漏り', 'rain', 'leak', '防水', 'シール']):
        return "🌧️ 雨漏り・防水関連"
    
    # 電気・電装系関連
    if any(keyword in query_lower for keyword in ['電気', '電装', 'electrical', 'led', '照明']):
        return "⚡ 電気・電装系関連"
    
    # 冷蔵庫関連
    if any(keyword in query_lower for keyword in ['冷蔵庫', '冷凍', 'コンプレッサー', '3way', 'dometic', 'waeco', 'engel']):
        return "❄️ 冷蔵庫・冷凍関連"
    
    # エアコン関連（カテゴリー候補と主要キーワード対応）
    if any(keyword in query_lower for keyword in ['エアコン', 'aircon', '冷房', '暖房', '冷暖房', '冷暖房システム', 
                                                 '車載クーラー', 'クーラー', '室内空調', '空調', 'クライメート', 'クライメートコントロール',
                                                 'ルーフエアコン', '車載エアコン', 'camcool', 'stage21', 'コンプレッサー', 'ガス漏れ',
                                                 'エアコンフィルター', 'フィルター', '風量', '温度調整', '冷媒', '故障']):
        return "❄️ エアコン・空調関連"
    
    # 排水タンク関連
    if any(keyword in query_lower for keyword in ['排水タンク', 'グレータンク', '汚水', 'drain', 'tank']):
        return "🚿 排水タンク関連"
    
    # 電装系関連
    if any(keyword in query_lower for keyword in ['電装系', '電気', '配線', 'ヒューズ', 'led', '照明', 'electrical']):
        return "⚡ 電装系関連"
    
    # 家具関連
    if any(keyword in query_lower for keyword in ['家具', 'furniture', 'テーブル', 'ベッド', 'ソファ', '収納', 'キャビネット']):
        return "🪑 家具・収納関連"
    
    # タイヤ関連
    if any(keyword in query_lower for keyword in ['タイヤ', 'tire', 'パンク', '空気圧', '摩耗', 'cp規格', 'lt規格']):
        return "🛞 タイヤ・ホイール関連"
    
    # ソーラーパネル関連
    if any(keyword in query_lower for keyword in ['ソーラーパネル', 'solar', 'パネル', '発電', '太陽光', 'チャージコントローラー']):
        return "☀️ ソーラーパネル・発電システム関連"
    
    # ガス関連
    if any(keyword in query_lower for keyword in ['ガス', 'gas', 'コンロ', 'ヒーター', 'ff']):
        return "🔥 ガス・ヒーター関連"
    
    # FFヒーター関連（詳細検索）
    ff_heater_keywords = [
        'ffヒーター', 'ff heater', 'forced fan heater', '車載ヒーター', '車載暖房',
        'ベバスト', 'webasto', 'ミクニ', 'mikuni', 'lvyuan', 'リョクエン',
        'エバポール', 'eberspacher', 'プラネー', 'planar',
        '点火しない', '白煙', '燃焼音', 'エラーコード', '燃料ポンプ', 'グロープラグ'
    ]
    if any(keyword in query_lower for keyword in ff_heater_keywords):
        return "🔥 FFヒーター関連"
    
    # トイレ関連
    if any(keyword in query_lower for keyword in ['トイレ', 'toilet', 'カセット', 'マリン']):
        return "🚽 トイレ関連"
    
    # ルーフベント関連
    if any(keyword in query_lower for keyword in ['ルーフベント', '換気扇', 'ファン', 'vent']):
        return "💨 ルーフベント・換気扇関連"
    
    # 異音・騒音関連
    if any(keyword in query_lower for keyword in ['異音', '騒音', '音', '振動', 'noise']):
        return "🔊 異音・騒音関連"
    
    # 基本修理・メンテナンス関連
    if any(keyword in query_lower for keyword in ['修理', 'メンテナンス', 'repair', 'maintenance']):
        return "🔧 基本修理・メンテナンス関連"
    
    # デフォルトカテゴリー
    return "📚 その他関連記事"

def display_repair_results(query):
    """修理アドバイス検索結果を表示"""
    query_lower = query.lower()
    
    # バッテリー関連の検索結果
    if any(keyword in query_lower for keyword in ["バッテリー", "充電", "サブバッテリー", "電圧"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #dc3545;">
            <h4 style="color: #dc3545; margin-bottom: 15px;">🔋 バッテリー関連の修理アドバイス</h4>
            <p><strong>問題:</strong> バッテリーが充電されない、電圧が低下する</p>
            <p><strong>原因:</strong> アイソレーター（切替リレー）の故障、DC-DCコンバーターの不具合、ヒューズ切れ</p>
            <p><strong>修理費用:</strong> 5,000円～25,000円</p>
            <p><strong>必要な部品:</strong> アイソレーター、ヒューズ、DC-DCコンバーター</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 詳細な修理手順
        with st.expander("🔧 詳細な修理手順"):
            st.markdown("""
            **1. 電圧チェック**
            - エンジン始動時に電圧を測定
            - 正常値: 13.5V以上
            - 異常値: 12.5V以下の場合、充電系の故障
            
            **2. アイソレーターの確認**
            - リレー作動音の有無を確認
            - 作動音がない場合はリレー本体の故障
            
            **3. ヒューズの点検**
            - リレー直後のヒューズを確認
            - 切れている場合は同容量で交換
            """)
    
    # トイレ関連の検索結果
    elif any(keyword in query_lower for keyword in ["トイレ", "カセット", "マリン", "水洗"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #28a745;">
            <h4 style="color: #28a745; margin-bottom: 15px;">🚽 トイレ関連の修理アドバイス</h4>
            <p><strong>問題:</strong> トイレのファンが回らない、水が流れない</p>
            <p><strong>原因:</strong> ポンプの詰まり、シール・パッキンの劣化、電源の問題</p>
            <p><strong>修理費用:</strong> 3,000円～15,000円</p>
            <p><strong>必要な部品:</strong> ポンプ、シール、パッキン、ヒューズ</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 代替品の紹介
        with st.expander("🛒 推奨代替品"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **トイレ部品**
                - テラデン カセットトイレ用パッキン: ¥2,500
                - サニテック マリントイレ用シール: ¥1,800
                - エコトイレ カセットタンク: ¥8,900
                """)
            with col2:
                st.markdown("""
                **電装部品**
                - シャワートイレ用ポンプ: ¥12,500
                - 12V トイレ用ヒューズセット: ¥850
                """)
    
    # エアコン関連の検索結果
    elif any(keyword in query_lower for keyword in ["エアコン", "冷房", "暖房", "空調"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #17a2b8;">
            <h4 style="color: #17a2b8; margin-bottom: 15px;">❄️ エアコン関連の修理アドバイス</h4>
            <p><strong>問題:</strong> エアコンが効かない、冷房・暖房が効かない</p>
            <p><strong>原因:</strong> フィルターの汚れ、冷媒ガスの不足、室外機の故障</p>
            <p><strong>修理費用:</strong> 8,000円～30,000円</p>
            <p><strong>必要な部品:</strong> エアコンフィルター、冷媒ガス、室外機部品</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 詳細な修理手順"):
            st.markdown("""
            **1. フィルター清掃**
            - 室内機のフィルターを取り外し
            - 水洗いまたは掃除機で清掃
            - 完全に乾燥させてから取り付け
            
            **2. 室外機の点検**
            - 室外機周辺の清掃
            - ファンの動作確認
            - 配管の損傷チェック
            
            **3. 冷媒ガスの確認**
            - 専門業者による冷媒ガス量の測定
            - 不足している場合は補充
            """)
    
    # 雨漏り関連の検索結果
    elif any(keyword in query_lower for keyword in ["雨漏り", "水漏れ", "防水", "シーリング"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #6f42c1;">
            <h4 style="color: #6f42c1; margin-bottom: 15px;">🌧️ 雨漏り関連の修理アドバイス</h4>
            <p><strong>問題:</strong> 雨漏り、水の浸入</p>
            <p><strong>原因:</strong> シーリング材の劣化、防水テープの剥がれ、パッキンの劣化</p>
            <p><strong>修理費用:</strong> 5,000円～20,000円</p>
            <p><strong>必要な部品:</strong> シーリング材、防水テープ、パッキン</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 詳細な修理手順"):
            st.markdown("""
            **1. 漏水箇所の特定**
            - 水の流れを追跡
            - 内側から外側への浸入経路を確認
            
            **2. シーリング材の補修**
            - 古いシーリング材を完全に除去
            - 新しいシーリング材を適切に施工
            
            **3. 防水テープの貼り直し**
            - 劣化した防水テープを剥がす
            - 新しい防水テープを重ねて貼る
            """)
    
    # FFヒーター関連の検索結果
    elif any(keyword in query_lower for keyword in [
        "ffヒーター", "ff heater", "forced fan heater", "車載ヒーター", "車載暖房",
        "ベバスト", "webasto", "ミクニ", "mikuni", "lvyuan", "リョクエン",
        "エバポール", "eberspacher", "プラネー", "planar",
        "点火しない", "白煙", "燃焼音", "エラーコード", "燃料ポンプ", "グロープラグ"
    ]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #dc3545;">
            <h4 style="color: #dc3545; margin-bottom: 15px;">🔥 FFヒーター（燃焼式車載ヒーター）修理アドバイス</h4>
            <p><strong>検索キーワード:</strong> {query}</p>
            <p>FFヒーターは燃焼式の車載暖房器で、燃料ポンプ、点火システム、燃焼室のトラブルが多く見られます。</p>
            <p><strong>よくある症状:</strong></p>
            <ul>
                <li>点火しない・起動しない</li>
                <li>白煙・黒煙が出る</li>
                <li>異音・燃焼音が大きい</li>
                <li>エラーコード表示（E13等）</li>
                <li>燃料ポンプの音がうるさい</li>
                <li>温度調節が効かない</li>
            </ul>
            <p><strong>修理費用目安:</strong></p>
            <ul>
                <li>動作確認・エラーチェック：3,000〜5,000円</li>
                <li>分解清掃（スス・燃焼室）：10,000〜15,000円</li>
                <li>燃料ポンプ交換：8,000〜12,000円</li>
                <li>グロープラグ交換：5,000〜9,000円</li>
                <li>吸排気パイプ交換：6,000〜10,000円</li>
            </ul>
            <p><strong>対応製品例:</strong> ベバスト（Webasto）、ミクニ、LVYUAN、エバポール（Eberspacher）</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 FFヒーター詳細修理手順"):
            st.markdown("""
            **1. 点火不良の対処**
            - バッテリー電圧を12.5V以上に確認
            - ヒューズの状態を点検
            - 燃料ポンプの動作音を確認
            
            **2. 白煙・燃焼不良の対処**
            - 燃料フィルターの清掃・交換
            - 燃焼室のカーボン除去
            - グロープラグの清掃・交換
            
            **3. 異音対策**
            - 燃料ポンプの防振マウント交換
            - 排気管のサイレンサー清掃
            - ファンの異物除去・ベアリング注油
            """)
    
    # 排水タンク関連の検索結果
    elif any(keyword in query_lower for keyword in ["排水タンク", "グレータンク", "汚水", "排水", "drain", "tank", "グレー"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #6c757d;">
            <h4 style="color: #6c757d; margin-bottom: 15px;">🚿 排水タンク（グレータンク）修理アドバイス</h4>
            <p><strong>検索キーワード:</strong> {query}</p>
            <p>排水タンクは生活排水（シンク、シャワー）を一時的に貯留し、適切な場所で排出するシステムです。</p>
            <p><strong>よくある症状:</strong></p>
            <ul>
                <li>タンクが全く排水しない</li>
                <li>排水後もレベルセンサーが満タン表示</li>
                <li>悪臭が室内に逆流</li>
                <li>バルブハンドルが抜けた</li>
                <li>タンク底からポタポタ漏れ</li>
                <li>冬に排水が凍結</li>
                <li>排水時にホースが外れて被害</li>
                <li>タンクが膨らんで車体から下がる</li>
                <li>排水時に黒い粒が出る</li>
                <li>排水口キャップを紛失</li>
            </ul>
            <p><strong>修理費用目安:</strong></p>
            <ul>
                <li>動作確認・点検：2,000〜3,000円</li>
                <li>バルブ清掃・潤滑：3,000〜5,000円</li>
                <li>Oリング交換：2,000〜4,000円</li>
                <li>バルブハンドル交換：5,000〜8,000円</li>
                <li>タンク洗浄・除菌：4,000〜6,000円</li>
                <li>タンク交換：15,000〜25,000円</li>
            </ul>
            <p><strong>対応製品例:</strong> THETFORD、DOMETIC、SEALAND、VALTERRA</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 排水タンク詳細修理手順"):
            st.markdown("""
            **1. 排水不良の対処**
            - バルブハンドルの固着確認
            - 浸透潤滑剤での潤滑
            - 逆洗いによる清掃
            
            **2. 臭気対策**
            - Pトラップの封水復活
            - 中性洗剤での清掃
            - RV用不凍剤の使用
            
            **3. 凍結対策**
            - 不凍剤の混入
            - 12Vヒーターパッドの設置
            - 保温材での断熱
            """)
    
    # 電装系関連の検索結果
    elif any(keyword in query_lower for keyword in ["電装系", "電気", "配線", "ヒューズ", "led", "照明", "electrical", "電源", "バッテリー", "インバーター"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #17a2b8;">
            <h4 style="color: #17a2b8; margin-bottom: 15px;">⚡ 電装系トラブル修理アドバイス</h4>
            <p><strong>検索キーワード:</strong> {query}</p>
            <p>キャンピングカーの電装系は12V/24V直流と100V交流の複合システムで、バッテリー管理が重要です。</p>
            <p><strong>よくある症状:</strong></p>
            <ul>
                <li>LED照明がチラつく</li>
                <li>100Vコンセントが全く出力しない</li>
                <li>ヒューズが頻繁に飛ぶ</li>
                <li>サブバッテリー残量計が動かない</li>
                <li>走行中に電子レンジを使うと照明が暗くなる</li>
                <li>DCシガーソケットが高温になる</li>
                <li>USBポートから充電できない</li>
                <li>インバーターから異音（ブーン）</li>
                <li>電線が温かい</li>
                <li>外部電源に繋いでも充電器が動かない</li>
            </ul>
            <p><strong>修理費用目安:</strong></p>
            <ul>
                <li>動作確認・点検：3,000〜5,000円</li>
                <li>ヒューズ・リレー交換：2,000〜4,000円</li>
                <li>配線点検・接続不良修正：5,000〜8,000円</li>
                <li>LED照明交換：3,000〜6,000円</li>
                <li>USBポート・シガーソケット交換：4,000〜7,000円</li>
                <li>インバーター修理・交換：15,000〜30,000円</li>
                <li>配線増設・太径化：8,000〜15,000円</li>
            </ul>
            <p><strong>対応製品例:</strong> VICTRON、SAMLEX、RENOGY、GOAL ZERO、BLUETTI</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 電装系詳細修理手順"):
            st.markdown("""
            **1. LED照明トラブル**
            - 調光器のPWM周波数確認
            - LED対応昇圧式調光器への交換
            - アース不良の点検
            
            **2. 電源トラブル**
            - ヒューズ容量の確認
            - 配線の擦れ・ショート点検
            - 負荷電流の測定
            
            **3. バッテリー管理**
            - シャント抵抗の配線確認
            - 電圧監視システムの点検
            - 充放電バランスの調整
            """)
    
    # 家具関連の検索結果
    elif any(keyword in query_lower for keyword in ["家具", "furniture", "テーブル", "ベッド", "ソファ", "収納", "キャビネット", "引き出し"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #28a745;">
            <h4 style="color: #28a745; margin-bottom: 15px;">🪑 家具・収納トラブル修理アドバイス</h4>
            <p><strong>検索キーワード:</strong> {query}</p>
            <p>キャンピングカーの家具は走行時の振動や狭い空間での使用に特化した設計が必要です。</p>
            <p><strong>よくある症状:</strong></p>
            <ul>
                <li>走行中に引き出しが飛び出す</li>
                <li>テーブル脚がガタつく</li>
                <li>収納扉のヒンジが割れた</li>
                <li>ベッド展開が固い</li>
                <li>キャビネットから異音（キシキシ）</li>
                <li>表面板（化粧板）が剥がれる</li>
                <li>床下収納のロックが閉まらない</li>
                <li>壁面にネジ穴が増えてしまった</li>
                <li>スライドクローゼットが勝手に開く</li>
                <li>家具の臭いが取れない</li>
            </ul>
            <p><strong>修理費用目安:</strong></p>
            <ul>
                <li>動作確認・点検：2,000〜3,000円</li>
                <li>ラッチ・ヒンジ交換：3,000〜5,000円</li>
                <li>テーブル脚ブッシュ交換：2,000〜4,000円</li>
                <li>表面板貼り替え：5,000〜8,000円</li>
                <li>ネジ穴補修：3,000〜5,000円</li>
                <li>家具清掃・消臭：4,000〜6,000円</li>
            </ul>
            <p><strong>対応製品例:</strong> 耐振動ラッチ、金属ダンパー付きヒンジ、耐水化粧板</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 家具詳細修理手順"):
            st.markdown("""
            **1. 引き出し・扉のトラブル**
            - ラッチ金具のスプリング点検
            - マグネットキャッチの追加
            - 耐振動ラッチへの交換
            
            **2. テーブル・ベッドのトラブル**
            - 脚根元ボルトの増し締め
            - 樹脂ブッシュの交換
            - スライドレールの清掃・潤滑
            
            **3. 表面・外観のトラブル**
            - 化粧板の再接着・貼り替え
            - ネジ穴の木工パテ補修
            - 家具の清掃・消臭処理
            """)
    
    # タイヤ関連の検索結果
    elif any(keyword in query_lower for keyword in ["タイヤ", "tire", "パンク", "空気圧", "摩耗", "交換", "cp規格", "lt規格"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #6f42c1;">
            <h4 style="color: #6f42c1; margin-bottom: 15px;">🛞 タイヤ・ホイールトラブル修理アドバイス</h4>
            <p><strong>検索キーワード:</strong> {query}</p>
            <p>キャンピングカーのタイヤは一般車より重量が大きく、長距離走行が前提のため適切な管理が重要です。</p>
            <p><strong>よくある症状:</strong></p>
            <ul>
                <li>空気圧不足・過多</li>
                <li>パンク・バースト</li>
                <li>偏摩耗・異常摩耗</li>
                <li>タイヤの亀裂・ひび割れ</li>
                <li>バランス不良による振動</li>
                <li>ローテーション未実施</li>
                <li>サイズ不適合</li>
                <li>過積載による負荷過多</li>
                <li>タイヤの経年劣化</li>
                <li>ホイールの損傷・変形</li>
            </ul>
            <p><strong>修理費用目安:</strong></p>
            <ul>
                <li>空気圧調整・点検：500〜1,000円</li>
                <li>パンク修理：2,000〜3,000円</li>
                <li>バランス調整：1,000〜2,000円</li>
                <li>ローテーション：2,000〜3,000円</li>
                <li>タイヤ交換（1本）：20,000〜40,000円</li>
                <li>4本交換：80,000〜160,000円</li>
            </ul>
            <p><strong>対応製品例:</strong> ミシュラン、ブリヂストン、ダンロップ、ヨコハマ（CP規格・LT規格）</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 タイヤ詳細修理手順"):
            st.markdown("""
            **1. 空気圧管理**
            - 規定値の確認（ドアラベル・説明書）
            - 季節・荷物量に応じた調整
            - 定期的な点検（月1回推奨）
            
            **2. パンク・バースト対策**
            - 応急修理キットの準備
            - スペアタイヤの点検
            - パンク保証制度の活用
            
            **3. メンテナンス**
            - ローテーション（5,000km毎）
            - バランス調整
            - 偏摩耗の早期発見
            """)
    
    # ソーラーパネル関連の検索結果
    elif any(keyword in query_lower for keyword in ["ソーラーパネル", "solar", "パネル", "発電", "太陽光", "チャージコントローラー", "mppt", "pwm"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #ffc107;">
            <h4 style="color: #ffc107; margin-bottom: 15px;">☀️ ソーラーパネル・発電システム修理アドバイス</h4>
            <p><strong>検索キーワード:</strong> {query}</p>
            <p>キャンピングカーのソーラーパネルシステムは、走行や停車環境に左右されやすく、適切な設置・点検・修理が重要です。</p>
            <p><strong>よくある症状:</strong></p>
            <ul>
                <li>発電量が急激に減少する</li>
                <li>表面にひび割れが入る</li>
                <li>配線の接続不良</li>
                <li>チャージコントローラーの故障</li>
                <li>角度調整による発電効率低下</li>
                <li>木や建物による影の影響</li>
                <li>表面の汚れによる効率低下</li>
                <li>配線の断線</li>
                <li>パネルの老朽化（10年以上経過）</li>
                <li>雷による故障</li>
            </ul>
            <p><strong>修理費用目安:</strong></p>
            <ul>
                <li>診断料：3,000〜5,000円</li>
                <li>清掃：5,000〜8,000円</li>
                <li>配線修理：5,000〜10,000円</li>
                <li>チャージコントローラー交換：15,000〜25,000円</li>
                <li>ソーラーパネル交換：80,000〜120,000円</li>
                <li>設置工事：10,000〜30,000円</li>
            </ul>
            <p><strong>対応製品例:</strong> トイファクトリー（Toy-Factory × シャープ）、京セラ（KYOCERA）、長州産業（CHOSHU）</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 ソーラーパネル詳細修理手順"):
            st.markdown("""
            **1. 発電量低下の対処**
            - パネル表面の汚れ確認・清掃
            - 影の影響確認・対策
            - チャージコントローラーの状態確認
            
            **2. 配線・接続トラブル**
            - コネクターの接続確認
            - 配線の断線点検
            - 防水処理の確認
            
            **3. システム最適化**
            - パネル角度の調整
            - バッテリー容量の確認
            - 負荷管理の最適化
            """)
    
    # 冷蔵庫関連の検索結果
    elif any(keyword in query_lower for keyword in ["冷蔵庫", "冷凍", "コンプレッサー", "refrigerator", "3way", "12v冷蔵庫"]):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #fd7e14;">
            <h4 style="color: #fd7e14; margin-bottom: 15px;">🧊 冷蔵庫（キャンピングカー用）修理アドバイス</h4>
            <p><strong>検索キーワード:</strong> {query}</p>
            <p>キャンピングカー用冷蔵庫は3WAY（12V/100V/ガス）対応で、コンプレッサー式とペルチェ式があります。</p>
            <p><strong>よくある症状:</strong></p>
            <ul>
                <li>まったく冷えない・無反応</li>
                <li>設定温度に届かない</li>
                <li>ガスモードで点火しない（3WAY）</li>
                <li>バッテリーが一晩で空になる</li>
                <li>庫内の氷が溶け水浸し</li>
                <li>アンモニア臭がする（吸収式）</li>
                <li>自動エネルギー切替がガスに戻らない</li>
                <li>コンプレッサーから異音</li>
                <li>エラーコード「E4」温度センサー異常</li>
                <li>ドアラッチが壊れて閉まらない</li>
            </ul>
            <p><strong>修理費用目安:</strong></p>
            <ul>
                <li>動作確認・エラーチェック：3,000〜5,000円</li>
                <li>ヒューズ交換・配線点検：2,000〜4,000円</li>
                <li>ドアパッキン交換：5,000〜8,000円</li>
                <li>温度センサー交換：8,000〜12,000円</li>
                <li>コンプレッサー交換：50,000〜80,000円</li>
                <li>冷却ユニット交換：80,000〜120,000円</li>
            </ul>
            <p><strong>対応製品例:</strong> DOMETIC、WAECO、ENGEL、ARB、NATIONAL LUNA</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 詳細な修理手順"):
            st.markdown("""
            **1. 電源の確認**
            - ヒューズの状態を確認
            - 電圧をマルチメーターで測定
            
            **2. ドアパッキンの点検**
            - パッキンの劣化状況を確認
            - 密閉性のテストを実施
            
            **3. コンプレッサーの動作確認**
            - 動作音の確認
            - 専門業者による点検を推奨
            """)
    
    # 水道ポンプ関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["水道ポンプ", "給水システム", "ポンプユニット", "給水設備", "配管・水回り", "ポンプ", "給水", "吐水", "吸水", "水圧", "流量", "故障", "モーター", "漏水"]):
        water_pump_info = get_water_pump_info(query)
        if water_pump_info:
            st.markdown(water_pump_info, unsafe_allow_html=True)
        else:
            st.info("水道ポンプ関連の情報を取得中です...")
    
    # 車体外装の破損関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["車体外装", "外装破損", "キズ", "ヘコミ", "塗装剥がれ", "FRP", "パネル交換", "修理費用", "車体補修", "ボディ修理"]):
        body_damage_info = get_body_damage_info(query)
        if body_damage_info:
            st.markdown(body_damage_info, unsafe_allow_html=True)
        else:
            st.info("車体外装の破損関連の情報を取得中です...")
    
    # 室内LED関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["室内LED", "照明", "車内ライト", "電球交換", "明るさ", "消費電力", "点灯不良", "フリッカー", "ちらつき", "配線", "電圧"]):
        indoor_led_info = get_indoor_led_info(query)
        if indoor_led_info:
            st.markdown(indoor_led_info, unsafe_allow_html=True)
        else:
            st.info("室内LED関連の情報を取得中です...")
    
    # 外部電源関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["外部電源", "AC100V", "コンセント", "電圧", "ブレーカー", "過電流", "漏電", "充電", "インバーター", "電装トラブル"]):
        external_power_info = get_external_power_info(query)
        if external_power_info:
            st.markdown(external_power_info, unsafe_allow_html=True)
        else:
            st.info("外部電源関連の情報を取得中です...")
    
    # 異音関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["異音", "騒音", "ガタガタ音", "キュルキュル音", "ゴトゴト音", "エンジン音", "モーター音", "振動", "異常音", "金属音"]):
        noise_info = get_noise_info(query)
        if noise_info:
            st.markdown(noise_info, unsafe_allow_html=True)
        else:
            st.info("異音関連の情報を取得中です...")
    
    # タイヤ関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["タイヤ", "パンク", "空気圧", "摩耗", "ひび割れ", "ホイール", "スペアタイヤ", "ローテーション", "グリップ", "交換"]):
        tire_info = get_tire_info(query)
        if tire_info:
            st.markdown(tire_info, unsafe_allow_html=True)
        else:
            st.info("タイヤ関連の情報を取得中です...")
    
    # ソーラーパネル関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["ソーラーパネル", "太陽光", "発電", "充電", "バッテリー充電", "発電効率", "配線", "コントローラー", "MPPT", "PWM", "設置", "故障"]):
        solar_panel_info = get_solar_panel_info(query)
        if solar_panel_info:
            st.markdown(solar_panel_info, unsafe_allow_html=True)
        else:
            st.info("ソーラーパネル関連の情報を取得中です...")
    
    # サブバッテリー関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["サブバッテリー", "充電", "放電", "劣化", "電圧", "容量", "過放電", "走行充電", "バッテリー交換", "寿命"]):
        sub_battery_info = get_sub_battery_info(query)
        if sub_battery_info:
            st.markdown(sub_battery_info, unsafe_allow_html=True)
        else:
            st.info("サブバッテリー関連の情報を取得中です...")
    
    # エアコン関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["エアコン", "冷房", "暖房", "コンプレッサー", "ガス漏れ", "エアコンフィルター", "風量", "温度調整", "冷媒", "故障"]):
        air_conditioner_info = get_air_conditioner_info(query)
        if air_conditioner_info:
            st.markdown(air_conditioner_info, unsafe_allow_html=True)
        else:
            st.info("エアコン関連の情報を取得中です...")
    
    # インバーター関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["インバーター", "DC-AC変換", "出力", "電圧不安定", "過負荷", "発熱", "配線", "ノイズ", "故障", "保護回路"]):
        inverter_info = get_inverter_info(query)
        if inverter_info:
            st.markdown(inverter_info, unsafe_allow_html=True)
        else:
            st.info("インバーター関連の情報を取得中です...")
    
    # ウインドウ関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["ウインドウ", "窓", "ガラス", "開閉", "網戸", "シーリング", "レール", "破損", "結露", "曇り止め"]):
        window_info = get_window_info(query)
        if window_info:
            st.markdown(window_info, unsafe_allow_html=True)
        else:
            st.info("ウインドウ関連の情報を取得中です...")
    
    # 雨漏り関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["雨漏り", "水漏れ", "浸水", "漏水", "水浸し", "水滴", "水の染み", "シーリング", "防水"]):
        rain_leak_info = get_rain_leak_info(query)
        if rain_leak_info:
            st.markdown(rain_leak_info, unsafe_allow_html=True)
        else:
            st.info("雨漏り関連の情報を取得中です...")
    
    # トイレ詳細関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["トイレ", "便器", "カセット", "マリン", "フラッパー", "ポンプ", "ファン", "水洗", "シール", "パッキン", "悪臭", "清掃"]):
        toilet_info = get_toilet_info(query)
        if toilet_info:
            st.markdown(toilet_info, unsafe_allow_html=True)
        else:
            st.info("トイレ関連の情報を取得中です...")
    
    # バッテリー詳細関連の検索結果（専用テキストデータから取得）
    elif any(keyword in query_lower for keyword in ["バッテリー", "充電", "放電", "電圧", "端子", "腐食", "ディープサイクル", "AGM", "リチウムイオン", "充電器", "チャージャー", "バッテリー液", "電解液"]):
        battery_info = get_battery_info(query)
        if battery_info:
            st.markdown(battery_info, unsafe_allow_html=True)
        else:
            st.info("バッテリー関連の情報を取得中です...")
    
    # 一般的な検索結果
    else:
        st.markdown("""
        <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #2196f3;">
            <h4 style="color: #2196f3; margin-bottom: 15px;">🔍 一般的な修理アドバイス</h4>
            <p><strong>検索キーワード:</strong> {query}</p>
            <p>詳細な修理アドバイスを取得するには、より具体的な症状や部品名を入力してください。</p>
            <p><strong>推奨検索例:</strong></p>
            <ul>
                <li>「バッテリー 充電されない」</li>
                <li>「トイレ 水が流れない」</li>
                <li>「エアコン 冷房効かない」</li>
                <li>「雨漏り 修理方法」</li>
            </ul>
        </div>
        """.format(query=query), unsafe_allow_html=True)
    
    # サポートセンター情報
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0; border: 2px solid #2196f3;">
        <h4 style="color: #1565c0; margin-bottom: 15px; text-align: center;">🏢 岡山キャンピングカー修理サポートセンター</h4>
        <div style="text-align: center;">
            <p><strong>📞 電話:</strong> 086-206-6622</p>
            <p><strong>📍 住所:</strong> 〒700-0921 岡山市北区東古松485-4 2F</p>
            <p><strong>⏰ 営業時間:</strong> 年中無休（9:00～21:00）</p>
            <p><strong>🌐 ホームページ:</strong> <a href="https://camper-repair.net/blog/" target="_blank">https://camper-repair.net/blog/</a></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_relevant_blog_links(query, knowledge_base=None):
    """クエリとテキストデータに基づいて関連ブログを返す"""
    query_lower = query.lower()
    
    # 質問から直接キーワードを抽出
    query_keywords = []
    
    # 主要な技術用語を質問から直接抽出
    main_keywords = [
        "バッテリー", "インバーター", "ポンプ", "冷蔵庫", "ヒーター", "コンロ",
        "トイレ", "ルーフベント", "換気扇", "水道", "給水", "排水", "雨漏り",
        "防水", "シーリング", "配線", "電装", "LED", "ソーラーパネル",
        "ガス", "電気", "異音", "振動", "故障", "修理", "メンテナンス",
        "シャワー", "水", "電圧", "充電", "出力", "電源", "音", "騒音",
        # FFヒーター関連キーワード
        "FFヒーター", "ffヒーター", "FF heater", "forced fan heater", "車載ヒーター", "車載暖房",
        "ベバスト", "webasto", "ミクニ", "mikuni", "lvyuan", "リョクエン",
        "エバポール", "eberspacher", "プラネー", "planar"
    ]
    
    for keyword in main_keywords:
        if keyword in query_lower:
            query_keywords.append(keyword)
    
    # トラブル関連キーワードを質問から直接抽出
    trouble_keywords = [
        "水が出ない", "圧力不足", "異音", "過熱", "電圧低下", "充電されない",
        "電源入らない", "出力ゼロ", "水漏れ", "臭い", "ファン故障", "開閉不良",
        "配管漏れ", "雨漏り", "防水", "シール", "音", "騒音", "振動",
        # FFヒーター特有のトラブルキーワード
        "点火しない", "点火不良", "つかない", "点かない", "起動しない", "動かない",
        "白煙", "煙が出る", "煙がでる", "白い煙", "黒い煙", "煙突", "排気",
        "燃焼音", "エラー", "エラーコード", "E13", "エラー表示", "リモコンエラー",
        "燃料", "燃料切れ", "燃料不足", "燃料ポンプ", "燃料フィルター",
        "燃焼", "燃焼不良", "燃焼室", "グロープラグ", "点火プラグ",
        "温度", "温風", "暖房", "暖かくならない", "温度調節"
    ]
    
    for keyword in trouble_keywords:
        if keyword in query_lower:
            query_keywords.append(keyword)
    
    # テキストデータからキーワードとURLを抽出
    extracted_keywords = []
    extracted_urls = []
    
    if knowledge_base:
        for category, content in knowledge_base.items():
            # カテゴリ名をキーワードとして追加
            if category.lower() in query_lower:
                extracted_keywords.append(category.lower())
            
            # コンテンツから重要なキーワードを抽出
            content_lower = content.lower()
            
            # 技術用語の抽出
            tech_keywords = [
                "バッテリー", "インバーター", "ポンプ", "冷蔵庫", "ヒーター", "コンロ",
                "トイレ", "ルーフベント", "換気扇", "水道", "給水", "排水", "雨漏り",
                "防水", "シーリング", "配線", "電装", "LED", "ソーラーパネル",
                "ガス", "電気", "異音", "振動", "故障", "修理", "メンテナンス"
            ]
            
            for keyword in tech_keywords:
                if keyword in content_lower and keyword in query_lower:
                    extracted_keywords.append(keyword)
            
            # トラブル関連キーワードの抽出
            trouble_keywords = [
                "水が出ない", "圧力不足", "異音", "過熱", "電圧低下", "充電されない",
                "電源入らない", "出力ゼロ", "水漏れ", "臭い", "ファン故障", "開閉不良",
                "配管漏れ", "雨漏り", "防水", "シール", "音", "騒音", "振動"
            ]
            
            for keyword in trouble_keywords:
                if keyword in content_lower and keyword in query_lower:
                    extracted_keywords.append(keyword)
            
            # URLを抽出
            urls = extract_urls_from_text(content)
            for url in urls:
                if url not in extracted_urls:
                    extracted_urls.append(url)
    
    # 質問から抽出したキーワードとテキストデータから抽出したキーワードを結合
    all_keywords = list(set(query_keywords + extracted_keywords))
    
    # 重複を除去
    extracted_keywords = list(set(extracted_keywords))
    
    # テキストデータから抽出したURLを基にブログリンクを生成
    blog_links = []
    
    # 抽出したURLからブログリンクを作成
    for url in extracted_urls:
        # URLにカンマが含まれている場合は分割
        individual_urls = url.split(',')
        
        for individual_url in individual_urls:
            individual_url = individual_url.strip()  # 前後の空白を除去
            if not individual_url:  # 空のURLはスキップ
                continue
                
            # URLから正確なタイトルを推測
            title = ""
            if "water-pump" in individual_url or "水道" in individual_url or "ポンプ" in individual_url:
                title = "水道ポンプ関連記事"
            elif "battery" in individual_url or "バッテリー" in individual_url:
                title = "バッテリー関連記事"
            elif "inverter" in individual_url or "インバーター" in individual_url:
                title = "インバーター関連記事"
            elif "rain-leak" in individual_url or "雨漏り" in individual_url:
                title = "雨漏り関連記事"
            elif "electrical" in individual_url or "電気" in individual_url or "電装" in individual_url:
                title = "電気・電装系関連記事"
            elif "shower" in individual_url:
                title = "シャワー・給水関連記事"
            elif "repair" in individual_url or "修理" in individual_url:
                title = "修理関連記事"
            else:
                title = "キャンピングカー関連記事"
            
            # キーワードを質問のキーワードとテキストデータから抽出したキーワードから設定
            keywords = all_keywords.copy()
            
            blog_links.append({
                "title": title,
                "url": individual_url,
                "keywords": keywords
            })
    
    # 基本的なブログリンクデータベース（フォールバック用）
    fallback_blog_links = [
        {
            "title": "サブバッテリーの種類と選び方",
            "url": "https://camper-repair.net/blog/battery-types/",
            "keywords": ["バッテリー", "AGM", "リチウム", "ニッケル水素", "価格比較", "容量計算", "選び方"]
        },
        {
            "title": "サブバッテリー容量計算のコツ",
            "url": "https://camper-repair.net/battery-selection/",
            "keywords": ["バッテリー", "容量計算", "消費電力", "連続運用", "充電サイクル", "最大負荷"]
        },
        {
            "title": "サブバッテリーの充電方法・充電器比較",
            "url": "https://camper-repair.net/blog/risk1/",
            "keywords": ["バッテリー", "充電方法", "走行充電", "外部電源", "ソーラーパネル", "AC充電器", "DC-DC充電器"]
        },
        {
            "title": "サブバッテリーとインバーターの組み合わせ",
            "url": "https://camper-repair.net/blog/battery-inverter/",
            "keywords": ["バッテリー", "インバーター", "DC-AC変換", "正弦波", "容量選定", "消費電力"]
        },
        {
            "title": "サブバッテリーとソーラーパネルの連携",
            "url": "https://camper-repair.net/blog/battery-solar/",
            "keywords": ["バッテリー", "ソーラーパネル", "充電制御", "MPPTコントローラー", "PWM制御", "発電量"]
        },
        {
            "title": "サブバッテリーの寿命と交換時期",
            "url": "https://camper-repair.net/blog/battery-life/",
            "keywords": ["バッテリー", "寿命", "サイクル回数", "容量低下", "経年劣化", "交換目安"]
        },
        {
            "title": "サブバッテリー運用時の注意点",
            "url": "https://camper-repair.net/blog/battery-care/",
            "keywords": ["バッテリー", "過放電", "過充電", "ショート防止", "ヒューズ", "温度上昇"]
        },
        {
            "title": "サブバッテリーのメンテナンス方法",
            "url": "https://camper-repair.net/battery-selection/",
            "keywords": ["バッテリー", "定期点検", "端子清掃", "バッテリー液", "比重測定", "電圧測定"]
        },
        {
            "title": "サブバッテリーの取り付け・配線例",
            "url": "https://camper-repair.net/blog/risk1/",
            "keywords": ["バッテリー", "取り付け", "配線方法", "配線図", "ヒューズ", "ケーブルサイズ"]
        },
        {
            "title": "サブバッテリーのトラブル・故障事例",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["バッテリー", "故障", "電圧低下", "容量不足", "過放電", "過充電", "膨張"]
        },
        {
            "title": "サブバッテリーの容量アップ・増設術",
            "url": "https://camper-repair.net/battery-selection/",
            "keywords": ["バッテリー", "容量アップ", "増設", "並列接続", "直列接続", "配線図"]
        },
        {
            "title": "サブバッテリーと家庭用家電の利用",
            "url": "https://camper-repair.net/blog/risk1/",
            "keywords": ["バッテリー", "家庭用家電", "インバーター", "消費電力", "冷蔵庫", "電子レンジ", "エアコン"]
        },
        {
            "title": "サブバッテリー残量管理・インジケーター活用",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["バッテリー", "残量管理", "インジケーター", "電圧計", "電流計", "モニター"]
        },
        {
            "title": "サブバッテリーと外部電源切替運用",
            "url": "https://camper-repair.net/battery-selection/",
            "keywords": ["バッテリー", "外部電源", "切替リレー", "優先給電", "AC/DC切替", "手動/自動切替"]
        },
        {
            "title": "サブバッテリーのDIYカスタム事例",
            "url": "https://camper-repair.net/blog/risk1/",
            "keywords": ["バッテリー", "DIY", "カスタム", "容量アップ", "配線見直し", "充電方法"]
        },
        {
            "title": "サブバッテリーの廃棄・リサイクル方法",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["バッテリー", "廃棄", "リサイクル", "回収業者", "鉛バッテリー", "リチウムバッテリー"]
        },
        {
            "title": "サブバッテリー車検・法規制まとめ",
            "url": "https://camper-repair.net/battery-selection/",
            "keywords": ["バッテリー", "車検", "保安基準", "追加装備", "配線基準", "容量制限"]
        },
        {
            "title": "サブバッテリーQ&A・よくある質問集",
            "url": "https://camper-repair.net/blog/risk1/",
            "keywords": ["バッテリー", "Q&A", "FAQ", "容量選定", "充電方法", "運用方法", "DIY"]
        },
        {
            "title": "サブバッテリー運用の体験談・口コミ",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["バッテリー", "体験談", "運用失敗", "成功事例", "トラブル事例", "口コミ"]
        },
        
        # インバーター関連（20テーマ）
        {
            "title": "インバーター完全ガイド",
            "url": "https://camper-repair.net/blog/inverter1/",
            "keywords": ["インバーター", "正弦波", "矩形波", "DC-AC変換", "容量選定", "出力波形", "連続出力"]
        },
        {
            "title": "インバーターの仕組みと役割",
            "url": "https://camper-repair.net/blog/inverter-selection/",
            "keywords": ["インバーター", "変換回路", "DC入力", "AC出力", "電圧変換", "周波数変換", "回路構成"]
        },
        {
            "title": "インバーターの種類と特徴",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["インバーター", "正弦波インバーター", "修正正弦波", "矩形波", "定格容量", "連続出力", "ピーク出力"]
        },
        {
            "title": "インバーター容量の選び方",
            "url": "https://camper-repair.net/blog/inverter1/",
            "keywords": ["インバーター", "容量選定", "必要容量計算", "家電消費電力", "ピーク電力", "同時使用機器"]
        },
        {
            "title": "インバーターの配線・設置方法",
            "url": "https://camper-repair.net/blog/inverter-selection/",
            "keywords": ["インバーター", "配線手順", "接続ケーブル", "端子加工", "アース線", "ヒューズ設置"]
        },
        {
            "title": "インバーター運用時の安全対策",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["インバーター", "安全基準", "ヒューズ設置", "ブレーカー", "アース接続", "ショート対策"]
        },
        {
            "title": "インバーターで使える家電リスト",
            "url": "https://camper-repair.net/blog/inverter1/",
            "keywords": ["インバーター", "家電使用可否", "冷蔵庫", "電子レンジ", "IH調理器", "エアコン", "TV"]
        },
        {
            "title": "インバーターとサブバッテリーの関係",
            "url": "https://camper-repair.net/blog/inverter-selection/",
            "keywords": ["インバーター", "サブバッテリー", "直結接続", "容量配分", "バッテリー消耗", "電圧降下"]
        },
        {
            "title": "インバーター切替運用のポイント",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["インバーター", "外部電源", "切替スイッチ", "サブバッテリー連動", "優先給電", "手動切替"]
        },
        {
            "title": "インバータートラブル事例と対策",
            "url": "https://camper-repair.net/blog/inverter1/",
            "keywords": ["インバーター", "電源入らない", "出力ゼロ", "波形異常", "ヒューズ切れ", "過熱停止"]
        },
        {
            "title": "インバーターの定期メンテナンス",
            "url": "https://camper-repair.net/blog/inverter-selection/",
            "keywords": ["インバーター", "メンテナンス", "定期点検", "端子清掃", "配線緩み", "ヒューズ確認"]
        },
        {
            "title": "インバーター選びの失敗例と注意点",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["インバーター", "容量不足", "波形選定ミス", "安価モデル", "発熱問題", "ノイズ問題"]
        },
        {
            "title": "インバーターと冷蔵庫の相性",
            "url": "https://camper-repair.net/blog/inverter1/",
            "keywords": ["インバーター", "冷蔵庫", "起動電流", "定格消費電力", "コンプレッサー方式", "正弦波必須"]
        },
        {
            "title": "インバーターのノイズ・電波障害対策",
            "url": "https://camper-repair.net/blog/inverter-selection/",
            "keywords": ["インバーター", "ノイズ対策", "電波障害", "出力波形", "アース強化", "配線分離"]
        },
        {
            "title": "インバーターの消費電力と省エネ運用",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["インバーター", "消費電力", "待機電力", "負荷効率", "省エネ家電", "エコ運転"]
        },
        {
            "title": "インバーターのDIY設置手順",
            "url": "https://camper-repair.net/blog/inverter1/",
            "keywords": ["インバーター", "DIY設置", "作業手順", "配線設計", "部品選定", "固定方法"]
        },
        {
            "title": "インバーターの人気モデル比較",
            "url": "https://camper-repair.net/blog/inverter-selection/",
            "keywords": ["インバーター", "人気モデル", "メーカー比較", "スペック比較", "容量別", "波形別"]
        },
        {
            "title": "インバーターと発電機の連携運用",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["インバーター", "発電機", "連動運転", "入力切替", "出力安定", "発電量制御"]
        },
        {
            "title": "インバーターとソーラー発電の組み合わせ",
            "url": "https://camper-repair.net/blog/inverter1/",
            "keywords": ["インバーター", "ソーラーパネル", "チャージコントローラー", "バッテリー充電", "連携運用", "出力安定化"]
        },
        {
            "title": "インバーターの保証・サポート活用法",
            "url": "https://camper-repair.net/blog/inverter-selection/",
            "keywords": ["インバーター", "メーカー保証", "保証期間", "保証内容", "初期不良対応", "修理サポート"]
        },
        
        # 電気・電装系関連
        {
            "title": "電気・電装系トラブル完全ガイド",
            "url": "https://camper-repair.net/blog/electrical/",
            "keywords": ["電気", "電装", "配線", "LED", "照明", "電装系"]
        },
        {
            "title": "ソーラーパネル・電気システム連携",
            "url": "https://camper-repair.net/blog/electrical-solar-panel/",
            "keywords": ["ソーラーパネル", "電気", "発電", "充電", "太陽光", "電装系"]
        },
        
        # 基本修理・メンテナンス
        {
            "title": "基本修理・キャンピングカー修理の基本",
            "url": "https://camper-repair.net/blog/risk1/",
            "keywords": ["修理", "基本", "手順", "工具", "部品", "故障", "メンテナンス"]
        },
        {
            "title": "定期点検・定期点検とメンテナンス",
            "url": "https://camper-repair.net/battery-selection/",
            "keywords": ["点検", "メンテナンス", "定期", "予防", "保守", "チェック", "定期点検"]
        },
        
        # その他のカテゴリ
        {
            "title": "ルーフベント・換気扇の選び方",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["ルーフベント", "換気扇", "ファン", "換気", "ベント"]
        },
        {
            "title": "トイレ・カセットトイレのトラブル対処",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["トイレ", "カセット", "マリン", "フラッパー", "トイレ"]
        },
                 {
             "title": "水道ポンプ・給水システム",
             "url": "https://camper-repair.net/blog/repair1/",
             "keywords": ["水道", "ポンプ", "給水", "水", "水道ポンプ"]
         },
         {
             "title": "水道ポンプ完全ガイド",
             "url": "https://camper-repair.net/blog/water-pump/",
             "keywords": ["水道ポンプ", "給水ポンプ", "ポンプ", "水道", "給水", "水", "圧力", "流量"]
         },
         {
             "title": "水道ポンプの種類と選び方",
             "url": "https://camper-repair.net/blog/water-pump-selection/",
             "keywords": ["水道ポンプ", "種類", "選び方", "圧力式", "流量式", "DCポンプ", "ACポンプ"]
         },
         {
             "title": "水道ポンプの取り付け・設置方法",
             "url": "https://camper-repair.net/blog/water-pump-installation/",
             "keywords": ["水道ポンプ", "取り付け", "設置", "配管", "配線", "固定", "アース"]
         },
         {
             "title": "水道ポンプのトラブル・故障事例",
             "url": "https://camper-repair.net/blog/water-pump-trouble/",
             "keywords": ["水道ポンプ", "故障", "トラブル", "水が出ない", "圧力不足", "異音", "過熱"]
         },
         {
             "title": "水道ポンプのメンテナンス方法",
             "url": "https://camper-repair.net/blog/water-pump-maintenance/",
             "keywords": ["水道ポンプ", "メンテナンス", "定期点検", "清掃", "フィルター", "オイル交換"]
         },
         {
             "title": "水道ポンプとタンクの関係",
             "url": "https://camper-repair.net/blog/water-pump-tank/",
             "keywords": ["水道ポンプ", "タンク", "給水タンク", "容量", "水位", "空焚き防止"]
         },
         {
             "title": "水道ポンプの配管・配線工事",
             "url": "https://camper-repair.net/blog/water-pump-piping/",
             "keywords": ["水道ポンプ", "配管", "配線", "工事", "ケーブル", "ヒューズ", "スイッチ"]
         },
         {
             "title": "水道ポンプの省エネ運用",
             "url": "https://camper-repair.net/blog/water-pump-energy/",
             "keywords": ["水道ポンプ", "省エネ", "消費電力", "効率", "運転時間", "自動停止"]
         },
         {
             "title": "水道ポンプのDIY修理術",
             "url": "https://camper-repair.net/blog/water-pump-diy/",
             "keywords": ["水道ポンプ", "DIY", "修理", "分解", "部品交換", "調整"]
         },
         {
             "title": "水道ポンプの人気モデル比較",
             "url": "https://camper-repair.net/blog/water-pump-comparison/",
             "keywords": ["水道ポンプ", "人気モデル", "比較", "スペック", "価格", "メーカー"]
         },
        {
            "title": "冷蔵庫・冷凍システム",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["冷蔵庫", "冷凍", "コンプレッサー", "冷蔵"]
        },
        {
            "title": "ガスシステム・FFヒーター",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["ガス", "コンロ", "ヒーター", "FF", "ガスシステム"]
        },
        # 雨漏り関連（20テーマ）
        {
            "title": "雨漏り完全ガイド",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["雨漏り", "屋根防水", "シーリング", "パッキン", "ウインドウ周り", "天窓"]
        },
        {
            "title": "雨漏りしやすい箇所と見分け方",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["雨漏り箇所", "屋根継ぎ目", "ウインドウ", "ドア", "ルーフベント", "天窓"]
        },
        {
            "title": "雨漏り点検のコツと頻度",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["雨漏り点検", "目視点検", "シーリングチェック", "パッキン硬化", "隙間確認"]
        },
        {
            "title": "雨漏り応急処置の方法",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["応急処置", "防水テープ", "ブルーシート", "シーリング材", "パテ", "止水スプレー"]
        },
        {
            "title": "雨漏りのDIY補修術",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["DIY補修", "シーリング打ち直し", "防水テープ貼付", "パッキン交換", "コーキング"]
        },
        {
            "title": "プロに依頼するべき雨漏り修理",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["プロ修理", "専門業者", "診断機器", "調査手法", "補修提案", "見積もり"]
        },
        {
            "title": "屋根防水の見直しポイント",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["屋根防水", "防水塗料", "トップコート", "シーリング材", "ジョイント部", "パネル接合部"]
        },
        {
            "title": "シーリング材の選び方と施工",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["シーリング材", "種類比較", "ウレタン系", "シリコン系", "ブチル系", "耐久性"]
        },
        {
            "title": "ウインドウ・天窓の防水対策",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["ウインドウ", "天窓", "ゴムパッキン", "パッキン交換", "シーリング", "結露防止"]
        },
        {
            "title": "ルーフベント・サイドオーニングの漏水防止",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["ルーフベント", "サイドオーニング", "取付部", "シーリング補修", "防水テープ", "構造確認"]
        },
        {
            "title": "配線取り出し部の雨対策",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["配線出口", "グロメット", "パッキン", "シーリング", "経年硬化", "結束バンド"]
        },
        {
            "title": "経年劣化による雨漏り原因",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["経年劣化", "パッキン硬化", "シーリングひび割れ", "コーキング剥がれ", "樹脂部品変形"]
        },
        {
            "title": "雨漏りと結露の違い",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["雨漏り", "結露", "現象比較", "発生タイミング", "場所の違い", "水滴の性状"]
        },
        {
            "title": "カビ・悪臭防止と室内換気",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["カビ", "悪臭", "湿度管理", "雨漏り", "室内換気", "換気扇", "ルーフベント"]
        },
        {
            "title": "雨漏りの再発防止策",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["再発防止", "予防点検", "定期シーリング補修", "パッキン交換", "塗装メンテナンス"]
        },
        {
            "title": "雨漏り補修後の確認ポイント",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["補修確認", "漏水チェック", "水かけ試験", "シーリング乾燥", "補修跡観察"]
        },
        {
            "title": "DIYでできる雨漏り対策グッズ",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["防水テープ", "シーリング材", "パテ", "防水スプレー", "ブルーシート", "コーキングガン"]
        },
        {
            "title": "雨漏りのプロ診断・高精度調査法",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["プロ診断", "散水テスト", "サーモグラフィ", "蛍光剤", "漏水検知機", "音響調査"]
        },
        {
            "title": "雨漏りと保険・保証制度",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["保険適用", "車両保険", "雨漏り補償", "修理保証", "自然災害対応", "補修範囲"]
        },
        {
            "title": "雨漏りトラブル体験談・事例集",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["雨漏り体験談", "修理事例", "失敗例", "DIY体験", "プロ修理体験", "再発例"]
        },
        {
            "title": "雨漏りトラブルを未然に防ぐ習慣",
            "url": "https://camper-repair.net/blog/rain-leak/",
            "keywords": ["予防習慣", "定期点検", "屋根掃除", "排水路確認", "パッキン保湿", "シーリング補修"]
        },
        {
            "title": "異音・騒音対策",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["異音", "音", "騒音", "振動", "ノイズ"]
                 }
     ]
    
    # テキストデータからURLが見つからない場合のみフォールバックを使用
    if not blog_links:
        # フォールバック用のブログリンクを使用
        blog_links = fallback_blog_links
    
    relevant_blogs = []
    for blog in blog_links:
        score = 0
        
        # テキストデータから抽出したURLかどうかを判定
        is_extracted_url = blog["url"] in extracted_urls
        
        # 質問のキーワードとの直接マッチング（最高優先度）
        for query_keyword in query_keywords:
            if query_keyword in blog["title"].lower():
                score += 20  # 質問キーワードがタイトルに含まれる場合は高スコア
            if query_keyword in blog["url"].lower():
                score += 15  # 質問キーワードがURLに含まれる場合も高スコア
            if query_keyword in blog["keywords"]:
                score += 10  # 質問キーワードがキーワードに含まれる場合
        
        # 基本キーワードマッチング
        for keyword in blog["keywords"]:
            if keyword in query_lower:
                score += 1
        
        # テキストデータから抽出したキーワードとのマッチング
        for extracted_keyword in extracted_keywords:
            if extracted_keyword in blog["keywords"]:
                score += 2  # テキストデータからのキーワードは重みを高く
        
        # カテゴリマッチング（より高い重み）
        for extracted_keyword in extracted_keywords:
            if extracted_keyword in blog["title"].lower():
                score += 3
        
        # カテゴリー判定による重み付け
        blog_category = determine_blog_category(blog, query)
        query_category = determine_query_category(query)
        
        # カテゴリーが一致する場合は大幅にスコアを上げる
        if blog_category == query_category:
            score += 10
        
        # テキストデータから抽出したURLの場合は大幅にスコアを上げる
        if is_extracted_url:
            score += 50  # テキストデータからのURLを最優先
        
        if score > 0:
            relevant_blogs.append((blog, score))
    
    relevant_blogs.sort(key=lambda x: x[1], reverse=True)
    
    # テキストデータから抽出したURLを最優先で返す
    result_blogs = []
    added_urls = set()  # 追加済みURLを追跡
    
    # まず、テキストデータから抽出したURLを含むブログを最優先で追加
    for blog, score in relevant_blogs:
        if blog["url"] in extracted_urls and blog["url"] not in added_urls:
            result_blogs.append(blog)
            added_urls.add(blog["url"])
    
    # 次に、その他の関連ブログを追加（重複を避ける）
    for blog, score in relevant_blogs:
        if blog["url"] not in added_urls and len(result_blogs) < 5:
            result_blogs.append(blog)
            added_urls.add(blog["url"])
    
    # 最終的に重複を除去してユニークなURLのみを返す
    final_blogs = []
    final_urls = set()
    
    for blog in result_blogs:
        if blog["url"] not in final_urls:
            final_blogs.append(blog)
            final_urls.add(blog["url"])
    
    # 最大5件まで返す（一つ一つ個別のブログ）
    return final_blogs[:5]

def show_ai_loading():
    """AI回答生成のローディング表示"""
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        st.info("⏳ AIが専門知識を活用して回答を生成中...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 関連情報を検索中...")
        progress_bar.progress(25)
        
        status_text.text("📚 知識ベースから情報を取得中...")
        progress_bar.progress(50)
        
        status_text.text("🤖 AIが回答を生成中...")
        progress_bar.progress(75)
        
        status_text.text("✅ 回答を整理中...")
        progress_bar.progress(100)
    
    return loading_placeholder

def generate_ai_response_with_knowledge(prompt, knowledge_base, show_loading=True):
    """知識ベースを活用したAI回答を生成（最適化版）"""
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return "⚠️ **OpenAI APIキーが設定されていません。**\n\nAPIキーを設定してから再度お試しください。\n\n## 🛠️ 岡山キャンピングカー修理サポートセンター\n専門的な修理やメンテナンスが必要な場合は、お気軽にご相談ください：\n\n**🏢 岡山キャンピングカー修理サポートセンター**\n📍 **住所**: 〒700-0921 岡山市北区東古松485-4 2F\n📞 **電話**: 086-206-6622\n📧 **お問合わせ**: https://camper-repair.net/contact/\n🌐 **ホームページ**: https://camper-repair.net/blog/\n⏰ **営業時間**: 年中無休（9:00～21:00）\n※不在時は折り返しお電話差し上げます。\n\n**（運営）株式会社リクエストプラス**"
        
        # キャッシュキーを生成
        cache_key = hashlib.md5(f"{prompt}_{str(knowledge_base.keys())}".encode()).hexdigest()
        
        # セッションキャッシュをチェック
        if "ai_response_cache" not in st.session_state:
            st.session_state.ai_response_cache = {}
        
        if cache_key in st.session_state.ai_response_cache:
            return st.session_state.ai_response_cache[cache_key]
        
        ChatOpenAI, HumanMessage, AIMessage = ensure_langchain()
        if not ChatOpenAI:
            return "❌ LangChainが利用できません"
        
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=openai_api_key,
            max_tokens=1000  # 応答を短縮してパフォーマンス向上
        )
        
        # 関連知識を抽出（最適化）
        relevant_knowledge = extract_relevant_knowledge(prompt, knowledge_base)
        blog_links = get_relevant_blog_links(prompt, knowledge_base)
        
        # Notionデータベースからの情報を取得（最適化版）
        notion_info = ""
        if NOTION_OPTIMIZATION_AVAILABLE:
            try:
                notion_data = search_camper_repair_info(prompt)
                if notion_data["total_results"] > 0:
                    notion_info = f"\n\n【Notionデータベースからの関連情報】\n"
                    
                    # 修理ケース情報
                    if notion_data["repair_cases"]:
                        notion_info += "**関連する修理ケース:**\n"
                        for case in notion_data["repair_cases"][:3]:  # 最大3件
                            notion_info += f"• {case.get('title', '')}: {case.get('description', '')[:100]}...\n"
                            if case.get('cost_estimate'):
                                notion_info += f"  費用目安: {case.get('cost_estimate')}\n"
                    
                    # 部品・工具情報
                    if notion_data["items"]:
                        notion_info += "\n**関連する部品・工具:**\n"
                        for item in notion_data["items"][:3]:  # 最大3件
                            notion_info += f"• {item.get('name', '')}: {item.get('description', '')[:50]}...\n"
                            if item.get('price'):
                                notion_info += f"  価格: {item.get('price')}\n"
            except Exception as e:
                print(f"Notion search error: {e}")
        
        # 知識ベースの内容をシステムプロンプトに含める
        knowledge_context = ""
        if relevant_knowledge:
            knowledge_context = "\n\n【関連する専門知識】\n" + "\n\n".join(relevant_knowledge[:3])
        
        system_prompt = f"""あなたは岡山キャンピングカー修理サポートセンターの専門スタッフです。
キャンピングカーのあらゆるトラブル・問題について、専門知識を活用して具体的で実用的な回答を提供してください。

{knowledge_context}{notion_info}

**回答の原則**:
1. ユーザーの質問を必ず回答してください（「トイレのファンが回らない」以外の質問も含む）
2. 提供された知識ベースとNotionデータベースを最大限活用してください
3. 知識ベースに該当する情報がない場合でも、一般的なキャンピングカー修理の知識に基づいて回答してください
4. 安全第一を最優先にしてください
5. 費用目安があれば必ず含めてください

**回答形式**:
1. **状況確認**: 問題の詳細な状況を確認
2. **安全上の注意点**: 安全上の注意点を明示
3. **緊急度の判断**: 緊急度を判断
4. **応急処置**: 必要な場合の応急処置
5. **具体的な修理手順**: 段階的な修理手順
6. **必要な工具・部品**: 必要な工具・部品のリスト
7. **予防メンテナンスのアドバイス**: 再発防止のためのアドバイス
8. **専門家への相談タイミング**: 専門店への相談が必要な場合

**対応可能なトラブル**:
- バッテリー・サブバッテリー関連
- インバーター・電源関連
- トイレ・水回り関連
- ルーフベント・換気扇関連
- 冷蔵庫・家電関連
- ガス・ヒーター関連
- 電気・電装系関連
- 雨漏り・防水関連
- ドア・窓の開閉不良
- タイヤ・外装関連
- エアコン・空調関連
- 家具・内装関連
- その他キャンピングカー全般のトラブル

ユーザーの質問に必ず回答し、専門的で実用的なアドバイスを提供してください。"""

        messages = [
            HumanMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        
        # 岡山キャンピングカー修理サポートセンター情報を追加
        support_section = "\n\n## 🛠️ 岡山キャンピングカー修理サポートセンター\n"
        support_section += "専門的な修理やメンテナンスが必要な場合は、お気軽にご相談ください：\n\n"
        support_section += "**🏢 岡山キャンピングカー修理サポートセンター**\n"
        support_section += "📍 **住所**: 〒700-0921 岡山市北区東古松485-4 2F\n"
        support_section += "📞 **電話**: 086-206-6622\n"
        support_section += "📧 **お問合わせ**: https://camper-repair.net/contact/\n"
        support_section += "🌐 **ホームページ**: https://camper-repair.net/blog/\n"
        support_section += "⏰ **営業時間**: 年中無休（9:00～21:00）\n"
        support_section += "※不在時は折り返しお電話差し上げます。\n\n"
        support_section += "**（運営）株式会社リクエストプラス**\n\n"
        support_section += "**🔧 対応サービス**:\n"
        support_section += "• バッテリー・インバーター修理・交換\n"
        support_section += "• 電気配線・電装系トラブル対応\n"
        support_section += "• 雨漏り・防水工事\n"
        support_section += "• 各種家電・設備の修理\n"
        support_section += "• 定期点検・メンテナンス\n"
        support_section += "• 緊急対応・出張修理（要相談）\n\n"
        support_section += "**💡 ご相談の際は**:\n"
        support_section += "• 車種・年式\n"
        support_section += "• 症状の詳細\n"
        support_section += "• 希望する対応方法\n"
        support_section += "をお教えください。\n\n"
        
        response.content += support_section
        
        # 関連ブログを追加
        if blog_links:
            blog_section = "\n\n## 📚 関連ブログ・参考記事\n"
            blog_section += "より詳しい情報や実践的な対処法については、以下の記事もご参考ください：\n\n"
            
            # デバッグ情報（開発時のみ表示）
            # blog_section += f"**🔍 抽出されたキーワード**: {', '.join(all_keywords[:5])}\n\n"
            
            # 重複するURLを除去して、ユニークなURLのみを表示
            unique_blogs = []
            seen_urls = set()
            
            for blog in blog_links:
                # URLにカンマが含まれている場合は分割
                urls = blog['url'].split(',')
                
                for url in urls:
                    url = url.strip()  # 前後の空白を除去
                    if url and url not in seen_urls:
                        # 分割されたURLごとに個別のブログエントリを作成
                        unique_blogs.append({
                            'title': blog['title'],
                            'url': url,
                            'keywords': blog['keywords']
                        })
                        seen_urls.add(url)
            
            # カテゴリーごとにブログを分類
            categorized_blogs = {}
            for blog in unique_blogs:
                category = determine_blog_category(blog, prompt)
                if category not in categorized_blogs:
                    categorized_blogs[category] = []
                categorized_blogs[category].append(blog)
            
            # カテゴリーごとに表示
            for category, blogs in categorized_blogs.items():
                if blogs:
                    blog_section += f"### {category}\n"
                    for i, blog in enumerate(blogs[:3], 1):  # 各カテゴリー最大3件
                        # テキストデータから抽出したURLかどうかを判定
                        is_extracted = False
                        source_indicator = "📄" if is_extracted else "📖"
                        blog_section += f"**{i}. {blog['title']}** {source_indicator}\n"
                        blog_section += f"   {blog['url']}\n\n"
            
            response.content += blog_section
        
        # キャッシュに保存
        st.session_state.ai_response_cache[cache_key] = response.content
        return response.content
        
    except Exception as e:
        return f"""⚠️ **エラーが発生しました: {str(e)}**

申し訳ございませんが、一時的に回答を生成できませんでした。
しばらく時間をおいてから再度お試しください。

## 🛠️ 岡山キャンピングカー修理サポートセンター
専門的な修理やメンテナンスが必要な場合は、お気軽にご相談ください：

**🏢 岡山キャンピングカー修理サポートセンター**
📍 **住所**: 〒700-0921 岡山市北区東古松485-4 2F
📞 **電話**: 086-206-6622
📧 **お問合わせ**: https://camper-repair.net/contact/
🌐 **ホームページ**: https://camper-repair.net/blog/
⏰ **営業時間**: 年中無休（9:00～21:00）
※不在時は折り返しお電話差し上げます。

**（運営）株式会社リクエストプラス**

**🔧 対応サービス**:
• バッテリー・インバーター修理・交換
• 電気配線・電装系トラブル対応
• 雨漏り・防水工事
• 各種家電・設備の修理
• 定期点検・メンテナンス
• 緊急対応・出張修理（要相談）"""

def run_diagnostic_flow():
    """対話式症状診断（NotionDB連携版）"""
    st.subheader("🔍 対話式症状診断")
    
    # NotionDBの接続状況を確認
    notion_status = "❌ 未接続"
    diagnostic_data = None
    repair_cases = []
    
    if notion_api_key:
        try:
            diagnostic_data = load_notion_diagnostic_data()
            repair_cases = load_notion_repair_cases()
            if diagnostic_data or repair_cases:
                notion_status = "✅ 接続済み"
            else:
                notion_status = "⚠️ データなし"
        except Exception as e:
            notion_status = f"❌ エラー: {str(e)[:50]}"
    
    # 接続状況を表示（非表示化）
    # st.info(f"**NotionDB接続状況**: {notion_status}")
    
    # NotionDB接続エラーメッセージを非表示化（本番環境対応）
    # if notion_status == "❌ 未接続":
    #     st.warning("NotionDBに接続できません。環境変数の設定を確認してください。")
    #     st.info("**必要な環境変数**:")
    #     st.code("NOTION_API_KEY=your_notion_token\nNODE_DB_ID=your_diagnostic_db_id\nCASE_DB_ID=your_repair_case_db_id")
    
    # 診断モードの選択
    diagnostic_mode = st.radio(
        "診断モードを選択してください:",
        ["🤖 AI診断（推奨）", "📋 対話式診断", "🔍 詳細診断"]
    )
    
    if diagnostic_mode == "🤖 AI診断（推奨）":
        run_ai_diagnostic(diagnostic_data, repair_cases)
    elif diagnostic_mode == "📋 対話式診断":
        run_interactive_diagnostic(diagnostic_data, repair_cases)
    else:
        run_detailed_diagnostic(diagnostic_data, repair_cases)

def run_ai_diagnostic(diagnostic_data, repair_cases):
    """AI診断モード（リレーション活用版）"""
    st.markdown("### 🤖 AI診断")
    st.markdown("症状を詳しく説明してください。最適な診断と解決策を提案します。")
    
    # 症状入力
    symptoms_input = st.text_area(
        "症状を詳しく説明してください:",
        placeholder="例: バッテリーの電圧が12V以下に下がって、インバーターが動作しません。充電器を接続しても充電されない状態です。",
        height=150
    )
    
    if st.button("🔍 AI診断開始", type="primary"):
        if symptoms_input.strip():
            # ローディング表示のコンテナ
            loading_container = st.container()
            
            with loading_container:
                # ローディングメッセージ
                st.info("⏳ AIがリレーションデータを活用して診断中...")
                
                # プログレスバー
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 段階的なローディング表示
                status_text.text("📚 知識ベースを読み込み中...")
                progress_bar.progress(20)
                
                status_text.text("🔗 リレーションデータを分析中...")
                progress_bar.progress(40)
                
                status_text.text("🤖 AIが症状を診断中...")
                progress_bar.progress(60)
                
                status_text.text("📋 診断結果を整理中...")
                progress_bar.progress(80)
                
                status_text.text("✅ 診断完了")
                progress_bar.progress(100)
            
            # 実際の診断処理
            # 知識ベースを読み込み
            knowledge_base = load_knowledge_base()
            
            # リレーションデータを活用した高度なコンテキスト作成
            context = create_relation_context(symptoms_input, diagnostic_data, repair_cases)
            
            # 診断プロンプトを作成
            diagnosis_prompt = f"""症状: {symptoms_input}

{context}

上記の症状について、3つのデータベースのリレーション情報を活用して、以下の形式で詳細な診断と解決策を提供してください：

1. **診断結果**
2. **関連する修理ケース**
3. **必要な部品・工具（価格・サプライヤー情報付き）**
4. **具体的な修理手順**
5. **予防メンテナンスのアドバイス**"""
            
            # AI診断を実行（ローディング表示は関数内で処理）
            diagnosis_result = generate_ai_response_with_knowledge(diagnosis_prompt, knowledge_base)
            
            # ローディング表示をクリア
            loading_container.empty()
            
            st.markdown("## 📋 AI診断結果")
            st.markdown(diagnosis_result)
            
            # リレーションデータの詳細表示
            show_relation_details(symptoms_input, diagnostic_data, repair_cases)
        else:
            st.warning("症状を入力してください。")

def create_relation_context(symptoms_input, diagnostic_data, repair_cases):
    """リレーションデータを活用したコンテキストを作成"""
    context = ""
    
    # 症状に基づいて関連する診断ノードを特定
    relevant_nodes = []
    if diagnostic_data and diagnostic_data.get("nodes"):
        for node in diagnostic_data["nodes"]:
            if any(symptom in symptoms_input.lower() for symptom in node.get("symptoms", [])):
                relevant_nodes.append(node)
    
    # 関連する修理ケースを特定
    relevant_cases = []
    for case in repair_cases:
        if any(symptom in symptoms_input.lower() for symptom in case.get("symptoms", [])):
            relevant_cases.append(case)
    
    # コンテキストの構築
    if relevant_nodes:
        context += "\n\n【関連診断ノード】\n"
        for node in relevant_nodes[:3]:
            context += f"- {node['title']} ({node['category']}): {', '.join(node['symptoms'])}\n"
            
            # 関連修理ケースの追加
            if node.get("related_cases"):
                context += "  関連修理ケース:\n"
                for case in node["related_cases"][:2]:
                    context += f"    • {case['title']}: {case['solution'][:100]}...\n"
            
            # 関連部品・工具の追加
            if node.get("related_items"):
                context += "  関連部品・工具:\n"
                for item in node["related_items"][:3]:
                    price_info = f" (¥{item['price']})" if item.get('price') else ""
                    supplier_info = f" - {item['supplier']}" if item.get('supplier') else ""
                    context += f"    • {item['name']}{price_info}{supplier_info}\n"
    
    if relevant_cases:
        context += "\n\n【関連修理ケース】\n"
        for case in relevant_cases[:3]:
            context += f"- {case['title']} ({case['category']}): {case['solution'][:150]}...\n"
            
            # 関連部品・工具の追加
            if case.get("related_items"):
                context += "  必要な部品・工具:\n"
                for item in case["related_items"][:3]:
                    price_info = f" (¥{item['price']})" if item.get('price') else ""
                    supplier_info = f" - {item['supplier']}" if item.get('supplier') else ""
                    context += f"    • {item['name']}{price_info}{supplier_info}\n"
    
    return context

def show_relation_details(symptoms_input, diagnostic_data, repair_cases):
    """リレーションデータの詳細を表示"""
    st.markdown("## 🔗 リレーションデータ詳細")
    
    # 関連診断ノードの表示
    if diagnostic_data and diagnostic_data.get("nodes"):
        relevant_nodes = []
        for node in diagnostic_data["nodes"]:
            if any(symptom in symptoms_input.lower() for symptom in node.get("symptoms", [])):
                relevant_nodes.append(node)
        
        if relevant_nodes:
            st.markdown("### 📊 関連診断ノード")
            for node in relevant_nodes[:3]:
                with st.expander(f"🔹 {node['title']} ({node['category']})"):
                    st.write("**症状**:", ", ".join(node["symptoms"]))
                    
                    if node.get("related_cases"):
                        st.write("**関連修理ケース**:")
                        for case in node["related_cases"][:2]:
                            st.write(f"  • {case['title']}: {case['solution'][:100]}...")
                    
                    if node.get("related_items"):
                        st.write("**関連部品・工具**:")
                        for item in node["related_items"][:3]:
                            price_info = f" (¥{item['price']})" if item.get('price') else ""
                            supplier_info = f" - {item['supplier']}" if item.get('supplier') else ""
                            st.write(f"  • {item['name']}{price_info}{supplier_info}")
    
    # 関連修理ケースの表示
    relevant_cases = []
    for case in repair_cases:
        if any(symptom in symptoms_input.lower() for symptom in case.get("symptoms", [])):
            relevant_cases.append(case)
    
    if relevant_cases:
        st.markdown("### 🔧 関連修理ケース")
        for case in relevant_cases[:3]:
            with st.expander(f"🔧 {case['title']} ({case['category']})"):
                st.write("**症状**:", ", ".join(case["symptoms"]))
                st.write("**解決方法**:", case["solution"])
                
                if case.get("related_items"):
                    st.write("**必要な部品・工具**:")
                    for item in case["related_items"][:5]:
                        price_info = f" (¥{item['price']})" if item.get('price') else ""
                        supplier_info = f" - {item['supplier']}" if item.get('supplier') else ""
                        st.write(f"  • {item['name']}{price_info}{supplier_info}")
                
                if case.get("related_nodes"):
                    st.write("**関連診断ノード**:")
                    for node in case["related_nodes"][:2]:
                        st.write(f"  • {node['title']}: {', '.join(node['symptoms'])}")

def display_blog_links(blog_links, query):
    """関連ブログリンクを表示"""
    if not blog_links:
        st.info("📚 関連するブログ記事が見つかりませんでした")
        return
    
    st.markdown("### 📚 関連ブログ記事")
    st.info(f"「{query}」に関連するブログ記事です")
    
    for i, blog in enumerate(blog_links, 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{i}. {blog['title']}**")
                st.caption(f"関連キーワード: {', '.join(blog['keywords'])}")
            with col2:
                if st.button(f"📖 読む", key=f"blog_{i}"):
                    st.markdown(f"[記事を開く]({blog['url']})")
                    st.info(f"新しいタブで {blog['url']} が開きます")
        
        st.divider()

def run_interactive_diagnostic(diagnostic_data, repair_cases):
    """対話式診断モード（NotionDB活用版）"""
    st.markdown("### 📋 対話式診断")
    
    # NotionDBからカテゴリを取得、または詳細なデフォルトを使用
    if diagnostic_data and diagnostic_data.get("start_nodes"):
        categories = {}
        for node in diagnostic_data["start_nodes"]:
            if node["title"]:
                categories[node["title"]] = node["symptoms"]
        # NotionDB接続成功メッセージを非表示化（本番環境対応）
        # st.success("✅ NotionDBから診断データを読み込みました")
    else:
        # 詳細なデフォルトのカテゴリ（NotionDBが利用できない場合）
        categories = {
            "🔋 バッテリー関連": [
                "電圧が12V以下に低下", "充電されない", "急激な消耗", "バッテリー液の減少",
                "端子の腐食", "充電時の異臭", "バッテリーの膨張", "充電器が動作しない",
                "エンジン始動時の異音", "電装品の動作不良", "バッテリーの温度上昇"
            ],
            "🔌 インバーター関連": [
                "電源が入らない", "出力ゼロ", "異音がする", "過熱する", "LEDが点滅する",
                "正弦波出力が不安定", "負荷時に停止", "ファンが回らない", "エラーコードが表示",
                "電圧が不安定", "周波数がずれる", "ノイズが発生"
            ],
            "🚽 トイレ関連": [
                "水漏れがする", "フラッパーが故障", "臭いがする", "水が流れない", "タンクが満杯",
                "パッキンが劣化", "レバーが動かない", "水が止まらない", "タンクの亀裂",
                "配管の詰まり", "排水ポンプが動作しない"
            ],
            "🌪️ ルーフベント・換気扇関連": [
                "ファンが回らない", "雨漏りがする", "開閉が不良", "異音がする", "モーターが過熱",
                "スイッチが効かない", "風量が弱い", "振動が激しい", "電源が入らない",
                "シャッターが動かない", "防水シールが劣化"
            ],
            "💧 水道・ポンプ関連": [
                "ポンプが動作しない", "水が出ない", "配管から漏れる", "水圧が弱い", "異音がする",
                "ポンプが過熱する", "タンクが空になる", "フィルターが詰まる", "配管が凍結",
                "水質が悪い", "ポンプが頻繁に動作"
            ],
            "❄️ 冷蔵庫関連": [
                "冷えない", "冷凍室が凍らない", "コンプレッサーが動作しない", "異音がする",
                "霜が付く", "ドアが閉まらない", "温度設定が効かない", "過熱する",
                "ガス漏れの臭い", "電気代が高い", "ドアパッキンが劣化"
            ],
            "🔥 ガス・ヒーター関連": [
                "火が付かない", "不完全燃焼", "異臭がする", "温度が上がらない", "安全装置が作動",
                "ガス漏れ", "点火音がしない", "炎が不安定", "過熱する", "ガス栓が固い"
            ],
            "⚡ 電気・電装系関連": [
                "LEDが点灯しない", "配線がショート", "ヒューズが切れる", "電圧が不安定",
                "スイッチが効かない", "配線が熱い", "漏電する", "コンセントが使えない",
                "バッテリーが消耗する", "電装品が動作不良"
            ],
            "🌧️ 雨漏り・防水関連": [
                "屋根から雨漏り", "ウインドウ周りから漏れる", "ドアから水が入る", "シーリングが劣化",
                "パッキンが硬化", "天窓から漏れる", "配線取り出し部から漏れる",
                "ルーフベントから漏れる", "継ぎ目から漏れる", "コーキングが剥がれる"
            ],
            "🔧 その他の故障": [
                "異音がする", "振動が激しい", "動作が不安定", "部品が破損", "配管が詰まる",
                "ドアが閉まらない", "窓が開かない", "家具が壊れる", "床が抜ける", "壁が剥がれる"
            ]
        }
        # NotionDB接続エラーメッセージを非表示化（本番環境対応）
        # st.warning("⚠️ NotionDBが利用できないため、デフォルトの診断データを使用しています")
        # st.info("💡 NotionDB接続を改善するには:")
        # st.info("1. .streamlit/secrets.tomlの設定を確認")
        # st.info("2. Notion APIキーとデータベースIDが正しいか確認")
        # st.info("3. データベースへのアクセス権限を確認")
    
    # カテゴリ選択
    selected_category = st.selectbox("症状のカテゴリを選択してください:", list(categories.keys()))
    
    if selected_category:
        st.write(f"**{selected_category}**の症状を詳しく教えてください:")
        
        # 症状選択（より詳細な選択肢）
        symptoms = categories[selected_category]
        selected_symptoms = st.multiselect(
            "該当する症状を選択（複数選択可）:", 
            symptoms,
            help="該当する症状を複数選択してください。より詳細な診断結果が得られます。"
        )
        
        if selected_symptoms:
            st.write("**選択された症状**:", ", ".join(selected_symptoms))
            
            # 診断結果の生成
            if st.button("🔍 診断開始", type="primary"):
                # ローディング表示のコンテナ
                loading_container = st.container()
                
                with loading_container:
                    # ローディングメッセージ
                    st.info("⏳ 症状を診断中...")
                    
                    # プログレスバー
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 段階的なローディング表示
                    status_text.text("📚 知識ベースを読み込み中...")
                    progress_bar.progress(30)
                    
                    status_text.text("🤖 AIが症状を分析中...")
                    progress_bar.progress(60)
                    
                    status_text.text("📋 診断結果を生成中...")
                    progress_bar.progress(90)
                    
                    status_text.text("✅ 診断完了")
                    progress_bar.progress(100)
                
                # 実際の診断処理
                diagnosis_prompt = f"{selected_category}の症状: {', '.join(selected_symptoms)}"
                knowledge_base = load_knowledge_base()
                diagnosis_result = generate_ai_response_with_knowledge(diagnosis_prompt, knowledge_base)
                
                # ローディング表示をクリア
                loading_container.empty()
                
                st.markdown("## 📋 診断結果")
                st.markdown(diagnosis_result)
                
                # 関連ブログの表示
                blog_links = get_relevant_blog_links(diagnosis_prompt, knowledge_base)
                if blog_links:
                    st.markdown("## 📚 関連ブログ")
                    display_blog_links(blog_links, diagnosis_prompt)

def run_detailed_diagnostic(diagnostic_data, repair_cases):
    """詳細診断モード（リレーション活用版）"""
    st.markdown("### 🔍 詳細診断")
    st.markdown("NotionDBの3つのデータベースのリレーションを活用した詳細な診断を行います。")
    
    # NotionDB接続エラーメッセージを非表示化（本番環境対応）
    # if not diagnostic_data:
    #     st.warning("NotionDBの診断データが利用できません。")
    #     return
    
    # リレーション統計の表示
    st.markdown("#### 📈 データベースリレーション統計")
    
    total_nodes = len(diagnostic_data.get("nodes", []))
    total_cases = len(repair_cases)
    
    # リレーションを持つノードとケースの数を計算
    nodes_with_relations = sum(1 for node in diagnostic_data.get("nodes", []) 
                              if node.get("related_cases") or node.get("related_items"))
    cases_with_relations = sum(1 for case in repair_cases 
                              if case.get("related_nodes") or case.get("related_items"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("診断ノード", total_nodes, f"{nodes_with_relations}件にリレーション")
    with col2:
        st.metric("修理ケース", total_cases, f"{cases_with_relations}件にリレーション")
    with col3:
        # st.metric("リレーション活用率", 
        #          f"{((nodes_with_relations + cases_with_relations) / (total_nodes + total_cases) * 100):.1f}%")  # 非表示化
        pass
    
    # 診断フローの表示（リレーション情報付き）
    if diagnostic_data.get("nodes"):
        st.markdown("#### 📊 診断ノード（リレーション情報付き）")
        for node in diagnostic_data["nodes"][:10]:  # 最初の10件を表示
            relation_count = len(node.get("related_cases", [])) + len(node.get("related_items", []))
            relation_badge = f"🔗 {relation_count}件のリレーション" if relation_count > 0 else "❌ リレーションなし"
            
            with st.expander(f"🔹 {node['title']} ({node['category']}) {relation_badge}"):
                if node["symptoms"]:
                    st.write("**症状**:", ", ".join(node["symptoms"]))
                
                # 関連修理ケースの表示
                if node.get("related_cases"):
                    st.write("**関連修理ケース**:")
                    for case in node["related_cases"][:3]:
                        st.write(f"  • {case['title']}: {case['solution'][:100]}...")
                
                # 関連部品・工具の表示
                if node.get("related_items"):
                    st.write("**関連部品・工具**:")
                    for item in node["related_items"][:3]:
                        price_info = f" (¥{item['price']})" if item.get('price') else ""
                        supplier_info = f" - {item['supplier']}" if item.get('supplier') else ""
                        st.write(f"  • {item['name']}{price_info}{supplier_info}")
    
    # 修理ケースの表示（リレーション情報付き）
    if repair_cases:
        st.markdown("#### 🔧 修理ケース（リレーション情報付き）")
        for case in repair_cases[:5]:  # 最初の5件を表示
            relation_count = len(case.get("related_nodes", [])) + len(case.get("related_items", []))
            relation_badge = f"🔗 {relation_count}件のリレーション" if relation_count > 0 else "❌ リレーションなし"
            
            with st.expander(f"🔧 {case['title']} ({case['category']}) {relation_badge}"):
                if case["symptoms"]:
                    st.write("**症状**:", ", ".join(case["symptoms"]))
                if case["solution"]:
                    st.write("**解決方法**:", case["solution"][:100] + "..." if len(case["solution"]) > 100 else case["solution"])
                
                # 関連診断ノードの表示
                if case.get("related_nodes"):
                    st.write("**関連診断ノード**:")
                    for node in case["related_nodes"][:3]:
                        st.write(f"  • {node['title']}: {', '.join(node['symptoms'])}")
                
                # 関連部品・工具の表示
                if case.get("related_items"):
                    st.write("**必要な部品・工具**:")
                    for item in case["related_items"][:5]:
                        price_info = f" (¥{item['price']})" if item.get('price') else ""
                        supplier_info = f" - {item['supplier']}" if item.get('supplier') else ""
                        st.write(f"  • {item['name']}{price_info}{supplier_info}")
                
                # 従来の形式（互換性のため）
                if case.get("parts"):
                    st.write("**必要な部品（従来形式）**:", ", ".join(case["parts"]))
                if case.get("tools"):
                    st.write("**必要な工具（従来形式）**:", ", ".join(case["tools"]))

def test_notion_connection():
    """NotionDB接続をテスト"""
    try:
        client = initialize_notion_client()
        if not client:
            return False, "Notionクライアントの初期化に失敗"
        
        # ユーザー情報を取得して接続をテスト
        user = client.users.me()
        
        # データベース接続テスト
        test_results = {}
        
        # 診断フローDBテスト
        node_db_id = st.secrets.get("NODE_DB_ID") or st.secrets.get("NOTION_DIAGNOSTIC_DB_ID") or os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
        if node_db_id:
            try:
                response = client.databases.query(database_id=node_db_id)
                test_results["diagnostic_db"] = {
                    "status": "success",
                    "count": len(response.get("results", [])),
                    "message": f"✅ 診断フローDB: {len(response.get('results', []))}件のノード"
                }
            except Exception as e:
                test_results["diagnostic_db"] = {
                    "status": "error",
                    "message": f"❌ 診断フローDB: {str(e)}"
                }
        else:
            test_results["diagnostic_db"] = {
                "status": "warning",
                "message": "⚠️ 診断フローDB: ID未設定"
            }
        
        # 修理ケースDBテスト
        case_db_id = st.secrets.get("CASE_DB_ID") or st.secrets.get("NOTION_REPAIR_CASE_DB_ID") or os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
        if case_db_id:
            try:
                response = client.databases.query(database_id=case_db_id)
                test_results["repair_case_db"] = {
                    "status": "success",
                    "count": len(response.get("results", [])),
                    "message": f"✅ 修理ケースDB: {len(response.get('results', []))}件のケース"
                }
            except Exception as e:
                test_results["repair_case_db"] = {
                    "status": "error",
                    "message": f"❌ 修理ケースDB: {str(e)}"
                }
        else:
            test_results["repair_case_db"] = {
                "status": "warning",
                "message": "⚠️ 修理ケースDB: ID未設定"
            }
        
        return True, test_results
        
    except Exception as e:
        return False, f"接続テスト失敗: {str(e)}"

def get_notion_repair_cases(category):
    """Notionから修理ケースデータを取得（キャッシュ付き）"""
    # セッション状態でキャッシュを管理
    cache_key = f"notion_cases_{category}"
    
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    try:
        client = initialize_notion_client()
        if not client:
            return []
        
        case_db_id = os.getenv("CASE_DB_ID")
        if not case_db_id:
            return []
        
        # カテゴリに基づいて修理ケースを検索（最大3件に制限）
        response = client.databases.query(
            database_id=case_db_id,
            filter={
                "property": "カテゴリ",
                "select": {
                    "equals": category
                }
            },
            page_size=3  # 最大3件に制限
        )
        
        cases = response.get("results", [])
        
        # キャッシュに保存
        st.session_state[cache_key] = cases
        return cases
        
    except Exception as e:
        st.warning(f"Notionデータの取得中にエラーが発生しました: {str(e)}")
        return []

def get_notion_items(category):
    """Notionから部品・工具データを取得（キャッシュ付き）"""
    # セッション状態でキャッシュを管理
    cache_key = f"notion_items_{category}"
    
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    try:
        client = initialize_notion_client()
        if not client:
            return []
        
        item_db_id = os.getenv("ITEM_DB_ID")
        if not item_db_id:
            return []
        
        # カテゴリに基づいて部品・工具を検索（最大5件に制限）
        response = client.databases.query(
            database_id=item_db_id,
            filter={
                "property": "カテゴリ",
                "select": {
                    "equals": category
                }
            },
            page_size=5  # 最大5件に制限
        )
        
        items = response.get("results", [])
        
        # キャッシュに保存
        st.session_state[cache_key] = items
        return items
        
    except Exception as e:
        st.warning(f"Notion部品データの取得中にエラーが発生しました: {str(e)}")
        return []

def get_repair_estimates(category, case_title):
    """修理の目安情報を取得"""
    estimates = {
        "雨漏り": {
            "time": "1-3時間",
            "difficulty": "中級",
            "cost_range": "8,000-25,000円",
            "parts_cost": "3,000-8,000円",
            "labor_cost": "5,000-17,000円"
        },
        "ドア・窓": {
            "time": "30分-2時間",
            "difficulty": "初級-中級",
            "cost_range": "3,000-15,000円",
            "parts_cost": "1,000-5,000円",
            "labor_cost": "2,000-10,000円"
        },
        "車体外装": {
            "time": "2-6時間",
            "difficulty": "中級-上級",
            "cost_range": "15,000-80,000円",
            "parts_cost": "5,000-30,000円",
            "labor_cost": "10,000-50,000円"
        },
        "バッテリー": {
            "time": "30分-1時間",
            "difficulty": "初級",
            "cost_range": "8,000-25,000円",
            "parts_cost": "6,000-20,000円",
            "labor_cost": "2,000-5,000円"
        },
        "サブバッテリー": {
            "time": "1-3時間",
            "difficulty": "中級",
            "cost_range": "15,000-50,000円",
            "parts_cost": "10,000-35,000円",
            "labor_cost": "5,000-15,000円"
        },
        "ヒューズ・リレー": {
            "time": "15分-1時間",
            "difficulty": "初級",
            "cost_range": "500-3,000円",
            "parts_cost": "200-1,500円",
            "labor_cost": "300-1,500円"
        },
        "エアコン": {
            "time": "2-4時間",
            "difficulty": "中級-上級",
            "cost_range": "20,000-80,000円",
            "parts_cost": "10,000-50,000円",
            "labor_cost": "10,000-30,000円"
        },
        "冷蔵庫": {
            "time": "1-3時間",
            "difficulty": "中級",
            "cost_range": "10,000-40,000円",
            "parts_cost": "5,000-25,000円",
            "labor_cost": "5,000-15,000円"
        },
        "トイレ": {
            "time": "1-2時間",
            "difficulty": "中級",
            "cost_range": "8,000-30,000円",
            "parts_cost": "3,000-15,000円",
            "labor_cost": "5,000-15,000円"
        },
        "ガスコンロ": {
            "time": "30分-2時間",
            "difficulty": "中級",
            "cost_range": "5,000-25,000円",
            "parts_cost": "2,000-10,000円",
            "labor_cost": "3,000-15,000円"
        },
        "水道ポンプ": {
            "time": "1-2時間",
            "difficulty": "中級",
            "cost_range": "8,000-25,000円",
            "parts_cost": "4,000-15,000円",
            "labor_cost": "4,000-10,000円"
        },
        "ソーラーパネル": {
            "time": "2-4時間",
            "difficulty": "上級",
            "cost_range": "30,000-100,000円",
            "parts_cost": "20,000-70,000円",
            "labor_cost": "10,000-30,000円"
        }
    }
    
    return estimates.get(category, {
        "time": "1-3時間",
        "difficulty": "中級",
        "cost_range": "5,000-30,000円",
        "parts_cost": "2,000-15,000円",
        "labor_cost": "3,000-15,000円"
    })

def display_repair_estimates(category, case_title):
    """修理目安情報を表示"""
    estimates = get_repair_estimates(category, case_title)
    
    st.markdown("#### 📊 修理目安情報")
    
    # 目安情報を3列で表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #fff5f5; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545; text-align: center;">
            <h4 style="color: #dc3545; margin-top: 0;">⏱️ 修理時間</h4>
            <p style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0;">{estimates['time']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        difficulty_color = "#28a745" if "初級" in estimates['difficulty'] else "#ffc107" if "中級" in estimates['difficulty'] else "#dc3545"
        st.markdown(f"""
        <div style="background-color: #fff5f5; padding: 1rem; border-radius: 8px; border-left: 4px solid {difficulty_color}; text-align: center;">
            <h4 style="color: {difficulty_color}; margin-top: 0;">🎯 難易度</h4>
            <p style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0;">{estimates['difficulty']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background-color: #fff5f5; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545; text-align: center;">
            <h4 style="color: #dc3545; margin-top: 0;">💰 総費用</h4>
            <p style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0;">{estimates['cost_range']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 詳細な費用内訳
    st.markdown("#### 💰 費用内訳")
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #dee2e6;">
            <h5 style="color: #495057; margin-top: 0;">🛠️ 部品代</h5>
            <p style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0; color: #dc3545;">{estimates['parts_cost']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #dee2e6;">
            <h5 style="color: #495057; margin-top: 0;">👷 工賃</h5>
            <p style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0; color: #dc3545;">{estimates['labor_cost']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 注意事項
    st.markdown("""
    <div style="background-color: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin-top: 1rem;">
        <h5 style="color: #856404; margin-top: 0;">⚠️ 注意事項</h5>
        <ul style="margin-bottom: 0; color: #856404;">
            <li>上記は目安の費用です。実際の費用は症状や車両により異なります</li>
            <li>部品の入手状況により修理期間が延びる場合があります</li>
            <li>複雑な修理の場合は専門店への相談をお勧めします</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def extract_repair_costs_and_alternatives(text_content, category):
    """テキストから修理費用と代替品情報を抽出"""
    import re
    
    costs = []
    alternatives = []
    
    # 修理費用のパターンを検索
    cost_patterns = [
        r'(\d+[,，]\d+円)',
        r'(\d+円)',
        r'約(\d+円)',
        r'(\d+万円)',
        r'(\d+千円)',
        r'工賃.*?(\d+円)',
        r'部品代.*?(\d+円)',
        r'(\d+時間).*?(\d+円)',
    ]
    
    for pattern in cost_patterns:
        matches = re.findall(pattern, text_content)
        for match in matches:
            if isinstance(match, tuple):
                costs.extend([m for m in match if m])
            else:
                costs.append(match)
    
    # 代替品・製品情報のパターンを検索
    alternative_patterns = [
        r'【対応製品例】',
        r'公式HP:.*?\[(.*?)\]',
        r'https://[^\s]+',
        r'[A-Za-z0-9\s]+（[^）]+）',
        r'[A-Za-z0-9\s]+エアコン',
        r'[A-Za-z0-9\s]+バッテリー',
        r'[A-Za-z0-9\s]+シーラント',
        r'[A-Za-z0-9\s]+テープ',
    ]
    
    for pattern in alternative_patterns:
        matches = re.findall(pattern, text_content)
        alternatives.extend(matches)
    
    # 重複を除去
    costs = list(set(costs))
    alternatives = list(set(alternatives))
    
    return costs, alternatives

def display_repair_costs_and_alternatives(text_content, category):
    """修理費用と代替品情報を表示"""
    try:
        costs, alternatives = extract_repair_costs_and_alternatives(text_content, category)
        
        # 修理費用の表示
        if costs:
            st.markdown("#### 💰 具体的な修理費用")
            cost_col1, cost_col2 = st.columns(2)
            
            with cost_col1:
                st.markdown("**発見された費用情報:**")
                for cost in costs[:5]:  # 最大5件表示
                    st.markdown(f"• {cost}")
            
            with cost_col2:
                st.markdown("**費用の種類:**")
                if any('工賃' in text_content or '時給' in text_content):
                    st.markdown("• 工賃・作業費")
                if any('部品' in text_content or '交換' in text_content):
                    st.markdown("• 部品代")
                if any('シーラント' in text_content or 'テープ' in text_content):
                    st.markdown("• 材料費")
        
        # 代替品・製品情報の表示
        if alternatives:
            st.markdown("#### 🛠️ 推奨代替品・製品")
            
            # 製品名を抽出
            product_names = []
            urls = []
            
            for alt in alternatives:
                if alt.startswith('http'):
                    urls.append(alt)
                elif len(alt) > 10 and not alt.startswith('【'):
                    product_names.append(alt)
            
            if product_names:
                st.markdown("**推奨製品:**")
                for product in product_names[:5]:  # 最大5件表示
                    st.markdown(f"• {product}")
            
            if urls:
                st.markdown("**関連リンク:**")
                for url in urls[:3]:  # 最大3件表示
                    st.markdown(f"• [{url}]({url})")
        
        # カテゴリ別の追加情報
        if category == "雨漏り":
            st.markdown("#### 🔧 雨漏り修理の追加情報")
            st.markdown("""
            **よく使用される材料:**
            • ブチルテープ
            • ウレタンシーラント
            • コーキング材
            • 防水テープ
            
            **修理のポイント:**
            • 古いシールの完全除去
            • 表面の清掃・乾燥
            • 適切な材料の選択
            """)
        
        elif category == "バッテリー":
            st.markdown("#### 🔋 バッテリー修理の追加情報")
            st.markdown("""
            **バッテリーの種類:**
            • 鉛バッテリー（2-3年で交換）
            • リチウムバッテリー（5-10年）
            • AGMバッテリー（3-5年）
            
            **点検項目:**
            • 電圧測定（12.6V以上が正常）
            • 充電システムの確認
            • 端子の清掃・締め付け
            """)
        
        elif category == "エアコン":
            st.markdown("#### ❄️ エアコン修理の追加情報")
            st.markdown("""
            **主要メーカー:**
            • ダイワデンギョウ CAMCOOL
            • Stage21 One Cool 21
            • ジェーピージェネレーターズ e-comfort
            
            **修理のポイント:**
            • 電源電圧の確認
            • フィルターの清掃
            • 冷媒の充填
            """)
        
    except Exception as e:
        st.warning(f"修理費用・代替品情報の抽出中にエラーが発生しました: {str(e)}")

def search_notion_database(query):
    """Notionデータベースから関連情報を検索"""
    try:
        client = initialize_notion_client()
        if not client:
            return []
        
        results = []
        query_lower = query.lower()
        
        # 修理ケースデータベースを検索
        case_db_id = os.getenv("CASE_DB_ID")
        if case_db_id:
            try:
                response = client.databases.query(
                    database_id=case_db_id,
                    page_size=5
                )
                
                for case in response.get("results", []):
                    properties = case.get("properties", {})
                    
                    # タイトルを取得
                    title = "ケース情報"
                    if "title" in properties and properties["title"].get("title"):
                        title = properties["title"]["title"][0]["text"]["content"]
                    
                    # 説明を取得
                    description = ""
                    if "説明" in properties and properties["説明"].get("rich_text"):
                        description = properties["説明"]["rich_text"][0]["text"]["content"]
                    
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
                            'tools': tools
                        })
            except Exception as e:
                pass
        
        # 部品・工具データベースを検索
        item_db_id = os.getenv("ITEM_DB_ID")
        if item_db_id:
            try:
                response = client.databases.query(
                    database_id=item_db_id,
                    page_size=3
                )
                
                for item in response.get("results", []):
                    properties = item.get("properties", {})
                    
                    # 部品名を取得
                    item_name = ""
                    if "部品名" in properties and properties["部品名"].get("title"):
                        item_name = properties["部品名"]["title"][0]["text"]["content"]
                    
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
                        
                        results.append({
                            'title': f"推奨部品: {item_name}",
                            'category': category,
                            'description': description,
                            'parts': [item_name],
                            'tools': []
                        })
            except Exception as e:
                pass
        
        return results[:3]  # 最大3件まで返す
        
    except Exception as e:
        return []

def get_general_repair_advice(query):
    """キーワードに基づく一般的な修理アドバイスを生成"""
    query_lower = query.lower()
    
    # キーワードに基づく一般的なアドバイス
    advice_templates = {
        "バッテリー": """
        **バッテリー関連の一般的なアドバイス:**
        - 電圧測定（12.6V以上が正常）
        - 端子の清掃・締め付け
        - 充電システムの確認
        - 交換時期：鉛バッテリー2-3年、リチウム5-10年
        """,
        "雨漏り": """
        **雨漏り関連の一般的なアドバイス:**
        - シーリング材の劣化確認
        - ルーフベント周囲の点検
        - ブチルテープ・ウレタンシーラントの使用
        - 古いシールの完全除去が重要
        """,
        "エアコン": """
        **エアコン関連の一般的なアドバイス:**
        - 電源電圧の確認
        - フィルターの清掃
        - 冷媒の充填
        - ダイワデンギョウ CAMCOOL等の推奨製品
        """,
        "冷蔵庫": """
        **冷蔵庫関連の一般的なアドバイス:**
        - 冷却不良の原因調査
        - 霜付きの解消
        - 異音の原因特定
        - 定期的なメンテナンス
        """,
        "トイレ": """
        **トイレ関連の一般的なアドバイス:**
        - 排水システムの確認
        - 水漏れの点検
        - ベンチレーターの動作確認
        - 清掃・メンテナンス
        """
    }
    
    # キーワードマッチング
    for keyword, advice in advice_templates.items():
        if keyword in query_lower:
            return advice
    
    # デフォルトの一般的なアドバイス
    return """
    **一般的な修理・メンテナンスのポイント:**
    - 安全第一：危険な作業は避け、専門家に相談
    - 定期的な点検：問題の早期発見が重要
    - 適切な工具・部品：専用工具の使用を推奨
    - 予防メンテナンス：故障前の対応が効果的
    
    **修理費用の目安:**
    - 軽微な修理：5,000円〜15,000円
    - 中程度の修理：15,000円〜50,000円
    - 大規模な修理：50,000円〜150,000円
    """

def search_repair_advice(query):
    """テキストデータから修理アドバイスを検索（全ファイル対応版）"""
    import os
    import glob
    
    # 全検索対象のテキストファイル（既存のリスト）
    text_files = [
        ("バッテリー", "バッテリー.txt"),
        ("雨漏り", "雨漏り.txt"),
        ("エアコン", "エアコン.txt"),
        ("冷蔵庫", "冷蔵庫.txt"),
        ("トイレ", "トイレ.txt"),
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
    
    # 全ファイルを検索（最適化版）
    for category, filename in text_files:
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # より柔軟なキーワードマッチング
                if (query_lower in content.lower() or 
                    any(keyword in content.lower() for keyword in query_lower.split())):
                    
                    # 関連度スコアを計算
                    score = content.lower().count(query_lower)
                    if any(keyword in content.lower() for keyword in query_lower.split()):
                        score += 2
                    
                    # 修理費用と代替品情報を詳細抽出
                    costs = []
                    alternatives = []
                    urls = []
                    
                    # 詳細な費用抽出
                    import re
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
                    # 製品名パターン
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
            continue
    
    # スコア順でソート
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results

def show_repair_loading(category):
    """修理アドバイスのローディング表示"""
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        st.info(f"⏳ {category}修理の情報を読み込み中...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📚 基本知識を読み込み中...")
        progress_bar.progress(30)
        
        status_text.text("💰 修理費用を抽出中...")
        progress_bar.progress(60)
        
        status_text.text("🛠️ 代替品情報を整理中...")
        progress_bar.progress(90)
        
        status_text.text("✅ 完了")
        progress_bar.progress(100)
    
    return loading_placeholder

def display_repair_advice(category, filename):
    """修理アドバイスを表示する関数（シンプル版）"""
    try:
        # マークダウン形式で表示
        st.markdown(f"### 🔧 {category}修理専門アドバイス")
        st.markdown("---")
        
        # 1. テキストファイルを読み込み
        text_content = ""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except FileNotFoundError:
            st.warning(f"テキストファイル '{filename}' が見つかりません。")
        except Exception as e:
            st.warning(f"ファイル読み込みエラー: {str(e)}")
        
        # テキストファイルの内容を表示
        if text_content:
            st.markdown("#### 📚 基本知識・トラブル事例")
            st.markdown(text_content)
            st.markdown("---")
            
            # 修理費用と代替品情報を抽出・表示
            display_repair_costs_and_alternatives(text_content, category)
        
        # 2. 修理目安情報を表示
        st.markdown("#### 📊 修理目安情報")
        estimates = get_repair_estimates(category, "")
        
        # 目安情報を3列で表示
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background-color: #fff5f5; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545; text-align: center;">
                <h4 style="color: #dc3545; margin-top: 0;">⏱️ 修理時間</h4>
                <p style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0;">{estimates['time']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            difficulty_color = "#28a745" if "初級" in estimates['difficulty'] else "#ffc107" if "中級" in estimates['difficulty'] else "#dc3545"
            st.markdown(f"""
            <div style="background-color: #fff5f5; padding: 1rem; border-radius: 8px; border-left: 4px solid {difficulty_color}; text-align: center;">
                <h4 style="color: {difficulty_color}; margin-top: 0;">🎯 難易度</h4>
                <p style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0;">{estimates['difficulty']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background-color: #fff5f5; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545; text-align: center;">
                <h4 style="color: #dc3545; margin-top: 0;">💰 総費用</h4>
                <p style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0;">{estimates['cost_range']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 3. 費用内訳を表示
        st.markdown("#### 💰 費用内訳")
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #dee2e6;">
                <h5 style="color: #495057; margin-top: 0;">🛠️ 部品代</h5>
                <p style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0; color: #dc3545;">{estimates['parts_cost']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #dee2e6;">
                <h5 style="color: #495057; margin-top: 0;">👷 工賃</h5>
                <p style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0; color: #dc3545;">{estimates['labor_cost']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 4. 注意事項
        st.markdown("#### ⚠️ 注意事項")
        st.markdown("""
        <div style="background-color: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin-top: 1rem;">
            <h5 style="color: #856404; margin-top: 0;">⚠️ 注意事項</h5>
            <ul style="margin-bottom: 0; color: #856404;">
                <li>上記は目安の費用です。実際の費用は症状や車両により異なります</li>
                <li>部品の入手状況により修理期間が延びる場合があります</li>
                <li>複雑な修理の場合は専門店への相談をお勧めします</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 5. Notionデータを取得・表示（簡略版）
        st.markdown("#### 🔧 関連修理ケース")
        try:
            notion_cases = get_notion_repair_cases(category)
            if notion_cases and len(notion_cases) > 0:
                for i, case in enumerate(notion_cases[:2]):  # 最大2件表示
                    try:
                        properties = case.get("properties", {})
                        title = "ケース情報"
                        if "title" in properties and properties["title"].get("title"):
                            title = properties["title"]["title"][0]["text"]["content"]
                        
                        with st.expander(f"🔧 {title}"):
                            st.markdown("詳細な修理ケース情報が表示されます。")
                    except Exception as e:
                        st.warning(f"ケース {i+1} の表示中にエラーが発生しました")
                        continue
            else:
                st.info("関連する修理ケースが見つかりませんでした。")
        except Exception as e:
            st.warning("修理ケースの取得中にエラーが発生しました。")
        
        # 6. 部品・工具を表示（簡略版）
        st.markdown("#### 🛠️ 推奨部品・工具")
        try:
            notion_items = get_notion_items(category)
            if notion_items and len(notion_items) > 0:
                for item in notion_items[:3]:  # 最大3件表示
                    try:
                        properties = item.get("properties", {})
                        item_name = "部品名"
                        if "部品名" in properties and properties["部品名"].get("title"):
                            item_name = properties["部品名"]["title"][0]["text"]["content"]
                        
                        st.markdown(f"**{item_name}**")
                    except Exception as e:
                        st.warning("部品情報の表示中にエラーが発生しました")
                        continue
            else:
                st.info("関連する部品・工具が見つかりませんでした。")
        except Exception as e:
            st.warning("部品情報の取得中にエラーが発生しました。")
        
    except Exception as e:
        st.error(f"アドバイス表示中にエラーが発生しました: {str(e)}")
        st.error(f"エラー詳細: {type(e).__name__}")

def main():
    st.set_page_config(
        page_title="キャンピングカー修理AI相談",
        page_icon="🚐",
        layout="wide"
    )
    
    # カスタムCSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    
        /* レスポンシブデザイン - スマホ対応 */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 1.0rem !important;
                line-height: 1.2;
            }
            .main-header p {
                font-size: 0.7rem !important;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 8px 12px;
                font-size: 0.9rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 1.3rem; margin-bottom: 0.5rem;">🚐 キャンピングカー修理専門AI相談</h1>
        <p style="font-size: 0.8rem; margin-top: 0;">修理費用相場から代替品まで紹介</p>
    </div>
    """, unsafe_allow_html=True)
    
    # タブ作成（Flask APIセンタータブを非表示）
    tab1, tab2, tab3 = st.tabs(["💬 AIチャット相談", "🔍 対話式症状診断", "🔧 修理専門アドバイスセンター"])
    
    with tab1:
        st.markdown("### 💬 AIチャット相談")
        st.markdown("キャンピングカーの修理・メンテナンスについて何でもお聞きください。")
        
        # チャット履歴の初期化
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # 知識ベースの読み込み（遅延読み込みでローディング時間短縮）
        if "knowledge_base" not in st.session_state:
            with st.spinner("知識ベースを読み込み中..."):
                st.session_state.knowledge_base = load_knowledge_base()
        knowledge_base = st.session_state.knowledge_base
        
        # チャット履歴の表示（最適化）
        for message in st.session_state.messages:
            if message["role"] == "assistant":
                with st.chat_message("assistant", avatar="https://camper-repair.net/blog/wp-content/uploads/2025/05/dummy_staff_01-150x138-1.png"):
                    st.write(message["content"])  # st.markdownの代わりにst.writeを使用
            else:
                with st.chat_message(message["role"]):
                    st.write(message["content"])  # st.markdownの代わりにst.writeを使用
        
        # ユーザー入力
        if prompt := st.chat_input("修理やメンテナンスについて質問してください..."):
            # ユーザーメッセージを追加
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)  # st.markdownの代わりにst.writeを使用
            
            # AI回答を生成
            with st.chat_message("assistant", avatar="https://camper-repair.net/blog/wp-content/uploads/2025/05/dummy_staff_01-150x138-1.png"):
                # 回答を生成（ローディング表示は関数内で処理）
                response = generate_ai_response_with_knowledge(prompt, knowledge_base)
                
                # 回答を表示
                st.write(response)  # st.markdownの代わりにst.writeを使用
                
                # AIメッセージを追加
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    with tab2:
        run_diagnostic_flow()
    
    with tab3:
        # 修理専門アドバイスセンター（手動リンクのみ）
        st.markdown("### 🔧 修理専門アドバイスセンター")
        
        # ユーザーへの案内
        st.info("🔗 修理アドバイスセンターにアクセスするには、下のリンクをクリックしてください。")
        
        # 直接リンク（確実な方法）
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <a href="http://localhost:5000/repair_advice_center.html" target="_blank" 
               style="display: inline-block; background: #dc3545; color: white; 
                      padding: 12px 24px; border-radius: 8px; text-decoration: none; 
                      font-weight: bold; font-size: 1.1rem;">
                🔗 修理アドバイスセンターを開く（直接リンク）
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # 軽量な説明のみ表示（ローディング時間短縮）
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">📋 修理アドバイスセンターの機能</h4>
            <ul style="color: #495057;">
                <li>🔍 統合検索機能</li>
                <li>💰 修理費用の目安</li>
                <li>🛠️ 部品検索・代替品</li>
                <li>📝 修理手順</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_system_info():
    """システム情報とNotionDB接続状況を表示"""
    st.markdown("### 🔧 システム情報")
    
    # OpenAI API設定状況
    st.markdown("#### 🤖 OpenAI API設定")
    if openai_api_key:
        st.success(f"✅ OpenAI API: 設定済み ({openai_api_key[:10]}...)")
    else:
        st.error("❌ OpenAI API: 未設定")
    
    # Notion API設定状況
    st.markdown("#### 📊 Notion API設定")
    if notion_api_key:
        st.success(f"✅ Notion API: 設定済み ({notion_api_key[:10]}...)")
        
        # NotionDB接続テスト
        st.markdown("##### 🔍 NotionDB接続テスト")
        
        # 接続テストボタン
        if st.button("🔄 接続テスト実行", type="secondary"):
            with st.spinner("接続テスト中..."):
                try:
                    # 詳細な接続テスト
                    test_results = perform_detailed_notion_test()
                    
                    if test_results["overall_success"]:
                        st.success("✅ 接続テスト完了")
                        
                        # 各データベースの結果を表示
                        for db_name, result in test_results["databases"].items():
                            if result["status"] == "success":
                                st.success(f"✅ {db_name}: {result['message']}")
                            elif result["status"] == "error":
                                st.error(f"❌ {db_name}: {result['message']}")
                                if result.get("solution"):
                                    st.info(f"💡 解決方法: {result['solution']}")
                            else:
                                st.warning(f"⚠️ {db_name}: {result['message']}")
                        
                        # 接続統計
                        st.info(f"📊 接続統計: {test_results['success_count']}/{test_results['total_count']}個のデータベースに接続成功")
                        
                    else:
                        st.error("❌ 接続テスト失敗")
                        st.info("💡 詳細なエラー情報を確認してください")
                        
                except Exception as e:
                    st.error(f"❌ 接続テスト実行エラー: {str(e)}")
        
        st.markdown("---")
        
        # クライアント初期化テスト
        client = initialize_notion_client()
        if client:
            st.success("✅ Notionクライアント: 初期化成功")
            
            # 診断フローデータベース（非表示化）
            # node_db_id = st.secrets.get("NODE_DB_ID") or st.secrets.get("NOTION_DIAGNOSTIC_DB_ID") or os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
            # if node_db_id:
            #     st.info(f"📋 診断フローDB: {node_db_id[:8]}...")
            #     try:
            #         diagnostic_data = load_notion_diagnostic_data()
            #         if diagnostic_data and diagnostic_data.get('nodes'):
            #             st.success(f"✅ 診断フローDB: 接続成功 ({len(diagnostic_data.get('nodes', []))}件のノード)")
            #             
            #             # リレーション統計
            #             nodes_with_relations = sum(1 for node in diagnostic_data.get('nodes', []) 
            #                                       if node.get("related_cases") or node.get("related_items"))
            #             # st.info(f"🔗 リレーション活用: {nodes_with_relations}/{len(diagnostic_data.get('nodes', []))}件のノード")  # 非表示化
            #         else:
            #             st.warning("⚠️ 診断フローDB: データなしまたは接続失敗")
            #     except Exception as e:
            #         st.error(f"❌ 診断フローDB: 接続失敗 - {str(e)}")
            #         st.info("💡 データベースIDとAPIキーの権限を確認してください")
            # else:
            #     st.warning("⚠️ 診断フローDB: ID未設定")
            #     st.info("💡 .streamlit/secrets.tomlにNODE_DB_IDを設定してください")
            
            # 修理ケースデータベース（非表示化）
            # case_db_id = st.secrets.get("CASE_DB_ID") or st.secrets.get("NOTION_REPAIR_CASE_DB_ID") or os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
            # if case_db_id:
            #     st.info(f"🔧 修理ケースDB: {case_db_id[:8]}...")
            #     try:
            #         repair_cases = load_notion_repair_cases()
            #         if repair_cases:
            #             st.success(f"✅ 修理ケースDB: 接続成功 ({len(repair_cases)}件のケース)")
            #             
            #             # リレーション統計
            #             cases_with_relations = sum(1 for case in repair_cases 
            #                                       if case.get("related_nodes") or case.get("related_items"))
            #             # st.info(f"🔗 リレーション活用: {cases_with_relations}/{len(repair_cases)}件のケース")  # 非表示化
            #     else:
            #         st.warning("⚠️ 修理ケースDB: データなし")
            #     except Exception as e:
            #         st.error(f"❌ 修理ケースDB: 接続失敗 - {str(e)}")
            #         st.info("💡 データベースIDとAPIキーの権限を確認してください")
            # else:
            #     st.warning("⚠️ 修理ケースDB: ID未設定")
            #     st.info("💡 .streamlit/secrets.tomlにCASE_DB_IDを設定してください")
            
            # 部品・工具データベース（非表示化）
            # item_db_id = st.secrets.get("ITEM_DB_ID") or os.getenv("ITEM_DB_ID")
            # if item_db_id:
            #     st.info(f"🛠️ 部品・工具DB: {item_db_id[:8]}...")
            #     st.info("ℹ️ 部品・工具DBの接続テストは実装予定")
            # else:
            #     st.warning("⚠️ 部品・工具DB: ID未設定")
            #     st.info("💡 .streamlit/secrets.tomlにITEM_DB_IDを設定してください")
        # else:
        #     st.error("❌ Notionクライアント: 初期化失敗")
        #     st.info("💡 notion-clientライブラリのインストールとAPIキーの確認が必要です")
        
    # else:
    #     st.error("❌ Notion API: 未設定")
    #     st.info("**設定方法**:")
    #     st.code("NOTION_API_KEY=your_notion_token\nNODE_DB_ID=your_diagnostic_db_id\nCASE_DB_ID=your_repair_case_db_id")
    
    # 知識ベース状況
    st.markdown("#### 📚 知識ベース状況")
    knowledge_base = load_knowledge_base()
    if knowledge_base:
        st.success(f"✅ 知識ベース: 読み込み成功 ({len(knowledge_base)}件のファイル)")
        for category in list(knowledge_base.keys())[:5]:  # 最初の5件を表示
            st.write(f"  - {category}")
        if len(knowledge_base) > 5:
            st.write(f"  - ... 他{len(knowledge_base) - 5}件")
    else:
        st.warning("⚠️ 知識ベース: ファイルが見つかりません")
    
    # 環境変数一覧
    st.markdown("#### 🌐 環境変数一覧")
    env_vars = {
        "OPENAI_API_KEY": openai_api_key,
        "NOTION_API_KEY": notion_api_key,
        "NODE_DB_ID": st.secrets.get("NODE_DB_ID") or st.secrets.get("NOTION_DIAGNOSTIC_DB_ID") or os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID"),
        "CASE_DB_ID": st.secrets.get("CASE_DB_ID") or st.secrets.get("NOTION_REPAIR_CASE_DB_ID") or os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID"),
        "ITEM_DB_ID": st.secrets.get("ITEM_DB_ID") or os.getenv("ITEM_DB_ID")
    }
    
    for key, value in env_vars.items():
        if value:
            if "KEY" in key or "TOKEN" in key:
                st.write(f"**{key}**: {value[:10]}...{value[-4:] if len(value) > 14 else ''}")
            else:
                st.write(f"**{key}**: {value}")
        else:
            st.write(f"**{key}**: ❌ 未設定")
    
    # トラブルシューティングガイド
    st.markdown("#### 🔧 トラブルシューティング")
    with st.expander("NotionDB接続の問題を解決するには"):
        st.markdown("""
        **よくある問題と解決方法:**
        
        1. **APIキーが無効**
           - Notionの設定ページで新しいAPIキーを生成
           - `.streamlit/secrets.toml`を更新
        
        2. **データベースIDが間違っている**
           - Notionでデータベースを開き、URLからIDを確認
           - 例: `https://notion.so/workspace/256709bb38f18069a903f7ade8f76c73`
        
        3. **データベースへのアクセス権限がない**
           - Notionでデータベースを開き、右上の「共有」ボタンをクリック
           - 統合（Integration）にアクセス権限を付与
        
        4. **ライブラリがインストールされていない**
           - ターミナルで実行: `pip install notion-client==2.2.1`
        
        5. **ネットワーク接続の問題**
           - インターネット接続を確認
           - ファイアウォールの設定を確認
        """)
        
        st.markdown("**設定ファイルの例:**")
        st.code("""
# .streamlit/secrets.toml
NOTION_API_KEY = "ntn_your_api_key_here"
NODE_DB_ID = "your_diagnostic_db_id"
CASE_DB_ID = "your_repair_case_db_id"
ITEM_DB_ID = "your_items_db_id"
        """)

# APIエンドポイント用の関数
def search_repair_advice_api(query):
    """修理アドバイス検索API用の関数"""
    try:
        # RAGシステムでの検索（データアクセス層を使用）
        data_access = ensure_data_access()
        if data_access['available']:
            rag_results = data_access['knowledge_base_manager'].search_in_content(query)
        else:
            rag_results = {}
        
        # 結果をフォーマット
        results = []
        
        for doc in rag_results:
            # テキストファイルの内容を解析して構造化
            content = doc.page_content
            source = doc.metadata.get('source', 'テキストファイル')
            
            # 基本的な情報
            result = {
                "title": f"📄 {source} からの情報",
                "category": "RAG検索",
                "content": content[:500] + "..." if len(content) > 500 else content,
                "source": "rag_text",
                "relevance": "high"
            }
            
            # バッテリー関連の構造化
            if "バッテリー" in content or "充電" in content:
                result.update({
                    "structured_content": {
                        "problem_description": "バッテリーの寿命は通常2-3年で、定期的な点検と適切な充電管理が重要です。",
                        "symptoms": [
                            "エンジンがかからない",
                            "電圧が低い（12.6V以下）",
                            "充電ができない",
                            "バッテリー液の減少"
                        ],
                        "causes": [
                            "バッテリーの寿命（2-3年経過）",
                            "端子の腐食・接触不良",
                            "充電不足・過放電",
                            "バッテリー液の不足"
                        ],
                        "solutions": [
                            "端子の清掃・接続確認（3,000円～5,000円）",
                            "充電器での充電（5,000円～10,000円）",
                            "バッテリーの交換（15,000円～25,000円）",
                            "充電システムの点検（5,000円～10,000円）"
                        ],
                        "tools_and_parts": [
                            "マルチメーター（電圧測定用）",
                            "端子ブラシ（清掃用）",
                            "充電器（12V対応）",
                            "レンチセット（端子取り外し用）"
                        ]
                    },
                    "warnings": [
                        "バッテリー液は危険です。直接触れないでください",
                        "充電中は換気を十分に行ってください",
                        "専門知識が必要な場合は専門店に相談してください"
                    ],
                    "substitutes": [
                        {
                            "name": "パナソニック カーバッテリー 55B24L",
                            "url": "https://www.panasonic.com/jp/consumer/automotive/battery/car-battery.html",
                            "price": "約18,000円"
                        },
                        {
                            "name": "GSユアサ カーバッテリー 55B24L",
                            "url": "https://www.gs-yuasa.com/jp/product/automotive/car_battery/",
                            "price": "約16,000円"
                        }
                    ],
                    "costs": "15,000円～35,000円",
                    "tools": "マルチメーター、端子ブラシ、充電器、レンチセット"
                })
            
            # トイレ関連の構造化
            elif "トイレ" in content or "水" in content:
                result.update({
                    "structured_content": {
                        "problem_description": "キャンピングカーのトイレは定期的な清掃とメンテナンスが重要です。",
                        "symptoms": [
                            "水が流れない",
                            "異臭がする",
                            "水漏れが発生する",
                            "ポンプが動かない"
                        ],
                        "causes": [
                            "カセットタンクの汚れ・詰まり",
                            "ポンプの故障・摩耗",
                            "シールの劣化・破損",
                            "配管の詰まり・汚れ"
                        ],
                        "solutions": [
                            "カセットタンクの清掃（0円～3,000円）",
                            "ポンプの点検・交換（3,000円～8,000円）",
                            "シールの交換（5,000円～15,000円）",
                            "配管の清掃（1,000円～5,000円）"
                        ],
                        "tools_and_parts": [
                            "専用ブラシ（トイレ清掃用）",
                            "トイレ用洗剤・消臭剤",
                            "シールキット（Oリング等）",
                            "ポンプ（交換用）"
                        ]
                    },
                    "warnings": [
                        "汚物の処理は適切に行ってください",
                        "清掃時は手袋を着用してください",
                        "シール交換は慎重に行ってください"
                    ],
                    "substitutes": [
                        {
                            "name": "テラード カセットトイレ用洗剤",
                            "url": "https://www.terado.co.jp/products/toilet/",
                            "price": "約800円"
                        },
                        {
                            "name": "サニテール トイレ用消臭剤",
                            "url": "https://www.sanitair.co.jp/products/",
                            "price": "約600円"
                        }
                    ],
                    "costs": "5,000円～25,000円",
                    "tools": "ブラシ、洗剤、シール、ポンプ"
                })
            
            results.append(result)
        
        return {
            "success": True,
            "results": results,
            "query": query
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

# Streamlit APIエンドポイント
@st.cache_data
def get_api_response(query):
    """API応答をキャッシュ"""
    return search_repair_advice_api(query)

def search_text_files_api(query):
    """テキストファイル検索API（HTML用）"""
    try:
        print(f"📄 テキストファイル検索開始: {query}")
        
        # テキストファイルの検索（データアクセス層を使用）
        data_access = ensure_data_access()
        if data_access['available']:
            results = data_access['knowledge_base_manager'].search_in_content(query)
        else:
            results = {}
        
        if results:
            print(f"✅ テキストファイル検索成功: {len(results)}件")
            return {
                "success": True,
                "results": results,
                "query": query,
                "source": "text_files"
            }
        else:
            print("⚠️ テキストファイル検索結果なし")
            return {
                "success": False,
                "error": "該当するテキストファイルが見つかりませんでした",
                "query": query,
                "source": "text_files"
            }
    except Exception as e:
        print(f"❌ テキストファイル検索エラー: {e}")
        return {
            "success": False,
            "error": f"テキストファイル検索中にエラーが発生しました: {str(e)}",
            "query": query,
            "source": "text_files"
        }

if __name__ == "__main__":
    # URLパラメータでAPI呼び出しを判定
    if st.query_params.get("api") == "search_repair_advice":
        query = st.query_params.get("query", "")
        if query:
            result = get_api_response(query)
            st.json(result)
        else:
            st.json({"success": False, "error": "クエリパラメータが指定されていません"})
    else:
        main()

def display_repair_advice_results(results, query):
    """修理アドバイス結果を表示"""
    st.markdown(f"### 🔍 「{query}」の検索結果")
    
    if isinstance(results, list):
        for i, result in enumerate(results):
            with st.expander(f"📋 {result.get('title', '修理アドバイス')}", expanded=True):
                # 基本情報
                st.markdown(f"**📂 カテゴリ:** {result.get('category', '不明')}")
                
                # 内容を整理して表示
                content = result.get('content', '内容なし')
                
                # 雨漏りなどの複雑な情報を整理
                if "雨漏り" in content or "Case" in content:
                    display_organized_repair_info(content, result)
                else:
                    if content and len(content) > 200:
                        # 長い内容の場合は要約を表示
                        st.markdown("**📋 概要:**")
                        st.markdown(content[:300] + "..." if len(content) > 300 else content)
                        
                        # 詳細を展開可能にする
                        with st.expander("📖 詳細情報を表示", expanded=False):
                            st.markdown(content)
                    else:
                        st.markdown(f"**📋 内容:** {content}")
                
                # 整理された情報を表示
                display_organized_repair_sections(result)
    
    elif isinstance(results, dict):
        # 単一の結果の場合
        result = results
        with st.expander(f"📋 {result.get('title', '修理アドバイス')}", expanded=True):
            st.markdown(f"**📂 カテゴリ:** {result.get('category', '不明')}")
            
            # 内容を整理して表示
            content = result.get('content', '内容なし')
            if "雨漏り" in content or "Case" in content:
                display_organized_repair_info(content, result)
            else:
                if content and len(content) > 200:
                    st.markdown("**📋 概要:**")
                    st.markdown(content[:300] + "..." if len(content) > 300 else content)
                    
                    with st.expander("📖 詳細情報を表示", expanded=False):
                        st.markdown(content)
                else:
                    st.markdown(f"**📋 内容:** {content}")
            
            # 整理された情報を表示
            display_organized_repair_sections(result)
    
    else:
        st.warning("結果の形式が正しくありません。")

def display_organized_repair_info(content, result):
    """整理された修理情報を表示"""
    import re
    
    # ケース情報を抽出
    cases = re.findall(r'## 【Case ([^】]+)】([^#]+)', content)
    
    if cases:
        st.markdown("**🔍 問題の種類別ケース:**")
        
        # ケースをカテゴリ別に整理
        case_categories = {
            "天井・ルーフ": [],
            "窓・ドア": [],
            "床・内装": [],
            "その他": []
        }
        
        for case_id, case_content in cases:
            case_text = f"**{case_id}**: {case_content.strip()[:100]}..."
            
            if "天井" in case_content or "ルーフ" in case_content or "スカイライト" in case_content:
                case_categories["天井・ルーフ"].append(case_text)
            elif "窓" in case_content or "ドア" in case_content or "モール" in case_content:
                case_categories["窓・ドア"].append(case_text)
            elif "床" in case_content or "内張り" in case_content or "壁紙" in case_content:
                case_categories["床・内装"].append(case_text)
            else:
                case_categories["その他"].append(case_text)
        
        # カテゴリ別に表示
        for category, cases_list in case_categories.items():
            if cases_list:
                with st.expander(f"📂 {category} ({len(cases_list)}件)", expanded=False):
                    for case in cases_list:
                        st.markdown(f"• {case}")
        
        # 詳細情報を展開可能にする
        with st.expander("📖 全ケースの詳細情報", expanded=False):
            st.markdown(content)
    else:
        # ケースが見つからない場合は通常の表示
        if content and len(content) > 200:
            st.markdown("**📋 概要:**")
            st.markdown(content[:300] + "..." if len(content) > 300 else content)
            
            with st.expander("📖 詳細情報を表示", expanded=False):
                st.markdown(content)
        else:
            st.markdown(f"**📋 内容:** {content}")

def display_organized_repair_sections(result):
    """整理された修理情報セクションを表示"""
    
    # 1. 問題の種類
    st.markdown("---")
    st.markdown("### 🔍 問題の種類")
    
    if result.get('structured_content', {}).get('problem_description'):
        st.markdown(result['structured_content']['problem_description'])
    elif result.get('content'):
        # 内容から問題の種類を抽出
        content = result['content']
        if "Case" in content:
            # ケース情報から問題を抽出
            import re
            cases = re.findall(r'## 【Case ([^】]+)】([^#]+)', content)
            if cases:
                st.markdown("**主な問題パターン:**")
                for case_id, case_content in cases[:3]:  # 最初の3件を表示
                    st.markdown(f"• **{case_id}**: {case_content.strip()[:80]}...")
            else:
                st.markdown(content[:200] + "..." if len(content) > 200 else content)
        else:
            st.markdown(content[:200] + "..." if len(content) > 200 else content)
    else:
        st.markdown("問題の詳細情報がありません。")
    
    # 2. 修理費用目安
    st.markdown("---")
    st.markdown("### 💰 修理費用目安")
    
    if result.get('costs'):
        for cost in result['costs']:
            st.markdown(f"• {cost}")
    elif result.get('structured_content', {}).get('repair_costs'):
        costs = result['structured_content']['repair_costs']
        if isinstance(costs, list):
            for cost in costs:
                st.markdown(f"• {cost}")
        else:
            st.markdown(f"• {costs}")
    else:
        # 雨漏りの場合の具体的な費用情報
        if content and "雨漏り" in content:
            st.markdown("• **シーリング材交換:** 8,000円～15,000円")
            st.markdown("• **ルーフパネル修理:** 20,000円～50,000円")
            st.markdown("• **窓枠モール交換:** 5,000円～12,000円")
            st.markdown("• **バックドアガスケット交換:** 3,000円～8,000円")
            st.markdown("• **内装材交換:** 10,000円～25,000円")
            st.markdown("• **緊急応急処置:** 2,000円～5,000円")
        else:
            st.markdown("• 費用情報は個別見積もりが必要です")
            st.markdown("• 専門店への相談をお勧めします")
    
    # 3. 必要な工具・部品
    st.markdown("---")
    st.markdown("### 🛠️ 必要な工具・部品")
    
    tools_and_parts = []
    
    # 構造化された内容から工具を取得
    if result.get('structured_content', {}).get('tools_needed'):
        tools_and_parts.extend(result['structured_content']['tools_needed'])
    
    # 代替品から部品を取得
    if result.get('alternatives'):
        tools_and_parts.extend(result['alternatives'])
    
    # 推奨製品から取得
    if result.get('recommended_products', {}).get('items'):
        tools_and_parts.extend(result['recommended_products']['items'])
    
    if tools_and_parts:
        for item in tools_and_parts:
            st.markdown(f"• {item}")
    else:
        # 雨漏りの場合の具体的な工具・部品情報
        if content and "雨漏り" in content:
            st.markdown("• **工具:** シーリングガン、カッター、ブラシ、マスキングテープ")
            st.markdown("• **シーリング材:** ウレタンシーラント、ブチルテープ")
            st.markdown("• **窓枠部品:** モール、スポンジゴム、防水シール")
            st.markdown("• **ルーフ部品:** ルーフパネル、ジョイント材")
            st.markdown("• **ガスケット:** バックドア用、ランプ用")
            st.markdown("• **内装材:** 壁紙、内張り材")
        else:
            st.markdown("• 基本的な工具セット")
            st.markdown("• 専門工具が必要な場合は専門店に相談")
    
    # 4. 修理手順
    st.markdown("---")
    st.markdown("### 🔧 修理手順")
    
    if result.get('structured_content', {}).get('solutions'):
        st.markdown("**基本的な修理手順:**")
        for i, solution in enumerate(result['structured_content']['solutions'], 1):
            st.markdown(f"{i}. {solution}")
    elif result.get('repair_steps'):
        st.markdown("**修理手順:**")
        for i, step in enumerate(result['repair_steps'], 1):
            st.markdown(f"{i}. {step}")
    else:
        # 雨漏りの場合の具体的な修理手順
        if content and "雨漏り" in content:
            st.markdown("**雨漏り修理の詳細手順:**")
            st.markdown("1. **原因特定:** 水の侵入箇所を特定（ルーフ、窓枠、ドア周り）")
            st.markdown("2. **古いシーリング除去:** カッターで古いシーリング材を除去")
            st.markdown("3. **清掃・乾燥:** 作業箇所を清掃し、完全に乾燥させる")
            st.markdown("4. **マスキング:** 周辺をマスキングテープで保護")
            st.markdown("5. **シーリング施工:** ウレタンシーラントを均一に塗布")
            st.markdown("6. **仕上げ:** 余分なシーリング材を除去し、仕上げ")
            st.markdown("7. **水密テスト:** 水をかけて水密性を確認")
        else:
            st.markdown("**一般的な手順:**")
            st.markdown("1. 問題箇所の特定")
            st.markdown("2. 安全確認と準備")
            st.markdown("3. 部品の交換・修理")
            st.markdown("4. 動作確認")
            st.markdown("5. 最終チェック")
    
    # 5. 注意事項
    st.markdown("---")
    st.markdown("### ⚠️ 注意事項")
    
    if result.get('warnings'):
        for warning in result['warnings']:
            st.markdown(f"• {warning}")
    elif result.get('structured_content', {}).get('causes'):
        st.markdown("**考えられる原因と注意点:**")
        for cause in result['structured_content']['causes']:
            st.markdown(f"• {cause}")
    else:
        # 雨漏りの場合の具体的な注意事項
        if content and "雨漏り" in content:
            st.markdown("• **高所作業:** ルーフ作業は転落の危険があるため、安全帯の着用必須")
            st.markdown("• **天候条件:** 雨天時や強風時は作業を避ける")
            st.markdown("• **シーリング材:** ウレタンシーラントは皮膚に付着すると危険")
            st.markdown("• **換気:** 密閉空間での作業時は十分な換気を確保")
            st.markdown("• **電気系統:** 電気配線近くでの作業時は感電に注意")
            st.markdown("• **専門知識:** 複雑な構造の場合は専門店に相談")
        else:
            st.markdown("• 安全第一で作業を行ってください")
            st.markdown("• 専門知識が必要な場合は専門店に相談")
            st.markdown("• 工具の取り扱いには十分注意")
    
    # 関連リンク
    if result.get('urls'):
        st.markdown("---")
        st.markdown("### 🔗 関連リンク")
        for url in result['urls']:
            st.markdown(f"• [{url}]({url})")
