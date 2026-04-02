"""检查小红书登录状态 Skill"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from xhs.bitbrowser_cdp import BitBrowserClient
from xhs.login import check_login_status, get_current_user_nickname

logger = logging.getLogger(__name__)

DEFAULT_BITBROWSER_API = "http://127.0.0.1:54345"
DEFAULT_API_KEY = "efb3b5286ce84011a9df96c660b27bd3"
DEFAULT_PROFILE_ID = "074e3ee40c95497da490a44a87473676"


def run() -> dict:
    """检查当前登录状态并返回用户信息。"""
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    bitbrowser_api = os.getenv("BITBROWSER_API", DEFAULT_BITBROWSER_API)
    api_key = os.getenv("BITBROWSER_API_KEY", DEFAULT_API_KEY)
    profile_id = os.getenv("BITBROWSER_PROFILE_ID", DEFAULT_PROFILE_ID)

    client = BitBrowserClient(
        bitbrowser_api=bitbrowser_api,
        api_key=api_key,
        profile_id=profile_id,
    )

    try:
        client.connect()
        page = client.get_existing_page()
        if not page:
            return {
                "success": False,
                "logged_in": False,
                "error": "没有可用的页面，请确保 BitBrowser 已打开小红书网页",
            }

        is_logged_in = check_login_status(page)
        result = {
            "success": True,
            "logged_in": is_logged_in,
        }

        if is_logged_in:
            nickname = get_current_user_nickname(page)
            result["nickname"] = nickname
            result["message"] = f"已登录，当前用户: {nickname}" if nickname else "已登录"
        else:
            result["message"] = "未登录"

        return result

    except Exception as e:
        logger.exception("检查登录状态失败")
        return {
            "success": False,
            "logged_in": False,
            "error": str(e),
        }
    finally:
        client.close()
