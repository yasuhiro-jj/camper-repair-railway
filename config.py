import os
from dotenv import load_dotenv

# .envファイルを読み込み（存在する場合）
# NOTE: 実行時のカレントディレクトリに依存しないよう、このファイルと同階層の .env を読む
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DOTENV_PATH = os.path.join(_BASE_DIR, ".env")

if os.path.exists(_DOTENV_PATH):
    try:
        # OS環境変数を優先（override=False）
        load_dotenv(_DOTENV_PATH, override=False)
    except UnicodeDecodeError:
        # .envファイルのエンコーディングエラーの場合、無視して続行
        print("Warning: .envファイルのエンコーディングエラーを無視して続行します")
    except Exception as e:
        # その他のエラーの場合も無視して続行
        print(f"Warning: .envファイルの読み込みエラーを無視して続行します: {e}")
else:
    print("Info: .envファイルが見つかりません。環境変数を設定してください。")

# APIキーの設定（環境変数から取得）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY") or "fa8d9dd975d4447caafe53b533125af6fb43e9bbdd4780c12f888865b4a3d4db"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "default")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

# LangChain Tracing設定
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT

# LangSmith設定（APIキーが設定されている場合のみ）
if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT
    print("Info: LangSmith設定が有効になりました")
else:
    print("Warning: LANGSMITH_API_KEYが設定されていません。LangSmith機能は無効です。")

# APIキーが設定されていない場合の警告
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEYが設定されていません。環境変数を設定してください。")
elif "your_" in OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEYにプレースホルダーが設定されています。実際のAPIキーに置き換えてください。")
    # キー全文/一部でもログに出さない（漏洩防止）
else:
    # キー全文/一部でもログに出さない（漏洩防止）
    print("Info: OPENAI_API_KEYが設定されています。")

if not SERP_API_KEY:
    print("Warning: SERP_API_KEYが設定されていません。環境変数を設定してください。")
else:
    # キー全文/一部でもログに出さない（漏洩防止）
    print("Info: SERP_API_KEYが設定されています。")