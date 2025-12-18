#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PartnerShopManagerをラップし、API向けのログ出力を担うモジュール。
"""

import os
import sys
import json
import time
from typing import List, Dict, Optional, Any

from data_access.partner_shop_manager import PartnerShopManager

LOG_PATH_CANDIDATES = [
    r"c:\Users\PC user\OneDrive\Desktop\移行用まとめフォルダー\.cursor\debug.log",
    os.path.join(os.getcwd(), ".cursor", "debug.log"),
    "/app/.cursor/debug.log",
]


def _write_agent_log(*, hypothesis_id: str, location: str, message: str, data: Dict[str, Any]) -> None:
    #region agent log
    payload = {
        "sessionId": "debug-session",
        "runId": "initial",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    for path in LOG_PATH_CANDIDATES:
        try:
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            with open(path, "a", encoding="utf-8") as _f:
                _f.write(json.dumps(payload, ensure_ascii=False) + "\n")
            break
        except Exception:
            continue
    #endregion


class PartnerManager:
    """PartnerShopManagerラッパー"""

    def __init__(self) -> None:
        self.db_id = os.getenv("NOTION_PARTNER_DB_ID", "")
        self._manager: Optional[PartnerShopManager] = None

        try:
            self._manager = PartnerShopManager()
            if getattr(self._manager, "partner_db_id", None):
                self.db_id = self._manager.partner_db_id

            sys.stderr.write("[AgentLog] ✅ PartnerShopManager initialized successfully\n")
            sys.stderr.write(f"[AgentLog] NOTION_PARTNER_DB_ID={'SET' if self.db_id else 'NOT SET'}\n")
            sys.stderr.flush()
            _write_agent_log(
                hypothesis_id="A",
                location="partner_manager.py:33",
                message="PartnerShopManager initialized",
                data={"db_id_present": bool(self.db_id)},
            )
        except Exception as e:
            sys.stderr.write(f"[AgentLog] ❌ Failed to initialize PartnerShopManager: {e}\n")
            sys.stderr.flush()
            _write_agent_log(
                hypothesis_id="A",
                location="partner_manager.py:40",
                message="PartnerShopManager initialization failed",
                data={"error": str(e)},
            )

    def list_shops(
        self,
        status: Optional[str] = None,
        prefecture: Optional[str] = None,
        specialty: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        sys.stderr.write(
            "[AgentLog] list_shops called with "
            f"status={status}, prefecture={prefecture}, specialty={specialty}, limit={limit}\n"
        )
        sys.stderr.flush()
        _write_agent_log(
            hypothesis_id="B",
            location="partner_manager.py:60",
            message="list_shops called",
            data={"status": status, "prefecture": prefecture, "specialty": specialty, "limit": limit},
        )

        if not self._manager:
            sys.stderr.write("[AgentLog] ERROR: PartnerShopManager is not available\n")
            sys.stderr.flush()
            _write_agent_log(
                hypothesis_id="A",
                location="partner_manager.py:70",
                message="PartnerShopManager missing",
                data={},
            )
            return []

        try:
            shops = self._manager.list_shops(
                status=status,
                prefecture=prefecture,
                specialty=specialty,
                limit=limit,
            )
            sys.stderr.write(f"[AgentLog] ✅ list_shops fetched {len(shops)} shops\n")
            sys.stderr.flush()
            preview = shops[0].get("shop_id") if shops else None
            _write_agent_log(
                hypothesis_id="B",
                location="partner_manager.py:84",
                message="list_shops result",
                data={"count": len(shops), "first_shop_id": preview},
            )
            return shops
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            sys.stderr.write(f"[AgentLog] ❌ list_shops exception: {e}\n")
            sys.stderr.write(f"[AgentLog] Traceback: {error_trace}\n")
            sys.stderr.flush()
            _write_agent_log(
                hypothesis_id="C",
                location="partner_manager.py:95",
                message="list_shops exception",
                data={"error": str(e)},
            )
            return []

    def get_all_partners(
        self,
        prefecture: Optional[str] = None,
        specialty: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.list_shops(status="アクティブ", prefecture=prefecture, specialty=specialty)

    def get_partner_by_id(self, shop_id: str) -> Optional[Dict[str, Any]]:
        sys.stderr.write(f"[AgentLog] get_partner_by_id called with shop_id={shop_id}\n")
        sys.stderr.flush()
        _write_agent_log(
            hypothesis_id="B",
            location="partner_manager.py:108",
            message="get_partner_by_id called",
            data={"shop_id": shop_id},
        )

        if not self._manager:
            sys.stderr.write("[AgentLog] ERROR: PartnerShopManager is not available\n")
            sys.stderr.flush()
            _write_agent_log(
                hypothesis_id="A",
                location="partner_manager.py:116",
                message="PartnerShopManager missing",
                data={},
            )
            return None

        try:
            shop = self._manager.get_shop(shop_id)
            if shop:
                sys.stderr.write(f"[AgentLog] ✅ Found partner shop: {shop.get('name', 'N/A')}\n")
            else:
                sys.stderr.write("[AgentLog] ⚠️ Partner shop not found\n")
            sys.stderr.flush()
            _write_agent_log(
                hypothesis_id="B",
                location="partner_manager.py:129",
                message="get_partner_by_id result",
                data={"found": bool(shop)},
            )
            return shop
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            sys.stderr.write(f"[AgentLog] ❌ get_partner_by_id exception: {e}\n")
            sys.stderr.write(f"[AgentLog] Traceback: {error_trace}\n")
            sys.stderr.flush()
            _write_agent_log(
                hypothesis_id="C",
                location="partner_manager.py:141",
                message="get_partner_by_id exception",
                data={"error": str(e)},
            )
            return None


partner_manager = PartnerManager()

