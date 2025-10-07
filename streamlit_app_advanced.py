# streamlit_app_advanced.py - 高度版UI
import streamlit as st
import os
from conversation_memory import NaturalConversationManager

def main():
    st.set_page_config(
        page_title="🔧 キャンピングカー修理チャットボット",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # カスタムCSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .mode-selector {
        display: flex;
        gap: 10px;
        margin-bottom: 2rem;
    }
    .quick-actions {
        display: flex;
        gap: 10px;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    .chat-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        min-height: 400px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <h1>🔧 キャンピングカー修理チャットボット</h1>
        <p>AI診断 + RAG検索 + リアルタイム情報 + 専門知識 = 修理支援</p>
    </div>
    """, unsafe_allow_html=True)
    
    # モード選択
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        chat_mode = st.button("🤖 統合チャット", key="chat")
    with col2:
        diagnostic_mode = st.button("🔍 症状診断", key="diagnostic")
    with col3:
        repair_mode = st.button("🛠️ 修理検索", key="repair")
    with col4:
        cost_mode = st.button("🔧 修理アドバイス", key="cost")
    
    # クイックアクション
    st.markdown("### ⚡ クイックアクション")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("バッテリー上がり"):
            st.session_state.quick_message = "バッテリーが上がりません"
    with col2:
        if st.button("トイレ詰まり"):
            st.session_state.quick_message = "トイレが詰まりました"
    with col3:
        if st.button("エアコン故障"):
            st.session_state.quick_message = "エアコンが効きません"
    with col4:
        if st.button("雨漏り"):
            st.session_state.quick_message = "雨漏りがします"
    with col5:
        if st.button("費用相談"):
            st.session_state.quick_message = "修理費用を知りたい"
    
    # 会話履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "🔧 キャンピングカー修理チャットボットにようこそ！\n修理について何でもお聞きください。AI診断、詳細検索、費用相談など、あらゆる機能を統合しています。"
            }
        ]
    
    # 関連ブログセクション
    with st.expander("📚 関連ブログ"):
        st.markdown("""
        - 🔋 [バッテリー・バッテリーの故障と修理方法](https://camper-repair.net/blog/repair1/)
        - 🛠️ [基本修理・キャンピングカー修理の基本](https://camper-repair.net/blog/risk1/)
        - 🔍 [定期点検・定期点検とメンテナンス](https://camper-repair.net/battery-selection/)
        """)
    
    # チャットコンテナ
    with st.container():
        st.markdown("### 💬 チャット")
        
        # メッセージ履歴の表示
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # クイックメッセージの処理
        if hasattr(st.session_state, 'quick_message'):
            user_message = st.session_state.quick_message
            del st.session_state.quick_message
            
            # ユーザーメッセージを追加
            st.session_state.messages.append({"role": "user", "content": user_message})
            
            # AI応答を生成
            try:
                # 自然な会話管理を使用
                conversation_manager = NaturalConversationManager()
                ai_response = conversation_manager.generate_natural_response(user_message)
                
                # AI応答を追加
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # ページを再読み込み
                st.rerun()
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
        
        # チャット入力
        if prompt := st.chat_input("修理について質問してください..."):
            # ユーザーメッセージを追加
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # AI応答を生成
            with st.spinner("AIが回答を生成中..."):
                try:
                    conversation_manager = NaturalConversationManager()
                    ai_response = conversation_manager.generate_natural_response(prompt)
                    
                    # AI応答を追加
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"申し訳ございません。エラーが発生しました: {e}"
                    })
            
            # ページを再読み込み
            st.rerun()

if __name__ == "__main__":
    main()