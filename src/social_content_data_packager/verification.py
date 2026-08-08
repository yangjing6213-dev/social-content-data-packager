"""Independent verification of generated ZIP archives."""

from __future__ import annotations

import hashlib
import hmac
import json
import zipfile
from pathlib import Path, PurePosixPath


def sha256_member(archive: zipfile.ZipFile, name: str) -> str:
    digest = hashlib.sha256()
    with archive.open(name) as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(path: str | Path) -> dict:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"找不到数据包：{path}")

    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile as error:
        raise ValueError(f"不是有效的 ZIP 数据包：{path}") from error

    with archive:
        bad_member = archive.testzip()
        if bad_member:
            raise ValueError(f"ZIP CRC 校验失败：{bad_member}")
        member_infos = [info for info in archive.infolist() if not info.is_dir()]
        members = [info.filename for info in member_infos]
        if len(members) != len(set(members)):
            raise ValueError("数据包包含重复的 ZIP 成员路径")
        info_by_name = {info.filename: info for info in member_infos}
        for name in members:
            member_path = PurePosixPath(name)
            if (
                member_path.is_absolute()
                or ".." in member_path.parts
                or "\\" in name
                or member_path.as_posix() != name
            ):
                raise ValueError(f"数据包包含不安全路径：{name}")

        manifests = [name for name in members if name.endswith("/数据清单.json")]
        if len(manifests) != 1:
            raise ValueError("数据包必须且只能包含一个数据清单.json")
        manifest_name = manifests[0]
        root = PurePosixPath(manifest_name).parent.as_posix()
        try:
            manifest = json.loads(archive.read(manifest_name).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("数据清单.json 不是有效的 UTF-8 JSON") from error
        if not isinstance(manifest, dict):
            raise ValueError("数据清单.json 根节点必须是 JSON 对象")

        items = manifest.get("文件")
        if not isinstance(items, list):
            raise ValueError("数据清单缺少文件列表")
        declared = {}
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("文件名"), str):
                raise ValueError("数据清单包含无效文件记录")
            filename = item["文件名"]
            filename_path = PurePosixPath(filename)
            if (
                filename in declared
                or not filename
                or filename_path.name != filename
                or filename_path.as_posix() != filename
            ):
                raise ValueError(f"数据清单包含重复或不安全文件名：{filename}")
            declared[filename] = item

        actual = {
            PurePosixPath(name).name
            for name in members
            if PurePosixPath(name).parent.as_posix() == root and name != manifest_name
        }
        if actual != set(declared):
            missing = sorted(set(declared) - actual)
            extra = sorted(actual - set(declared))
            raise ValueError(f"数据包文件集合不匹配；缺少={missing}，多出={extra}")
        if any(
            PurePosixPath(name).parent.as_posix() != root
            for name in members
            if name != manifest_name
        ):
            raise ValueError("数据包包含清单目录之外的文件")

        for filename, item in declared.items():
            member_name = f"{root}/{filename}"
            if item.get("字节数") != info_by_name[member_name].file_size:
                raise ValueError(f"文件大小校验失败：{filename}")
            expected = item.get("SHA-256")
            actual_hash = sha256_member(archive, member_name)
            if not isinstance(expected, str) or not hmac.compare_digest(
                expected.lower(), actual_hash
            ):
                raise ValueError(f"SHA-256 校验失败：{filename}")

    return {
        "数据包": str(path),
        "格式版本": manifest.get("格式版本"),
        "已校验文件数": len(declared),
    }
