#!/usr/bin/env python3
"""小红书 Skills 命令行入口

用法：
    python run_skill.py search_notes --keyword "高中数学"
    python run_skill.py search_notes -k "高中数学" --sort-by "最多收藏"
    python run_skill.py "搜索高中数学最火的图文笔记，返回前5条"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 添加 skills 目录到路径
SKILLS_DIR = Path(__file__).parent / "skills"
sys.path.insert(0, str(SKILLS_DIR))

from search_notes import run as search_notes, parse_natural_language


def main():
    # 修复 Windows 控制台编码
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="小红书自动化 Skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s search_notes --keyword "高中数学"
  %(prog)s search_notes -k "Python学习" --sort-by "最多点赞" --limit 10
  %(prog)s "搜索高中数学最火的图文笔记，返回前5条"
        """,
    )

    parser.add_argument(
        "command",
        nargs="?",
        help="Skill 名称或自然语言查询",
    )

    # search_notes 参数
    parser.add_argument("--keyword", "-k", help="搜索关键词")
    parser.add_argument("--sort-by", default="最多收藏", help="排序方式")
    parser.add_argument("--note-type", default="图文", help="笔记类型")
    parser.add_argument("--publish-time", default="一周内", help="发布时间")
    parser.add_argument("--limit", "-n", type=int, default=5, help="返回数量")

    # 解析参数
    args, unknown = parser.parse_known_args()

    # 如果没有提供命令，显示帮助
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 判断是自然语言还是 Skill 名称
    if args.command == "search_notes":
        # 标准 Skill 调用
        if not args.keyword:
            print("错误：必须提供 --keyword 参数", file=sys.stderr)
            sys.exit(1)

        result = search_notes(
            keyword=args.keyword,
            sort_by=args.sort_by,
            note_type=args.note_type,
            publish_time=args.publish_time,
            limit=args.limit,
        )
    else:
        # 尝试作为自然语言解析
        query = args.command
        params = parse_natural_language(query)

        # 命令行参数覆盖解析结果
        if args.keyword:
            params["keyword"] = args.keyword
        if args.sort_by != "最多收藏":
            params["sort_by"] = args.sort_by
        if args.note_type != "图文":
            params["note_type"] = args.note_type
        if args.publish_time != "一周内":
            params["publish_time"] = args.publish_time
        if args.limit != 5:
            params["limit"] = args.limit

        print(f"解析参数: {params}")
        result = search_notes(**params)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)

    # 保存到文件
    if result.get("success"):
        output_file = "skill_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\n结果已保存到: {output_file}")

    # 返回退出码
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
