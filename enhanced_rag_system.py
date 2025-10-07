#!/usr/bin/env python3
"""
ブログURLも含めた拡張RAGシステム
"""

import os
import glob
import shutil
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


def process_markdown_content(content, filename):
    """マークダウンテキストを構造化してRAGで活用しやすくする"""
    try:
        # ケース別の構造化処理
        if "トイレ" in filename:
            return process_toilet_content(content)
        elif "バッテリー" in filename:
            return process_battery_content(content)
        elif "サブバッテリー" in filename:
            return process_subbattery_content(content)
        elif "ドア" in filename or "窓" in filename:
            return process_door_window_content(content)
        else:
            return process_general_content(content)
    except Exception as e:
        print(f"Warning: マークダウン処理エラー ({filename}): {e}")
        return content

def process_toilet_content(content):
    """トイレ関連コンテンツの構造化"""
    # 元の構造を保持しつつ、ケース情報も抽出
    import re
    
    # ケースを分割
    cases = re.split(r'## \[Case ([^\]]+)\]', content)
    structured_content = []
    
    if len(cases) > 1:  # ケースが見つかった場合
        for i in range(1, len(cases), 2):
            if i + 1 < len(cases):
                case_id = cases[i]
                case_content = cases[i + 1]
                
                # 症状と解決策を抽出
                symptoms = extract_symptoms(case_content)
                solutions = extract_solutions(case_content)
                costs = extract_costs(case_content)
                
                structured_case = f"""
ケースID: {case_id}
症状: {symptoms}
解決策: {solutions}
費用目安: {costs}
詳細: {case_content}
"""
                structured_content.append(structured_case)
        
        # ケース情報と元の内容を組み合わせ
        return "\n".join(structured_content) + "\n\n---\n\n" + content
    else:
        # ケースが見つからない場合は元の内容をそのまま返す
        return content

def process_battery_content(content):
    """バッテリー関連コンテンツの構造化"""
    # 元の構造を保持しつつ、ケース情報も抽出
    import re
    
    # ケースを分割
    cases = re.split(r'## \[Case ([^\]]+)\]', content)
    structured_content = []
    
    if len(cases) > 1:  # ケースが見つかった場合
        for i in range(1, len(cases), 2):
            if i + 1 < len(cases):
                case_id = cases[i]
                case_content = cases[i + 1]
                
                # バッテリー特有の情報を抽出
                voltage_info = extract_voltage_info(case_content)
                charging_info = extract_charging_info(case_content)
                maintenance_info = extract_maintenance_info(case_content)
                
                structured_case = f"""
ケースID: {case_id}
電圧情報: {voltage_info}
充電情報: {charging_info}
メンテナンス情報: {maintenance_info}
詳細: {case_content}
"""
                structured_content.append(structured_case)
        
        # ケース情報と元の内容を組み合わせ
        return "\n".join(structured_content) + "\n\n---\n\n" + content
    else:
        # ケースが見つからない場合は元の内容をそのまま返す
        return content

def process_subbattery_content(content):
    """サブバッテリー関連コンテンツの構造化"""
    import re
    
    # ケースを分割
    cases = re.split(r'## \[Case ([^\]]+)\]', content)
    structured_content = []
    
    for i in range(1, len(cases), 2):
        if i + 1 < len(cases):
            case_id = cases[i]
            case_content = cases[i + 1]
            
            # サブバッテリー特有の情報を抽出
            capacity_info = extract_capacity_info(case_content)
            charging_system = extract_charging_system(case_content)
            usage_pattern = extract_usage_pattern(case_content)
            
            structured_case = f"""
ケースID: {case_id}
容量情報: {capacity_info}
充電システム: {charging_system}
使用パターン: {usage_pattern}
詳細: {case_content}
"""
            structured_content.append(structured_case)
    
    return "\n".join(structured_content)


def process_door_window_content(content):
    """ドア・窓関連コンテンツの構造化"""
    import re
    
    # DW-ケースを抽出
    cases = re.findall(r'### DW-(\d+): ([^\n]+)\n\*\*症状\*\*: ([^\n]+)\n\*\*原因\*\*: ([^\n]+)\n\*\*対処法\*\*: ([^\n]+)\n\*\*修理時間\*\*: ([^\n]+)\n\*\*費用目安\*\*: ([^\n]+)', content)
    
    structured_cases = []
    for case in cases:
        case_id, title, symptoms, cause, solution, time, cost = case
        structured_cases.append({
            'case_id': f'DW-{case_id}',
            'title': title,
            'symptoms': symptoms,
            'cause': cause,
            'solution': solution,
            'time': time,
            'cost': cost
        })
    
    # 構造化されたコンテンツを作成
    structured_content = f"# ドア・窓の開閉不良 - 修理ケース一覧\n\n"
    
    for case in structured_cases:
        structured_content += f"## {case['case_id']}: {case['title']}\n"
        structured_content += f"**症状**: {case['symptoms']}\n"
        structured_content += f"**原因**: {case['cause']}\n"
        structured_content += f"**対処法**: {case['solution']}\n"
        structured_content += f"**修理時間**: {case['time']}\n"
        structured_content += f"**費用目安**: {case['cost']}\n\n"
    
    # 元のコンテンツも含める
    structured_content += "\n---\n\n" + content
    
    return structured_content


def process_general_content(content):
    """一般的なコンテンツの構造化"""
    # 基本的な構造化処理
    import re
    
    # 見出しを抽出
    headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
    
    # リスト項目を抽出
    list_items = re.findall(r'^[-*+]\s+(.+)$', content, re.MULTILINE)
    
    structured_content = f"""
見出し: {' | '.join(headers)}
リスト項目: {' | '.join(list_items)}
内容: {content}
"""
    return structured_content


def extract_symptoms(content):
    """症状を抽出"""
    import re
    symptoms = re.findall(r'症状[：:]\s*(.+?)(?=\n|$)', content, re.DOTALL)
    return ' | '.join(symptoms) if symptoms else "症状情報なし"


def extract_solutions(content):
    """解決策を抽出"""
    import re
    solutions = re.findall(r'解決[策法][：:]\s*(.+?)(?=\n|$)', content, re.DOTALL)
    return ' | '.join(solutions) if solutions else "解決策情報なし"


def extract_costs(content):
    """費用情報を抽出"""
    import re
    costs = re.findall(r'(\d+[,，]\d+円|\d+円)', content)
    return ' | '.join(costs) if costs else "費用情報なし"


def extract_voltage_info(content):
    """電圧情報を抽出"""
    import re
    voltages = re.findall(r'(\d+\.\d+V|\d+V)', content)
    return ' | '.join(voltages) if voltages else "電圧情報なし"


def extract_charging_info(content):
    """充電情報を抽出"""
    import re
    charging = re.findall(r'(充電|チャージ|アイソレーター|DC-DC)', content)
    return ' | '.join(charging) if charging else "充電情報なし"


def extract_maintenance_info(content):
    """メンテナンス情報を抽出"""
    import re
    maintenance = re.findall(r'(点検|清掃|交換|メンテナンス)', content)
    return ' | '.join(maintenance) if maintenance else "メンテナンス情報なし"


def extract_capacity_info(content):
    """容量情報を抽出"""
    import re
    capacity = re.findall(r'(\d+Ah|\d+W|\d+Wh)', content)
    return ' | '.join(capacity) if capacity else "容量情報なし"


def extract_charging_system(content):
    """充電システム情報を抽出"""
    import re
    system = re.findall(r'(アイソレーター|DC-DC|リレー|ヒューズ)', content)
    return ' | '.join(system) if system else "充電システム情報なし"


def extract_usage_pattern(content):
    """使用パターン情報を抽出"""
    import re
    usage = re.findall(r'(冷蔵庫|エアコン|テレビ|照明|24時間)', content)
    return ' | '.join(usage) if usage else "使用パターン情報なし"


def create_enhanced_rag_system():
    """ブログURLも含めたRAGシステムを作成"""
    
    # 既存のChromaデータベースを削除（安全な方法）
    chroma_db_path = "./chroma_db"
    if os.path.exists(chroma_db_path):
        print("既存のChromaデータベースを削除中...")
        try:
            # プロセスが使用中の場合はスキップ
            import time
            time.sleep(1)  # 少し待機
            shutil.rmtree(chroma_db_path)
            print("✅ 既存のデータベースを削除しました")
        except Exception as e:
            print(f"⚠️ データベース削除エラー: {e}")
            print("💡 既存のデータベースを使用して続行します")
    
    # 埋め込みモデルを設定
    embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # 既存のデータベースがある場合は再利用を試行
    if os.path.exists(chroma_db_path):
        try:
            print("🔄 既存のデータベースを読み込み中...")
            db = Chroma(persist_directory=chroma_db_path, embedding_function=embeddings_model)
            print("✅ 既存のデータベースを読み込みました")
            return db
        except Exception as e:
            print(f"⚠️ 既存データベース読み込みエラー: {e}")
            print("🔄 新しいデータベースを作成します...")
    
    # ドキュメントを準備
    documents = []

    # PDFドキュメントを追加
    main_path = os.path.dirname(os.path.abspath(__file__))
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
                
                # マークダウンコンテンツの構造化処理
                processed_content = process_markdown_content(doc.page_content, os.path.basename(txt_file))
                
                doc.page_content = processed_content
                doc.metadata["source_type"] = "text_file"
                doc.metadata["url"] = os.path.basename(txt_file)
                doc.metadata["title"] = os.path.basename(txt_file).replace('.txt', '')
                doc.metadata["content_type"] = "markdown_structured"
                documents.append(doc)
            print(f"✅ テキストファイル {os.path.basename(txt_file)} を読み込みました")
        except Exception as e:
            print(f"⚠️ テキストファイル {txt_file} 読み込みエラー: {e}")
    
    # ブログドキュメントを追加
    blog_documents = [
        {
            "title": "サブバッテリー完全ガイド",
            "content": "サブバッテリー、ディープサイクル、リチウムイオン、鉛バッテリー、容量選定、寿命、充電方法、バッテリー管理、放電深度、残量計、運用時間、バッテリー並列、直列接続、温度管理、メンテナンス、取り付け方法、電圧監視、車両改造、保安基準、交換目安",
            "url": "https://camper-repair.net/blog/risk1/",
            "tags": ["サブバッテリー", "完全ガイド", "容量選定", "寿命"]
        },
        {
            "title": "バッテリー・バッテリーの故障と修理方法",
            "content": "バッテリー故障、充電不良、電圧低下、始動不良、バッテリー交換、充電器故障、端子腐食、電解液不足、バッテリー診断、電圧測定、充電システム、アイソレーター、DC-DCコンバーター、バッテリー管理システム、BMS、リチウムイオンバッテリー、鉛バッテリー、AGMバッテリー、ディープサイクルバッテリー",
            "url": "https://camper-repair.net/blog/repair1/",
            "tags": ["バッテリー", "故障", "修理方法", "充電システム"]
        },
        {
            "title": "定期点検とメンテナンス",
            "content": "定期点検、メンテナンス、予防保全、点検項目、バッテリー点検、電装系点検、水回り点検、ガス系点検、エアコン点検、冷蔵庫点検、トイレ点検、給水システム、排水システム、ガス配管、電気配線、安全装置、消防設備、点検記録、メンテナンススケジュール",
            "url": "https://camper-repair.net/battery-selection/",
            "tags": ["定期点検", "メンテナンス", "予防保全", "点検項目"]
        }
    ]
    
    for blog in blog_documents:
        doc = Document(
            page_content=f"タイトル: {blog['title']}\n\n内容: {blog['content']}\n\nタグ: {', '.join(blog['tags'])}",
            metadata={
                "title": blog['title'],
                "url": blog['url'],
                "tags": ', '.join(blog['tags']),
                "source_type": "blog"
            }
        )
        documents.append(doc)
    
    print(f"✅ 総ドキュメント数: {len(documents)} 件")
    
    # ChromaDBが利用可能かチェック
    if not CHROMA_AVAILABLE:
        raise ImportError("ChromaDBが利用できません。langchain-chromaとchromadbをインストールしてください。")
    
    # 新しいデータベースを作成
    try:
        print("新しいChromaデータベースを作成中...")
        db = Chroma.from_documents(
            documents=documents, 
            embedding=embeddings_model,
            persist_directory=chroma_db_path
        )
        print("✅ Chromaデータベースを作成しました")
        return db
    except Exception as e:
        print(f"❌ Chromaデータベース作成エラー: {e}")
        return None


def enhanced_rag_retrieve(question: str, db, max_results: int = 5):
    """拡張RAG検索（ブログURLも含む）"""
    if db is None:
        return {
            "manual_content": "ChromaDBが利用できません。",
            "text_file_content": "テキストファイルが利用できません。",
            "blog_links": []
        }
    
    try:
        # similarity_searchを直接使用
        docs = db.similarity_search(question, k=max_results)
        
        # 結果を整理
        manual_content = []
        text_file_content = []
        blog_links = []
        
        for doc in docs:
            if doc.metadata.get("source_type") == "manual":
                manual_content.append(doc.page_content)
            elif doc.metadata.get("source_type") == "text_file":
                text_file_content.append(doc.page_content)
            elif doc.metadata.get("source_type") == "blog":
                tags_str = doc.metadata.get("tags", "")
                tags = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
                
                blog_links.append({
                    "title": doc.metadata.get("title", "ブログ記事"),
                    "url": doc.metadata.get("url", "#"),
                    "content": doc.page_content,
                    "tags": tags
                })
        
        return {
            "manual_content": "\n".join(manual_content),
            "text_file_content": "\n".join(text_file_content),
            "blog_links": blog_links
        }
    except Exception as e:
        print(f"❌ RAG検索エラー: {e}")
        return {
            "manual_content": "検索エラーが発生しました。",
            "text_file_content": "検索エラーが発生しました。",
            "blog_links": []
        }


def format_blog_links(blog_links, max_links: int = 3):
    """ブログリンクをフォーマット"""
    if not blog_links:
        return ""
    
    formatted_links = []
    for i, blog in enumerate(blog_links[:max_links]):
        formatted_links.append(f"• {blog['title']}: {blog['url']}")
    
    return "\n".join(formatted_links)


# 使用例
def create_notion_based_rag_system(use_text_files=False):
    """
    Notionデータベースベースの拡張RAGシステムを作成
    
    Args:
        use_text_files (bool): テキストファイルも含めるか（デフォルト: False）
    
    Returns:
        Chroma: ChromaDBインスタンス、エラー時はNone
    """
    
    # 既存のChromaデータベースのパス
    chroma_db_path = "./chroma_db"
    
    # 埋め込みモデルを設定
    embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # ドキュメントを準備
    documents = []
    
    # Notionからナレッジベースを取得
    print("🔄 Notionからナレッジベースデータを取得中...")
    try:
        from data_access.notion_client import notion_client
        print(f"🔍 Notionクライアント状態: {notion_client is not None}")
        if notion_client:
            print("🔍 Notionクライアントの初期化状況を確認中...")
            knowledge_items = notion_client.load_knowledge_base()
            print(f"📊 取得したナレッジベースアイテム数: {len(knowledge_items) if knowledge_items else 0}")
        else:
            print("❌ Notionクライアントが利用できません")
            knowledge_items = None
        
        if knowledge_items:
            for item in knowledge_items:
                # ドキュメント内容を構築
                content_parts = []
                
                # すべての値を文字列に変換してエラーを防止
                if item.get("title"):
                    content_parts.append(f"タイトル: {str(item['title'])}")
                
                if item.get("category"):
                    content_parts.append(f"カテゴリ: {str(item['category'])}")
                
                if item.get("content"):
                    content_parts.append(f"\n内容:\n{str(item['content'])}")
                
                # キーワードの処理（リストまたは文字列に対応）
                keywords = item.get("keywords")
                if keywords:
                    if isinstance(keywords, list):
                        keywords_str = ', '.join(str(k) for k in keywords if k)
                    else:
                        keywords_str = str(keywords)
                    if keywords_str:
                        content_parts.append(f"\nキーワード: {keywords_str}")
                
                # タグの処理（リストまたは文字列に対応）
                tags = item.get("tags")
                if tags:
                    if isinstance(tags, list):
                        tags_str = ', '.join(str(t) for t in tags if t)
                    else:
                        tags_str = str(tags)
                    if tags_str:
                        content_parts.append(f"\nタグ: {tags_str}")
                
                # 最低限のコンテンツがあることを確認
                if not content_parts:
                    content_parts.append("データなし")
                
                # Documentオブジェクトを作成
                doc = Document(
                    page_content="\n".join(content_parts),
                    metadata={
                        "title": str(item.get("title", "")),
                        "category": str(item.get("category", "")),
                        "url": str(item.get("url", "")),
                        "source_type": "notion_knowledge_base",
                        "notion_id": str(item.get("id", ""))
                    }
                )
                documents.append(doc)
            
            print(f"✅ Notionナレッジベース: {len(knowledge_items)}件を読み込みました")
        else:
            print("⚠️ Notionナレッジベースが空です")
    
    except ImportError as e:
        print(f"⚠️ Notionクライアントのインポートエラー: {e}")
    except Exception as e:
        print(f"⚠️ Notionデータ取得エラー: {e}")
        import traceback
        traceback.print_exc()
    
    # オプション: テキストファイルも含める
    if use_text_files:
        print("🔄 テキストファイルも読み込み中...")
        main_path = os.path.dirname(os.path.abspath(__file__))
        txt_files = glob.glob(os.path.join(main_path, "*.txt"))
        
        for txt_file in txt_files:
            try:
                loader = TextLoader(txt_file, encoding='utf-8')
                txt_docs = loader.load()
                
                for doc in txt_docs:
                    if not isinstance(doc.page_content, str):
                        doc.page_content = str(doc.page_content)
                    
                    # マークダウンコンテンツの構造化処理
                    processed_content = process_markdown_content(doc.page_content, os.path.basename(txt_file))
                    
                    doc.page_content = processed_content
                    doc.metadata["source_type"] = "text_file"
                    doc.metadata["url"] = os.path.basename(txt_file)
                    doc.metadata["title"] = os.path.basename(txt_file).replace('.txt', '')
                    doc.metadata["content_type"] = "markdown_structured"
                    documents.append(doc)
                
                print(f"✅ テキストファイル {os.path.basename(txt_file)} を読み込みました")
            except Exception as e:
                print(f"⚠️ テキストファイル {txt_file} 読み込みエラー: {e}")
    
    # 修理ケースもNotionから取得して追加
    print("🔄 Notionから修理ケースデータを取得中...")
    try:
        from data_access.notion_client import notion_client
        repair_cases = notion_client.load_repair_cases()
        
        if repair_cases:
            for case in repair_cases:
                # ドキュメント内容を構築
                content_parts = []
                
                # すべての値を文字列に変換してエラーを防止
                if case.get("title"):
                    content_parts.append(f"ケースID: {str(case['title'])}")
                
                if case.get("category"):
                    content_parts.append(f"カテゴリ: {str(case['category'])}")
                
                # 症状の処理（リストまたは文字列に対応）
                symptoms = case.get("symptoms")
                if symptoms:
                    if isinstance(symptoms, list):
                        symptoms_str = ', '.join(str(s) for s in symptoms if s)
                    else:
                        symptoms_str = str(symptoms)
                    if symptoms_str:
                        content_parts.append(f"症状: {symptoms_str}")
                
                if case.get("solution"):
                    content_parts.append(f"解決方法: {str(case['solution'])}")
                
                if case.get("cost_estimate"):
                    content_parts.append(f"費用見積もり: {str(case['cost_estimate'])}")
                
                if case.get("difficulty"):
                    content_parts.append(f"難易度: {str(case['difficulty'])}")
                
                # 最低限のコンテンツがあることを確認
                if not content_parts:
                    content_parts.append("ケース情報")
                
                # Documentオブジェクトを作成
                doc = Document(
                    page_content="\n".join(content_parts),
                    metadata={
                        "title": str(case.get("title", "")),
                        "category": str(case.get("category", "")),
                        "source_type": "notion_repair_case",
                        "notion_id": str(case.get("id", ""))
                    }
                )
                documents.append(doc)
            
            print(f"✅ Notion修理ケース: {len(repair_cases)}件を読み込みました")
        else:
            print("⚠️ Notion修理ケースが空です")
    
    except Exception as e:
        print(f"⚠️ Notion修理ケース取得エラー: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"✅ 総ドキュメント数: {len(documents)}件")
    
    if len(documents) == 0:
        print("❌ ドキュメントが1件もありません。RAGシステムを作成できません。")
        return None
    
    # ChromaDBが利用可能かチェック
    if not CHROMA_AVAILABLE:
        print("❌ ChromaDBが利用できません。langchain-chromaとchromadbをインストールしてください。")
        return None
    
    # 既存のデータベースを削除して新規作成
    if os.path.exists(chroma_db_path):
        print("🔄 既存のChromaデータベースを削除中...")
        try:
            import time
            time.sleep(1)
            shutil.rmtree(chroma_db_path)
            print("✅ 既存のデータベースを削除しました")
        except Exception as e:
            print(f"⚠️ データベース削除エラー: {e}")
    
    # 新しいデータベースを作成
    try:
        print("🔄 新しいChromaデータベースを作成中...")
        print(f"📊 ドキュメント数: {len(documents)}")
        
        # ドキュメントの検証と修正
        print("🔍 ドキュメントの検証中...")
        valid_documents = []
        
        for i, doc in enumerate(documents):
            try:
                # page_contentの検証
                if not isinstance(doc.page_content, str):
                    print(f"⚠️ ドキュメント{i}: page_contentが文字列ではありません（型: {type(doc.page_content)}）")
                    doc.page_content = str(doc.page_content)
                
                # 空のコンテンツをチェック
                if not doc.page_content or len(doc.page_content) < 1:
                    print(f"⚠️ ドキュメント{i}: page_contentが空です - スキップします")
                    continue
                
                # metadataの検証と修正
                if doc.metadata:
                    cleaned_metadata = {}
                    for key, value in doc.metadata.items():
                        if value is None:
                            cleaned_metadata[key] = ""
                        elif isinstance(value, (str, int, float, bool)):
                            cleaned_metadata[key] = str(value) if not isinstance(value, (int, float, bool)) else value
                        elif isinstance(value, list):
                            # リストは文字列に変換
                            cleaned_metadata[key] = ', '.join(str(v) for v in value)
                        else:
                            print(f"⚠️ ドキュメント{i}: metadata['{key}']の型が不正（型: {type(value)}） - 文字列に変換")
                            cleaned_metadata[key] = str(value)
                    doc.metadata = cleaned_metadata
                
                # ドキュメントを検証済みリストに追加
                valid_documents.append(doc)
                    
            except Exception as e:
                print(f"❌ ドキュメント{i}の検証エラー: {e} - スキップします")
                continue
        
        print(f"✅ ドキュメント検証完了: {len(valid_documents)}/{len(documents)}件が有効")
        
        if len(valid_documents) == 0:
            print("❌ 有効なドキュメントが1件もありません")
            return None
        
        # ChromaDBを作成（バッチ処理で問題のあるドキュメントを特定）
        print(f"🔄 ChromaDBに{len(valid_documents)}件のドキュメントを埋め込み中...")
        
        # 小バッチでテストして問題のあるドキュメントを特定
        batch_size = 10
        final_valid_documents = []
        
        for batch_start in range(0, len(valid_documents), batch_size):
            batch_end = min(batch_start + batch_size, len(valid_documents))
            batch = valid_documents[batch_start:batch_end]
            
            try:
                # このバッチをテスト
                print(f"  🔄 バッチ {batch_start//batch_size + 1}: ドキュメント{batch_start}-{batch_end-1} をテスト中...")
                
                # 各ドキュメントを個別にチェック
                for j, doc in enumerate(batch):
                    doc_index = batch_start + j
                    try:
                        # page_contentとmetadataの最終チェック
                        if not isinstance(doc.page_content, str):
                            print(f"    ⚠️ ドキュメント{doc_index}: page_content型エラー - 修正")
                            doc.page_content = str(doc.page_content)
                        
                        # metadataの全キーをチェック
                        if doc.metadata:
                            for k, v in list(doc.metadata.items()):
                                if isinstance(v, list):
                                    print(f"    ⚠️ ドキュメント{doc_index}: metadata['{k}']がリスト - 文字列に変換")
                                    doc.metadata[k] = ', '.join(str(item) for item in v)
                                elif not isinstance(v, (str, int, float, bool, type(None))):
                                    print(f"    ⚠️ ドキュメント{doc_index}: metadata['{k}']の型が不正（{type(v)}）- 文字列に変換")
                                    doc.metadata[k] = str(v)
                        
                        final_valid_documents.append(doc)
                        
                    except Exception as e:
                        print(f"    ❌ ドキュメント{doc_index}でエラー: {e} - スキップ")
                        print(f"       page_content: {str(doc.page_content)[:50]}...")
                        print(f"       metadata: {doc.metadata}")
                        continue
                
                print(f"  ✅ バッチ{batch_start//batch_size + 1}完了: {len(batch)}件中{len([d for d in batch if d in final_valid_documents])}件有効")
                
            except Exception as e:
                print(f"  ❌ バッチ{batch_start//batch_size + 1}エラー: {e}")
                continue
        
        print(f"✅ 最終検証完了: {len(final_valid_documents)}件のドキュメントが使用可能")
        
        if len(final_valid_documents) == 0:
            print("❌ 使用可能なドキュメントが1件もありません")
            return None
        
        # ChromaDBを作成
        print(f"🔄 ChromaDBに{len(final_valid_documents)}件のドキュメントを埋め込み開始...")
        db = Chroma.from_documents(
            documents=final_valid_documents,
            embedding=embeddings_model,
            persist_directory=chroma_db_path
        )
        print("✅ Chromaデータベースを作成しました")
        return db
        
    except Exception as e:
        print(f"❌ Chromaデータベース作成エラー: {e}")
        print(f"❌ エラー型: {type(e)}")
        import traceback
        print("❌ スタックトレース:")
        traceback.print_exc()
        
        # エラーの詳細を表示
        print("\n🔍 デバッグ情報:")
        print(f"  - 元のドキュメント総数: {len(documents)}")
        print(f"  - 有効なドキュメント数: {len(valid_documents) if 'valid_documents' in locals() else 'N/A'}")
        
        if len(documents) > 0:
            print(f"\n  - サンプルドキュメント:")
            for i in range(min(3, len(documents))):
                print(f"    ドキュメント{i}:")
                print(f"      - page_content型: {type(documents[i].page_content)}")
                print(f"      - page_content長: {len(documents[i].page_content) if isinstance(documents[i].page_content, str) else 'N/A'}")
                print(f"      - page_content: {str(documents[i].page_content)[:100]}...")
                print(f"      - metadata: {documents[i].metadata}")
        
        return None


if __name__ == "__main__":
    print("=== Notion統合RAGシステムテスト ===")
    
    # Notion統合RAGシステムを作成
    db = create_notion_based_rag_system(use_text_files=False)
    
    if db:
        # テスト検索
        question = "サブバッテリーの調子が悪い"
        results = enhanced_rag_retrieve(question, db)
        
        print("\n=== 検索結果 ===")
        print(f"質問: {question}")
        print(f"\nマニュアル内容: {results['manual_content'][:200] if results['manual_content'] else 'なし'}...")
        print(f"\nテキストファイル内容: {results['text_file_content'][:200] if results['text_file_content'] else 'なし'}...")
        print(f"\n関連ブログ:")
        for blog in results.get('blog_links', []):
            print(f"• {blog['title']}: {blog['url']}")
    else:
        print("❌ RAGシステムの作成に失敗しました")