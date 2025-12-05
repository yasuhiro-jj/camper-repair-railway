#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIレスポンス共通ユーティリティ
APIエンドポイントのレスポンス形式を統一するためのヘルパー関数
"""

from flask import jsonify
from typing import Dict, Any, Optional, Union
import traceback


def success_response(
    data: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    status_code: int = 200
) -> tuple:
    """
    成功レスポンスを生成
    
    Args:
        data: レスポンスデータ（辞書形式）
        message: 成功メッセージ
        status_code: HTTPステータスコード（デフォルト: 200）
    
    Returns:
        (jsonifyレスポンス, ステータスコード)のタプル
    """
    response = {"success": True}
    
    if message:
        response["message"] = message
    
    if data:
        response.update(data)
    
    return jsonify(response), status_code


def error_response(
    error: Union[str, Exception],
    status_code: int = 500,
    error_type: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    log_error: bool = True
) -> tuple:
    """
    エラーレスポンスを生成
    
    Args:
        error: エラーメッセージまたはExceptionオブジェクト
        status_code: HTTPステータスコード（デフォルト: 500）
        error_type: エラータイプ（例: "ValidationError", "NotFoundError"）
        details: 追加のエラー詳細情報
        log_error: エラーをログに記録するか（デフォルト: True）
    
    Returns:
        (jsonifyレスポンス, ステータスコード)のタプル
    """
    error_message = str(error) if isinstance(error, Exception) else error
    
    response = {
        "success": False,
        "error": error_message
    }
    
    if error_type:
        response["error_type"] = error_type
    
    if details:
        response["details"] = details
    
    # エラーログを記録
    if log_error:
        if isinstance(error, Exception):
            print(f"❌ APIエラー ({error_type or 'Unknown'}): {error_message}")
            print(traceback.format_exc())
        else:
            print(f"❌ APIエラー ({error_type or 'Unknown'}): {error_message}")
    
    return jsonify(response), status_code


def validation_error_response(
    field: str,
    message: Optional[str] = None
) -> tuple:
    """
    バリデーションエラーレスポンスを生成
    
    Args:
        field: バリデーションエラーのフィールド名
        message: カスタムエラーメッセージ
    
    Returns:
        (jsonifyレスポンス, 400ステータスコード)のタプル
    """
    error_msg = message or f"{field}は必須です"
    return error_response(
        error=error_msg,
        status_code=400,
        error_type="ValidationError",
        details={"field": field},
        log_error=False
    )


def not_found_response(
    resource: str,
    resource_id: Optional[str] = None
) -> tuple:
    """
    リソースが見つからない場合のレスポンスを生成
    
    Args:
        resource: リソース名（例: "工場", "ビルダー"）
        resource_id: リソースID（オプション）
    
    Returns:
        (jsonifyレスポンス, 404ステータスコード)のタプル
    """
    error_msg = f"{resource}が見つかりません"
    if resource_id:
        error_msg += f" (ID: {resource_id})"
    
    return error_response(
        error=error_msg,
        status_code=404,
        error_type="NotFoundError",
        details={"resource": resource, "resource_id": resource_id},
        log_error=False
    )


def service_unavailable_response(
    service_name: str
) -> tuple:
    """
    サービスが利用できない場合のレスポンスを生成
    
    Args:
        service_name: サービス名（例: "Factory Manager", "Notion Client"）
    
    Returns:
        (jsonifyレスポンス, 503ステータスコード)のタプル
    """
    return error_response(
        error=f"{service_name}が利用できません",
        status_code=503,
        error_type="ServiceUnavailableError",
        details={"service": service_name},
        log_error=True
    )


def handle_api_exception(
    func
):
    """
    APIエンドポイントのデコレータ
    例外を自動的にキャッチしてエラーレスポンスを返す
    
    Usage:
        @app.route("/api/example")
        @handle_api_exception
        def example_endpoint():
            # エラーが発生すると自動的にエラーレスポンスを返す
            return success_response(data={"result": "ok"})
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return validation_error_response("request", str(e))
        except KeyError as e:
            return validation_error_response(str(e))
        except Exception as e:
            return error_response(e, status_code=500)
    
    wrapper.__name__ = func.__name__
    return wrapper

