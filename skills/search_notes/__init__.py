"""小红书笔记搜索 Skill

使用 BitBrowser CDP 接口搜索小红书笔记，模拟人工操作避免风控。
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

# 添加 scripts 目录到路径
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from xhs.bitbrowser_cdp import BitBrowserClient
from xhs.search import search_feeds
from xhs.types import FilterOption

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_BITBROWSER_API = "http://127.0.0.1:54345"
DEFAULT_API_KEY = "efb3b5286ce84011a9df96c660b27bd3"
DEFAULT_PROFILE_ID = "074e3ee40c95497da490a44a87473676"


def run(
    keyword: str,
    sort_by: str = "最多收藏",
    note_type: str = "图文",
    publish_time: str = "一周内",
    limit: int = 5,
) -> dict:
    """执行小红书笔记搜索。

    Args:
        keyword: 搜索关键词
        sort_by: 排序方式（综合/最新/最多点赞/最多评论/最多收藏）
        note_type: 笔记类型（不限/视频/图文）
        publish_time: 发布时间（不限/一天内/一周内/半年内）
        limit: 返回结果数量（1-20）

    Returns:
        包含搜索结果的字典
    """
    # 修复 Windows 控制台编码
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # 从环境变量读取配置，或使用默认值
    bitbrowser_api = os.getenv("BITBROWSER_API", DEFAULT_BITBROWSER_API)
    api_key = os.getenv("BITBROWSER_API_KEY", DEFAULT_API_KEY)
    profile_id = os.getenv("BITBROWSER_PROFILE_ID", DEFAULT_PROFILE_ID)

    # 创建 BitBrowser 客户端
    client = BitBrowserClient(
        bitbrowser_api=bitbrowser_api,
        api_key=api_key,
        profile_id=profile_id,
    )

    try:
        # 连接到 BitBrowser
        client.connect()

        # 获取现有页面
        page = client.get_existing_page()
        if not page:
            return {
                "success": False,
                "error": "没有可用的页面，请确保 BitBrowser 已打开小红书网页",
            }

        logger.info("已连接到页面: %s", page.target_id)

        # 构建筛选条件
        filter_opt = FilterOption(
            sort_by=sort_by,
            note_type=note_type,
            publish_time=publish_time,
        )

        # 执行搜索
        logger.info("搜索关键词: %s, 筛选: %s", keyword, filter_opt)
        feeds = search_feeds(page, keyword, filter_opt)

        # 格式化结果
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
            })

        return {
            "success": True,
            "keyword": keyword,
            "total": len(feeds),
            "returned": len(results),
            "filters": {
                "sort_by": sort_by,
                "note_type": note_type,
                "publish_time": publish_time,
            },
            "results": results,
        }

    except Exception as e:
        logger.exception("搜索失败")
        return {
            "success": False,
            "error": str(e),
        }

    finally:
        client.close()


# 自然语言解析辅助函数
KEYWORD_MAP = {
    "最火的": "最多收藏",
    "最热的": "最多点赞",
    "最新的": "最新",
    "最多评论的": "最多评论",
}

TYPE_MAP = {
    "图文": "图文",
    "视频": "视频",
    "全部": "不限",
    "所有": "不限",
}

TIME_MAP = {
    "今天": "一天内",
    "24小时": "一天内",
    "最近一周": "一周内",
    "本周": "一周内",
    "最近半年": "半年内",
    "半年": "半年内",
    "全部时间": "不限",
}


def parse_natural_language(query: str) -> dict:
    """解析自然语言搜索请求。

    示例：
        "搜索高中数学最火的图文笔记，返回前5条"
        -> {"keyword": "高中数学", "sort_by": "最多收藏", "note_type": "图文", "limit": 5}
    """
    import re

    params = {
        "keyword": "",
        "sort_by": "最多收藏",
        "note_type": "图文",
        "publish_time": "一周内",
        "limit": 5,
    }

    # 提取数量
    limit_match = re.search(r'(\d+)条', query)
    if limit_match:
        params["limit"] = int(limit_match.group(1))

    # 提取排序方式
    for key, value in KEYWORD_MAP.items():
        if key in query:
            params["sort_by"] = value
            break

    # 提取笔记类型
    for key, value in TYPE_MAP.items():
        if key in query:
            params["note_type"] = value
            break

    # 提取时间范围
    for key, value in TIME_MAP.items():
        if key in query:
            params["publish_time"] = value
            break

    # 提取关键词（移除常见修饰词后的剩余部分）
    # 简单的关键词提取：取"搜索"和"笔记"之间的内容，或直接取开头
    keyword_match = re.search(r'搜索(.+?)(?:的|笔记|视频|图文|$)', query)
    if keyword_match:
        params["keyword"] = keyword_match.group(1).strip()
    else:
        # 默认取前10个字符作为关键词
        params["keyword"] = query[:20].strip()

    return params


if __name__ == "__main__":
    # 测试运行
    result = run(
        keyword="高中数学",
        sort_by="最多收藏",
        note_type="图文",
        publish_time="一周内",
        limit=5,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
