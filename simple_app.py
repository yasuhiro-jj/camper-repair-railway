#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易Flaskアプリケーション（デバッグ用）
"""

from flask import Flask, render_template, request, jsonify
from repair_category_manager import RepairCategoryManager

# Flaskアプリケーションを作成
app = Flask(__name__)

# カテゴリーマネージャーを初期化
try:
    category_manager = RepairCategoryManager()
    print("✅ カテゴリーマネージャー初期化成功")
    print(f"📊 読み込み済みカテゴリー数: {len(category_manager.categories)}")
except Exception as e:
    print(f"❌ カテゴリーマネージャー初期化エラー: {e}")
    category_manager = None

@app.route("/")
def index():
    """メインページ"""
    return """
    <html>
    <head>
        <title>キャンピングカー修理サポート</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>🏠 キャンピングカー修理サポート</h1>
        <p>Flaskアプリケーションが正常に動作しています！</p>
        
        <h2>🧪 テスト機能</h2>
        <ul>
            <li><a href="/test">基本テスト</a></li>
            <li><a href="/test/water-leak">雨漏りテスト</a></li>
            <li><a href="/api/health">ヘルスチェック</a></li>
        </ul>
        
        <h2>🔍 検索テスト</h2>
        <form action="/search" method="POST">
            <input type="text" name="query" placeholder="検索クエリを入力" style="width: 300px;">
            <button type="submit">検索</button>
        </form>
    </body>
    </html>
    """

@app.route("/test")
def test():
    """基本テスト"""
    if category_manager:
        return f"""
        <h1>🧪 基本テスト</h1>
        <p>✅ Flaskアプリケーション: 正常</p>
        <p>✅ カテゴリーマネージャー: 正常</p>
        <p>📊 カテゴリー数: {len(category_manager.categories)}</p>
        <p><a href="/">← 戻る</a></p>
        """
    else:
        return """
        <h1>❌ 基本テスト</h1>
        <p>❌ カテゴリーマネージャーが初期化されていません</p>
        <p><a href="/">← 戻る</a></p>
        """

@app.route("/test/water-leak")
def test_water_leak():
    """雨漏りテスト"""
    if not category_manager:
        return "<h1>❌ カテゴリーマネージャーが初期化されていません</h1>"
    
    try:
        # 雨漏りカテゴリーのテスト
        category = "雨漏り"
        
        # カテゴリー特定テスト
        identified_category = category_manager.identify_category("雨漏り")
        
        # 修理費用目安の取得
        costs = category_manager.get_repair_costs(category)
        
        # 修理手順の取得
        steps = category_manager.get_repair_steps_from_json(category)
        
        # 注意事項の取得
        warnings = category_manager.get_warnings_from_json(category)
        
        result = f"""
        <h1>🧪 雨漏りテスト結果</h1>
        <h2>📋 カテゴリー特定</h2>
        <p>クエリ: "雨漏り"</p>
        <p>特定されたカテゴリー: {identified_category or 'なし'}</p>
        
        <h2>💰 修理費用目安</h2>
        <pre>{costs or '取得失敗'}</pre>
        
        <h2>🛠 修理手順</h2>
        <pre>{steps or '取得失敗'}</pre>
        
        <h2>⚠️ 注意事項</h2>
        <pre>{warnings or '取得失敗'}</pre>
        
        <p><a href="/">← 戻る</a></p>
        """
        
        return result
        
    except Exception as e:
        return f"""
        <h1>❌ 雨漏りテストエラー</h1>
        <p>エラー: {str(e)}</p>
        <p><a href="/">← 戻る</a></p>
        """

@app.route("/api/health")
def health_check():
    """ヘルスチェックAPI"""
    return jsonify({
        "status": "healthy",
        "category_manager": category_manager is not None,
        "categories_count": len(category_manager.categories) if category_manager else 0
    })

@app.route("/search", methods=["POST"])
def search():
    """検索API"""
    if not category_manager:
        return jsonify({"error": "カテゴリーマネージャーが初期化されていません"})
    
    try:
        query = request.form.get("query", "")
        if not query:
            return jsonify({"error": "検索クエリが空です"})
        
        # カテゴリー特定
        category = category_manager.identify_category(query)
        
        result = {
            "query": query,
            "category": category,
            "success": True
        }
        
        if category:
            # 修理費用目安
            costs = category_manager.get_repair_costs(category)
            result["costs"] = costs
            
            # 修理手順
            steps = category_manager.get_repair_steps_from_json(category)
            result["steps"] = steps
            
            # 注意事項
            warnings = category_manager.get_warnings_from_json(category)
            result["warnings"] = warnings
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    print("🚀 簡易Flaskアプリケーションを起動中...")
    print("🌐 アクセスURL: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
