"""Local transcription helpers."""

from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

TRANSCRIPT_FILENAMES = (
    "视频文案（分段数据）.json",
    "视频文案.txt",
    "视频文案（时间轴）.srt",
)


def ensure_transcript_targets_available(input_dir: Path, force: bool) -> None:
    existing = [
        input_dir / name for name in TRANSCRIPT_FILENAMES if (input_dir / name).exists()
    ]
    if existing and not force:
        names = "、".join(path.name for path in existing)
        raise FileExistsError(f"拒绝覆盖已有视频文案：{names}；确认后使用 --force")


def normalize_transcript(data: object) -> list[dict]:
    if not isinstance(data, dict):
        raise ValueError("转写数据根节点必须是 JSON 对象")
    raw_segments = data.get("分段")
    if raw_segments is None:
        raw_segments = data.get("segments")
    if not isinstance(raw_segments, list) or not raw_segments:
        raise ValueError("转写数据中没有可用分段")

    normalized = []
    previous_end = 0.0
    for index, segment in enumerate(raw_segments, start=1):
        if not isinstance(segment, dict):
            raise ValueError(f"第{index}段必须是对象")
        start_value: object = segment.get("开始秒", segment.get("start", 0.0))
        end_value: object = segment.get("结束秒", segment.get("end", 0.0))
        if isinstance(start_value, bool) or not isinstance(
            start_value, (int, float, str)
        ):
            raise ValueError(f"第{index}段时间必须是数字")
        if isinstance(end_value, bool) or not isinstance(end_value, (int, float, str)):
            raise ValueError(f"第{index}段时间必须是数字")
        try:
            start = float(start_value)
            end = float(end_value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"第{index}段时间必须是数字") from error
        if not math.isfinite(start) or not math.isfinite(end):
            raise ValueError(f"第{index}段时间必须是有限数字")
        text = str(segment.get("文案", segment.get("text", ""))).strip()
        if start < 0 or end < start:
            raise ValueError(f"第{index}段时间范围无效")
        if start < previous_end:
            if end <= previous_end:
                raise ValueError(f"第{index}段完全落在前一段时间内")
            start = previous_end
        if not text:
            raise ValueError(f"第{index}段文案为空")
        normalized.append(
            {
                "序号": index,
                "开始秒": round(start, 3),
                "结束秒": round(end, 3),
                "文案": text,
            }
        )
        previous_end = end
    return normalized


def format_timestamp(seconds: float, decimal: str = ",") -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}{decimal}{milliseconds:03d}"


def build_whisper_command(
    video: str | Path,
    output_dir: str | Path,
    model: str = "small",
    language: str = "zh",
    initial_prompt: str = "",
) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "whisper",
        str(video),
        "--model",
        model,
        "--language",
        language,
        "--task",
        "transcribe",
        "--output_dir",
        str(output_dir),
        "--output_format",
        "json",
        "--verbose",
        "False",
        "--fp16",
        "False",
        "--temperature",
        "0",
        "--beam_size",
        "1",
        "--best_of",
        "1",
    ]
    if initial_prompt:
        command.extend(["--initial_prompt", initial_prompt])
    return command


def write_transcript_files(
    input_dir: Path,
    segments: list[dict],
    model: str,
    language: str,
    force: bool = False,
) -> dict:
    ensure_transcript_targets_available(input_dir, force)
    notice = "自动语音识别生成，非作者官方字幕，使用前请人工复核。"
    result = {
        "说明": notice,
        "识别模型": f"OpenAI Whisper {model}",
        "语言": language,
        "分段数量": len(segments),
        "完整文案": "\n".join(segment["文案"] for segment in segments),
        "分段": segments,
    }
    (input_dir / "视频文案（分段数据）.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    full_text = "\n".join(segment["文案"] for segment in segments)
    (input_dir / "视频文案.txt").write_text(
        notice + "\n\n" + full_text + "\n", encoding="utf-8-sig"
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
    (input_dir / "视频文案（时间轴）.srt").write_text(
        "\n".join(srt_lines), encoding="utf-8-sig"
    )
    return result


def transcribe_workspace(
    workspace: str | Path,
    model: str = "small",
    language: str = "zh",
    initial_prompt: str = "",
    force: bool = False,
    runner: Callable = subprocess.run,
) -> dict:
    workspace = Path(workspace)
    input_dir = workspace / "输入"
    output_dir = workspace / "输出"
    video = input_dir / "视频素材.mp4"
    if not video.is_file():
        raise FileNotFoundError(f"缺少视频文件：{video}")
    ensure_transcript_targets_available(input_dir, force)
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="转写临时_", dir=output_dir) as temporary:
        command = build_whisper_command(
            video=video,
            output_dir=temporary,
            model=model,
            language=language,
            initial_prompt=initial_prompt,
        )
        try:
            runner(command, check=True)
        except subprocess.CalledProcessError as error:
            detail = str(error.stderr or error.stdout or "").strip()
            message = f"Whisper 转写失败（退出码 {error.returncode}）"
            if detail:
                message += f"：{detail}"
            raise RuntimeError(message) from error
        raw_path = Path(temporary) / f"{video.stem}.json"
        if not raw_path.is_file():
            raise RuntimeError("Whisper 未生成预期的 JSON 文件")
        raw_data = json.loads(raw_path.read_text(encoding="utf-8-sig"))

    segments = normalize_transcript(raw_data)
    return write_transcript_files(input_dir, segments, model, language, force=force)
