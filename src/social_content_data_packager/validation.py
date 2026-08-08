"""Input validation for collection workspaces."""

from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from openpyxl import load_workbook

from .transcript import normalize_transcript

REQUIRED_TEXT_FIELDS = (
    "平台",
    "笔记编号",
    "标题",
    "作者",
    "笔记正文",
    "公开链接",
    "授权依据",
)
AUTHORIZATION_VALUES = {"公开内容", "本人所有", "明确授权"}
COMMENT_CONTENT_HEADERS = {"评论内容", "评论", "内容"}


def probe_video(
    path: str | Path,
    runner: Callable = subprocess.run,
) -> None:
    """Require FFprobe to recognize at least one video stream."""
    path = Path(path)
    if runner is subprocess.run and shutil.which("ffprobe") is None:
        raise RuntimeError("缺少 FFprobe，无法验证视频素材")
    completed = runner(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        result = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        result = {}
    streams = result.get("streams")
    if completed.returncode != 0 or not isinstance(streams, list) or not streams:
        detail = (completed.stderr or "FFprobe 未识别到视频流").strip()
        raise ValueError(f"视频素材不是有效视频：{detail}")


def validate_metadata(metadata: object) -> dict:
    if not isinstance(metadata, dict):
        raise ValueError("元数据根节点必须是 JSON 对象")

    errors = []
    for field in REQUIRED_TEXT_FIELDS:
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field}不能为空")
        elif value.strip().startswith("请填写"):
            errors.append(f"{field}不能使用占位值")

    authorization = metadata.get("授权依据")
    if authorization and authorization not in AUTHORIZATION_VALUES:
        allowed = "、".join(sorted(AUTHORIZATION_VALUES))
        errors.append(f"授权依据必须是：{allowed}")

    public_url = metadata.get("公开链接")
    if isinstance(public_url, str) and public_url.strip():
        parsed = urlparse(public_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("公开链接必须是有效的 HTTP 或 HTTPS 地址")

    tags = metadata.get("标签")
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        errors.append("标签必须是字符串数组")

    interactions = metadata.get("互动数据")
    if not isinstance(interactions, dict):
        errors.append("互动数据必须是对象")
    else:
        invalid_counts = [
            key
            for key, value in interactions.items()
            if value is not None
            and (isinstance(value, bool) or not isinstance(value, (int, float)))
        ]
        if invalid_counts:
            errors.append("互动数据必须为数字或 null：" + "、".join(invalid_counts))

    collected_at = metadata.get("采集时间")
    if collected_at is not None:
        if not isinstance(collected_at, str):
            errors.append("采集时间必须是 ISO 8601 字符串或 null")
        else:
            try:
                datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
            except ValueError:
                errors.append("采集时间必须使用 ISO 8601 格式")

    datatool_version = metadata.get("DATATOOL版本")
    if datatool_version is not None and not isinstance(datatool_version, str):
        errors.append("DATATOOL版本必须是字符串或 null")

    if errors:
        raise ValueError("元数据校验失败：\n- " + "\n- ".join(errors))
    return metadata


def validate_comments(path: Path) -> int:
    try:
        workbook = load_workbook(path, read_only=True, data_only=False)
    except Exception as error:
        raise ValueError(f"原始评论工作簿无法读取：{error}") from error
    try:
        sheet = workbook[workbook.sheetnames[0]]
        rows = sheet.iter_rows(values_only=True)
        header = next(rows, None)
        if not header:
            raise ValueError("原始评论工作簿缺少表头")
        normalized = {str(value).strip() for value in header if value is not None}
        if not normalized.intersection(COMMENT_CONTENT_HEADERS):
            expected = "、".join(sorted(COMMENT_CONTENT_HEADERS))
            raise ValueError(f"评论表头缺少评论内容列，支持：{expected}")
        return sum(1 for row in rows if any(value is not None for value in row))
    finally:
        workbook.close()


def validate_workspace(
    workspace: str | Path,
    media_probe: Callable[[Path], None] = probe_video,
) -> dict:
    workspace = Path(workspace)
    input_dir = workspace / "输入"
    metadata_path = input_dir / "元数据.json"
    video_path = input_dir / "视频素材.mp4"
    if not metadata_path.is_file():
        raise FileNotFoundError(f"缺少元数据文件：{metadata_path}")
    if not video_path.is_file():
        raise FileNotFoundError(f"缺少视频文件：{video_path}")

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"元数据.json 不是有效的 UTF-8 JSON：{error}") from error
    metadata = validate_metadata(metadata)
    media_probe(video_path)

    comments_path = input_dir / "原始评论.xlsx"
    comment_rows = validate_comments(comments_path) if comments_path.is_file() else 0
    transcript_path = input_dir / "视频文案（分段数据）.json"
    segment_count = 0
    if transcript_path.is_file():
        try:
            transcript = json.loads(transcript_path.read_text(encoding="utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError(f"视频文案分段数据不是有效 JSON：{error}") from error
        segment_count = len(normalize_transcript(transcript))

    return {
        "平台": metadata["平台"],
        "标题": metadata["标题"],
        "评论行数": comment_rows,
        "视频文案分段数": segment_count,
    }
