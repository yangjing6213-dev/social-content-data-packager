import json

from social_content_data_packager.workspace import initialize_workspace


def test_initialize_workspace_creates_expected_structure(tmp_path):
    workspace = initialize_workspace(tmp_path / "任务")

    assert workspace == tmp_path / "任务"
    assert (workspace / "输入").is_dir()
    assert (workspace / "输出").is_dir()
    metadata = json.loads(
        (workspace / "输入" / "元数据.json").read_text(encoding="utf-8")
    )
    assert metadata["平台"] == "小红书"
    assert metadata["标题"] == "请填写内容标题"
    assert metadata["授权依据"] == "公开内容"
    assert metadata["采集时间"] is None
    assert metadata["DATATOOL版本"] is None
    assert (workspace / "输入" / "放置采集文件说明.txt").is_file()


def test_initialize_workspace_rejects_nonempty_directory(tmp_path):
    workspace = tmp_path / "任务"
    workspace.mkdir()
    (workspace / "existing.txt").write_text("keep", encoding="utf-8")

    try:
        initialize_workspace(workspace)
    except ValueError as exc:
        assert "非空目录" in str(exc)
    else:
        raise AssertionError("Expected non-empty workspace to be rejected")
