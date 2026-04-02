"""小红书自动化 Skills

封装 xiaohongshu-skills 为可复用的 Claude Skills。
"""

__version__ = "0.1.0"

from search_notes import run as search_notes

__all__ = ["search_notes"]
