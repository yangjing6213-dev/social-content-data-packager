import json
import subprocess
import sys

import pytest

from social_content_data_packager.transcript import (
    build_whisper_command,
    normalize_transcript,
    transcribe_workspace,
)


def test_normalize_transcript_accepts_whisper_json():
    data = {
        "segments": [
            {"id": 0, "start": 0.0, "end": 1.25, "text": " 第一句。 "},
            {"id": 1, "start": 1.25, "end": 3.5, "text": "第二句。"},
        ]
    }

    segments = normalize_transcript(data)

    assert segments == [
        {"序号": 1, "开始秒": 0.0, "结束秒": 1.25, "文案": "第一句。"},
        {"序号": 2, "开始秒": 1.25, "结束秒": 3.5, "文案": "第二句。"},
    ]


def test_normalize_transcript_clips_small_whisper_overlap():
    data = {
        "segments": [
            {"start": 0.0, "end": 1.5, "text": "第一句。"},
            {"start": 1.45, "end": 2.5, "text": "第二句。"},
        ]
    }

    segments = normalize_transcript(data)

    assert segments[1]["开始秒"] == 1.5


@pytest.mark.parametrize(
    "data",
    [[], {"segments": [None]}, {"segments": [{"start": "bad", "end": 1}]}],
)
def test_normalize_transcript_rejects_malformed_input(data):
    with pytest.raises(ValueError):
        normalize_transcript(data)


def test_build_whisper_command_uses_local_python_module(tmp_path):
    video = tmp_path / "视频素材.mp4"
    output = tmp_path / "转写"

    command = build_whisper_command(
        video=video,
        output_dir=output,
        model="small",
        language="zh",
        initial_prompt="人工智能、隐私安全",
    )

    assert command[:3] == [sys.executable, "-m", "whisper"]
    assert str(video) in command
    assert command[command.index("--model") + 1] == "small"
    assert command[command.index("--language") + 1] == "zh"
    assert command[command.index("--initial_prompt") + 1] == "人工智能、隐私安全"


def test_transcribe_workspace_writes_standard_chinese_files(tmp_path):
    workspace = tmp_path / "任务"
    input_dir = workspace / "输入"
    input_dir.mkdir(parents=True)
    (input_dir / "视频素材.mp4").write_bytes(b"fake")

    def fake_runner(command, check):
        assert check is True
        output_dir = command[command.index("--output_dir") + 1]
        import json
        from pathlib import Path

        raw = {"segments": [{"id": 0, "start": 0.0, "end": 1.25, "text": "测试文案。"}]}
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / "视频素材.json").write_text(
            json.dumps(raw, ensure_ascii=False), encoding="utf-8"
        )

    result = transcribe_workspace(workspace, model="tiny", runner=fake_runner)

    assert result["分段数量"] == 1
    assert (
        (input_dir / "视频文案.txt")
        .read_text(encoding="utf-8-sig")
        .endswith("测试文案。\n")
    )
    assert "00:00:00,000 --> 00:00:01,250" in (
        input_dir / "视频文案（时间轴）.srt"
    ).read_text(encoding="utf-8-sig")
    transcript_data = json.loads(
        (input_dir / "视频文案（分段数据）.json").read_text(encoding="utf-8")
    )
    assert transcript_data["完整文案"] == "测试文案。"


def test_transcribe_workspace_requires_force_to_replace_existing_files(tmp_path):
    workspace = tmp_path / "任务"
    input_dir = workspace / "输入"
    input_dir.mkdir(parents=True)
    (input_dir / "视频素材.mp4").write_bytes(b"fake")
    existing = input_dir / "视频文案.txt"
    existing.write_text("人工修订内容", encoding="utf-8")
    called = False

    def runner(command, check):
        nonlocal called
        called = True

    with pytest.raises(FileExistsError, match="--force"):
        transcribe_workspace(workspace, runner=runner)

    assert called is False
    assert existing.read_text(encoding="utf-8") == "人工修订内容"


def test_transcribe_workspace_reports_whisper_process_failure(tmp_path):
    workspace = tmp_path / "任务"
    input_dir = workspace / "输入"
    input_dir.mkdir(parents=True)
    (input_dir / "视频素材.mp4").write_bytes(b"fake")

    def failed_runner(command, check):
        raise subprocess.CalledProcessError(
            returncode=2,
            cmd=command,
            stderr="模型加载失败",
        )

    with pytest.raises(RuntimeError, match="Whisper 转写失败.*模型加载失败"):
        transcribe_workspace(workspace, runner=failed_runner)
