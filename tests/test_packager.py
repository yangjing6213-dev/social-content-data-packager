import json
import re
import warnings
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import pytest
from openpyxl import Workbook, load_workbook

from social_content_data_packager.packager import build_package
from social_content_data_packager.verification import verify_archive


def create_workspace(root: Path) -> Path:
    input_dir = root / "输入"
    (root / "输出").mkdir(parents=True)
    input_dir.mkdir()
    metadata = {
        "平台": "小红书",
        "笔记编号": "note-1",
        "标题": "隐私安全测试",
        "作者": "测试作者",
        "笔记正文": "这是页面文案。",
        "标签": ["人工智能", "隐私"],
        "公开链接": "https://example.com/note-1",
        "授权依据": "公开内容",
        "采集时间": "2026-07-30T10:00:00+08:00",
        "DATATOOL版本": "测试版本",
        "互动数据": {"点赞": 10, "收藏": 2, "页面评论": 1},
    }
    (input_dir / "元数据.json").write_text(
        json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
    )

    comments = Workbook()
    sheet = comments.active
    sheet.append(["评论内容", "评论人", "评论时间", "点赞数", "回复数"])
    sheet.append(["=2+2", "用户甲", "2026-07-30 10:00:00", "1", "0"])
    comments.save(input_dir / "原始评论.xlsx")

    (input_dir / "视频素材.mp4").write_bytes(b"fake-mp4")
    (input_dir / "封面图片.webp").write_bytes(b"fake-webp")
    transcript = {
        "说明": "自动识别，非官方字幕。",
        "分段": [
            {"序号": 1, "开始秒": 0.0, "结束秒": 1.5, "文案": "第一句。"},
            {"序号": 2, "开始秒": 1.5, "结束秒": 3.0, "文案": "第二句。"},
        ],
    }
    (input_dir / "视频文案（分段数据）.json").write_text(
        json.dumps(transcript, ensure_ascii=False), encoding="utf-8"
    )
    return root


def test_build_package_creates_auditable_chinese_archive(tmp_path):
    workspace = create_workspace(tmp_path / "任务")
    fixed_now = datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)

    archive_path = build_package(
        workspace, now=fixed_now, media_probe=lambda path: None
    )

    assert archive_path.parent == workspace / "输出"
    assert archive_path.name == "社交内容数据包_隐私安全测试_20260730_120000.zip"
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        basenames = {Path(name).name for name in names}
        assert basenames == {
            "使用说明.txt",
            "元数据.json",
            "封面图片.webp",
            "数据清单.json",
            "汇总数据.xlsx",
            "笔记文案.txt",
            "视频文案.txt",
            "视频文案（分段数据）.json",
            "视频文案（时间轴）.srt",
            "视频素材.mp4",
        }
        assert not [
            Path(name).stem for name in names if re.search(r"[A-Za-z]", Path(name).stem)
        ]

        workbook_member = next(
            name for name in names if name.endswith("/汇总数据.xlsx")
        )
        workbook = load_workbook(
            BytesIO(archive.read(workbook_member)), data_only=False
        )
        assert workbook.sheetnames == ["元数据", "评论数据", "视频文案"]
        assert workbook["评论数据"].max_row == 2
        assert workbook["评论数据"]["A2"].value == "=2+2"
        assert workbook["评论数据"]["A2"].data_type == "s"
        assert workbook["视频文案"].max_row == 3

        transcript_member = next(
            name for name in names if name.endswith("/视频文案（分段数据）.json")
        )
        transcript = json.loads(archive.read(transcript_member).decode("utf-8"))
        assert transcript["完整文案"] == "第一句。\n第二句。"
        transcript_text_member = next(
            name for name in names if name.endswith("/视频文案.txt")
        )
        transcript_text = (
            archive.read(transcript_text_member)
            .decode("utf-8-sig")
            .replace("\r\n", "\n")
        )
        assert "第一句。\n第二句。" in transcript_text
        transcript_srt_member = next(
            name for name in names if name.endswith("/视频文案（时间轴）.srt")
        )
        assert "00:00:01,500 --> 00:00:03,000" in archive.read(
            transcript_srt_member
        ).decode("utf-8-sig")


def test_build_package_accepts_utf8_bom_json_inputs(tmp_path):
    workspace = create_workspace(tmp_path / "任务")
    input_dir = workspace / "输入"
    metadata_path = input_dir / "元数据.json"
    transcript_path = input_dir / "视频文案（分段数据）.json"
    metadata_path.write_bytes(b"\xef\xbb\xbf" + metadata_path.read_bytes())
    transcript_path.write_bytes(b"\xef\xbb\xbf" + transcript_path.read_bytes())

    archive_path = build_package(workspace, media_probe=lambda path: None)

    assert verify_archive(archive_path)["已校验文件数"] == 9


def test_build_package_without_transcript_excludes_empty_transcript_files(tmp_path):
    workspace = create_workspace(tmp_path / "任务")
    (workspace / "输入" / "视频文案（分段数据）.json").unlink()

    archive_path = build_package(workspace, media_probe=lambda path: None)

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        basenames = {Path(name).name for name in names}
        assert "视频文案.txt" not in basenames
        assert "视频文案（分段数据）.json" not in basenames
        assert "视频文案（时间轴）.srt" not in basenames
        readme_member = next(name for name in names if name.endswith("/使用说明.txt"))
        readme = archive.read(readme_member).decode("utf-8-sig")
        assert "本次数据包未提取完整视频口播文案" in readme

    assert verify_archive(archive_path)["已校验文件数"] == 6


def test_manifest_hashes_match_packaged_payload(tmp_path):
    workspace = create_workspace(tmp_path / "任务")
    archive_path = build_package(
        workspace,
        now=datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc),
        media_probe=lambda path: None,
    )

    with zipfile.ZipFile(archive_path) as archive:
        manifest_member = next(
            name for name in archive.namelist() if name.endswith("/数据清单.json")
        )
        manifest = json.loads(archive.read(manifest_member).decode("utf-8"))
        root = manifest_member.rsplit("/", 1)[0]
        for item in manifest["文件"]:
            payload = archive.read(f"{root}/{item['文件名']}")
            import hashlib

            assert len(payload) == item["字节数"]
            assert hashlib.sha256(payload).hexdigest() == item["SHA-256"]


def test_workbook_treats_metadata_and_transcript_formulas_as_text(tmp_path):
    workspace = create_workspace(tmp_path / "任务")
    input_dir = workspace / "输入"
    metadata = json.loads((input_dir / "元数据.json").read_text(encoding="utf-8"))
    metadata["作者"] = '=HYPERLINK("https://example.com","打开")'
    (input_dir / "元数据.json").write_text(
        json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
    )
    transcript = {"分段": [{"序号": 1, "开始秒": 0, "结束秒": 1, "文案": "=2+2"}]}
    (input_dir / "视频文案（分段数据）.json").write_text(
        json.dumps(transcript, ensure_ascii=False), encoding="utf-8"
    )

    archive_path = build_package(workspace, media_probe=lambda path: None)

    with zipfile.ZipFile(archive_path) as archive:
        member = next(
            name for name in archive.namelist() if name.endswith("/汇总数据.xlsx")
        )
        workbook = load_workbook(BytesIO(archive.read(member)), data_only=False)
        metadata_values = {
            row[0].value: row[1] for row in workbook["元数据"].iter_rows(min_row=2)
        }
        assert metadata_values["作者"].value.startswith("=HYPERLINK")
        assert metadata_values["作者"].data_type == "s"
        assert workbook["视频文案"]["D2"].value == "=2+2"
        assert workbook["视频文案"]["D2"].data_type == "s"


def test_build_package_rejects_placeholder_metadata(tmp_path):
    workspace = create_workspace(tmp_path / "任务")
    metadata_path = workspace / "输入" / "元数据.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["标题"] = "请填写内容标题"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="标题.*占位"):
        build_package(workspace, media_probe=lambda path: None)


def test_build_package_refuses_to_replace_existing_archive(tmp_path):
    workspace = create_workspace(tmp_path / "任务")
    fixed_now = datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)
    archive_path = build_package(
        workspace, now=fixed_now, media_probe=lambda path: None
    )
    original_hash = archive_path.read_bytes()

    with pytest.raises(FileExistsError):
        build_package(workspace, now=fixed_now, media_probe=lambda path: None)

    assert archive_path.read_bytes() == original_hash
    assert not list(archive_path.parent.glob("*.part"))


def test_verify_archive_detects_modified_payload(tmp_path):
    workspace = create_workspace(tmp_path / "任务")
    archive_path = build_package(workspace, media_probe=lambda path: None)
    result = verify_archive(archive_path)
    assert result["已校验文件数"] == 9

    tampered_path = tmp_path / "篡改数据包.zip"
    with (
        zipfile.ZipFile(archive_path) as source,
        zipfile.ZipFile(tampered_path, "w", compression=zipfile.ZIP_DEFLATED) as target,
    ):
        for name in source.namelist():
            payload = source.read(name)
            if name.endswith("/笔记文案.txt"):
                payload += b"tampered"
            target.writestr(name, payload)

    with pytest.raises(ValueError, match="校验失败"):
        verify_archive(tampered_path)


def test_build_package_includes_raw_comments_only_when_requested(tmp_path):
    workspace = create_workspace(tmp_path / "任务")

    archive_path = build_package(
        workspace,
        include_raw_comments=True,
        media_probe=lambda path: None,
    )

    with zipfile.ZipFile(archive_path) as archive:
        assert any(
            name.endswith("/原始评论（未净化）.xlsx") for name in archive.namelist()
        )
        assert verify_archive(archive_path)["已校验文件数"] == 10


def test_build_package_can_anonymize_comment_identity_columns(tmp_path):
    workspace = create_workspace(tmp_path / "任务")

    archive_path = build_package(
        workspace,
        anonymize_comments=True,
        media_probe=lambda path: None,
    )

    with zipfile.ZipFile(archive_path) as archive:
        member = next(
            name for name in archive.namelist() if name.endswith("/汇总数据.xlsx")
        )
        workbook = load_workbook(BytesIO(archive.read(member)), data_only=False)
        assert workbook["评论数据"]["A2"].value == "=2+2"
        assert workbook["评论数据"]["B2"].value == "[已脱敏]"
        assert not any("原始评论" in name for name in archive.namelist())


def test_verify_archive_streams_payload_files(tmp_path, monkeypatch):
    workspace = create_workspace(tmp_path / "任务")
    archive_path = build_package(workspace, media_probe=lambda path: None)
    original_read = zipfile.ZipFile.read

    def manifest_only_read(archive, name, *args, **kwargs):
        if str(name).endswith("/数据清单.json"):
            return original_read(archive, name, *args, **kwargs)
        raise AssertionError(f"payload read into memory: {name}")

    monkeypatch.setattr(zipfile.ZipFile, "read", manifest_only_read)

    assert verify_archive(archive_path)["已校验文件数"] == 9


def test_verify_archive_rejects_duplicate_members(tmp_path):
    workspace = create_workspace(tmp_path / "任务")
    archive_path = build_package(workspace, media_probe=lambda path: None)
    duplicate_path = tmp_path / "重名成员.zip"

    with (
        zipfile.ZipFile(archive_path) as source,
        zipfile.ZipFile(
            duplicate_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as target,
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("ignore", UserWarning)
        for name in source.namelist():
            payload = source.read(name)
            target.writestr(name, payload)
            if name.endswith("/笔记文案.txt"):
                target.writestr(name, payload)

    with pytest.raises(ValueError, match="重复"):
        verify_archive(duplicate_path)


def test_verify_archive_rejects_non_object_manifest(tmp_path):
    archive_path = tmp_path / "无效清单.zip"
    with zipfile.ZipFile(
        archive_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        archive.writestr("数据包/数据清单.json", "[]")

    with pytest.raises(ValueError, match="根节点必须是 JSON 对象"):
        verify_archive(archive_path)


def test_verify_archive_rejects_noncanonical_member_paths(tmp_path):
    archive_path = tmp_path / "非规范路径.zip"
    with zipfile.ZipFile(
        archive_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        archive.writestr("数据包/./数据清单.json", '{"文件": []}')

    with pytest.raises(ValueError, match="不安全路径"):
        verify_archive(archive_path)
