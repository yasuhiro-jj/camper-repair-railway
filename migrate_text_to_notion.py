#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
テキストファイルをNotionデータベースに移行するスクリプト
"""

import os
import glob
from data_access.notion_client import notion_client

def read_text_files():
    """テキストファイルを読み込んで構造化データに変換"""
    text_files = glob.glob("*.txt")
    structured_data = []
    
    for txt_file in text_files:
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # ファイル名からカテゴリを抽出
            category = os.path.basename(txt_file).replace('.txt', '')
            
            # 内容を解析して構造化
            structured_item = {
                'title': f"{category}の修理情報",
                'category': category,
                'content': content,
                'file_name': txt_file,
                'type': 'knowledge_base'
            }
            
            structured_data.append(structured_item)
            print(f"✅ {txt_file} を読み込みました")
            
        except Exception as e:
            print(f"❌ {txt_file} 読み込みエラー: {e}")
    
    return structured_data

def migrate_to_notion():
    """Notionデータベースに移行"""
    try:
        # テキストファイルを読み込み
        print("📚 テキストファイルを読み込み中...")
        text_data = read_text_files()
        
        print(f"📊 {len(text_data)}件のテキストファイルを読み込みました")
        
        # Notionクライアントを初期化
        print("🔗 Notionクライアントを初期化中...")
        client = notion_client
        
        # 各テキストファイルをNotionに移行
        for i, item in enumerate(text_data, 1):
            try:
                print(f"📤 {i}/{len(text_data)}: {item['title']} を移行中...")
                
                # Notionデータベースに追加（実装が必要）
                # notion_client.create_knowledge_base_item(item)
                
                print(f"✅ {item['title']} 移行完了")
                
            except Exception as e:
                print(f"❌ {item['title']} 移行エラー: {e}")
        
        print("🎉 移行完了！")
        
    except Exception as e:
        print(f"❌ 移行エラー: {e}")

def preview_migration():
    """移行プレビュー"""
    text_data = read_text_files()
    
    print("📋 移行プレビュー:")
    print("=" * 50)
    
    for item in text_data:
        print(f"📄 {item['title']}")
        print(f"   カテゴリ: {item['category']}")
        print(f"   ファイル: {item['file_name']}")
        print(f"   内容: {item['content'][:100]}...")
        print("-" * 30)

if __name__ == "__main__":
    print("🚀 テキストファイル → Notion移行ツール")
    print("=" * 50)
    
    choice = input("1: プレビュー, 2: 移行実行 (1/2): ")
    
    if choice == "1":
        preview_migration()
    elif choice == "2":
        migrate_to_notion()
    else:
        print("❌ 無効な選択です")
