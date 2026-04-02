# 小红书自动化 Skills

基于 xiaohongshu-skills + BitBrowser CDP 的小红书自动化 Skill 集合。

## 核心特性

- **防风控设计**: 使用 BitBrowser 指纹浏览器，模拟人工操作
- **自然语言支持**: 支持自然语言查询解析
- **类型安全**: 完整的数据类型定义和验证
- **易扩展**: 模块化设计，方便添加新 Skill

## 已实现的 Skills

### search_notes - 搜索笔记

搜索小红书笔记，支持多种筛选条件。

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| keyword | string | 必填 | 搜索关键词 |
| sort_by | string | 最多收藏 | 排序方式：综合/最新/最多点赞/最多评论/最多收藏 |
| note_type | string | 图文 | 笔记类型：不限/视频/图文 |
| publish_time | string | 一周内 | 发布时间：不限/一天内/一周内/半年内 |
| limit | integer | 5 | 返回数量（1-20） |

**使用示例：**

```bash
# 标准调用
python run_skill.py search_notes --keyword "高中数学"
python run_skill.py search_notes -k "Python学习" --sort-by "最多点赞" --limit 10

# 自然语言调用
python run_skill.py "搜索高中数学最火的图文笔记，返回前5条"
python run_skill.py "查找Python学习视频，按最多点赞排序"
python run_skill.py "搜索一周内发布的健身图文，采集10条"
```

**Python 调用：**

```python
from skills.search_notes import run as search_notes

result = search_notes(
    keyword="高中数学",
    sort_by="最多收藏",
    note_type="图文",
    publish_time="一周内",
    limit=5,
)

if result["success"]:
    for note in result["results"]:
        print(f"{note['title']} - {note['author']}")
```

**返回格式：**

```json
{
  "success": true,
  "keyword": "高中数学",
  "total": 44,
  "returned": 5,
  "filters": {
    "sort_by": "最多收藏",
    "note_type": "图文",
    "publish_time": "一周内"
  },
  "results": [
    {
      "id": "69c64eff000000002100459f",
      "title": "无限接近26高考数学的一套卷",
      "author": "北大胡源讲数学—消除学习认知差",
      "likes": "13034",
      "collects": "7774",
      "comments": "892",
      "link": "https://www.xiaohongshu.com/explore/69c64eff000000002100459f?xsec_token=..."
    }
  ]
}
```

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

## 防爬虫机制

本实现采用以下策略避免被平台风控：

1. **指纹浏览器**: 使用 BitBrowser 隔离真实浏览器环境
2. **随机延迟**: 操作间添加随机延迟模拟人工
3. **DOM 稳定检测**: 等待页面完全加载后再操作
4. **真实 CDP 协议**: 直接调用 Chrome DevTools Protocol，非模拟点击
5. **IP 隔离**: 建议配合代理 IP 使用

## 扩展新 Skill

参考 `search_notes/` 目录结构：

1. 在 `skills/` 下创建新目录
2. 创建 `skill.yaml` 定义接口
3. 创建 `__init__.py` 实现逻辑
4. 在 `run_skill.py` 中添加命令行支持

## 注意事项

- 首次使用需在 BitBrowser 中登录小红书账号
- 建议控制采集频率，避免过于频繁的请求
- 遵守小红书平台规则和相关法律法规
