import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from openpyxl import Workbook

from social_content_data_packager.validation import probe_video, validate_workspace


def create_valid_workspace(root: Path) -> Path:
    input_dir = root / "输入"
    input_dir.mkdir(parents=True)
    metadata = {
        "平台": "小红书",
        "笔记编号": "note-1",
        "标题": "测试标题",
        "作者": "测试作者",
        "笔记正文": "测试正文",
        "标签": ["测试"],
        "公开链接": "https://example.com/note-1",
        "授权依据": "公开内容",
        "采集时间": "2026-07-30T10:00:00+08:00",
        "DATATOOL版本": None,
        "互动数据": {
            "点赞": 1,
            "收藏": 2,
            "页面评论": 3,
            "实际导出评论": 1,
        },
    }
    (input_dir / "元数据.json").write_text(
        json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
    )
    (input_dir / "视频素材.mp4").write_bytes(b"video checked by injected probe")
    comments = Workbook()
    comments.active.append(["评论内容", "评论人", "评论时间", "点赞数", "回复数"])
    comments.active.append(["测试评论", "用户", "2026-07-30", 1, 0])
    comments.save(input_dir / "原始评论.xlsx")
    return root


def test_validate_workspace_checks_media_and_returns_summary(tmp_path):
    workspace = create_valid_workspace(tmp_path / "任务")
    checked = []

    result = validate_workspace(
        workspace, media_probe=lambda path: checked.append(path)
    )

    assert checked == [workspace / "输入" / "视频素材.mp4"]
    assert result["平台"] == "小红书"
    assert result["评论行数"] == 1


def test_validate_workspace_rejects_unknown_comment_headers(tmp_path):
    workspace = create_valid_workspace(tmp_path / "任务")
    comments = Workbook()
    comments.active.append(["未知字段", "另一个字段"])
    comments.save(workspace / "输入" / "原始评论.xlsx")

    with pytest.raises(ValueError, match="评论内容"):
        validate_workspace(workspace, media_probe=lambda path: None)


def test_probe_video_rejects_ffprobe_failure(tmp_path):
    video = tmp_path / "视频素材.mp4"
    video.write_bytes(b"fake-mp4")

    def failed_runner(*args, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="Invalid data")

    with pytest.raises(ValueError, match="有效视频"):
        probe_video(video, runner=failed_runner)


def test_probe_video_accepts_a_video_stream(tmp_path):
    video = tmp_path / "视频素材.mp4"
    video.write_bytes(b"probe handles content")

    def successful_runner(command, **kwargs):
        assert command[0] == "ffprobe"
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"streams": [{"codec_type": "video"}]}),
            stderr="",
        )

    probe_video(video, runner=successful_runner)


@pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="FFmpeg/FFprobe not installed",
)
def test_validate_workspace_with_real_generated_video(tmp_path):
    workspace = create_valid_workspace(tmp_path / "任务")
    video = workspace / "输入" / "视频素材.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=16x16:d=0.1",
            "-c:v",
            "mpeg4",
            str(video),
        ],
        check=True,
    )

    result = validate_workspace(workspace)

    assert result["标题"] == "测试标题"
