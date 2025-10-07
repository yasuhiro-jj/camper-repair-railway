#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('.')

def test_search_system():
    """検索システムの動作をテスト"""
    print("=== 検索システム動作テスト ===\n")
    
    try:
        from repair_center_api import search_with_rag, search_repair_advice
        print("✅ モジュールのインポート成功")
    except Exception as e:
        print(f"❌ モジュールのインポート失敗: {e}")
        return
    
    # テストクエリ
    test_queries = [
        'FFヒーター 点火しない',
        'バッテリー 充電できない', 
        '水道ポンプ 動かない',
        'ガスコンロ 火がつかない',
        '冷蔵庫 冷えない'
    ]
    
    for query in test_queries:
        print(f"--- クエリ: {query} ---")
        
        try:
            # RAG検索テスト
            rag_result = search_with_rag(query)
            rag_count = len(rag_result) if rag_result else 0
            print(f"RAG検索結果: {rag_count}件")
            
            # テキスト検索テスト
            text_result = search_repair_advice(query)
            text_count = len(text_result)
            print(f"テキスト検索結果: {text_count}件")
            
            if text_result:
                first_result = text_result[0]
                print(f"最初の結果:")
                print(f"  タイトル: {first_result.get('title', 'N/A')}")
                print(f"  カテゴリ: {first_result.get('category', 'N/A')}")
                print(f"  スコア: {first_result.get('score', 'N/A')}")
                print(f"  ファイル名: {first_result.get('filename', 'N/A')}")
            else:
                print("  結果なし")
                
        except Exception as e:
            print(f"❌ 検索エラー: {e}")
        
        print()

def test_rag_database():
    """RAGデータベースの状態を確認"""
    print("=== RAGデータベース状態確認 ===\n")
    
    try:
        from repair_center_api import rag_db
        if rag_db:
            print("✅ RAGデータベース: 初期化済み")
            # データベースの内容を確認
            try:
                # 簡単な検索テスト
                results = rag_db.similarity_search("テスト", k=1)
                print(f"✅ データベース検索テスト: {len(results)}件の結果")
            except Exception as e:
                print(f"❌ データベース検索エラー: {e}")
        else:
            print("❌ RAGデータベース: 初期化されていない")
    except Exception as e:
        print(f"❌ RAGデータベース確認エラー: {e}")

def test_text_files():
    """テキストファイルの存在確認"""
    print("=== テキストファイル確認 ===\n")
    
    text_files = [
        'FFヒーター.txt',
        'バッテリー.txt', 
        '水道ポンプ.txt',
        'ガスコンロ.txt',
        '冷蔵庫.txt'
    ]
    
    for filename in text_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename}: {size} bytes")
        else:
            print(f"❌ {filename}: ファイルが見つかりません")

if __name__ == "__main__":
    test_text_files()
    print()
    test_rag_database()
    print()
    test_search_system()
