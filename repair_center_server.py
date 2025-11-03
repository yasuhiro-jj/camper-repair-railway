#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修理アドバイスセンター用の簡単なサーバー
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

# 修理アドバイスセンターのHTMLを提供
@app.route("/")
def repair_advice_center():
    """修理アドバイスセンターのメインページ"""
    try:
        return render_template('repair_advice_center.html')
    except Exception as e:
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
                .status {{
                    background: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .error {{
                    background: #ffebee;
                    border: 1px solid #f44336;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔧 修理アドバイスセンター</h1>
                    <p>キャンピングカー修理の専門サポート</p>
                </div>
                
                <div class="status">
                    <h3>✅ サーバーが正常に動作しています</h3>
                    <p>修理アドバイスセンターが利用可能です</p>
                </div>
                
                <div class="error">
                    <h3>⚠️ テンプレート読み込みエラー</h3>
                    <p>エラー: {str(e)}</p>
                    <p>基本的な機能は利用可能です</p>
                </div>
                
                <h2>🔍 利用可能な機能</h2>
                <ul>
                    <li>📋 カテゴリ別修理情報</li>
                    <li>💰 修理費用の見積もり</li>
                    <li>🛠️ 修理手順の詳細</li>
                    <li>⚠️ 安全注意事項</li>
                </ul>
                
                <h2>🧪 API テスト</h2>
                <p><a href="/api/health">ヘルスチェック</a></p>
                <p><a href="/api/categories">カテゴリ一覧</a></p>
            </div>
        </body>
        </html>
        """

@app.route("/api/health")
def health_check():
    """ヘルスチェックAPI"""
    return jsonify({
        "status": "healthy",
        "message": "修理アドバイスセンターAPIが正常に動作しています",
        "services": {
            "repair_advice": True,
            "categories": True,
            "search": True
        }
    })

@app.route("/api/categories")
def get_categories():
    """カテゴリ一覧API"""
    try:
        # RepairCategoryManagerを使用してカテゴリを取得
        try:
            from repair_category_manager import RepairCategoryManager
            category_manager = RepairCategoryManager()
            categories = category_manager.get_all_categories()
            
            if categories:
                return jsonify({
                    "success": True,
                    "categories": categories,
                    "source": "category_definitions"
                })
        except Exception as e:
            print(f"⚠️ RepairCategoryManagerの読み込みに失敗: {e}")
            # フォールバック: 基本的なカテゴリ定義を返す
            pass
        
        # フォールバック: 基本的なカテゴリ定義
        categories_dict = {
            "バッテリー": {
                "name": "バッテリー",
                "icon": "🔋",
                "keywords": ["バッテリー", "電池", "電源"],
                "description": "バッテリー関連の修理情報",
                "repair_costs": [],
                "repair_steps": [],
                "warnings": []
            },
            "トイレ": {
                "name": "トイレ",
                "icon": "🚽",
                "keywords": ["トイレ", "便器", "カセット"],
                "description": "トイレ関連の修理情報",
                "repair_costs": [],
                "repair_steps": [],
                "warnings": []
            },
            "エアコン": {
                "name": "エアコン",
                "icon": "❄️",
                "keywords": ["エアコン", "冷房", "暖房", "空調"],
                "description": "エアコン関連の修理情報",
                "repair_costs": [],
                "repair_steps": [],
                "warnings": []
            },
            "雨漏り": {
                "name": "雨漏り",
                "icon": "🌧️",
                "keywords": ["雨漏り", "漏水", "水漏れ"],
                "description": "雨漏り関連の修理情報",
                "repair_costs": [],
                "repair_steps": [],
                "warnings": []
            },
            "FFヒーター": {
                "name": "FFヒーター",
                "icon": "🔥",
                "keywords": ["FFヒーター", "ヒーター", "暖房"],
                "description": "FFヒーター関連の修理情報",
                "repair_costs": [],
                "repair_steps": [],
                "warnings": []
            },
            "水道ポンプ": {
                "name": "水道ポンプ",
                "icon": "💧",
                "keywords": ["水道ポンプ", "ポンプ", "水"],
                "description": "水道ポンプ関連の修理情報",
                "repair_costs": [],
                "repair_steps": [],
                "warnings": []
            },
            "インバーター": {
                "name": "インバーター",
                "icon": "⚡",
                "keywords": ["インバーター", "電源", "変換"],
                "description": "インバーター関連の修理情報",
                "repair_costs": [],
                "repair_steps": [],
                "warnings": []
            }
        }
        
        return jsonify({
            "success": True,
            "categories": categories_dict,
            "source": "fallback"
        })
        
    except Exception as e:
        print(f"❌ カテゴリ定義取得エラー: {e}")
        return jsonify({
            "success": False,
            "error": f"カテゴリ定義取得中にエラーが発生しました: {str(e)}",
            "source": "error"
        }), 500

@app.route("/api/search", methods=["POST"])
def search_repair_info():
    """修理情報検索API"""
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({"error": "検索クエリが空です"}), 400
        
        # クエリに基づいて詳細な検索結果を生成
        results = generate_detailed_search_results(query)
        
        # デバッグ用ログ
        print(f"🔍 検索クエリ: {query}")
        print(f"📊 生成された結果数: {len(results)}")
        for i, result in enumerate(results):
            print(f"  [{i}] タイトル: {result.get('title', 'N/A')}")
            print(f"  [{i}] カテゴリ: {result.get('category', 'N/A')}")
            print(f"  [{i}] 費用データ: {result.get('costs', 'N/A')}")
        
        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "total": len(results)
        })
        
    except Exception as e:
        return jsonify({"error": f"検索エラー: {str(e)}"}), 500

def generate_detailed_search_results(query):
    """詳細な検索結果を生成"""
    query_lower = query.lower()
    
    # カテゴリ別の詳細情報
    category_info = {
        "バッテリー": {
            "title": "🔋 バッテリーの故障と修理",
            "content": "バッテリーの故障はキャンピングカーの電源問題の主要原因です。",
            "repair_steps": [
                "バッテリー電圧を測定（12.6V以上が正常）",
                "端子の清掃と接続確認",
                "バッテリー液の確認と補充",
                "充電システムの点検"
            ],
            "warnings": [
                "バッテリー液は有毒です。手袋と保護メガネを使用してください",
                "端子の接続時は必ずマイナス端子から外してください",
                "充電中は換気を十分に行ってください"
            ],
            "costs": [
                "バッテリー交換: 15,000-30,000円",
                "端子清掃: 無料（自分で作業）",
                "充電器交換: 5,000-15,000円"
            ]
        },
        "トイレ": {
            "title": "🚽 トイレの故障と修理",
            "content": "キャンピングカーのトイレは適切なメンテナンスが重要です。",
            "repair_steps": [
                "カセットタンクの取り外し",
                "内部の清掃と除菌",
                "パッキンやバルブの点検",
                "薬剤の適切な投入"
            ],
            "warnings": [
                "汚水処理は適切な場所で行ってください",
                "薬剤は指定量を守って使用してください",
                "パッキンは定期的に交換が必要です"
            ],
            "costs": [
                "カセットタンク交換: 8,000-15,000円",
                "パッキン交換: 2,000-5,000円",
                "バルブ交換: 5,000-10,000円"
            ]
        },
        "エアコン": {
            "title": "❄️ エアコンの故障と修理",
            "content": "エアコンの故障は快適性に大きく影響します。",
            "repair_steps": [
                "フィルターの清掃",
                "コンプレッサーの動作確認",
                "冷媒ガスの圧力チェック",
                "電気配線の点検"
            ],
            "warnings": [
                "冷媒ガスの取り扱いは専門業者に依頼してください",
                "電気系統の作業は感電の危険があります",
                "フィルターは定期的な清掃が必要です"
            ],
            "costs": [
                "フィルター交換: 3,000-8,000円",
                "冷媒ガス補充: 10,000-20,000円",
                "コンプレッサー交換: 50,000-100,000円"
            ]
        },
        "雨漏り": {
            "title": "🌧️ 雨漏りの修理",
            "content": "雨漏りは早期発見と修理が重要です。",
            "repair_steps": [
                "漏水箇所の特定",
                "シーリング材の除去",
                "新しいシーリング材の充填",
                "防水テープの貼付"
            ],
            "warnings": [
                "高所作業は安全対策を十分に行ってください",
                "シーリング材は完全に乾燥してから使用してください",
                "雨天時は作業を避けてください"
            ],
            "costs": [
                "シーリング材: 1,000-3,000円",
                "防水テープ: 2,000-5,000円",
                "専門業者修理: 20,000-50,000円"
            ]
        }
    }
    
    # クエリにマッチするカテゴリを検索
    matched_results = []
    
    for category, info in category_info.items():
        if (category.lower() in query_lower or 
            any(keyword in query_lower for keyword in ["故障", "修理", "問題", "不調", "不良"])):
            matched_results.append({
                "title": info["title"],
                "content": info["content"],
                "category": category,
                "repair_steps": info["repair_steps"],
                "warnings": info["warnings"],
                "costs": info["costs"],
                "relevance": "high",
                "source": "knowledge_base"
            })
    
    # マッチするカテゴリがない場合のデフォルト結果
    if not matched_results:
        matched_results.append({
            "title": f"🔧 {query}の修理情報",
            "content": f"{query}に関する修理情報を提供します。詳細な診断には専門業者への相談をお勧めします。",
            "category": "general",
            "repair_steps": [
                "症状の詳細確認",
                "基本点検項目のチェック",
                "専門業者への相談",
                "適切な修理方法の選択"
            ],
            "warnings": [
                "安全第一で作業を行ってください",
                "不明な点は専門業者に相談してください",
                "電気系統の作業は感電の危険があります"
            ],
            "costs": [
                "基本点検: 無料（自分で作業）",
                "専門診断: 5,000-15,000円",
                "修理費用: 要見積もり"
            ],
            "relevance": "medium",
            "source": "general"
        })
    
    return matched_results

@app.route("/api/search_text_files", methods=["POST"])
def search_text_files():
    """テキストファイル検索API"""
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({"error": "検索クエリが空です"}), 400
        
        # 詳細なテキストファイル検索結果を生成
        results = generate_text_file_results(query)
        
        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "total": len(results)
        })
        
    except Exception as e:
        return jsonify({"error": f"テキストファイル検索エラー: {str(e)}"}), 500

def generate_text_file_results(query):
    """テキストファイル検索結果を生成"""
    query_lower = query.lower()
    
    # テキストファイルの内容（実際のファイルから読み込む場合はここを修正）
    text_files_content = {
        "バッテリー": {
            "title": "🔋 バッテリーマニュアル",
            "content": "バッテリーの基本的なメンテナンスとトラブルシューティングについて説明します。",
            "file": "バッテリー.txt",
            "source": "manual"
        },
        "トイレ": {
            "title": "🚽 トイレマニュアル",
            "content": "キャンピングカーのトイレの使用方法とメンテナンスについて説明します。",
            "file": "トイレ.txt",
            "source": "manual"
        },
        "エアコン": {
            "title": "❄️ エアコンマニュアル",
            "content": "エアコンの操作方法とメンテナンスについて説明します。",
            "file": "エアコン.txt",
            "source": "manual"
        },
        "雨漏り": {
            "title": "🌧️ 雨漏り対策マニュアル",
            "content": "雨漏りの原因と対策について説明します。",
            "file": "雨漏り.txt",
            "source": "manual"
        }
    }
    
    results = []
    
    # クエリにマッチするファイルを検索
    for category, info in text_files_content.items():
        if category.lower() in query_lower or any(keyword in query_lower for keyword in ["故障", "修理", "問題"]):
            results.append(info)
    
    # マッチするファイルがない場合のデフォルト結果
    if not results:
        results.append({
            "title": f"📄 {query}のマニュアル情報",
            "content": f"{query}に関するマニュアル情報が利用可能です。詳細な情報は専門業者にご相談ください。",
            "file": f"{query}.txt",
            "source": "manual"
        })
    
    return results

if __name__ == "__main__":
    print("🚀 修理アドバイスセンターサーバーを起動中...")
    print("🌐 アクセスURL: http://localhost:5003")
    print("🔧 修理アドバイスセンター: http://localhost:5003/")
    print("🧪 ヘルスチェック: http://localhost:5003/api/health")
    print("📋 カテゴリ一覧: http://localhost:5003/api/categories")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5003)
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        print("🔧 対処法:")
        print("1. ポート5003が使用中でないか確認してください")
        print("2. ファイアウォール設定を確認してください")
        print("3. 管理者権限で実行してください")
