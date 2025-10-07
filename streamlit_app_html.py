# streamlit_app_html.py - HTML版をStreamlit Cloudでデプロイ
import streamlit as st
import os

def main():
    st.set_page_config(
        page_title="🔧 キャンピングカー修理チャットボット",
        page_icon="🔧",
        layout="wide"
    )
    
    # HTMLファイルのパス
    html_file_path = "templates/unified_chatbot.html"
    
    # HTMLファイルが存在するかチェック
    if os.path.exists(html_file_path):
        # HTMLファイルを読み込み
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # HTMLを表示
        st.components.v1.html(html_content, height=800, scrolling=True)
    else:
        st.error(f"HTMLファイルが見つかりません: {html_file_path}")
        st.info("templates/unified_chatbot.htmlファイルが存在することを確認してください。")

if __name__ == "__main__":
    main()
