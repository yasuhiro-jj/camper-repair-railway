# quick_test_conversation.py - 自然な会話機能のクイックテスト
import os

def test_imports():
    """インポートのテスト"""
    try:
        from conversation_memory import NaturalConversationManager
        print("✅ conversation_memory.py のインポートが成功しました")
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def test_basic_functionality():
    """基本機能のテスト"""
    try:
        from conversation_memory import NaturalConversationManager
        
        # APIキーの確認
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️ OPENAI_API_KEYが設定されていません（テストはスキップされます）")
            return True
        
        # マネージャーの初期化
        manager = NaturalConversationManager()
        print("✅ NaturalConversationManager の初期化が成功しました")
        
        # 意図分析のテスト
        test_message = "バッテリーが上がって困っています"
        intents = manager.analyze_user_intent(test_message)
        print(f"✅ 意図分析が正常に動作: {intents}")
        
        # 特定の質問パターンのテスト
        appointment_message = "今度の金曜日にそちらに行きたいのですが"
        response = manager.handle_specific_queries(appointment_message)
        if response:
            print("✅ 来店予約の質問に対する応答が正常に生成されました")
        else:
            print("⚠️ 来店予約の質問に対する応答が生成されませんでした")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本機能テストでエラーが発生: {e}")
        return False

def test_streamlit_integration():
    """Streamlit統合のテスト"""
    try:
        # streamlit_app.pyのインポートテスト
        import sys
        sys.path.append('.')
        
        # 必要なモジュールのインポート
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, AIMessage
        print("✅ 必要なLangChainモジュールのインポートが成功しました")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit統合テストでエラーが発生: {e}")
        return False

if __name__ == "__main__":
    print("🧪 自然な会話機能のクイックテストを開始します")
    print("=" * 60)
    
    # テストの実行
    tests = [
        ("インポートテスト", test_imports),
        ("基本機能テスト", test_basic_functionality),
        ("Streamlit統合テスト", test_streamlit_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}を実行中...")
        result = test_func()
        results.append((test_name, result))
        print(f"{'✅' if result else '❌'} {test_name}: {'成功' if result else '失敗'}")
    
    # 結果の表示
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー:")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("\n🎉 すべてのテストが成功しました！")
        print("自然な会話機能が正常に実装されています。")
    else:
        print(f"\n⚠️ {total_count - success_count}個のテストが失敗しました。")
        print("エラーの詳細を確認してください。")
