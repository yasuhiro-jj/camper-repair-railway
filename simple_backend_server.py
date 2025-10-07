#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易バックエンドサーバー - 接続テスト用
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
from datetime import datetime

# === Flask アプリケーションの設定 ===
app = Flask(__name__)
CORS(app, origins=['http://localhost:8501', 'http://localhost:3000', 'http://localhost:3001', 'http://localhost:5001'])

# 簡易テスト用HTML
TEST_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 修理アドバイスセンター（簡易版）</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .search-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
        }
        .search-input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #667eea;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
            margin-bottom: 15px;
        }
        .search-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
        }
        .results-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        .status {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 修理アドバイスセンター（簡易版）</h1>
            <p>接続テスト用サーバー</p>
        </div>
        
        <div class="status">
            ✅ <strong>サーバー接続成功！</strong><br>
            現在時刻: <span id="currentTime"></span><br>
            サーバーポート: 5001<br>
            ステータス: 正常稼働中
        </div>
        
        <div class="search-container">
            <h2>🔍 簡易検索テスト</h2>
            <input type="text" id="searchInput" class="search-input" placeholder="検索テスト（例: バッテリー）" value="バッテリー">
            <button class="search-btn" onclick="testSearch()">検索テスト</button>
        </div>
        
        <div class="results-container" id="resultsContainer">
            <h3>📋 検索結果</h3>
            <div id="resultsContent"></div>
        </div>
        
        <div style="margin-top: 30px; text-align: center;">
            <h3>🔗 利用可能なエンドポイント</h3>
            <p><a href="/api/test">/api/test</a> - テスト用API</p>
            <p><a href="/api/health">/api/health</a> - ヘルスチェック</p>
            <p><a href="/api/search">/api/search</a> - 検索API（POST）</p>
        </div>
    </div>
    
    <script>
        // 現在時刻を表示
        document.getElementById('currentTime').textContent = new Date().toLocaleString('ja-JP');
        
        async function testSearch() {
            const query = document.getElementById('searchInput').value;
            const resultsContainer = document.getElementById('resultsContainer');
            const resultsContent = document.getElementById('resultsContent');
            
            if (!query) {
                alert('検索クエリを入力してください');
                return;
            }
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultsContent.innerHTML = `
                        <div style="background: #d4edda; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                            <strong>✅ 検索成功</strong><br>
                            クエリ: ${data.query}<br>
                            結果数: ${data.results ? data.results.length : 0}件
                        </div>
                        <pre style="background: #f8f9fa; padding: 15px; border-radius: 10px; overflow-x: auto;">
${JSON.stringify(data, null, 2)}
                        </pre>
                    `;
                } else {
                    resultsContent.innerHTML = `
                        <div style="background: #f8d7da; padding: 15px; border-radius: 10px;">
                            <strong>❌ 検索エラー</strong><br>
                            エラー: ${data.error || 'Unknown error'}
                        </div>
                    `;
                }
                
                resultsContainer.style.display = 'block';
            } catch (error) {
                resultsContent.innerHTML = `
                    <div style="background: #f8d7da; padding: 15px; border-radius: 10px;">
                        <strong>❌ 接続エラー</strong><br>
                        エラー: ${error.message}
                    </div>
                `;
                resultsContainer.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    """メインページ - 簡易テスト用HTMLを返す"""
    return render_template_string(TEST_HTML)

@app.route("/api/test", methods=["GET"])
def test_api():
    """テスト用API"""
    return jsonify({
        "status": "OK",
        "message": "簡易サーバーが正常に動作しています",
        "timestamp": datetime.now().isoformat(),
        "server": "simple_backend_server",
        "port": 5001
    })

@app.route("/api/health", methods=["GET"])
def health_check():
    """ヘルスチェック"""
    return jsonify({
        "status": "healthy",
        "server": "simple_backend_server",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "web_server": True,
            "api_endpoints": True,
            "database": False,  # 簡易版では未使用
            "external_apis": False  # 簡易版では未使用
        }
    })

@app.route("/api/search", methods=["POST"])
def search_api():
    """簡易検索API"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "検索クエリが空です"}), 400
        
        # 簡易検索結果を返す
        mock_results = [
            {
                "title": f"📚 {query}の修理情報",
                "content": f"{query}に関する基本的な修理手順と注意事項を説明します。まずは安全確認から始めてください。",
                "source": "簡易検索システム",
                "url": None
            },
            {
                "title": f"🔧 {query}の点検方法",
                "content": f"{query}の点検時には、以下の項目を確認してください: 1) 外観の確認 2) 動作テスト 3) 異常音の確認",
                "source": "簡易検索システム", 
                "url": None
            },
            {
                "title": f"💰 {query}の費用目安",
                "content": f"{query}の修理費用は一般的に5,000円〜50,000円程度です。部品代と工賃により変動します。",
                "source": "簡易検索システム",
                "url": None
            }
        ]
        
        return jsonify({
            "query": query,
            "results": mock_results,
            "total": len(mock_results),
            "server": "simple_backend_server",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"検索エラー: {str(e)}"}), 500

# === アプリケーション起動 ===
if __name__ == "__main__":
    print("🚀 簡易バックエンドサーバーを起動中...")
    print("🌐 アクセスURL: http://localhost:5001")
    print("🔧 修理アドバイスセンター: http://localhost:5001/")
    print("🔍 テストAPI: http://localhost:5001/api/test")
    print("💚 ヘルスチェック: http://localhost:5001/api/health")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5001, threaded=True)
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        print("🔧 対処法:")
        print("1. ポート5001が使用中でないか確認してください")
        print("2. ファイアウォール設定を確認してください")
        print("3. 管理者権限で実行してください")
