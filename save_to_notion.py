import os
import time
import json
import requests
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Tuple, Optional, List, Union
from dotenv import load_dotenv

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 読み込み
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_LOG_DB_ID = os.getenv("NOTION_LOG_DB_ID")

def _sanitize_db_id(db_id: Optional[str]) -> Optional[str]:
    if not db_id:
        return None
    try:
        import re
        cleaned = re.sub(r"[^0-9a-fA-F]", "", db_id).lower()
        return cleaned
    except Exception:
        return db_id.replace("-", "") if db_id else None

# データベースIDをサニタイズ（ハイフン・空白・不可視文字の除去）
NOTION_LOG_DB_ID = _sanitize_db_id(NOTION_LOG_DB_ID)
NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2022-06-28")
NOTION_PAGES_URL = "https://api.notion.com/v1/pages"
NOTION_DATABASE_URL = "https://api.notion.com/v1/databases"
NOTION_LOG_TITLE_PROP = os.getenv("NOTION_LOG_TITLE_PROP")

_LOG_DB_SCHEMA: Optional[Dict[str, str]] = None
_LOG_DB_TITLE_PROP: Optional[str] = None


MAX_RICH_TEXT_LENGTH = 1900


def _chunk_text(text: str, chunk_size: int = MAX_RICH_TEXT_LENGTH) -> List[str]:
    safe_text = text or ""
    if not safe_text:
        return [""]
    return [safe_text[i : i + chunk_size] for i in range(0, len(safe_text), chunk_size)]


def _rt(text: str) -> List[Dict[str, Any]]:
    return [{"type": "text", "text": {"content": chunk}} for chunk in _chunk_text(text)]


def _ensure_log_db_schema(headers: Dict[str, str]) -> Tuple[Dict[str, str], Optional[str]]:
    """NotionログDBのスキーマとタイトルプロパティ名をキャッシュ付きで取得"""
    global _LOG_DB_SCHEMA, _LOG_DB_TITLE_PROP

    if _LOG_DB_SCHEMA is not None:
        return _LOG_DB_SCHEMA, _LOG_DB_TITLE_PROP

    schema: Dict[str, str] = {}
    title_prop = NOTION_LOG_TITLE_PROP or None

    if NOTION_LOG_DB_ID:
        try:
            resp = requests.get(
                f"{NOTION_DATABASE_URL}/{NOTION_LOG_DB_ID}",
                headers=headers,
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                properties = data.get("properties", {})
                logger.info(f"🧭 NotionログDBのプロパティ数: {len(properties)}")
                for name, prop in properties.items():
                    prop_type = prop.get("type")
                    schema[name] = prop_type
                    if prop_type == "title" and not title_prop:
                        title_prop = name
                    logger.info(f"   - {name}: {prop_type}")
                logger.info("🧭 NotionログDBスキーマ取得成功 (title=%s, プロパティ数=%d)", title_prop, len(schema))
            else:
                logger.warning(
                    "⚠️ NotionログDBスキーマ取得失敗: %s - %s",
                    resp.status_code,
                    resp.text[:200],
                )
        except requests.RequestException as exc:
            logger.warning("⚠️ NotionログDBスキーマ取得エラー: %s", exc)

    if not title_prop:
        for candidate in ("名前", "Name", "タイトル", "Title"):
            if schema.get(candidate) == "title":
                title_prop = candidate
                break

    if not title_prop:
        title_prop = NOTION_LOG_TITLE_PROP or "Name"

    _LOG_DB_SCHEMA = schema
    _LOG_DB_TITLE_PROP = title_prop
    return _LOG_DB_SCHEMA, _LOG_DB_TITLE_PROP


def _assign_text_property(
    props: Dict[str, Any],
    schema: Dict[str, str],
    name: str,
    value: Optional[str],
) -> None:
    if value is None:
        return

    text_value = str(value)
    if not text_value and name not in schema:
        return

    prop_type = schema.get(name)
    if prop_type is None:
        logger.info("ℹ️ NotionログDBに '%s' プロパティが存在しないためスキップします", name)
        return
    if prop_type == "title":
        props[name] = {"title": _rt(text_value)}
    elif prop_type in {"rich_text", "text"}:
        props[name] = {"rich_text": _rt(text_value)}
    elif prop_type == "url":
        props[name] = {"url": text_value}
    else:
        props[name] = {"rich_text": _rt(text_value)}


def _build_title_value(user_msg: str, bot_msg: str, session_id: str) -> str:
    parts: List[str] = []
    if session_id:
        parts.append(session_id)
    if user_msg:
        parts.append(user_msg.strip().splitlines()[0])
    if bot_msg and (not parts or len(" ".join(parts)) < 40):
        parts.append(bot_msg.strip().splitlines()[0])

    title = " | ".join(filter(None, parts)).strip()
    if not title:
        title = f"ログ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
    return title[:100]


def save_chat_log_to_notion(
    user_msg: str,
    bot_msg: str,
    session_id: str = "default",
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    urgency: Optional[float] = None,
    keywords: Optional[List[str]] = None,
    tool_used: Optional[str] = None,
    rag_score: Optional[float] = None,
    confidence: Optional[str] = None,
    confidence_score: Optional[float] = None,
    sources_summary: Optional[str] = None,
) -> Tuple[bool, str]:
    """会話ログを Notion の Chat Logs DB に1件保存する。

    失敗時は例外を投げず (False, エラーメッセージ) を返す（アプリ動作は継続）。
    成功時は (True, "") を返す。
    """
    logger.info("💾 Notion保存処理開始")
    logger.info(f"   - NOTION_API_KEY: {'設定済み' if NOTION_API_KEY else '❌ 未設定'}")
    logger.info(f"   - NOTION_LOG_DB_ID: {'設定済み' if NOTION_LOG_DB_ID else '❌ 未設定'}")
    
    if not NOTION_API_KEY or not NOTION_LOG_DB_ID:
        error_msg = "Notion環境変数が未設定のため保存をスキップします"
        logger.warning(f"⚠️ {error_msg}")
        return False, error_msg

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }

    schema, title_prop = _ensure_log_db_schema(headers)

    props: Dict[str, Any] = {}

    _assign_text_property(props, schema, "user_message", user_msg)
    _assign_text_property(props, schema, "bot_message", bot_msg)

    timestamp_value = datetime.now(timezone.utc).isoformat()
    if "timestamp" in schema:
        if schema.get("timestamp") == "rich_text":
            props["timestamp"] = {"rich_text": _rt(timestamp_value)}
        else:
            props["timestamp"] = {"date": {"start": timestamp_value}}
    else:
        logger.info("ℹ️ NotionログDBに 'timestamp' プロパティが存在しないためスキップします")

    _assign_text_property(props, schema, "session_id", session_id)

    if category:
        prop_type = schema.get("category")
        if not prop_type:
            logger.info("ℹ️ NotionログDBに 'category' プロパティが存在しないためスキップします")
        elif prop_type == "multi_select":
            props["category"] = {"multi_select": [{"name": category}]}
        elif prop_type in {"rich_text", "text"}:
            props["category"] = {"rich_text": _rt(category)}
        else:
            props["category"] = {"select": {"name": category}}

    if subcategory:
        prop_type = schema.get("subcategory")
        if not prop_type:
            logger.info("ℹ️ NotionログDBに 'subcategory' プロパティが存在しないためスキップします")
        elif prop_type == "multi_select":
            props["subcategory"] = {"multi_select": [{"name": subcategory}]}
        elif prop_type in {"rich_text", "text"}:
            props["subcategory"] = {"rich_text": _rt(subcategory)}
        else:
            props["subcategory"] = {"select": {"name": subcategory}}

    if urgency is not None:
        try:
            urgency_value = float(urgency)
        except (TypeError, ValueError):
            logger.warning("⚠️ urgencyを数値に変換できませんでした: %s", urgency)
        else:
            prop_type = schema.get("urgency")
            if not prop_type:
                logger.info("ℹ️ NotionログDBに 'urgency' プロパティが存在しないためスキップします")
            elif prop_type in {"rich_text", "text"}:
                props["urgency"] = {"rich_text": _rt(str(urgency_value))}
            elif prop_type == "select":
                props["urgency"] = {"select": {"name": str(int(urgency_value))}}
            else:
                props["urgency"] = {"number": urgency_value}

    if keywords:
        cleaned_keywords = [str(k).strip() for k in keywords if str(k).strip()]
        if cleaned_keywords:
            prop_type = schema.get("keywords")
            if not prop_type:
                logger.info("ℹ️ NotionログDBに 'keywords' プロパティが存在しないためスキップします")
            elif prop_type in {"rich_text", "text"}:
                props["keywords"] = {"rich_text": _rt(", ".join(cleaned_keywords))}
            else:
                props["keywords"] = {
                    "multi_select": [{"name": keyword} for keyword in cleaned_keywords]
                }

    if tool_used:
        prop_type = schema.get("tool_used")
        if not prop_type:
            logger.info("ℹ️ NotionログDBに 'tool_used' プロパティが存在しないためスキップします")
        elif prop_type in {"rich_text", "text"}:
            props["tool_used"] = {"rich_text": _rt(tool_used)}
        else:
            props["tool_used"] = {"select": {"name": tool_used}}

    # Phase 3対応: rag_score (number型)
    if rag_score is not None:
        try:
            rag_score_value = float(rag_score)
        except (TypeError, ValueError):
            logger.warning("⚠️ rag_scoreを数値に変換できませんでした: %s", rag_score)
        else:
            prop_type = schema.get("rag_score")
            if not prop_type:
                logger.info("ℹ️ NotionログDBに 'rag_score' プロパティが存在しないためスキップします")
            elif prop_type in {"rich_text", "text"}:
                props["rag_score"] = {"rich_text": _rt(str(rag_score_value))}
            else:
                props["rag_score"] = {"number": rag_score_value}

    # Phase 3対応: confidence (select型、lower case必須)
    if confidence:
        # lower caseに統一（"low" | "medium" | "high"）
        confidence_lower = str(confidence).lower().strip()
        if confidence_lower in ("low", "medium", "high"):
            prop_type = schema.get("confidence")
            if not prop_type:
                logger.info("ℹ️ NotionログDBに 'confidence' プロパティが存在しないためスキップします")
            elif prop_type in {"rich_text", "text"}:
                props["confidence"] = {"rich_text": _rt(confidence_lower)}
            else:
                props["confidence"] = {"select": {"name": confidence_lower}}
        else:
            logger.warning("⚠️ confidenceの値が無効です（low/medium/highのみ）: %s", confidence)

    # Phase 3対応: confidence_score (number型)
    if confidence_score is not None:
        try:
            confidence_score_value = float(confidence_score)
        except (TypeError, ValueError):
            logger.warning("⚠️ confidence_scoreを数値に変換できませんでした: %s", confidence_score)
        else:
            prop_type = schema.get("confidence_score")
            if not prop_type:
                logger.info("ℹ️ NotionログDBに 'confidence_score' プロパティが存在しないためスキップします")
            elif prop_type in {"rich_text", "text"}:
                props["confidence_score"] = {"rich_text": _rt(str(confidence_score_value))}
            else:
                props["confidence_score"] = {"number": confidence_score_value}

    # Phase 3対応: sources_summary (rich_text型、200文字にトリム)
    if sources_summary:
        # 200文字にトリム（Notionの指示に従う）
        sources_summary_trimmed = str(sources_summary).strip()[:200]
        if sources_summary_trimmed:
            prop_type = schema.get("sources_summary")
            if not prop_type:
                logger.info("ℹ️ NotionログDBに 'sources_summary' プロパティが存在しないためスキップします")
            elif prop_type in {"rich_text", "text"}:
                props["sources_summary"] = {"rich_text": _rt(sources_summary_trimmed)}
            else:
                props["sources_summary"] = {"rich_text": _rt(sources_summary_trimmed)}

    has_title_prop = any(schema.get(name) == "title" for name in props)
    if not has_title_prop and title_prop:
        props[title_prop] = {"title": _rt(_build_title_value(user_msg, bot_msg, session_id))}

    logger.info(f"📋 設定するプロパティ: {list(props.keys())}")
    logger.info(f"   - プロパティ数: {len(props)}")
    # プロパティの型情報を簡潔に出力
    prop_types = {k: list(v.keys())[0] if isinstance(v, dict) else type(v).__name__ for k, v in props.items()}
    logger.info(f"   - プロパティ型: {prop_types}")

    data = {"parent": {"database_id": NOTION_LOG_DB_ID}, "properties": props}

    last_error_details = ""

    # 429/5xx 簡易リトライ
    for i in range(3):
        try:
            logger.info(f"🔄 Notion API呼び出し中... (試行 {i+1}/3)")
            if i == 0:  # 最初の試行時のみペイロードをログ出力
                logger.info(f"   - リクエストペイロード（簡易）: database_id={NOTION_LOG_DB_ID}, properties={list(props.keys())}")
                # ペイロードの一部を出力（タイトルプロパティの値など）
                for key, value in props.items():
                    if isinstance(value, dict) and "title" in value:
                        title_content = ""
                        if value.get("title") and isinstance(value["title"], list) and len(value["title"]) > 0:
                            title_content = value["title"][0].get("text", {}).get("content", "")[:50]
                        logger.info(f"   - {key} (title): {title_content}")
                    elif isinstance(value, dict) and "rich_text" in value:
                        content_preview = ""
                        if value.get("rich_text") and isinstance(value["rich_text"], list) and len(value["rich_text"]) > 0:
                            content_preview = value["rich_text"][0].get("text", {}).get("content", "")[:50]
                        logger.info(f"   - {key} (rich_text): {content_preview}...")
            resp = requests.post(NOTION_PAGES_URL, headers=headers, json=data, timeout=15)
            logger.info(f"   - ステータスコード: {resp.status_code}")
            
            if 200 <= resp.status_code < 300:
                logger.info("✅ Notion保存成功!")
                return True, ""
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 2 ** i))
                logger.warning(f"⚠️ レート制限 (429) - {wait}秒待機")
                time.sleep(max(wait, 1))
                continue
            if resp.status_code in (500, 502, 503, 504):
                last_error_details = f"HTTP {resp.status_code}: {resp.text[:200]}"
                logger.warning(
                    "⚠️ サーバーエラー (%s) - レスポンス: %s",
                    resp.status_code,
                    resp.text[:200],
                )
                time.sleep(2 ** i)
                continue
            
            # その他のエラー（400, 401, 403, 404など）
            error_json = {}
            try:
                error_json = resp.json()
            except:
                pass
            error_msg = f"Notion APIエラー: {resp.status_code}"
            if error_json:
                error_msg += f" - {json.dumps(error_json, ensure_ascii=False)[:500]}"
            else:
                error_msg += f" - {resp.text[:500]}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
        except requests.RequestException as e:
            error_msg = f"リクエストエラー: {str(e)}"
            logger.error(f"❌ {error_msg}")
            last_error_details = error_msg
            time.sleep(2 ** i)
            continue
    
    error_msg = "Notion保存失敗（3回リトライ後も失敗）"
    if last_error_details:
        error_msg = f"{error_msg}: {last_error_details}"
    logger.error(f"❌ {error_msg}")
    return False, error_msg


