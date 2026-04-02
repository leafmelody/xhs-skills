# 小红书自动化 Skills

小红书自动化 Skills，基于 BitBrowser CDP 实现。复刻了原 MCP 的 11 个工具功能。

## 核心特性

- **完整功能**: 复刻原 MCP 全部 11 个工具
- **防风控设计**: 使用 BitBrowser 指纹浏览器，模拟人工操作
- **类型安全**: 完整的数据类型定义和验证
- **命令行支持**: 统一的 CLI 入口，方便调用

## 已实现的 Skills（11个）

| # | Skill | 功能 | 原 MCP 对应 |
|---|-------|------|------------|
| 1 | [check_login](#check_login) | 检查登录状态 | ✅ |
| 2 | [search_notes](#search_notes) | 搜索内容 | ✅ |
| 3 | [get_feeds](#get_feeds) | 获取推荐列表 | ✅ |
| 4 | [get_feed_detail](#get_feed_detail) | 获取帖子详情 | ✅ |
| 5 | [get_user_profile](#get_user_profile) | 获取用户主页 | ✅ |
| 6 | [post_comment](#post_comment) | 发表评论 | ✅ |
| 7 | [reply_comment](#reply_comment) | 回复评论 | ✅ |
| 8 | [interact](#interact) | 点赞/收藏 | ✅ |
| 9 | [publish_image](#publish_image) | 发布图文 | ✅ |
| 10 | [publish_video](#publish_video) | 发布视频 | ✅ |

---

## 详细使用说明

### check_login

检查当前登录状态。

```bash
python run_skill.py check_login
```

**返回:**
```json
{
  "success": true,
  "logged_in": true,
  "nickname": "用户名"
}
```

---

### search_notes

搜索小红书内容。

```bash
python run_skill.py search_notes --keyword "高中数学" --limit 10
```

**参数:**
- `keyword`: 搜索关键词（必填）
- `sort_by`: 排序方式（综合/最新/最多点赞/最多评论/最多收藏）
- `note_type`: 笔记类型（不限/视频/图文）
- `publish_time`: 发布时间（不限/一天内/一周内/半年内）
- `limit`: 返回数量

---

### get_feeds

获取首页推荐列表。

```bash
python run_skill.py get_feeds --limit 10
```

**参数:**
- `limit`: 返回数量（默认20）

---

### get_feed_detail

获取帖子完整详情，包括评论。

```bash
python run_skill.py get_feed_detail \
  --feed_id "69c64eff000000002100459f" \
  --xsec_token "xxx" \
  --max_comments 20
```

**参数:**
- `feed_id`: 帖子 ID（必填）
- `xsec_token`: 安全令牌（必填）
- `load_comments`: 是否加载评论（默认true）
- `max_comments`: 最大评论数（默认20）

**注意:** `feed_id` 和 `xsec_token` 可从搜索结果或推荐列表中获取。

---

### get_user_profile

获取用户主页信息。

```bash
python run_skill.py get_user_profile \
  --user_id "5f3c8b9a000000000101f1e0" \
  --xsec_token "xxx" \
  --limit 20
```

**参数:**
- `user_id`: 用户 ID（必填）
- `xsec_token`: 安全令牌（必填）
- `limit`: 返回笔记数量限制

---

### post_comment

发表评论到帖子。

```bash
python run_skill.py post_comment \
  --feed_id "xxx" \
  --xsec_token "xxx" \
  --content "写得太好了！"
```

**参数:**
- `feed_id`: 帖子 ID（必填）
- `xsec_token`: 安全令牌（必填）
- `content`: 评论内容（必填，不超过1000字）

---

### reply_comment

回复帖子下的指定评论。

```bash
python run_skill.py reply_comment \
  --feed_id "xxx" \
  --xsec_token "xxx" \
  --comment_id "xxx" \
  --content "谢谢你的评论！"
```

**参数:**
- `feed_id`: 帖子 ID（必填）
- `xsec_token`: 安全令牌（必填）
- `content`: 回复内容（必填）
- `comment_id`: 评论 ID（优先使用）
- `user_id`: 用户 ID（备选）

**注意:** `comment_id` 和 `user_id` 至少提供一个。

---

### interact

点赞/取消点赞、收藏/取消收藏。

```bash
# 点赞
python run_skill.py interact --feed_id "xxx" --xsec_token "xxx" --action like

# 取消点赞
python run_skill.py interact --feed_id "xxx" --xsec_token "xxx" --action unlike

# 收藏
python run_skill.py interact --feed_id "xxx" --xsec_token "xxx" --action favorite

# 取消收藏
python run_skill.py interact --feed_id "xxx" --xsec_token "xxx" --action unfavorite
```

**参数:**
- `feed_id`: 帖子 ID（必填）
- `xsec_token`: 安全令牌（必填）
- `action`: 操作类型（like/unlike/favorite/unfavorite）

**特性:** 智能检测当前状态，已点赞时跳过点赞，避免重复操作。

---

### publish_image

发布图文内容。

```bash
python run_skill.py publish_image \
  --title "我的旅行日记" \
  --desc "今天去了故宫，太壮观了！" \
  --image_paths '["/Users/me/photos/1.jpg", "/Users/me/photos/2.jpg"]' \
  --tags '["旅行", "故宫", "北京"]' \
  --is_original true
```

**参数:**
- `title`: 标题（必填，不超过20字）
- `desc`: 正文内容（必填，不超过1000字）
- `image_paths`: 图片路径列表 JSON（必填，本地绝对路径）
- `tags`: 标签列表 JSON（可选，最多10个）
- `schedule_time`: 定时发布时间（ISO8601格式，可选）
- `is_original`: 是否声明原创（默认false）
- `visibility`: 可见范围（公开可见/仅自己可见/仅互关好友可见）

---

### publish_video

发布视频内容。

```bash
python run_skill.py publish_video \
  --title "我的vlog" \
  --desc "今天记录了美好的一天" \
  --video_path "/Users/me/videos/day1.mp4" \
  --tags '["vlog", "日常"]'
```

**参数:**
- `title`: 标题（必填，不超过20字）
- `desc`: 正文内容（必填，不超过1000字）
- `video_path`: 视频路径（必填，本地绝对路径）
- `tags`: 标签列表 JSON（可选）
- `schedule_time`: 定时发布时间（可选）
- `visibility`: 可见范围（可选）

**注意:** 仅支持本地视频文件，不支持 HTTP 链接。

---

## Python 调用

```python
from skills import search_notes, get_feed_detail, interact

# 搜索笔记
result = search_notes(keyword="Python学习", limit=5)

# 获取详情
note = result["results"][0]
detail = get_feed_detail(
    feed_id=note["id"],
    xsec_token=note["xsec_token"],
    max_comments=10
)

# 点赞
interact(
    feed_id=note["id"],
    xsec_token=note["xsec_token"],
    action="like"
)
```

---

## 环境配置

### 1. 启动 BitBrowser

确保 BitBrowser 已启动并启用 API 服务（默认端口 54345）。

### 2. 配置环境变量（可选）

```bash
export BITBROWSER_API="http://127.0.0.1:54345"
export BITBROWSER_API_KEY="your-api-key"
export BITBROWSER_PROFILE_ID="your-profile-id"
```

### 3. 安装依赖

```bash
cd xhs-skills
pip install requests websockets
```

---

## 防爬虫机制

1. **指纹浏览器**: 使用 BitBrowser 隔离真实浏览器环境
2. **随机延迟**: 操作间添加随机延迟（300-600ms）模拟人工
3. **DOM 稳定检测**: 等待页面完全加载后再操作
4. **真实 CDP 协议**: 直接调用 Chrome DevTools Protocol
5. **智能等待**: 二维码验证等场景自动等待重试

---

## 注意事项

- 首次使用需在 BitBrowser 中登录小红书账号
- 小红书同一账号不允许在多个网页端登录
- 标题不超过 20 字，正文不超过 1000 字
- 建议控制操作频率，避免触发风控
- 遵守小红书平台规则和相关法律法规
