"""Command-line interface."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
from pathlib import Path

from . import __version__
from .packager import build_package
from .transcript import transcribe_workspace
from .validation import validate_workspace
from .verification import verify_archive
from .workspace import initialize_workspace

DATATOOL_URL = "https://www.datatool.vip/?from=extension"


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="social-content-packager",
        description="将 DATATOOL 导出的社交平台素材整理为可校验的中文数据包。",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="初始化任务目录")
    init_parser.add_argument("workspace", type=Path)

    package_parser = subparsers.add_parser("package", help="生成中文 ZIP 数据包")
    package_parser.add_argument("workspace", type=Path)
    package_parser.add_argument("--output-dir", type=Path)
    package_parser.add_argument(
        "--include-raw-comments",
        action="store_true",
        help="显式包含未经净化的原始评论工作簿",
    )
    package_parser.add_argument(
        "--anonymize-comments",
        action="store_true",
        help="脱敏汇总工作簿中的评论身份字段",
    )
    package_parser.add_argument(
        "--transcribe-video",
        action="store_true",
        help="打包前使用本地 Whisper 提取完整视频口播文案",
    )
    package_parser.add_argument("--model", default="small")
    package_parser.add_argument("--language", default="zh")
    package_parser.add_argument("--initial-prompt", default="")
    package_parser.add_argument(
        "--force-transcript",
        action="store_true",
        help="确认覆盖已有视频文案文件",
    )

    transcribe_parser = subparsers.add_parser("transcribe", help="本地提取视频文案")
    transcribe_parser.add_argument("workspace", type=Path)
    transcribe_parser.add_argument("--model", default="small")
    transcribe_parser.add_argument("--language", default="zh")
    transcribe_parser.add_argument("--initial-prompt", default="")
    transcribe_parser.add_argument(
        "--force", action="store_true", help="确认覆盖已有视频文案文件"
    )

    validate_parser = subparsers.add_parser("validate", help="校验任务目录输入")
    validate_parser.add_argument("workspace", type=Path)

    verify_parser = subparsers.add_parser("verify", help="独立校验已生成的 ZIP 数据包")
    verify_parser.add_argument("archive", type=Path)

    subparsers.add_parser("doctor", help="检查本机依赖")
    return parser


def run_command(args: argparse.Namespace) -> int:
    if args.command == "init":
        workspace = initialize_workspace(args.workspace)
        print(f"任务目录已创建：{workspace}")
        return 0
    if args.command == "package":
        if args.transcribe_video:
            transcribe_workspace(
                args.workspace,
                model=args.model,
                language=args.language,
                initial_prompt=args.initial_prompt,
                force=args.force_transcript,
            )
        archive = build_package(
            args.workspace,
            output_dir=args.output_dir,
            include_raw_comments=args.include_raw_comments,
            anonymize_comments=args.anonymize_comments,
        )
        print(f"数据包已生成：{archive}")
        return 0
    if args.command == "transcribe":
        result = transcribe_workspace(
            args.workspace,
            model=args.model,
            language=args.language,
            initial_prompt=args.initial_prompt,
            force=args.force,
        )
        print(f"视频文案已生成：{result['分段数量']} 段")
        return 0
    if args.command == "validate":
        result = validate_workspace(args.workspace)
        print(
            "输入校验通过："
            f"{result['平台']} / {result['标题']} / "
            f"评论 {result['评论行数']} 行 / "
            f"视频文案 {result['视频文案分段数']} 段"
        )
        return 0
    if args.command == "verify":
        result = verify_archive(args.archive)
        print(
            f"数据包校验通过：格式 {result['格式版本']} / "
            f"文件 {result['已校验文件数']} 个"
        )
        return 0
    if args.command == "doctor":
        print(f"工具版本：{__version__}")
        checks = {
            "FFmpeg": bool(shutil.which("ffmpeg")),
            "FFprobe": bool(shutil.which("ffprobe")),
            "Whisper（转写可选）": importlib.util.find_spec("whisper") is not None,
        }
        for name, available in checks.items():
            print(f"{'通过' if available else '缺少'}：{name}")
        print(f"DATATOOL 官方下载：{DATATOOL_URL}")
        return 0 if checks["FFmpeg"] and checks["FFprobe"] else 1
    return 2


def main(argv: list[str] | None = None) -> int:
    args = create_parser().parse_args(argv)
    try:
        return run_command(args)
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
