"""小红书自动化 Skills

完整复刻原 xiaohongshu-mcp 的 11 个工具功能：
1. check_login - 检查登录状态
2. search_notes - 搜索内容
3. get_feeds - 获取推荐列表
4. get_feed_detail - 获取帖子详情
5. get_user_profile - 获取用户主页
6. post_comment - 发表评论
7. reply_comment - 回复评论
8. interact - 点赞/收藏
9. publish_image - 发布图文
10. publish_video - 发布视频
"""

__version__ = "2.0.0"

from check_login import run as check_login
from search_notes import run as search_notes
from get_feeds import run as get_feeds
from get_feed_detail import run as get_feed_detail
from get_user_profile import run as get_user_profile
from post_comment import run as post_comment
from reply_comment import run as reply_comment
from interact import run as interact
from publish_image import run as publish_image
from publish_video import run as publish_video

__all__ = [
    "check_login",
    "search_notes",
    "get_feeds",
    "get_feed_detail",
    "get_user_profile",
    "post_comment",
    "reply_comment",
    "interact",
    "publish_image",
    "publish_video",
]
