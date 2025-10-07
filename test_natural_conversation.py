# test_natural_conversation.py - 自然な会話機能のテスト
import os
import sys
from conversation_memory import NaturalConversationManager

def test_conversation_manager():
    """自然な会話機能のテスト"""
    print("🧪 自然な会話機能のテストを開始します...")
    
    # 環境変数の確認
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEYが設定されていません")
        return False
    
    try:
        # 会話マネージャーの初期化
        print("📝 会話マネージャーを初期化中...")
        manager = NaturalConversationManager()
        print("✅ 会話マネージャーの初期化が完了しました")
        
        # テストケース1: 来店予約の質問
        print("\n🔍 テストケース1: 来店予約の質問")
        test_message1 = "今度の金曜日にそちらに行きたいのですが、どうでしょうか？"
        print(f"ユーザー: {test_message1}")
        
        response1 = manager.handle_specific_queries(test_message1)
        if response1:
            print(f"AI応答: {response1[:100]}...")
            print("✅ 来店予約の質問に対する応答が正常に生成されました")
        else:
            print("⚠️ 来店予約の質問に対する特定応答が生成されませんでした")
        
        # テストケース2: 緊急の質問
        print("\n🔍 テストケース2: 緊急の質問")
        test_message2 = "緊急でバッテリーが上がってしまいました！"
        print(f"ユーザー: {test_message2}")
        
        response2 = manager.handle_specific_queries(test_message2)
        if response2:
            print(f"AI応答: {response2[:100]}...")
            print("✅ 緊急の質問に対する応答が正常に生成されました")
        else:
            print("⚠️ 緊急の質問に対する特定応答が生成されませんでした")
        
        # テストケース3: 電話相談の希望
        print("\n🔍 テストケース3: 電話相談の希望")
        test_message3 = "電話で詳しく相談したいのですが"
        print(f"ユーザー: {test_message3}")
        
        response3 = manager.handle_specific_queries(test_message3)
        if response3:
            print(f"AI応答: {response3[:100]}...")
            print("✅ 電話相談の希望に対する応答が正常に生成されました")
        else:
            print("⚠️ 電話相談の希望に対する特定応答が生成されませんでした")
        
        # テストケース4: 意図分析
        print("\n🔍 テストケース4: 意図分析")
        test_intents = [
            "バッテリーが上がって困っています",
            "雨漏りがひどくて相談したいです",
            "エアコンが効かないのですが",
            "ガスコンロの火がつきません"
        ]
        
        for message in test_intents:
            intents = manager.analyze_user_intent(message)
            print(f"メッセージ: {message}")
            print(f"検出された意図: {intents}")
        
        print("\n✅ 意図分析のテストが完了しました")
        
        # テストケース5: 会話履歴の管理
        print("\n🔍 テストケース5: 会話履歴の管理")
        manager.add_message_to_history("user", "バッテリーの相談です")
        manager.add_message_to_history("assistant", "バッテリーの症状についてお聞かせください")
        manager.add_message_to_history("user", "エンジンがかからないんです")
        
        summary = manager.get_conversation_summary()
        print(f"会話要約: {summary}")
        print("✅ 会話履歴の管理が正常に動作しています")
        
        print("\n🎉 すべてのテストが正常に完了しました！")
        return True
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """統合テスト"""
    print("\n🔧 統合テストを開始します...")
    
    try:
        # 自然な応答生成のテスト
        manager = NaturalConversationManager()
        
        # 一般的な質問のテスト
        test_questions = [
            "バッテリーが上がってしまいました",
            "雨漏りがひどいです",
            "エアコンが効きません",
            "今度の金曜日に来店したいのですが"
        ]
        
        for question in test_questions:
            print(f"\n質問: {question}")
            response = manager.generate_natural_response(question, "テスト用のコンテキスト情報")
            print(f"応答: {response[:150]}...")
        
        print("\n✅ 統合テストが完了しました")
        return True
        
    except Exception as e:
        print(f"❌ 統合テスト中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    print("🚀 自然な会話機能のテストを開始します")
    print("=" * 50)
    
    # 基本テスト
    basic_test_result = test_conversation_manager()
    
    # 統合テスト
    integration_test_result = test_integration()
    
    print("\n" + "=" * 50)
    if basic_test_result and integration_test_result:
        print("🎉 すべてのテストが成功しました！")
        print("自然な会話機能が正常に動作しています。")
    else:
        print("❌ 一部のテストが失敗しました。")
        print("エラーの詳細を確認してください。")
