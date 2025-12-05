#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
エラーハンドリング強化モジュール
フェーズ2-1: エラーハンドリングの強化
"""

import json
import traceback
from typing import Dict, Any, Optional, Tuple
from utils.response_logger import response_logger


class ErrorHandler:
    """エラーハンドリングクラス"""
    
    @staticmethod
    def handle_openai_error(error: Exception, attempt: int, max_retries: int) -> Tuple[str, bool]:
        """
        OpenAI APIエラーを処理
        
        Args:
            error: エラーオブジェクト
            attempt: 現在の試行回数
            max_retries: 最大リトライ回数
        
        Returns:
            (エラーメッセージ, リトライ可能かどうか)
        """
        error_str = str(error)
        error_lower = error_str.lower()
        
        # 429エラー（クォータ超過）
        if "429" in error_str or "insufficient_quota" in error_lower or "quota" in error_lower:
            error_details = ""
            try:
                if hasattr(error, 'response') and hasattr(error.response, 'json'):
                    error_data = error.response.json()
                    error_details = f"\n\n**エラー詳細:**\n```json\n{json.dumps(error_data, ensure_ascii=False, indent=2)}\n```"
            except:
                pass
            
            error_message = f"""⚠️ **OpenAI API クォータ超過エラー（429）**

**エラー内容：**
```
{error_str}
```{error_details}

**対処方法：**

1. **APIキーの確認**
   - OpenAIダッシュボード（https://platform.openai.com/account/usage）で使用量を確認
   - 支払い上限を引き上げた場合は、反映まで数分かかる場合があります

2. **環境変数の更新**
   - Railwayの環境変数`OPENAI_API_KEY`を確認・更新
   - ローカルの`.env`ファイルを確認・更新
   - サーバーを再起動してください

3. **リトライ**
   - 数分待ってから再度お試しください
   - 支払い情報の反映には時間がかかる場合があります

**確認事項：**
- ✅ 支払い方法が正しく登録されているか
- ✅ 使用上限が十分に設定されているか
- ✅ APIキーが有効か
- ✅ 環境変数が正しく設定されているか

詳細は管理者にお問い合わせください。"""
            
            # エラーログに記録
            response_logger.log_error(
                error_type="OpenAI_429",
                error_message=error_str,
                context={
                    "attempt": attempt,
                    "max_retries": max_retries,
                    "error_details": error_details
                }
            )
            
            return error_message, attempt < max_retries - 1
        
        # 401エラー（認証エラー）
        elif "401" in error_str or "unauthorized" in error_lower or "invalid" in error_lower:
            error_message = f"""⚠️ **OpenAI API 認証エラー（401）**

**エラー内容：**
```
{error_str}
```

**対処方法：**
1. APIキーが正しく設定されているか確認してください
2. APIキーが有効か確認してください
3. 環境変数`OPENAI_API_KEY`を確認・更新してください

詳細は管理者にお問い合わせください。"""
            
            response_logger.log_error(
                error_type="OpenAI_401",
                error_message=error_str,
                context={"attempt": attempt}
            )
            
            return error_message, False
        
        # 500エラー（サーバーエラー）
        elif "500" in error_str or "internal server error" in error_lower:
            error_message = f"""⚠️ **OpenAI API サーバーエラー（500）**

**エラー内容：**
```
{error_str}
```

**対処方法：**
1. しばらく待ってから再度お試しください
2. OpenAIのサービス状況を確認してください（https://status.openai.com/）

詳細は管理者にお問い合わせください。"""
            
            response_logger.log_error(
                error_type="OpenAI_500",
                error_message=error_str,
                context={"attempt": attempt}
            )
            
            return error_message, attempt < max_retries - 1
        
        # その他のエラー
        else:
            error_message = f"""⚠️ **OpenAI API エラー**

**エラー内容：**
```
{error_str}
```

**エラータイプ：** {type(error).__name__}

**対処方法：**
1. サーバーログを確認してください
2. APIキーが正しく設定されているか確認してください
3. 管理者にお問い合わせください"""
            
            response_logger.log_error(
                error_type="OpenAI_Other",
                error_message=error_str,
                context={
                    "attempt": attempt,
                    "error_type": type(error).__name__,
                    "traceback": traceback.format_exc()
                }
            )
            
            return error_message, attempt < max_retries - 1
    
    @staticmethod
    def handle_notion_error(error: Exception, operation: str) -> Dict[str, Any]:
        """
        Notion APIエラーを処理
        
        Args:
            error: エラーオブジェクト
            operation: 実行していた操作名
        
        Returns:
            エラー情報を含む辞書
        """
        error_str = str(error)
        error_lower = error_str.lower()
        
        # データベースが見つからないエラー
        if "could not find database" in error_lower or "database with id" in error_lower:
            error_info = {
                "error": "Notionデータベースが見つかりません",
                "error_type": "Notion_DatabaseNotFound",
                "message": f"""⚠️ **Notionデータベースが見つかりません**

**エラー内容：**
```
{error_str}
```

**対処方法：**
1. Notionデータベースが正しく共有されているか確認してください
2. データベースIDが正しく設定されているか確認してください
3. Notion Integrationに適切な権限が付与されているか確認してください

詳細は管理者にお問い合わせください。""",
                "retry": False
            }
        # 認証エラー
        elif "unauthorized" in error_lower or "401" in error_str:
            error_info = {
                "error": "Notion API認証エラー",
                "error_type": "Notion_Unauthorized",
                "message": f"""⚠️ **Notion API認証エラー**

**エラー内容：**
```
{error_str}
```

**対処方法：**
1. Notion APIキーが正しく設定されているか確認してください
2. 環境変数`NOTION_API_KEY`を確認・更新してください

詳細は管理者にお問い合わせください。""",
                "retry": False
            }
        # レート制限エラー
        elif "rate limit" in error_lower or "429" in error_str:
            error_info = {
                "error": "Notion APIレート制限エラー",
                "error_type": "Notion_RateLimit",
                "message": f"""⚠️ **Notion APIレート制限エラー**

**エラー内容：**
```
{error_str}
```

**対処方法：**
1. しばらく待ってから再度お試しください
2. Notion APIのレート制限を確認してください

詳細は管理者にお問い合わせください。""",
                "retry": True
            }
        # その他のエラー
        else:
            error_info = {
                "error": f"Notion APIエラー: {operation}",
                "error_type": "Notion_Other",
                "message": f"""⚠️ **Notion APIエラー**

**エラー内容：**
```
{error_str}
```

**操作：** {operation}

**対処方法：**
1. サーバーログを確認してください
2. Notion APIの状態を確認してください
3. 管理者にお問い合わせください""",
                "retry": False
            }
        
        # エラーログに記録
        response_logger.log_error(
            error_type=error_info["error_type"],
            error_message=error_str,
            context={
                "operation": operation,
                "traceback": traceback.format_exc()
            }
        )
        
        return error_info
    
    @staticmethod
    def handle_rag_error(error: Exception, query: str) -> Dict[str, Any]:
        """
        RAG検索エラーを処理
        
        Args:
            error: エラーオブジェクト
            query: 検索クエリ
        
        Returns:
            エラー情報を含む辞書
        """
        error_str = str(error)
        
        error_info = {
            "error": "RAG検索エラー",
            "error_type": "RAG_SearchError",
            "message": f"""⚠️ **RAG検索エラー**

**エラー内容：**
```
{error_str}
```

**検索クエリ：** {query[:100]}

**対処方法：**
1. サーバーログを確認してください
2. ChromaDBの状態を確認してください
3. 管理者にお問い合わせください""",
            "retry": True
        }
        
        # エラーログに記録
        response_logger.log_error(
            error_type="RAG_SearchError",
            error_message=error_str,
            context={
                "query": query,
                "traceback": traceback.format_exc()
            }
        )
        
        return error_info
    
    @staticmethod
    def handle_serp_error(error: Exception, query: str) -> Dict[str, Any]:
        """
        SERP検索エラーを処理
        
        Args:
            error: エラーオブジェクト
            query: 検索クエリ
        
        Returns:
            エラー情報を含む辞書
        """
        error_str = str(error)
        error_lower = error_str.lower()
        
        # APIキーエラー
        if "api key" in error_lower or "unauthorized" in error_lower:
            error_info = {
                "error": "SERP API認証エラー",
                "error_type": "SERP_Unauthorized",
                "message": f"""⚠️ **SERP API認証エラー**

**エラー内容：**
```
{error_str}
```

**対処方法：**
1. SERP APIキーが正しく設定されているか確認してください
2. 環境変数`SERP_API_KEY`を確認・更新してください

詳細は管理者にお問い合わせください。""",
                "retry": False
            }
        # レート制限エラー
        elif "rate limit" in error_lower or "429" in error_str:
            error_info = {
                "error": "SERP APIレート制限エラー",
                "error_type": "SERP_RateLimit",
                "message": f"""⚠️ **SERP APIレート制限エラー**

**エラー内容：**
```
{error_str}
```

**対処方法：**
1. しばらく待ってから再度お試しください
2. SERP APIのレート制限を確認してください

詳細は管理者にお問い合わせください。""",
                "retry": True
            }
        # その他のエラー
        else:
            error_info = {
                "error": "SERP検索エラー",
                "error_type": "SERP_Other",
                "message": f"""⚠️ **SERP検索エラー**

**エラー内容：**
```
{error_str}
```

**検索クエリ：** {query[:100]}

**対処方法：**
1. サーバーログを確認してください
2. SERP APIの状態を確認してください
3. 管理者にお問い合わせください""",
                "retry": True
            }
        
        # エラーログに記録
        response_logger.log_error(
            error_type=error_info["error_type"],
            error_message=error_str,
            context={
                "query": query,
                "traceback": traceback.format_exc()
            }
        )
        
        return error_info


# グローバルインスタンス
error_handler = ErrorHandler()

