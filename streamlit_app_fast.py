#!/usr/bin/env python
# -*- coding: utf-8 -*-
import streamlit as st
import os
import time
from functools import lru_cache

# 軽量化されたStreamlitアプリ
def main():
    st.set_page_config(
        page_title="キャンピングカー修理AI",
        page_icon="🚐",
        layout="wide"
    )
    
    # ヘッダー
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 8px; color: white; text-align: center; margin-bottom: 1rem;">
        <h1>🚐 キャンピングカー修理AI</h1>
        <p>AI搭載の修理アドバイスシステム</p>
    </div>
    """, unsafe_allow_html=True)
    
    # タブ
    tab1, tab2, tab3 = st.tabs(["💬 チャット相談", "🔍 診断フロー", "🔧 修理アドバイス"])
    
    with tab1:
        # チャット機能（軽量化）
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # チャット履歴
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # ユーザー入力
        if prompt := st.chat_input("修理について質問してください..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # AI回答（簡易版）
            with st.chat_message("assistant"):
                with st.spinner("AIが回答を生成中..."):
                    time.sleep(1)  # 簡易的な処理時間
                    response = f"「{prompt}」についての修理アドバイスを生成中です。詳細な回答は準備中です。"
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
    
    with tab2:
        st.markdown("### 🔍 診断フロー")
        st.info("診断機能は準備中です。")
    
    with tab3:
        st.markdown("### 🔧 修理アドバイス")
        st.info("修理アドバイス機能は準備中です。")

if __name__ == "__main__":
    main()
