"""Auditable data package builder."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import tempfile
import uuid
import zipfile
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

from . import __version__
from .transcript import format_timestamp, normalize_transcript
from .validation import probe_video, validate_workspace
from .verification import verify_archive

SCHEMA_VERSION = "1.0"
COMMENT_IDENTITY_HEADERS = {
    "评论人",
    "用户",
    "用户名",
    "昵称",
    "用户ID",
    "账号",
    "主页",
    "IP属地",
    "位置",
    "联系方式",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]+', "_", value.strip())
    cleaned = re.sub(r"\s+", "_", cleaned).strip("._")
    return cleaned[:48] or "未命名内容"


def set_text(cell, value) -> None:
    cell.value = value
    if isinstance(value, str):
        cell.data_type = "s"


def find_cover(input_dir: Path) -> Path | None:
    for suffix in (".webp", ".jpg", ".jpeg", ".png"):
        candidate = input_dir / f"封面图片{suffix}"
        if candidate.is_file():
            return candidate
    return None


def read_comments(path: Path | None) -> list[tuple]:
    if path is None or not path.is_file():
        return []
    workbook = load_workbook(path, read_only=True, data_only=False)
    sheet = workbook[workbook.sheetnames[0]]
    rows = [tuple(cell.value for cell in row) for row in sheet.iter_rows()]
    workbook.close()
    return rows


def anonymize_comment_rows(comments: list[tuple]) -> list[tuple]:
    if not comments:
        return comments
    identity_columns = {
        index
        for index, value in enumerate(comments[0])
        if str(value).strip() in COMMENT_IDENTITY_HEADERS
    }
    if not identity_columns:
        return comments
    anonymized = [comments[0]]
    for row in comments[1:]:
        anonymized.append(
            tuple(
                "[已脱敏]" if index in identity_columns and value is not None else value
                for index, value in enumerate(row)
            )
        )
    return anonymized


def create_workbook(
    path: Path,
    metadata: dict,
    comments: list[tuple],
    segments: list[dict],
) -> None:
    workbook = Workbook()
    metadata_sheet = workbook.active
    metadata_sheet.title = "元数据"
    metadata_sheet.append(["字段", "值"])
    for row_index, (key, value) in enumerate(metadata.items(), start=2):
        display = (
            json.dumps(value, ensure_ascii=False)
            if isinstance(value, (dict, list))
            else value
        )
        set_text(metadata_sheet.cell(row_index, 1), key)
        set_text(metadata_sheet.cell(row_index, 2), display)

    comments_sheet = workbook.create_sheet("评论数据")
    if comments:
        for row_index, row in enumerate(comments, start=1):
            for column_index, value in enumerate(row, start=1):
                set_text(comments_sheet.cell(row_index, column_index), value)
    else:
        comments_sheet.append(["评论内容", "评论人", "评论时间", "点赞数", "回复数"])

    transcript_sheet = workbook.create_sheet("视频文案")
    transcript_sheet.append(["序号", "开始时间", "结束时间", "文案"])
    for row_index, segment in enumerate(segments, start=2):
        values = (
            segment["序号"],
            format_timestamp(segment["开始秒"], "."),
            format_timestamp(segment["结束秒"], "."),
            segment["文案"],
        )
        for column_index, value in enumerate(values, start=1):
            set_text(transcript_sheet.cell(row_index, column_index), value)

    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    widths = {
        "元数据": {"A": 28, "B": 100},
        "评论数据": {"A": 80, "B": 24, "C": 24, "D": 12, "E": 12},
        "视频文案": {"A": 10, "B": 16, "C": 16, "D": 100},
    }
    for sheet in workbook:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
        for column, width in widths[sheet.title].items():
            sheet.column_dimensions[column].width = width
    metadata_sheet.column_dimensions["B"].width = 100
    for row in comments_sheet.iter_rows(min_row=2):
        row[0].alignment = Alignment(wrap_text=True, vertical="top")
    for row in transcript_sheet.iter_rows(min_row=2):
        row[3].alignment = Alignment(wrap_text=True, vertical="top")
    workbook.save(path)


def detect_git_commit() -> str | None:
    configured = os.environ.get("SOCIAL_CONTENT_PACKAGER_COMMIT")
    if configured:
        return configured
    root = Path(__file__).resolve().parents[2]
    if not (root / ".git").exists() or shutil.which("git") is None:
        return None
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    commit = completed.stdout.strip()
    return commit if completed.returncode == 0 and commit else None


def build_package(
    workspace: str | Path,
    output_dir: str | Path | None = None,
    now: datetime | None = None,
    include_raw_comments: bool = False,
    anonymize_comments: bool = False,
    media_probe: Callable[[Path], None] = probe_video,
) -> Path:
    if include_raw_comments and anonymize_comments:
        raise ValueError("评论脱敏与包含未净化原始评论不能同时启用")
    workspace = Path(workspace)
    input_dir = workspace / "输入"
    output_dir = Path(output_dir) if output_dir else workspace / "输出"
    validate_workspace(workspace, media_probe=media_probe)
    metadata_path = input_dir / "元数据.json"
    video_path = input_dir / "视频素材.mp4"

    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    transcript_path = input_dir / "视频文案（分段数据）.json"
    if transcript_path.is_file():
        transcript_data = json.loads(transcript_path.read_text(encoding="utf-8-sig"))
        segments = normalize_transcript(transcript_data)
    else:
        segments = []
    comments_path = input_dir / "原始评论.xlsx"
    comments = read_comments(comments_path if comments_path.is_file() else None)
    if anonymize_comments:
        comments = anonymize_comment_rows(comments)
    cover_path = find_cover(input_dir)

    generated_at = now or datetime.now().astimezone()
    timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
    package_name = f"社交内容数据包_{safe_name(str(metadata['标题']))}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"{package_name}.zip"
    if archive_path.exists():
        raise FileExistsError(f"拒绝覆盖已有数据包：{archive_path}")
    temporary_archive = output_dir / f".{package_name}.{uuid.uuid4().hex}.zip.part"

    try:
        with tempfile.TemporaryDirectory(
            prefix="打包临时_", dir=output_dir
        ) as temporary:
            stage = Path(temporary) / package_name
            stage.mkdir()
            shutil.copy2(video_path, stage / "视频素材.mp4")
            if comments_path.is_file() and include_raw_comments:
                shutil.copy2(comments_path, stage / "原始评论（未净化）.xlsx")
            if cover_path:
                shutil.copy2(cover_path, stage / f"封面图片{cover_path.suffix.lower()}")

            packaged_metadata = dict(metadata)
            packaged_metadata["数据格式版本"] = SCHEMA_VERSION
            packaged_metadata["打包时间"] = generated_at.isoformat()
            (stage / "元数据.json").write_text(
                json.dumps(packaged_metadata, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            note_text = "\n".join(
                [
                    f"标题：{metadata.get('标题', '')}",
                    f"作者：{metadata.get('作者', '')}",
                    f"正文：{metadata.get('笔记正文', '')}",
                    "标签：" + " ".join(f"#{tag}" for tag in metadata.get("标签", [])),
                    f"公开链接：{metadata.get('公开链接', '')}",
                    f"授权依据：{metadata.get('授权依据', '')}",
                    "",
                ]
            )
            (stage / "笔记文案.txt").write_text(note_text, encoding="utf-8-sig")

            transcript_notice = "自动语音识别生成，非作者官方字幕，使用前请人工复核。"
            if segments:
                transcript_text = "\n".join(segment["文案"] for segment in segments)
                transcript_payload = {
                    "说明": transcript_notice,
                    "分段数量": len(segments),
                    "完整文案": transcript_text,
                    "分段": segments,
                }
                (stage / "视频文案（分段数据）.json").write_text(
                    json.dumps(transcript_payload, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                (stage / "视频文案.txt").write_text(
                    transcript_notice + "\n\n" + transcript_text + "\n",
                    encoding="utf-8-sig",
                )
                srt_lines = []
                for segment in segments:
                    srt_lines.extend(
                        [
                            str(segment["序号"]),
                            (
                                f"{format_timestamp(segment['开始秒'])} --> "
                                f"{format_timestamp(segment['结束秒'])}"
                            ),
                            segment["文案"],
                            "",
                        ]
                    )
                (stage / "视频文案（时间轴）.srt").write_text(
                    "\n".join(srt_lines), encoding="utf-8-sig"
                )

            create_workbook(
                stage / "汇总数据.xlsx", packaged_metadata, comments, segments
            )
            raw_comment_notice = (
                "数据包包含原始评论（未净化）.xlsx，打开前请确认来源；"
                "优先使用汇总数据.xlsx。\n"
                if include_raw_comments
                else "数据包默认不包含未净化的原始评论工作簿。\n"
            )
            privacy_notice = (
                "汇总工作簿中的评论身份字段已脱敏。\n"
                if anonymize_comments
                else "评论可能包含个人数据，请避免不必要的二次传播。\n"
            )
            transcript_status = (
                "视频文案为自动语音识别结果，非作者官方字幕，使用前请人工复核。\n"
                if segments
                else (
                    "本次数据包未提取完整视频口播文案。"
                    "需要完整口播时，请使用 package --transcribe-video "
                    "重新生成数据包。\n"
                )
            )
            readme = (
                "本数据包由 social-content-data-packager 生成。\n\n"
                "视频和评论来自用户通过 DATATOOL 导出的公开或已授权内容。\n"
                + transcript_status
                + privacy_notice
                + raw_comment_notice
            )
            (stage / "使用说明.txt").write_text(readme, encoding="utf-8-sig")

            payload_files = sorted(path for path in stage.iterdir() if path.is_file())
            manifest = {
                "格式版本": SCHEMA_VERSION,
                "数据包名称": package_name,
                "生成时间": packaged_metadata["打包时间"],
                "生成工具": {
                    "名称": "social-content-data-packager",
                    "版本": __version__,
                    "Git提交": detect_git_commit(),
                    "Python版本": platform.python_version(),
                    "操作系统": platform.platform(),
                },
                "采集信息": {
                    "平台": metadata.get("平台"),
                    "内容编号": metadata.get("笔记编号"),
                    "采集时间": metadata.get("采集时间"),
                    "授权依据": metadata.get("授权依据"),
                    "DATATOOL版本": metadata.get("DATATOOL版本"),
                },
                "隐私处理": {
                    "评论身份字段已脱敏": anonymize_comments,
                    "包含未净化原始评论": include_raw_comments,
                },
                "文件": [
                    {
                        "文件名": path.name,
                        "字节数": path.stat().st_size,
                        "SHA-256": sha256(path),
                    }
                    for path in payload_files
                ],
                "清单是否包含自身哈希": False,
            }
            (stage / "数据清单.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            with zipfile.ZipFile(
                temporary_archive,
                "x",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=6,
            ) as archive:
                for path in sorted(stage.iterdir()):
                    archive.write(path, arcname=f"{package_name}/{path.name}")

        verify_archive(temporary_archive)
        if archive_path.exists():
            raise FileExistsError(f"拒绝覆盖已有数据包：{archive_path}")
        temporary_archive.replace(archive_path)
    finally:
        temporary_archive.unlink(missing_ok=True)
    return archive_path
