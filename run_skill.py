#!/usr/bin/env python3
"""小红书 Skills 命令行入口

完整复刻原 xiaohongshu-mcp 的 11 个工具功能。

用法：
    python run_skill.py check_login
    python run_skill.py search_notes --keyword "高中数学"
    python run_skill.py get_feeds --limit 10
    python run_skill.py get_feed_detail --feed_id "xxx" --xsec_token "xxx"
    python run_skill.py get_user_profile --user_id "xxx" --xsec_token "xxx"
    python run_skill.py post_comment --feed_id "xxx" --xsec_token "xxx" --content "赞！"
    python run_skill.py reply_comment --feed_id "xxx" --xsec_token "xxx" --comment_id "xxx" --content "谢谢！"
    python run_skill.py interact --feed_id "xxx" --xsec_token "xxx" --action like
    python run_skill.py publish_image --title "xxx" --content "xxx" --image_paths "[\"a.jpg\",\"b.jpg\"]"
    python run_skill.py publish_video --title "xxx" --content "xxx" --video_path "video.mp4"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 添加 skills 目录到路径
SKILLS_DIR = Path(__file__).parent / "skills"
sys.path.insert(0, str(SKILLS_DIR))

import check_login
import search_notes
import get_feeds
import get_feed_detail
import get_user_profile
import post_comment
import reply_comment
import interact
import publish_image
import publish_video


SKILL_MAP = {
    "check_login": check_login.run,
    "search_notes": search_notes.run,
    "get_feeds": get_feeds.run,
    "get_feed_detail": get_feed_detail.run,
    "get_user_profile": get_user_profile.run,
    "post_comment": post_comment.run,
    "reply_comment": reply_comment.run,
    "interact": interact.run,
    "publish_image": publish_image.run,
    "publish_video": publish_video.run,
}


def main():
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="小红书自动化 Skills (复刻 xiaohongshu-mcp)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
可用 Skills:
  check_login      检查登录状态
  search_notes     搜索内容
  get_feeds        获取推荐列表
  get_feed_detail  获取帖子详情
  get_user_profile 获取用户主页
  post_comment     发表评论
  reply_comment    回复评论
  interact         点赞/收藏 (action: like/unlike/favorite/unfavorite)
  publish_image    发布图文
  publish_video    发布视频

示例:
  python run_skill.py check_login
  python run_skill.py search_notes -k "Python学习" --limit 10
  python run_skill.py get_feeds --limit 5
  python run_skill.py get_feed_detail --feed_id "xxx" --xsec_token "xxx"
  python run_skill.py interact --feed_id "xxx" --xsec_token "xxx" --action like
        """,
    )

    parser.add_argument("skill", choices=list(SKILL_MAP.keys()), help="Skill 名称")

    # 通用参数
    parser.add_argument("--keyword", "-k", help="搜索关键词")
    parser.add_argument("--limit", type=int, help="返回数量限制")
    parser.add_argument("--feed_id", help="帖子 ID")
    parser.add_argument("--xsec_token", help="安全令牌")
    parser.add_argument("--user_id", help="用户 ID")
    parser.add_argument("--comment_id", help="评论 ID")
    parser.add_argument("--content", help="评论/回复/正文内容")
    parser.add_argument("--action", default="like", help="互动类型")
    parser.add_argument("--title", help="标题")
    parser.add_argument("--desc", dest="content_desc", help="正文内容")
    parser.add_argument("--image_paths", help="图片路径 JSON 数组")
    parser.add_argument("--video_path", help="视频路径")
    parser.add_argument("--tags", help="标签 JSON 数组")
    parser.add_argument("--schedule_time", help="定时发布时间")
    parser.add_argument("--is_original", type=bool, default=False, help="是否原创")
    parser.add_argument("--visibility", default="", help="可见范围")
    parser.add_argument("--load_comments", type=bool, default=True, help="是否加载评论")
    parser.add_argument("--max_comments", type=int, default=20, help="最大评论数")

    args = parser.parse_args()

    # 构建参数
    skill_func = SKILL_MAP[args.skill]
    kwargs = {}

    # 根据 skill 添加参数
    if args.skill == "check_login":
        pass
    elif args.skill == "search_notes":
        if not args.keyword:
            print("错误: search_notes 需要 --keyword 参数", file=sys.stderr)
            sys.exit(1)
        kwargs = {"keyword": args.keyword}
        if args.limit:
            kwargs["limit"] = args.limit
    elif args.skill in ("get_feed_detail",):
        if not args.feed_id or not args.xsec_token:
            print("错误: 需要 --feed_id 和 --xsec_token 参数", file=sys.stderr)
            sys.exit(1)
        kwargs = {
            "feed_id": args.feed_id,
            "xsec_token": args.xsec_token,
            "load_comments": args.load_comments,
            "max_comments": args.max_comments,
        }
    elif args.skill == "get_feeds":
        if args.limit:
            kwargs["limit"] = args.limit
    elif args.skill == "get_user_profile":
        if not args.user_id or not args.xsec_token:
            print("错误: 需要 --user_id 和 --xsec_token 参数", file=sys.stderr)
            sys.exit(1)
        kwargs = {
            "user_id": args.user_id,
            "xsec_token": args.xsec_token,
        }
        if args.limit:
            kwargs["limit"] = args.limit
    elif args.skill == "post_comment":
        if not args.feed_id or not args.xsec_token or not args.content:
            print("错误: 需要 --feed_id, --xsec_token 和 --content 参数", file=sys.stderr)
            sys.exit(1)
        kwargs = {
            "feed_id": args.feed_id,
            "xsec_token": args.xsec_token,
            "content": args.content,
        }
    elif args.skill == "reply_comment":
        if not args.feed_id or not args.xsec_token or not args.content:
            print("错误: 需要 --feed_id, --xsec_token 和 --content 参数", file=sys.stderr)
            sys.exit(1)
        kwargs = {
            "feed_id": args.feed_id,
            "xsec_token": args.xsec_token,
            "content": args.content,
        }
        if args.comment_id:
            kwargs["comment_id"] = args.comment_id
    elif args.skill == "interact":
        if not args.feed_id or not args.xsec_token:
            print("错误: 需要 --feed_id 和 --xsec_token 参数", file=sys.stderr)
            sys.exit(1)
        kwargs = {
            "feed_id": args.feed_id,
            "xsec_token": args.xsec_token,
            "action": args.action,
        }
    elif args.skill == "publish_image":
        if not args.title or not args.content_desc or not args.image_paths:
            print("错误: 需要 --title, --desc 和 --image_paths 参数", file=sys.stderr)
            sys.exit(1)
        kwargs = {
            "title": args.title,
            "content": args.content_desc,
            "image_paths": json.loads(args.image_paths),
        }
        if args.tags:
            kwargs["tags"] = json.loads(args.tags)
        if args.schedule_time:
            kwargs["schedule_time"] = args.schedule_time
        kwargs["is_original"] = args.is_original
        kwargs["visibility"] = args.visibility
    elif args.skill == "publish_video":
        if not args.title or not args.content_desc or not args.video_path:
            print("错误: 需要 --title, --desc 和 --video_path 参数", file=sys.stderr)
            sys.exit(1)
        kwargs = {
            "title": args.title,
            "content": args.content_desc,
            "video_path": args.video_path,
        }
        if args.tags:
            kwargs["tags"] = json.loads(args.tags)
        if args.schedule_time:
            kwargs["schedule_time"] = args.schedule_time
        kwargs["visibility"] = args.visibility

    # 执行
    result = skill_func(**kwargs)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)

    # 保存结果
    if result.get("success"):
        with open("skill_output.json", "w", encoding="utf-8") as f:
            f.write(output)

    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
