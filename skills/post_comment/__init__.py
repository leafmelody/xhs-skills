"""发表评论到小红书帖子 Skill"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from xhs.bitbrowser_cdp import BitBrowserClient
from xhs.comment import post_comment

logger = logging.getLogger(__name__)

DEFAULT_BITBROWSER_API = "http://127.0.0.1:54345"
DEFAULT_API_KEY = "efb3b5286ce84011a9df96c660b27bd3"
DEFAULT_PROFILE_ID = "074e3ee40c95497da490a44a87473676"


def run(
    feed_id: str,
    xsec_token: str,
    content: str,
) -> dict:
    """发表评论到指定帖子。

    Args:
        feed_id: 帖子 ID
        xsec_token: 安全令牌
        content: 评论内容
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

        logger.info("发表评论到: %s", feed_id)
        post_comment(page, feed_id, xsec_token, content)

        return {
            "success": True,
            "feed_id": feed_id,
            "content": content,
            "message": "评论发表成功",
        }

    except Exception as e:
        logger.exception("发表评论失败")
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        client.close()
