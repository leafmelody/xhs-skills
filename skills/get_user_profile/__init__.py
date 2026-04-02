"""获取小红书用户主页 Skill"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from xhs.bitbrowser_cdp import BitBrowserClient
from xhs.user_profile import get_user_profile

logger = logging.getLogger(__name__)

DEFAULT_BITBROWSER_API = "http://127.0.0.1:54345"
DEFAULT_API_KEY = "efb3b5286ce84011a9df96c660b27bd3"
DEFAULT_PROFILE_ID = "074e3ee40c95497da490a44a87473676"


def run(
    user_id: str,
    xsec_token: str,
    limit: int = 20,
) -> dict:
    """获取用户主页信息。

    Args:
        user_id: 用户 ID
        xsec_token: 安全令牌
        limit: 返回笔记数量限制
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

        logger.info("获取用户主页: %s", user_id)
        profile = get_user_profile(page, user_id, xsec_token)

        basic = profile.user_basic_info
        feeds = profile.feeds[:limit]

        return {
            "success": True,
            "user": {
                "user_id": basic.user_id,
                "nickname": basic.nickname,
                "red_id": basic.red_id,
                "desc": basic.desc,
                "gender": basic.gender,
                "ip_location": basic.ip_location,
                "avatar": basic.images or basic.imageb,
            },
            "interactions": [
                {"type": i.type, "name": i.name, "count": i.count}
                for i in profile.interactions
            ],
            "feeds": [
                {
                    "id": f.id,
                    "title": f.note_card.display_title or "（无标题）",
                    "type": f.note_card.type,
                    "likes": f.note_card.interact_info.liked_count,
                    "collects": f.note_card.interact_info.collected_count,
                    "link": f"https://www.xiaohongshu.com/explore/{f.id}?xsec_token={f.xsec_token}",
                    "xsec_token": f.xsec_token,
                }
                for f in feeds
            ],
            "total_feeds": len(profile.feeds),
        }

    except Exception as e:
        logger.exception("获取用户主页失败")
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        client.close()
