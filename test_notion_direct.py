#!/usr/bin/env python3
"""
Notion接続直接テストスクリプト（Streamlit不要）
"""

import os
import sys

def test_environment():
    """環境変数の確認"""
    print("🔧 Notion接続直接テスト")
    print("=" * 50)
    
    # .envファイルの確認
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .envファイルが見つかりました: {env_file}")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ .envファイルを読み込みました")
        except ImportError:
            print("⚠️ python-dotenvがインストールされていません")
        except Exception as e:
            print(f"⚠️ .envファイルの読み込みエラー: {e}")
    else:
        print(f"⚠️ .envファイルが見つかりません: {env_file}")
        print("環境変数が直接設定されているか確認します...")
    
    # 環境変数の確認
    print("\n📋 環境変数確認")
    
    # APIキーの確認
    api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    if api_key:
        if "your_" in api_key or "your_notion" in api_key:
            print("❌ APIキーにプレースホルダーが設定されています")
            print(f"現在の値: {api_key}")
            return False
        else:
            print(f"✅ APIキー: {api_key[:10]}...")
    else:
        print("❌ APIキーが設定されていません")
        print("環境変数 NOTION_API_KEY または NOTION_TOKEN を設定してください")
        return False
    
    # データベースIDの確認
    node_db_id = os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
    case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
    item_db_id = os.getenv("ITEM_DB_ID")
    
    print(f"📊 診断フローDB: {node_db_id or '未設定'}")
    print(f"🔧 修理ケースDB: {case_db_id or '未設定'}")
    print(f"🛠️ 部品・工具DB: {item_db_id or '未設定'}")
    
    return True, api_key, node_db_id, case_db_id, item_db_id

def test_notion_connection(api_key, node_db_id, case_db_id, item_db_id):
    """Notion接続テスト"""
    print("\n🔌 Notion接続テスト")
    
    try:
        from notion_client import Client
        print("✅ notion-clientライブラリをインポートしました")
    except ImportError:
        print("❌ notion-clientライブラリがインストールされていません")
        print("以下のコマンドでインストールしてください:")
        print("pip install notion-client")
        return False
    
    try:
        client = Client(auth=api_key)
        print("✅ Notionクライアントの初期化に成功しました")
        
        # データベースアクセステスト
        success_count = 0
        total_tests = 0
        
        if node_db_id:
            total_tests += 1
            print("\n📋 診断フローデータベーステスト")
            try:
                response = client.databases.query(database_id=node_db_id)
                nodes = response.get("results", [])
                print(f"✅ 診断フローデータベースにアクセス成功: {len(nodes)}件のノード")
                success_count += 1
                
                # 診断ノードの構造を確認
                if nodes:
                    first_node = nodes[0]
                    properties = first_node.get("properties", {})
                    print("📄 診断ノードのプロパティ:")
                    for key, value in properties.items():
                        prop_type = value.get("type", "unknown")
                        print(f"  - {key}: {prop_type}")
                
            except Exception as e:
                print(f"❌ 診断フローデータベースアクセス失敗: {e}")
        
        if case_db_id:
            total_tests += 1
            print("\n🔧 修理ケースデータベーステスト")
            try:
                response = client.databases.query(database_id=case_db_id)
                cases = response.get("results", [])
                print(f"✅ 修理ケースデータベースにアクセス成功: {len(cases)}件のケース")
                success_count += 1
                
            except Exception as e:
                print(f"❌ 修理ケースデータベースアクセス失敗: {e}")
        
        if item_db_id:
            total_tests += 1
            print("\n🛠️ 部品・工具データベーステスト")
            try:
                response = client.databases.query(database_id=item_db_id)
                items = response.get("results", [])
                print(f"✅ 部品・工具データベースにアクセス成功: {len(items)}件のアイテム")
                success_count += 1
                
            except Exception as e:
                print(f"❌ 部品・工具データベースアクセス失敗: {e}")
        
        # 結果サマリー
        print(f"\n📊 テスト結果: {success_count}/{total_tests} 成功")
        
        if success_count == total_tests and total_tests > 0:
            print("🎉 すべてのテストが成功しました！")
            print("✅ 症状診断システムは正常に動作する準備ができています。")
            return True
        elif success_count > 0:
            print("⚠️ 一部のデータベースにアクセスできません。")
            print("症状診断システムは部分的に動作する可能性があります。")
            return True
        else:
            print("❌ すべてのデータベースアクセスに失敗しました。")
            return False
        
    except Exception as e:
        print(f"❌ Notionクライアントの初期化に失敗: {e}")
        print("APIキーが正しく設定されているか確認してください")
        return False

def main():
    """メイン関数"""
    try:
        # 環境変数の確認
        result = test_environment()
        if not result:
            print("\n❌ 環境変数の設定に問題があります")
            return False
        
        success, api_key, node_db_id, case_db_id, item_db_id = result
        
        if not success:
            return False
        
        # Notion接続テスト
        return test_notion_connection(api_key, node_db_id, case_db_id, item_db_id)
        
    except Exception as e:
        print(f"\n💥 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Python環境でNotion接続テストを実行します...")
    print("=" * 60)
    
    result = main()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ テスト完了: 症状診断システムは使用可能です")
    else:
        print("❌ テスト失敗: 設定を確認してください")
    
    print("\n何かキーを押すと終了します...")
    input()
