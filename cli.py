#!/usr/bin/env python3
"""
おおつきチャットボット CLIツール
コマンドラインからチャットボットの機能を利用できます。
"""

import argparse
import sys
import json
import asyncio
from typing import Optional
import logging

# プロジェクトのモジュールをインポート
sys.path.append('.')

from app.services.chat_service import ChatService
from app.services.notion_service import NotionService
from app.models.conversation import ChatRequest
from app.config import settings, load_environment_variables

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotCLI:
    """チャットボットCLIクラス"""
    
    def __init__(self):
        load_environment_variables()
        self.chat_service = ChatService()
        self.notion_service = NotionService()
    
    def chat(self, message: str, session_id: Optional[str] = None):
        """チャット機能"""
        try:
            request = ChatRequest(message=message, session_id=session_id)
            response = self.chat_service.process_message(request)
            
            print(f"\n🤖 おおつき: {response.message}")
            print(f"   セッションID: {response.session_id}")
            
            if response.suggestions:
                print("\n💡 提案:")
                for i, suggestion in enumerate(response.suggestions, 1):
                    print(f"  {i}. {suggestion}")
            
            return response.session_id
            
        except Exception as e:
            logger.error(f"チャットエラー: {e}")
            print(f"❌ エラーが発生しました: {e}")
            return None
    
    def list_menus(self, category: Optional[str] = None):
        """メニュー一覧表示"""
        try:
            from app.models.notion_models import MenuCategory
            
            menu_category = None
            if category:
                try:
                    menu_category = MenuCategory(category)
                except ValueError:
                    print(f"❌ 無効なカテゴリです: {category}")
                    print(f"有効なカテゴリ: {[c.value for c in MenuCategory]}")
                    return
            
            menu_items = self.notion_service.get_menu_items(menu_category)
            
            if not menu_items:
                print("📋 メニューが見つかりません")
                return
            
            print(f"\n📋 メニュー一覧 ({len(menu_items)}件)")
            if category:
                print(f"カテゴリ: {category}")
            
            for item in menu_items:
                print(f"\n🍽️  {item.name}")
                print(f"   カテゴリ: {item.category.value}")
                print(f"   価格: ¥{item.price:,}")
                print(f"   説明: {item.description}")
                
                if item.allergy_info:
                    print(f"   アレルギー: {', '.join(item.allergy_info)}")
                
                if item.seasonal:
                    print("   🌸 季節限定")
                
                if item.vegetarian:
                    print("   🌱 ベジタリアン対応")
                
                if item.popularity > 0:
                    print(f"   人気度: {'⭐' * (item.popularity // 20)}")
            
        except Exception as e:
            logger.error(f"メニュー取得エラー: {e}")
            print(f"❌ エラーが発生しました: {e}")
    
    def show_store_info(self):
        """店舗情報表示"""
        try:
            store_info = self.notion_service.get_store_info()
            
            if not store_info:
                print("🏪 店舗情報が見つかりません")
                return
            
            print("\n🏪 おおつき 店舗情報")
            print("=" * 40)
            print(f"営業時間: {store_info.business_hours}")
            print(f"定休日: {store_info.holidays}")
            print(f"アクセス: {store_info.access}")
            print(f"特徴: {store_info.features}")
            print(f"予約方法: {store_info.reservation_method}")
            print(f"駐車場: {'あり' if store_info.parking else 'なし'}")
            
        except Exception as e:
            logger.error(f"店舗情報取得エラー: {e}")
            print(f"❌ エラーが発生しました: {e}")
    
    def search_menus(self, query: str, category: Optional[str] = None):
        """メニュー検索"""
        try:
            from app.models.notion_models import MenuCategory
            
            menu_items = self.notion_service.get_menu_items()
            
            # カテゴリフィルタリング
            if category:
                try:
                    menu_category = MenuCategory(category)
                    menu_items = [item for item in menu_items if item.category == menu_category]
                except ValueError:
                    print(f"❌ 無効なカテゴリです: {category}")
                    return
            
            # 検索クエリでフィルタリング
            query_lower = query.lower()
            filtered_items = []
            
            for item in menu_items:
                if (query_lower in item.name.lower() or 
                    query_lower in item.description.lower() or
                    any(query_lower in allergy.lower() for allergy in item.allergy_info)):
                    filtered_items.append(item)
            
            if not filtered_items:
                print(f"🔍 検索結果: '{query}' に一致するメニューが見つかりません")
                return
            
            print(f"\n   検索結果: '{query}' ({len(filtered_items)}件)")
            if category:
                print(f"カテゴリ: {category}")
            
            for item in filtered_items:
                print(f"\n🍽️  {item.name}")
                print(f"   カテゴリ: {item.category.value}")
                print(f"   価格: ¥{item.price:,}")
                print(f"   説明: {item.description}")
            
        except Exception as e:
            logger.error(f"メニュー検索エラー: {e}")
            print(f"❌ エラーが発生しました: {e}")
    
    def interactive_chat(self):
        """対話型チャット"""
        print("\n🤖 おおつきチャットボットへようこそ！")
        print("   チャットを開始します。'quit' または 'exit' で終了します。")
        print("=" * 50)
        
        session_id = None
        
        while True:
            try:
                user_input = input("\n👤 あなた: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '終了']:
                    print("👋 チャットを終了します。またのご利用をお待ちしています！")
                    break
                
                if not user_input:
                    continue
                
                session_id = self.chat(user_input, session_id)
                
            except KeyboardInterrupt:
                print("\n\n👋 チャットを終了します。")
                break
            except Exception as e:
                logger.error(f"対話型チャットエラー: {e}")
                print(f"❌ エラーが発生しました: {e}")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="おおつきチャットボット CLIツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python cli.py chat "メニューについて教えてください"
  python cli.py menus --category "テイクアウト"
  python cli.py search "カレー" --category "ランチ"
  python cli.py store
  python cli.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # チャットコマンド
    chat_parser = subparsers.add_parser('chat', help='チャットメッセージを送信')
    chat_parser.add_argument('message', help='送信するメッセージ')
    chat_parser.add_argument('--session-id', help='セッションID')
    
    # メニュー一覧コマンド
    menus_parser = subparsers.add_parser('menus', help='メニュー一覧を表示')
    menus_parser.add_argument('--category', choices=['テイクアウト', '宴会', 'ランチ', 'ディナー'], 
                             help='カテゴリでフィルタリング')
    
    # 店舗情報コマンド
    store_parser = subparsers.add_parser('store', help='店舗情報を表示')
    
    # メニュー検索コマンド
    search_parser = subparsers.add_parser('search', help='メニューを検索')
    search_parser.add_argument('query', help='検索クエリ')
    search_parser.add_argument('--category', choices=['テイクアウト', '宴会', 'ランチ', 'ディナー'], 
                              help='カテゴリでフィルタリング')
    
    # 対話型チャットコマンド
    interactive_parser = subparsers.add_parser('interactive', help='対話型チャットを開始')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ChatbotCLI()
    
    try:
        if args.command == 'chat':
            cli.chat(args.message, args.session_id)
        elif args.command == 'menus':
            cli.list_menus(args.category)
        elif args.command == 'store':
            cli.show_store_info()
        elif args.command == 'search':
            cli.search_menus(args.query, args.category)
        elif args.command == 'interactive':
            cli.interactive_chat()
    
    except KeyboardInterrupt:
        print("\n\n   プログラムを終了します。")
    except Exception as e:
        logger.error(f"CLI実行エラー: {e}")
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()