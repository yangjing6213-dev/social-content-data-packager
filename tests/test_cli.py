from test_packager import create_workspace

from social_content_data_packager.cli import main
from social_content_data_packager.packager import build_package


def test_cli_init_creates_workspace(tmp_path, capsys):
    workspace = tmp_path / "任务"

    result = main(["init", str(workspace)])

    assert result == 0
    assert (workspace / "输入" / "元数据.json").is_file()
    assert str(workspace) in capsys.readouterr().out


def test_cli_validate_reports_errors_without_traceback(tmp_path, capsys):
    workspace = tmp_path / "任务"

    result = main(["validate", str(workspace)])

    assert result == 1
    captured = capsys.readouterr()
    assert "错误：缺少元数据文件" in captured.err


def test_cli_verify_reports_verified_archive(tmp_path, capsys):
    workspace = create_workspace(tmp_path / "任务")
    archive_path = build_package(workspace, media_probe=lambda path: None)

    result = main(["verify", str(archive_path)])

    assert result == 0
    assert "文件 9 个" in capsys.readouterr().out


def test_cli_verify_rejects_invalid_zip(tmp_path, capsys):
    archive_path = tmp_path / "损坏数据包.zip"
    archive_path.write_bytes(b"not-a-zip")

    result = main(["verify", str(archive_path)])

    assert result == 1
    assert "不是有效的 ZIP" in capsys.readouterr().err


def test_cli_package_can_transcribe_complete_video_before_packaging(
    tmp_path, monkeypatch, capsys
):
    workspace = tmp_path / "任务"
    archive_path = tmp_path / "完整视频文案数据包.zip"
    calls = []

    def fake_transcribe(
        workspace_arg,
        model,
        language,
        initial_prompt,
        force,
    ):
        calls.append(
            (
                "transcribe",
                workspace_arg,
                model,
                language,
                initial_prompt,
                force,
            )
        )
        return {"分段数量": 2}

    def fake_build(workspace_arg, **kwargs):
        calls.append(("package", workspace_arg, kwargs))
        return archive_path

    monkeypatch.setattr(
        "social_content_data_packager.cli.transcribe_workspace", fake_transcribe
    )
    monkeypatch.setattr("social_content_data_packager.cli.build_package", fake_build)

    result = main(
        [
            "package",
            str(workspace),
            "--transcribe-video",
            "--model",
            "medium",
            "--language",
            "en",
            "--initial-prompt",
            "brand terms",
            "--force-transcript",
        ]
    )

    assert result == 0
    assert calls == [
        ("transcribe", workspace, "medium", "en", "brand terms", True),
        (
            "package",
            workspace,
            {
                "output_dir": None,
                "include_raw_comments": False,
                "anonymize_comments": False,
            },
        ),
    ]
    assert str(archive_path) in capsys.readouterr().out


def test_cli_package_reports_transcription_failure_without_traceback(
    tmp_path, monkeypatch, capsys
):
    workspace = tmp_path / "任务"

    def fail_transcription(*args, **kwargs):
        raise RuntimeError("Whisper 转写失败：模型加载失败")

    monkeypatch.setattr(
        "social_content_data_packager.cli.transcribe_workspace", fail_transcription
    )

    result = main(["package", str(workspace), "--transcribe-video"])

    assert result == 1
    captured = capsys.readouterr()
    assert "错误：Whisper 转写失败：模型加载失败" in captured.err
    assert "Traceback" not in captured.err
