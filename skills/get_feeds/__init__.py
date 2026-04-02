"""获取小红书首页推荐列表 Skill"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from xhs.bitbrowser_cdp import BitBrowserClient
from xhs.feeds import list_feeds

logger = logging.getLogger(__name__)

DEFAULT_BITBROWSER_API = "http://127.0.0.1:54345"
DEFAULT_API_KEY = "efb3b5286ce84011a9df96c660b27bd3"
DEFAULT_PROFILE_ID = "074e3ee40c95497da490a44a87473676"


def run(limit: int = 20) -> dict:
    """获取首页推荐列表。

    Args:
        limit: 返回数量限制（默认20）
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

        logger.info("获取首页推荐列表...")
        feeds = list_feeds(page)

        results = []
        for feed in feeds[:limit]:
            results.append({
                "id": feed.id,
                "title": feed.note_card.display_title or "（无标题）",
                "author": feed.note_card.user.nickname or feed.note_card.user.nick_name or "未知",
                "likes": feed.note_card.interact_info.liked_count,
                "collects": feed.note_card.interact_info.collected_count,
                "comments": feed.note_card.interact_info.comment_count,
                "link": f"https://www.xiaohongshu.com/explore/{feed.id}?xsec_token={feed.xsec_token}",
                "xsec_token": feed.xsec_token,
            })

        return {
            "success": True,
            "total": len(feeds),
            "returned": len(results),
            "feeds": results,
        }

    except Exception as e:
        logger.exception("获取推荐列表失败")
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        client.close()
