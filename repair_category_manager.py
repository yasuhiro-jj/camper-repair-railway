import json
import logging
import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class RepairCategoryManager:
    """修理カテゴリー管理クラス - データ駆動型アプローチ"""
    
    def __init__(self, config_file: str = "category_definitions.json"):
        """
        カテゴリーマネージャーの初期化
        
        Args:
            config_file: カテゴリー定義ファイルのパス
        """
        self.config_file = config_file
        self.categories = {}
        self.general_settings = {}
        self._cache = {}  # キャッシュ用辞書を追加
        self.setup_logging()
        self.load_categories()
    
    def setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('repair_category_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_categories(self):
        """カテゴリー定義ファイルを読み込み"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.config_file)
            print(f"🔍 設定ファイルパス: {config_path}")
            print(f"🔍 ファイル存在確認: {os.path.exists(config_path)}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                print(f"🔍 読み込まれたJSONデータのキー: {list(config_data.keys())}")
                
                # 設定ファイルの妥当性をチェック
                if not self.validate_config(config_data):
                    print("❌ 設定ファイルの妥当性チェックに失敗しました")
                    return
                
                self.categories = config_data.get("categories", {})
                self.general_settings = config_data.get("general_settings", {})
                
                print(f"🔍 カテゴリー数: {len(self.categories)}")
                print(f"🔍 カテゴリー名: {list(self.categories.keys())}")
                
            print(f"✅ カテゴリー定義ファイル読み込み成功: {len(self.categories)}個のカテゴリー")
        except Exception as e:
            print(f"❌ カテゴリー定義ファイル読み込みエラー: {e}")
            import traceback
            print(f"詳細エラー: {traceback.format_exc()}")
            self.categories = {}
            self.general_settings = {}
    
    def validate_config(self, config_data: dict) -> bool:
        """
        設定ファイルの妥当性をチェック
        
        Args:
            config_data: 設定データ
            
        Returns:
            妥当性チェック結果
        """
        required_keys = ["categories", "general_settings"]
        
        for key in required_keys:
            if key not in config_data:
                self.logger.error(f"必須キー '{key}' が見つかりません")
                return False
        
        # カテゴリーの必須フィールドをチェック
        for category_name, category_data in config_data.get("categories", {}).items():
            required_category_keys = ["keywords", "files", "repair_costs"]
            for key in required_category_keys:
                if key not in category_data:
                    self.logger.error(f"カテゴリー '{category_name}' に必須キー '{key}' が見つかりません")
                    return False
        
        self.logger.info("設定ファイルの妥当性チェック完了")
        return True
    
    def identify_category(self, query: str) -> Optional[str]:
        """
        クエリからカテゴリーを特定
        
        Args:
            query: 検索クエリ
            
        Returns:
            特定されたカテゴリー名（None if not found）
        """
        query_lower = query.lower()
        print(f"🔍 カテゴリー特定開始: '{query}'")
        
        for category_name, category_data in self.categories.items():
            if self._is_category_related(query_lower, category_data):
                print(f"✅ {category_name}関連と判定")
                self.log_category_identification(query, category_name)
                return category_name
        
        print("❌ どのカテゴリーにも該当しません")
        return None
    
    def _is_category_related(self, query_lower: str, category_data: Dict) -> bool:
        """
        クエリがカテゴリーに関連しているかチェック
        
        Args:
            query_lower: 小文字に変換されたクエリ
            category_data: カテゴリーデータ
            
        Returns:
            関連している場合True
        """
        keywords = category_data.get("keywords", {})
        exclusion_keywords = category_data.get("exclusion_keywords", [])
        
        # デバッグ情報を追加
        category_name = category_data.get("name", "Unknown")
        if "ff" in query_lower or "ヒーター" in query_lower:
            print(f"🔍 FFヒーター関連クエリ検出: {query_lower}")
            print(f"🔍 カテゴリー名: {category_name}")
            print(f"🔍 主要キーワード: {keywords.get('primary', [])}")
            print(f"🔍 クエリ小文字: {query_lower}")
            print(f"🔍 キーワードマッチングテスト:")
            for kw in keywords.get('primary', []):
                match_result = kw in query_lower
                print(f"  - '{kw}' in '{query_lower}': {match_result}")
        
        # 除外キーワードが含まれている場合は関連なし
        if any(exclusion_keyword in query_lower for exclusion_keyword in exclusion_keywords):
            return False
        
        # 主要キーワードチェック（改善版）
        primary_keywords = keywords.get("primary", [])
        matched_primary = [kw for kw in primary_keywords if kw in query_lower]
        if matched_primary:
            print(f"✅ 主要キーワードマッチ: {matched_primary}")
            return True
        
        # 詳細キーワード + 文脈チェック（改善版）
        secondary_keywords = keywords.get("secondary", [])
        context_phrases = keywords.get("context", [])
        
        # 詳細キーワードがマッチした場合
        matched_secondary = [kw for kw in secondary_keywords if kw in query_lower]
        if matched_secondary:
            print(f"🔍 詳細キーワードマッチ: {matched_secondary}")
            # 文脈フレーズもチェック（より柔軟に）
            if context_phrases:
                matched_context = [phrase for phrase in context_phrases if phrase in query_lower]
                if matched_context:
                    print(f"✅ 文脈フレーズマッチ: {matched_context}")
                    return True
                # 文脈フレーズがなくても、詳細キーワードが複数マッチした場合は関連とみなす
                elif len(matched_secondary) >= 2:
                    print(f"✅ 複数詳細キーワードマッチ: {matched_secondary}")
                    return True
                # 単一の詳細キーワードでも、主要キーワードと組み合わせてマッチした場合は関連とみなす
                elif any(primary_kw in query_lower for primary_kw in primary_keywords):
                    print(f"✅ 主要+詳細キーワードマッチ: {matched_secondary}")
                    return True
            else:
                # 文脈フレーズが定義されていない場合は詳細キーワードのみで判定
                print(f"✅ 詳細キーワードのみマッチ: {matched_secondary}")
                return True
        
        # FFヒーター専用の特別なマッチングロジック
        if category_name == "FFヒーター":
            # FFヒーター関連のキーワードをより広くカバー
            ff_related_terms = [
                "ff", "ヒーター", "暖房", "燃焼", "車載", "強制送風", "ディーゼル",
                "交換", "修理", "故障", "不調", "点火", "温風", "白煙", "異音",
                "燃焼音", "エラー", "リモコン", "燃料", "グロー", "ファン", "煙突",
                "排気", "換気", "一酸化炭素", "タンク", "点火システム", "燃焼室",
                "熱交換器", "温度制御", "自動停止", "安全装置"
            ]
            
            matched_ff_terms = [term for term in ff_related_terms if term in query_lower]
            if matched_ff_terms:
                print(f"✅ FFヒーター関連用語マッチ: {matched_ff_terms}")
                return True
            
            # 「FFヒーターの交換を考えている」のようなクエリの特別処理
            if "ff" in query_lower and "交換" in query_lower:
                print(f"✅ FFヒーター交換クエリマッチ: {query_lower}")
                return True
            if "ヒーター" in query_lower and "交換" in query_lower:
                print(f"✅ ヒーター交換クエリマッチ: {query_lower}")
                return True
        
        return False
    
    def get_repair_costs(self, category: str) -> str:
        """
        カテゴリーの修理費用目安を取得
        
        Args:
            category: カテゴリー名
            
        Returns:
            修理費用目安の文字列
        """
        if category not in self.categories:
            return ""
        
        repair_costs = self.categories[category].get("repair_costs", [])
        cost_lines = []
        
        for cost_item in repair_costs:
            item = cost_item.get("item", "")
            price_range = cost_item.get("price_range", "")
            cost_lines.append(f"**{item}**: {price_range}")
        
        return "\n".join(cost_lines)
    
    def get_fallback_steps(self, category: str) -> List[str]:
        """
        カテゴリーのフォールバック修理手順を取得
        
        Args:
            category: カテゴリー名
            
        Returns:
            修理手順のリスト
        """
        if category not in self.categories:
            return []
        
        return self.categories[category].get("fallback_steps", [])
    
    def get_repair_steps_from_json(self, category: str) -> str:
        """
        JSONファイルから修理手順を取得（フォールバック用）
        
        Args:
            category: カテゴリー名
            
        Returns:
            修理手順の文字列
        """
        if category not in self.categories:
            return ""
        
        fallback_steps = self.categories[category].get("fallback_steps", [])
        if fallback_steps:
            return "\n".join(fallback_steps)
        return ""
    
    def get_fallback_warnings(self, category: str) -> List[str]:
        """
        カテゴリーのフォールバック注意事項を取得
        
        Args:
            category: カテゴリー名
            
        Returns:
            注意事項のリスト
        """
        if category not in self.categories:
            return []
        
        return self.categories[category].get("fallback_warnings", [])
    
    def get_warnings_from_json(self, category: str) -> str:
        """
        JSONファイルから注意事項を取得（フォールバック用）
        
        Args:
            category: カテゴリー名
            
        Returns:
            注意事項の文字列
        """
        if category not in self.categories:
            return ""
        
        fallback_warnings = self.categories[category].get("fallback_warnings", [])
        if fallback_warnings:
            return "\n".join(fallback_warnings)
        return ""
    
    def get_file_paths(self, category: str) -> Dict[str, str]:
        """
        カテゴリーのファイルパスを取得
        
        Args:
            category: カテゴリー名
            
        Returns:
            ファイルパスの辞書
        """
        if category not in self.categories:
            return {}
        
        return self.categories[category].get("files", {})
    
    def get_content_from_file(self, category: str, content_type: str) -> Optional[str]:
        """
        専用ファイルから内容を取得
        
        Args:
            category: カテゴリー名
            content_type: 内容タイプ (repair_steps, warnings, text_content)
            
        Returns:
            ファイル内容（None if error）
        """
        file_paths = self.get_file_paths(category)
        filename = file_paths.get(content_type)
        
        if not filename:
            print(f"  ❌ {category}の{content_type}ファイルが設定されていません")
            return None
        
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"  ✅ {filename}から内容を取得しました ({len(content)}文字)")
                    return content
            else:
                print(f"  ❌ {filename}が存在しません")
                return None
        except Exception as e:
            print(f"  ❌ {filename}の読み込みエラー: {e}")
            return None
    
    def extract_section_from_content(self, content: str, section_type: str) -> Optional[str]:
        """
        コンテンツから特定セクションを抽出
        
        Args:
            content: ファイル内容
            section_type: セクションタイプ (cost_section, repair_steps_section, warnings_section)
            
        Returns:
            抽出されたセクション内容（None if not found）
        """
        patterns = self.general_settings.get("extraction_patterns", {}).get(section_type, [])
        
        for i, pattern in enumerate(patterns):
            print(f"  パターン {i+1} を試行中...")
            match = re.search(pattern, content, re.DOTALL)
            if match:
                print(f"  ✅ パターン {i+1} でマッチしました")
                section_content = match.group(1).strip()
                
                # セクション内容を整理
                if section_type == "cost_section":
                    lines = [line.strip() for line in section_content.split('\n') 
                            if line.strip() and '円' in line]
                elif section_type in ["repair_steps_section", "warnings_section"]:
                    lines = [line.strip() for line in section_content.split('\n') 
                            if line.strip() and not line.startswith('---')]
                else:
                    lines = [line.strip() for line in section_content.split('\n') if line.strip()]
                
                if lines:
                    result = '\n'.join(lines)
                    print(f"  ✅ {section_type}抽出成功: {result[:100]}...")
                    return result
        
        print(f"  ❌ {section_type}が見つかりませんでした")
        return None
    
    def get_category_icon(self, category: str) -> str:
        """
        カテゴリーのアイコンを取得
        
        Args:
            category: カテゴリー名
            
        Returns:
            アイコン文字列
        """
        if category not in self.categories:
            return "🔧"
        
        return self.categories[category].get("icon", "🔧")
    
    def get_repair_center_info(self) -> Dict[str, str]:
        """
        修理センター情報を取得
        
        Returns:
            修理センター情報の辞書
        """
        return self.general_settings.get("default_repair_center", {})
    
    def get_cached_content(self, cache_key: str, content_func, *args, **kwargs):
        """
        コンテンツのキャッシュ機能
        
        Args:
            cache_key: キャッシュキー
            content_func: コンテンツ取得関数
            *args, **kwargs: 関数の引数
            
        Returns:
            キャッシュされたコンテンツ
        """
        if cache_key not in self._cache:
            self._cache[cache_key] = content_func(*args, **kwargs)
        return self._cache[cache_key]
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self._cache.clear()
        print("🗑️ キャッシュをクリアしました")
    
    def log_category_identification(self, query: str, category: str, confidence: float = 1.0):
        """カテゴリー特定のログ"""
        self.logger.info(f"カテゴリー特定: '{query}' -> {category} (信頼度: {confidence})")
    
    def get_all_categories(self):
        """全カテゴリ情報を取得（API用）"""
        try:
            print("📋 全カテゴリ情報取得開始")
            
            # 基本カテゴリ情報を構築
            all_categories = {}
            
            for category_name, category_data in self.categories.items():
                # カテゴリの基本情報
                category_info = {
                    "name": category_name,
                    "icon": category_data.get("icon", "🔧"),
                    "keywords": category_data.get("keywords", []),
                    "description": category_data.get("description", ""),
                    "repair_costs": self.get_repair_costs(category_name),
                    "repair_steps": self.get_repair_steps_from_json(category_name),
                    "warnings": self.get_warnings_from_json(category_name)
                }
                
                # ファイルベースの情報も取得
                file_content = self.get_content_from_file(category_name, "general")
                if file_content:
                    category_info["file_content"] = file_content[:500] + "..." if len(file_content) > 500 else file_content
                
                all_categories[category_name] = category_info
            
            print(f"✅ 全カテゴリ情報取得成功: {len(all_categories)}件")
            return all_categories
            
        except Exception as e:
            print(f"❌ 全カテゴリ情報取得エラー: {e}")
            return {}