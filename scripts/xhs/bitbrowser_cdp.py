"""BitBrowser CDP 适配器

适配 BitBrowser 的 Chrome DevTools Protocol，替代原生的 Chrome 连接。
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests
import websockets.sync.client as ws_client

from .cdp import CDPClient, Page, CDPError
from .errors import ElementNotFoundError

logger = logging.getLogger(__name__)


class BitBrowserClient:
    """BitBrowser CDP 连接管理器。"""

    def __init__(
        self,
        bitbrowser_api: str = "http://127.0.0.1:54345",
        api_key: str = "efb3b5286ce84011a9df96c660b27bd3",
        profile_id: str = "074e3ee40c95497da490a44a87473676",
    ) -> None:
        self.bitbrowser_api = bitbrowser_api
        self.api_key = api_key
        self.profile_id = profile_id
        self._ws_url: str | None = None
        self._cdp: CDPClient | None = None

    def _open_browser(self) -> str:
        """调用 BitBrowser API 开启浏览器并获取 WebSocket URL。"""
        url = f"{self.bitbrowser_api}/browser/open"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        data = {"id": self.profile_id}

        logger.info("正在启动 BitBrowser...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        if not result.get("success"):
            raise CDPError(f"BitBrowser 启动失败: {result}")

        ws_url = result["data"]["ws"]
        logger.info("BitBrowser 已启动，WebSocket: %s", ws_url)
        return ws_url

    def connect(self) -> None:
        """连接到 BitBrowser。"""
        if not self._ws_url:
            self._ws_url = self._open_browser()

        self._cdp = CDPClient(self._ws_url)
        logger.info("已连接到 BitBrowser CDP")

    def get_cdp(self) -> CDPClient:
        """获取 CDP 客户端。"""
        if not self._cdp:
            self.connect()
        return self._cdp

    def attach_to_page(self, target_id: str) -> Page:
        """附加到指定页面。"""
        cdp = self.get_cdp()
        result = cdp.send(
            "Target.attachToTarget",
            {"targetId": target_id, "flatten": True},
        )
        session_id = result.get("sessionId")
        if not session_id:
            raise CDPError(f"无法附加到页面: {target_id}")

        page = Page(cdp, target_id, session_id)
        # 启用必要的 CDP domain
        page._send_session("Page.enable")
        page._send_session("DOM.enable")
        page._send_session("Runtime.enable")
        return page

    def get_existing_page(self) -> Page | None:
        """获取已存在的第一个页面。"""
        cdp = self.get_cdp()

        # 获取所有目标
        result = cdp.send("Target.getTargets")
        targets = result.get("targetInfos", [])

        for target in targets:
            if target.get("type") == "page":
                target_id = target["targetId"]
                try:
                    return self.attach_to_page(target_id)
                except CDPError:
                    continue
        return None

    def close(self) -> None:
        """关闭连接。"""
        if self._cdp:
            self._cdp.close()
            self._cdp = None

    def close_browser(self) -> None:
        """关闭 BitBrowser。"""
        url = f"{self.bitbrowser_api}/browser/close"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        data = {"id": self.profile_id}

        try:
            requests.post(url, headers=headers, json=data, timeout=10)
            logger.info("BitBrowser 已关闭")
        except Exception as e:
            logger.warning("关闭 BitBrowser 失败: %s", e)


class BitBrowserPage:
    """BitBrowser 页面包装器，提供更方便的操作接口。"""

    def __init__(self, client: BitBrowserClient) -> None:
        self.client = client
        self._page: Page | None = None

    def __enter__(self) -> Page:
        """上下文管理器入口。"""
        self._page = self.client.get_existing_page()
        if not self._page:
            raise CDPError("没有可用的页面，请确保 BitBrowser 已打开小红书")
        return self._page

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口。"""
        # 不关闭页面，保持浏览器状态
        pass

    @property
    def page(self) -> Page:
        """获取底层 Page 对象。"""
        if not self._page:
            raise CDPError("页面未初始化")
        return self._page
