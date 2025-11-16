#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromaDB管理モジュール（ロードマップ準拠）
RAGシステムのベクトル検索機能をモジュール化
"""

import os
import glob
import shutil
from typing import List, Dict, Optional, Any
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# ChromaDBの安全なインポート
try:
    from langchain_chroma import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    Chroma = None
    CHROMA_AVAILABLE = False
    print("⚠️ ChromaDBが利用できません。langchain-chromaとchromadbをインストールしてください。")


class ChromaManager:
    """ChromaDB管理クラス（ロードマップ準拠）"""
    
    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        ChromaManagerを初期化
        
        Args:
            persist_dir: ChromaDBの永続化ディレクトリ（デフォルト: ./chroma_db）
            collection_name: コレクション名（デフォルト: camper_repair_knowledge）
            openai_api_key: OpenAI APIキー（環境変数から取得可能）
        """
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self.collection_name = collection_name or os.getenv("RAG_COLLECTION", "camper_repair_knowledge")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定してください。")
        
        self.embeddings_model = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.db = None
    
    def initialize(self, force_rebuild: bool = False) -> bool:
        """
        ChromaDBを初期化
        
        Args:
            force_rebuild: 既存のDBを強制的に再構築するか
        
        Returns:
            bool: 初期化成功時True
        """
        if not CHROMA_AVAILABLE:
            print("❌ ChromaDBが利用できません")
            return False
        
        # 既存のDBがある場合の処理
        if os.path.exists(self.persist_dir):
            if force_rebuild:
                print(f"🔄 既存のChromaDBを削除中: {self.persist_dir}")
                try:
                    shutil.rmtree(self.persist_dir)
                    print("✅ 既存のDBを削除しました")
                except Exception as e:
                    print(f"⚠️ DB削除エラー: {e}")
                    print("💡 既存のDBを使用して続行します")
            else:
                # 既存のDBを読み込む
                try:
                    print(f"🔄 既存のChromaDBを読み込み中: {self.persist_dir}")
                    self.db = Chroma(
                        persist_directory=self.persist_dir,
                        embedding_function=self.embeddings_model,
                        collection_name=self.collection_name
                    )
                    print("✅ 既存のChromaDBを読み込みました")
                    return True
                except Exception as e:
                    print(f"⚠️ 既存DB読み込みエラー: {e}")
                    print("🔄 新しいDBを作成します...")
        
        # 新しいDBを作成
        try:
            documents = self._load_documents()
            if not documents:
                print("⚠️ ドキュメントがありません。空のDBを作成します。")
                self.db = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings_model,
                    collection_name=self.collection_name
                )
            else:
                print(f"📚 {len(documents)}件のドキュメントでChromaDBを作成中...")
                self.db = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings_model,
                    persist_directory=self.persist_dir,
                    collection_name=self.collection_name
                )
                print("✅ ChromaDBを作成しました")
            return True
        except Exception as e:
            print(f"❌ ChromaDB作成エラー: {e}")
            return False
    
    def _load_documents(self) -> List[Document]:
        """
        ドキュメントを読み込む（既存のenhanced_rag_system.pyのロジックを参考）
        
        Returns:
            List[Document]: 読み込んだドキュメントのリスト
        """
        documents = []
        main_path = os.path.dirname(os.path.abspath(__file__))
        
        # PDFドキュメントを追加
        pdf_path = os.path.join(main_path, "キャンピングカー修理マニュアル.pdf")
        if os.path.exists(pdf_path):
            try:
                loader = PyPDFLoader(pdf_path)
                pdf_docs = loader.load()
                for doc in pdf_docs:
                    if not isinstance(doc.page_content, str):
                        doc.page_content = str(doc.page_content)
                    doc.metadata["source_type"] = "manual"
                    doc.metadata["url"] = "キャンピングカー修理マニュアル.pdf"
                    documents.append(doc)
                print(f"✅ PDFドキュメント {len(pdf_docs)} 件を読み込みました")
            except Exception as e:
                print(f"⚠️ PDF読み込みエラー: {e}")
        
        # テキストファイルの読み込み
        txt_files = glob.glob(os.path.join(main_path, "*.txt"))
        for txt_file in txt_files:
            try:
                loader = TextLoader(txt_file, encoding='utf-8')
                txt_docs = loader.load()
                for doc in txt_docs:
                    if not isinstance(doc.page_content, str):
                        doc.page_content = str(doc.page_content)
                    doc.metadata["source_type"] = "text_file"
                    doc.metadata["url"] = os.path.basename(txt_file)
                    doc.metadata["title"] = os.path.basename(txt_file).replace('.txt', '')
                    documents.append(doc)
                print(f"✅ テキストファイル {os.path.basename(txt_file)} を読み込みました")
            except Exception as e:
                print(f"⚠️ テキストファイル {txt_file} 読み込みエラー: {e}")
        
        return documents
    
    def upsert_docs(self, docs: List[Document], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        ドキュメントを登録・更新（ロードマップ準拠）
        
        Args:
            docs: 登録するドキュメントのリスト
            metadata: 追加メタデータ（各ドキュメントにマージ）
        
        Returns:
            bool: 成功時True
        """
        if not self.db:
            print("❌ ChromaDBが初期化されていません")
            return False
        
        try:
            # メタデータをマージ
            if metadata:
                for doc in docs:
                    doc.metadata.update(metadata)
            
            # ChromaDBに追加（既存のIDがある場合は更新）
            self.db.add_documents(docs)
            print(f"✅ {len(docs)}件のドキュメントを登録しました")
            return True
        except Exception as e:
            print(f"❌ ドキュメント登録エラー: {e}")
            return False
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        RAG検索を実行（ロードマップ準拠）
        
        Args:
            query: 検索クエリ
            max_results: 最大結果数
            score_threshold: 類似度スコアのしきい値（オプション）
        
        Returns:
            Dict: {
                "manual_content": str,
                "text_file_content": str,
                "blog_links": List[Dict],
                "scores": List[float]
            }
        """
        if not self.db:
            return {
                "manual_content": "",
                "text_file_content": "",
                "blog_links": [],
                "scores": []
            }
        
        try:
            # similarity_search_with_scoreを使用してスコアも取得
            # ChromaDBの距離（distance）は小さいほど類似度が高い
            # スコアに変換: score = 1 / (1 + distance) → 0.0-1.0の範囲
            try:
                docs_with_scores = self.db.similarity_search_with_score(query, k=max_results)
                docs = []
                scores = []
                
                for doc, distance in docs_with_scores:
                    # 距離を類似度スコアに変換（Phase 3対応）
                    # distance = 0.0 → score = 1.0（完全一致）
                    # distance = 1.0 → score = 0.5（中程度）
                    # distance = 2.0 → score = 0.33（低い）
                    similarity_score = 1.0 / (1.0 + distance)
                    
                    if score_threshold is None or similarity_score >= score_threshold:
                        docs.append(doc)
                        scores.append(similarity_score)
            except AttributeError:
                # similarity_search_with_scoreが利用できない場合のフォールバック
                docs = self.db.similarity_search(query, k=max_results)
                scores = [0.5] * len(docs)  # デフォルトスコア
            
            # 結果を整理
            manual_content = []
            text_file_content = []
            blog_links = []
            
            for i, doc in enumerate(docs):
                source_type = doc.metadata.get("source_type", "")
                score = scores[i] if i < len(scores) else 0.0
                
                if source_type == "manual":
                    manual_content.append(doc.page_content)
                elif source_type == "text_file":
                    text_file_content.append(doc.page_content)
                elif source_type == "blog":
                    tags_str = doc.metadata.get("tags", "")
                    tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
                    
                    blog_links.append({
                        "title": doc.metadata.get("title", "ブログ記事"),
                        "url": doc.metadata.get("url", "#"),
                        "content": doc.page_content,
                        "tags": tags,
                        "score": score
                    })
            
            return {
                "manual_content": "\n".join(manual_content),
                "text_file_content": "\n".join(text_file_content),
                "blog_links": blog_links,
                "scores": scores
            }
        except Exception as e:
            print(f"❌ RAG検索エラー: {e}")
            return {
                "manual_content": "",
                "text_file_content": "",
                "blog_links": [],
                "scores": []
            }
    
    def rebuild(self, source: str = "notion") -> bool:
        """
        RAGシステムを再構築（ロードマップ準拠: /rag/rebuild）
        
        Args:
            source: データソース（"notion", "text_files", "all"）
        
        Returns:
            bool: 成功時True
        """
        print(f"🔄 RAGシステムを再構築中（ソース: {source}）...")
        
        # 既存のDBを削除して再構築
        if os.path.exists(self.persist_dir):
            try:
                shutil.rmtree(self.persist_dir)
                print("✅ 既存のDBを削除しました")
            except Exception as e:
                print(f"⚠️ DB削除エラー: {e}")
        
        # 再初期化
        return self.initialize(force_rebuild=True)
    
    def get_db(self) -> Optional[Chroma]:
        """
        ChromaDBインスタンスを取得
        
        Returns:
            Chroma: ChromaDBインスタンス、未初期化時はNone
        """
        return self.db


# グローバルインスタンス（既存コードとの互換性のため）
_chroma_manager_instance = None


def get_chroma_manager(
    persist_dir: Optional[str] = None,
    collection_name: Optional[str] = None,
    openai_api_key: Optional[str] = None
) -> ChromaManager:
    """
    グローバルChromaManagerインスタンスを取得（シングルトンパターン）
    
    Returns:
        ChromaManager: ChromaManagerインスタンス
    """
    global _chroma_manager_instance
    
    if _chroma_manager_instance is None:
        _chroma_manager_instance = ChromaManager(
            persist_dir=persist_dir,
            collection_name=collection_name,
            openai_api_key=openai_api_key
        )
    
    return _chroma_manager_instance

