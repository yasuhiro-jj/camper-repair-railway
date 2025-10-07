
from flask import Flask, jsonify
import socket

app = Flask(__name__)

@app.route("/")
def hello():
    return jsonify({
        "message": "最小限サーバーが動作しています",
        "timestamp": "2024-01-01T00:00:00",
        "port": 5001
    })

@app.route("/test")
def test():
    return "テスト成功！"

if __name__ == "__main__":
    print("🚀 最小限サーバーを起動中...")
    print("🌐 アクセスURL: http://localhost:5001")
    print("🔍 テストURL: http://localhost:5001/test")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5001)
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        print("🔧 対処法:")
        print("1. ポート5001が使用中でないか確認")
        print("2. ファイアウォール設定を確認")
        print("3. 管理者権限で実行")
