# streamlit_app.py - シンプル版
import streamlit as st
import os

def main():
    st.set_page_config(
        page_title="🔧 キャンピングカー修理チャットボット",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 キャンピングカー修理チャットボット")
    st.markdown("---")
    
    # 簡単なチャットボットUI
    st.markdown("### 💬 修理について質問してください")
    
    # チャット入力
    user_input = st.text_input("質問を入力してください:", placeholder="例: バッテリーが上がらない")
    
    if st.button("送信"):
        if user_input:
            st.success(f"質問: {user_input}")
            st.info("申し訳ございません。現在、AI機能は準備中です。")
        else:
            st.warning("質問を入力してください。")
    
    # よくある質問
    st.markdown("### ❓ よくある質問")
    faqs = [
        "バッテリーが上がらない",
        "エアコンが効かない", 
        "水漏れがする",
        "ドアが開かない"
    ]
    
    for faq in faqs:
        if st.button(f"Q: {faq}", key=faq):
            st.info(f"「{faq}」についての回答を準備中です。")

if __name__ == "__main__":
    main()