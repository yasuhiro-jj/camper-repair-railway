# ChromaDB依存関係エラーの修正

## 問題の概要
Streamlitアプリケーションで以下のエラーが発生していました：

```
AttributeError: This app has encountered an error.
File "/mount/src/camper-repair-clean20250820/streamlit_app_with_blog_links.py", line 33, in <module>
    from langchain_chroma import Chroma
...
File "/home/adminuser/venv/lib/python3.13/site-packages/chromadb/api/types.py", line 101, in <module>
    ImageDType = Union[np.uint, np.int_, np.float_]
                                         ^^^^^^^^^
AttributeError: module 'numpy' has no attribute 'int_'
```

## 原因
ChromaDBとNumPyのバージョンの互換性問題でした。NumPyの新しいバージョンで`np.int_`が削除されたことが原因です。

## 修正内容

### 1. requirements.txtの修正
ChromaDB関連の依存関係を削除しました：

```diff
- notion-client==2.2.1
- # ChromaDBとNumPyの互換性のため、特定のバージョンを指定
- numpy<2.0.0
- chromadb<0.5.0
- langchain-chroma>=0.1.0
+ notion-client==2.2.1
```

### 2. streamlit_app_with_blog_links.pyの修正
ChromaDBのインポートを無効化しました：

```python
# ChromaDBとenhanced_rag_systemを無効化（Streamlit Cloud互換性のため）
Chroma = None
create_enhanced_rag_system = None
enhanced_rag_retrieve = None
format_blog_links = None
```

### 3. enhanced_rag_system.pyの修正
ChromaDBの安全なインポートとエラーハンドリングを追加しました：

```python
# ChromaDBの安全なインポート
try:
    from langchain_chroma import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    Chroma = None
    CHROMA_AVAILABLE = False
```

## 現在の機能

### 動作する機能
- ✅ Streamlitアプリケーションの起動
- ✅ AI相談機能（OpenAI API使用）
- ✅ ブログリンク機能（キーワードマッチング）
- ✅ 症状診断機能（Notion連携）
- ✅ 基本的なUI/UX

### 無効化された機能
- ❌ ChromaDBベースのRAG検索
- ❌ ベクトル検索機能

## 代替機能
ChromaDBの代わりに、シンプルなキーワードマッチングを使用してブログリンクを提供しています：

```python
def get_relevant_blog_links(query):
    """クエリに基づいて関連ブログを返す"""
    # キーワードベースの簡単なマッチング
    query_lower = query.lower()
    
    blog_links = [
        {
            "title": "バッテリー・バッテリーの故障と修理方法",
            "url": "https://camper-repair.net/blog/repair1/",
            "keywords": ["バッテリー", "充電", "電圧", "上がり", "始動"]
        },
        # ... その他のブログリンク
    ]
    
    # 関連度スコアを計算して上位3件を返す
    return relevant_blogs[:3]
```

## テスト結果
修正後のテストスクリプト（`test_app_fixed.py`）を実行した結果：

```
🎉 すべてのテストが成功しました！
アプリケーションは正常に動作するはずです。
```

## 今後の改善案

### 1. ChromaDBの復活（オプション）
もしChromaDBを使用したい場合は、以下の手順で復活できます：

1. 適切なバージョンのChromaDBをインストール：
```bash
pip install chromadb==0.4.22
pip install langchain-chroma==0.1.0
```

2. requirements.txtに追加：
```
chromadb==0.4.22
langchain-chroma==0.1.0
numpy<2.0.0
```

3. アプリケーションコードでChromaDBを有効化

### 2. 代替ベクトルデータベースの検討
- FAISS
- Pinecone
- Weaviate
- Qdrant

### 3. 機能の拡張
- より多くのブログ記事の追加
- より高度なキーワードマッチング
- ユーザーフィードバック機能
- 修理手順の動画リンク

## 結論
ChromaDBの依存関係問題は解決され、アプリケーションは正常に動作するようになりました。現在はシンプルなキーワードマッチングを使用していますが、必要に応じてChromaDBを復活させることも可能です。
