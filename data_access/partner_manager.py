#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PartnerShopManagerをラップし、API向けのログ出力を担うモジュール。
"""

import os
import sys
from typing import List, Dict, Optional, Any

from data_access.partner_shop_manager import PartnerShopManager


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
        except Exception as e:
            sys.stderr.write(f"[AgentLog] ❌ Failed to initialize PartnerShopManager: {e}\n")
            sys.stderr.flush()

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

        if not self._manager:
            sys.stderr.write("[AgentLog] ERROR: PartnerShopManager is not available\n")
            sys.stderr.flush()
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
            return shops
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            sys.stderr.write(f"[AgentLog] ❌ list_shops exception: {e}\n")
            sys.stderr.write(f"[AgentLog] Traceback: {error_trace}\n")
            sys.stderr.flush()
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

        if not self._manager:
            sys.stderr.write("[AgentLog] ERROR: PartnerShopManager is not available\n")
            sys.stderr.flush()
            return None

        try:
            shop = self._manager.get_shop(shop_id)
            if shop:
                sys.stderr.write(f"[AgentLog] ✅ Found partner shop: {shop.get('name', 'N/A')}\n")
            else:
                sys.stderr.write("[AgentLog] ⚠️ Partner shop not found\n")
            sys.stderr.flush()
            return shop
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            sys.stderr.write(f"[AgentLog] ❌ get_partner_by_id exception: {e}\n")
            sys.stderr.write(f"[AgentLog] Traceback: {error_trace}\n")
            sys.stderr.flush()
            return None


partner_manager = PartnerManager()

