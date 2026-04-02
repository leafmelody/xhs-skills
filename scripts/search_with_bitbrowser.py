"""使用 BitBrowser 搜索小红书笔记

替代原生的 Chrome + 扩展方案，直接使用 BitBrowser 的 CDP 接口。
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

# 添加父目录到路径
sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

from xhs.bitbrowser_cdp import BitBrowserClient
from xhs.search import search_feeds
from xhs.types import FilterOption

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("xhs-search")


def main():
    # 修复 Windows 控制台编码
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="小红书搜索工具（BitBrowser 版）")
    parser.add_argument("--keyword", "-k", required=True, help="搜索关键词")
    parser.add_argument("--sort-by", default="最多收藏", help="排序：综合|最新|最多点赞|最多评论|最多收藏")
    parser.add_argument("--note-type", default="图文", help="类型：不限|视频|图文")
    parser.add_argument("--publish-time", default="一周内", help="时间：不限|一天内|一周内|半年内")
    parser.add_argument("--bitbrowser-api", default="http://127.0.0.1:54345", help="BitBrowser API 地址")
    parser.add_argument("--api-key", default="efb3b5286ce84011a9df96c660b27bd3", help="BitBrowser API Key")
    parser.add_argument("--profile-id", default="074e3ee40c95497da490a44a87473676", help="BitBrowser Profile ID")
    parser.add_argument("--limit", "-n", type=int, default=5, help="返回结果数量")

    args = parser.parse_args()

    # 创建 BitBrowser 客户端
    client = BitBrowserClient(
        bitbrowser_api=args.bitbrowser_api,
        api_key=args.api_key,
        profile_id=args.profile_id,
    )

    try:
        # 连接到 BitBrowser
        client.connect()

        # 获取现有页面
        page = client.get_existing_page()
        if not page:
            print(json.dumps({"error": "没有可用的页面，请确保 BitBrowser 已打开小红书"}, ensure_ascii=False))
            sys.exit(1)

        logger.info("已连接到页面: %s", page.target_id)

        # 构建筛选条件
        filter_opt = FilterOption(
            sort_by=args.sort_by,
            note_type=args.note_type,
            publish_time=args.publish_time,
        )

        # 执行搜索
        logger.info("搜索关键词: %s, 筛选: %s", args.keyword, filter_opt)
        feeds = search_feeds(page, args.keyword, filter_opt)

        # 格式化结果
        results = []
        for feed in feeds[:args.limit]:
            results.append({
                "id": feed.id,
                "title": feed.note_card.display_title or "（无标题）",
                "author": feed.note_card.user.nickname or feed.note_card.user.nick_name or "未知",
                "likes": feed.note_card.interact_info.liked_count,
                "collects": feed.note_card.interact_info.collected_count,
                "link": f"https://www.xiaohongshu.com/explore/{feed.id}?xsec_token={feed.xsec_token}",
            })

        output = {
            "success": True,
            "keyword": args.keyword,
            "total": len(feeds),
            "results": results,
        }

        # 输出到文件避免编码问题
        output_file = "search_result.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_file}")
        print(json.dumps(output, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.exception("搜索失败")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    finally:
        client.close()


if __name__ == "__main__":
    main()
