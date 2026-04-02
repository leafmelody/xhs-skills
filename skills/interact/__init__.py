"""小红书帖子互动 Skill（点赞/收藏）"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from xhs.bitbrowser_cdp import BitBrowserClient
from xhs.like_favorite import like_feed, unlike_feed, favorite_feed, unfavorite_feed

logger = logging.getLogger(__name__)

DEFAULT_BITBROWSER_API = "http://127.0.0.1:54345"
DEFAULT_API_KEY = "efb3b5286ce84011a9df96c660b27bd3"
DEFAULT_PROFILE_ID = "074e3ee40c95497da490a44a87473676"


def run(
    feed_id: str,
    xsec_token: str,
    action: str = "like",
) -> dict:
    """执行帖子互动操作。

    Args:
        feed_id: 帖子 ID
        xsec_token: 安全令牌
        action: 操作类型（like/unlike/favorite/unfavorite）
    """
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
                "error": "没有可用的页面，请确保 BitBrowser 已打开小红书网页",
            }

        action_map = {
            "like": ("点赞", like_feed),
            "unlike": ("取消点赞", unlike_feed),
            "favorite": ("收藏", favorite_feed),
            "unfavorite": ("取消收藏", unfavorite_feed),
        }

        if action not in action_map:
            return {
                "success": False,
                "error": f"无效的操作: {action}，可选: like/unlike/favorite/unfavorite",
            }

        action_name, func = action_map[action]
        logger.info("执行%s: %s", action_name, feed_id)
        result = func(page, feed_id, xsec_token)

        return {
            "success": result.success,
            "feed_id": feed_id,
            "action": action,
            "message": result.message,
        }

    except Exception as e:
        logger.exception("互动操作失败")
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        client.close()
