"""发布小红书图文内容 Skill"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from xhs.bitbrowser_cdp import BitBrowserClient
from xhs.publish import publish_image_content
from xhs.types import PublishImageContent

logger = logging.getLogger(__name__)

DEFAULT_BITBROWSER_API = "http://127.0.0.1:54345"
DEFAULT_API_KEY = "efb3b5286ce84011a9df96c660b27bd3"
DEFAULT_PROFILE_ID = "074e3ee40c95497da490a44a87473676"


def run(
    title: str,
    content: str,
    image_paths: list[str],
    tags: list[str] | None = None,
    schedule_time: str | None = None,
    is_original: bool = False,
    visibility: str = "",
) -> dict:
    """发布图文内容。

    Args:
        title: 标题（不超过20字）
        content: 正文内容（不超过1000字）
        image_paths: 图片路径列表（本地绝对路径）
        tags: 标签列表（可选，最多10个）
        schedule_time: 定时发布时间（ISO8601格式，可选）
        is_original: 是否声明原创（默认False）
        visibility: 可见范围（公开可见/仅自己可见/仅互关好友可见，默认公开）
    """
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # 验证图片路径
    valid_paths = [p for p in image_paths if os.path.exists(p)]
    if not valid_paths:
        return {
            "success": False,
            "error": "没有有效的图片文件，请提供本地绝对路径",
        }

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

        publish_content = PublishImageContent(
            title=title,
            content=content,
            image_paths=valid_paths,
            tags=tags or [],
            schedule_time=schedule_time,
            is_original=is_original,
            visibility=visibility,
        )

        logger.info("发布图文: %s", title)
        publish_image_content(page, publish_content)

        return {
            "success": True,
            "title": title,
            "images_count": len(valid_paths),
            "message": "图文发布成功",
        }

    except Exception as e:
        logger.exception("发布图文失败")
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        client.close()
