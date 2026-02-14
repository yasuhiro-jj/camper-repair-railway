#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
認証ユーティリティモジュール
JWT認証とパスワードハッシュ化を提供
"""

import jwt
import bcrypt
import re
from datetime import datetime, timedelta
from functools import wraps
from typing import Tuple
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

# JWT設定
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))


class AuthUtils:
    """認証ユーティリティクラス"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        パスワードをbcryptでハッシュ化
        
        Args:
            password: 平文のパスワード
        
        Returns:
            ハッシュ化されたパスワード
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        パスワードを検証
        
        Args:
            password: 平文のパスワード
            hashed_password: ハッシュ化されたパスワード
        
        Returns:
            検証成功時True、失敗時False
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            print(f"⚠️ パスワード検証エラー: {e}")
            return False
    
    @staticmethod
    def generate_token(factory_id: str, login_id: str, role: str) -> str:
        """
        JWTトークンを生成
        
        Args:
            factory_id: 工場のページID
            login_id: ログインID
            role: ロール（factory/admin）
        
        Returns:
            JWTトークン
        """
        payload = {
            'factory_id': factory_id,
            'login_id': login_id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """
        JWTトークンをデコード
        
        Args:
            token: JWTトークン
        
        Returns:
            デコードされたペイロード
        
        Raises:
            Exception: トークンが無効または期限切れの場合
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('トークンの有効期限が切れています')
        except jwt.InvalidTokenError as e:
            raise Exception(f'無効なトークンです: {str(e)}')
    
    @staticmethod
    def generate_reset_token(email: str, expiration_minutes: int = 60) -> str:
        """
        パスワードリセット用のJWTトークンを生成
        
        Args:
            email: メールアドレス
            expiration_minutes: 有効期限（分）
        
        Returns:
            リセットトークン
        """
        payload = {
            'type': 'password_reset',
            'email': email,
            'exp': datetime.utcnow() + timedelta(minutes=expiration_minutes),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def decode_reset_token(token: str) -> str:
        """
        パスワードリセットトークンをデコードしてメールアドレスを取得
        
        Args:
            token: リセットトークン
        
        Returns:
            メールアドレス
        
        Raises:
            Exception: トークンが無効または期限切れの場合
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if payload.get('type') != 'password_reset':
                raise Exception('無効なトークンです')
            email = payload.get('email')
            if not email:
                raise Exception('無効なトークンです')
            return email
        except jwt.ExpiredSignatureError:
            raise Exception('リセットリンクの有効期限が切れています。再度パスワードリセットを申請してください')
        except jwt.InvalidTokenError as e:
            raise Exception(f'無効なトークンです: {str(e)}')


def require_auth(allowed_roles=None):
    """
    認証が必要なエンドポイントに使用するデコレータ
    
    Args:
        allowed_roles: 許可するロールのリスト（デフォルト: ['factory', 'admin']）
    
    Usage:
        @app.route('/api/v1/some-endpoint')
        @require_auth(allowed_roles=['factory', 'admin'])
        def some_endpoint():
            pass
    """
    if allowed_roles is None:
        allowed_roles = ['factory', 'admin']
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Authorizationヘッダーからトークンを取得
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'error': '認証が必要です'}), 401
            
            try:
                # "Bearer <token>" 形式を想定
                token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
                
                # トークンをデコード
                payload = AuthUtils.decode_token(token)
                
                # ロールチェック
                if payload.get('role') not in allowed_roles:
                    return jsonify({'error': 'アクセス権限がありません'}), 403
                
                # リクエストにユーザー情報を追加
                request.current_user = payload
                
            except Exception as e:
                return jsonify({'error': str(e)}), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def get_current_user():
    """
    現在ログイン中のユーザー情報を取得
    
    Returns:
        ユーザー情報（dict）またはNone
    """
    return getattr(request, 'current_user', None)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    パスワードの強度を検証
    
    Args:
        password: 検証するパスワード
    
    Returns:
        (is_valid, error_message) のタプル
        is_valid: 有効な場合True、無効な場合False
        error_message: エラーメッセージ（有効な場合は空文字列）
    """
    if not password:
        return False, "パスワードを入力してください"
    
    if len(password) < 8:
        return False, "パスワードは8文字以上である必要があります"
    
    if len(password) > 128:
        return False, "パスワードは128文字以下である必要があります"
    
    # 大文字が含まれているか
    if not re.search(r'[A-Z]', password):
        return False, "パスワードには大文字が1文字以上含まれている必要があります"
    
    # 小文字が含まれているか
    if not re.search(r'[a-z]', password):
        return False, "パスワードには小文字が1文字以上含まれている必要があります"
    
    # 数字が含まれているか
    if not re.search(r'[0-9]', password):
        return False, "パスワードには数字が1文字以上含まれている必要があります"
    
    # 記号が含まれているか（オプション、推奨）
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     return False, "パスワードには記号が1文字以上含まれている必要があります"
    
    return True, ""
