"""获取小红书帖子详情 Skill"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from xhs.bitbrowser_cdp import BitBrowserClient
from xhs.feed_detail import get_feed_detail
from xhs.types import CommentLoadConfig

logger = logging.getLogger(__name__)

DEFAULT_BITBROWSER_API = "http://127.0.0.1:54345"
DEFAULT_API_KEY = "efb3b5286ce84011a9df96c660b27bd3"
DEFAULT_PROFILE_ID = "074e3ee40c95497da490a44a87473676"


def run(
    feed_id: str,
    xsec_token: str,
    load_comments: bool = True,
    max_comments: int = 20,
) -> dict:
    """获取帖子详情。

    Args:
        feed_id: 帖子 ID（从搜索结果或推荐列表获取）
        xsec_token: 安全令牌（从搜索结果或推荐列表获取）
        load_comments: 是否加载评论
        max_comments: 最大评论数量（0=不限）
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

        config = CommentLoadConfig(
            click_more_replies=True,
            max_replies_threshold=10,
            max_comment_items=max_comments,
            scroll_speed="normal",
        )

        logger.info("获取帖子详情: %s", feed_id)
        response = get_feed_detail(
            page=page,
            feed_id=feed_id,
            xsec_token=xsec_token,
            load_all_comments=load_comments,
            config=config,
        )

        note = response.note
        comments = response.comments

        return {
            "success": True,
            "note": {
                "id": note.note_id,
                "title": note.title,
                "desc": note.desc,
                "type": note.type,
                "time": note.time,
                "ip_location": note.ip_location,
                "user": {
                    "user_id": note.user.user_id,
                    "nickname": note.user.nickname or note.user.nick_name,
                    "avatar": note.user.avatar,
                },
                "interact_info": {
                    "liked": note.interact_info.liked,
                    "liked_count": note.interact_info.liked_count,
                    "collected": note.interact_info.collected,
                    "collected_count": note.interact_info.collected_count,
                    "comment_count": note.interact_info.comment_count,
                    "shared_count": note.interact_info.shared_count,
                },
                "images": [
                    {
                        "width": img.width,
                        "height": img.height,
                        "url": img.url_default or img.url_pre,
                    }
                    for img in note.image_list
                ],
            },
            "comments": {
                "total": len(comments.list_),
                "has_more": comments.has_more,
                "list": [
                    {
                        "id": c.id,
                        "content": c.content,
                        "like_count": c.like_count,
                        "create_time": c.create_time,
                        "ip_location": c.ip_location,
                        "user": {
                            "user_id": c.user_info.user_id,
                            "nickname": c.user_info.nickname or c.user_info.nick_name,
                        },
                        "sub_comment_count": c.sub_comment_count,
                        "sub_comments": [
                            {
                                "id": sc.id,
                                "content": sc.content,
                                "user": {
                                    "user_id": sc.user_info.user_id,
                                    "nickname": sc.user_info.nickname or sc.user_info.nick_name,
                                },
                            }
                            for sc in c.sub_comments
                        ] if c.sub_comments else [],
                    }
                    for c in comments.list_
                ],
            },
        }

    except Exception as e:
        logger.exception("获取帖子详情失败")
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        client.close()
