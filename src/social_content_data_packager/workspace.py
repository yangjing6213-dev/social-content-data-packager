"""Workspace initialization."""

from __future__ import annotations

import json
from pathlib import Path

METADATA_TEMPLATE: dict[str, object] = {
    "平台": "小红书",
    "笔记编号": "请填写平台内容编号",
    "标题": "请填写内容标题",
    "作者": "请填写作者",
    "笔记正文": "请填写页面正文",
    "标签": [],
    "公开链接": "请填写公开内容链接",
    "授权依据": "公开内容",
    "采集时间": None,
    "DATATOOL版本": None,
    "互动数据": {
        "点赞": None,
        "收藏": None,
        "页面评论": None,
        "实际导出评论": None,
    },
}

INPUT_GUIDE = """请使用 DATATOOL 采集公开或已授权内容，并按以下名称放入本目录：

必需：
- 元数据.json
- 视频素材.mp4

可选：
- 原始评论.xlsx
- 封面图片.webp（也支持 .jpg、.jpeg、.png）
- 视频文案（分段数据）.json

视频文案可通过 social-content-packager transcribe <任务目录> 自动生成。
授权依据只能填写“公开内容”“本人所有”或“明确授权”。
采集时间使用 ISO 8601 格式；无法确认 DATATOOL 版本时保留 null。
请勿提交账号凭据、浏览器 profile、Cookie 或未授权个人数据。
"""


def initialize_workspace(path: str | Path) -> Path:
    workspace = Path(path)
    if workspace.exists() and any(workspace.iterdir()):
        raise ValueError(f"拒绝覆盖非空目录：{workspace}")

    input_dir = workspace / "输入"
    output_dir = workspace / "输出"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "元数据.json").write_text(
        json.dumps(METADATA_TEMPLATE, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (input_dir / "放置采集文件说明.txt").write_text(INPUT_GUIDE, encoding="utf-8-sig")
    return workspace
