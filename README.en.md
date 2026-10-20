# social-content-data-packager

A local Python command-line tool that packages public or authorized social-content exports into ZIP archives with integrity checks.

[简体中文](README.md) | English

[![License: MIT](https://img.shields.io/github/license/yangjing6213-dev/social-content-data-packager?style=flat-square)](https://github.com/yangjing6213-dev/social-content-data-packager/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-%233670A0.svg?style=flat-square&logo=python&logoColor=ffdd54)](https://www.python.org/) [![OpenPyXL](https://img.shields.io/badge/OpenPyXL-3.x-2F6FEB?style=flat-square)](https://openpyxl.readthedocs.io/)
[![FFmpeg](https://img.shields.io/badge/ffmpeg-%23007808.svg?style=flat-square&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/) [![Whisper optional](https://img.shields.io/badge/Whisper-optional-412991?style=flat-square&logo=openai&logoColor=white)](https://pypi.org/project/openai-whisper/)

The tool accepts local exports such as videos, covers, page copy and comments. It checks the files and creates a Chinese Excel workbook, a ZIP package and a SHA-256 integrity manifest. Video transcription is optional and runs with local Whisper.

Users handle platform sign-in, exports and authorization. You can start with existing files that follow the layout below; this project does not automate collection.

## What it does

| Command | Purpose |
| --- | --- |
| `init` | Creates a task folder and metadata template. |
| `validate` | Checks required metadata and comment headers, then uses FFprobe to confirm a valid video stream. |
| `package` | Creates a Chinese Excel workbook, ZIP archive and SHA-256 file manifest. |
| `verify` | Independently checks ZIP contents, paths, file sizes and SHA-256 hashes. |
| `transcribe` | Optional: uses local Whisper to create full-video speech text as TXT, segmented JSON and SRT. |

`package --transcribe-video` transcribes before packaging. Transcripts are automatic and are not official creator captions; review them before sharing or analysis.

## Workflow

1. Export public or authorized content with DATATOOL or another method.
2. Create a task folder:

   ```bash
   social-content-packager init "My task"
   ```

3. Put files in `My task/输入/`. `元数据.json` and `视频素材.mp4` are required; a comments workbook, cover and existing transcript are optional. See the [metadata example](examples/元数据示例.json).
4. Complete the metadata and validate the input:

   ```bash
   social-content-packager validate "My task"
   ```

5. Build the package:

   ```bash
   social-content-packager package "My task"
   ```

   The command prints the full ZIP path.

6. Pass that path to the verification command:

   ```bash
   social-content-packager verify "replace this with the ZIP path printed above"
   ```

A task folder usually looks like this:

```text
My task/
├── 输入/
│   ├── 元数据.json                  required
│   ├── 视频素材.mp4                 required
│   ├── 原始评论.xlsx                optional
│   ├── 封面图片.webp                optional; jpg/jpeg/png also work
│   └── 视频文案（分段数据）.json     optional
└── 输出/                            generated packages
```

## Install

Python 3.10 or newer is required. `pip install -e .` installs OpenPyXL. Install FFmpeg and FFprobe before validating or packaging video files.

```bash
git clone https://github.com/yangjing6213-dev/social-content-data-packager.git
cd social-content-data-packager
python -m venv .venv
```

Activate the virtual environment with the command for your system:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Then install the package and check the media tools:

```bash
python -m pip install -e .
social-content-packager doctor
```

`doctor` checks that FFmpeg and FFprobe are available. See the [installation guide](docs/installation.md) for installing media tools.

### Optional: local video transcription

Install the optional dependency, then transcribe during packaging:

```bash
python -m pip install -e ".[transcribe]"
social-content-packager package "My task" --transcribe-video --model small --language zh
```

You can also run `social-content-packager transcribe "My task"` separately. Existing transcript files are not overwritten by default; use `--force` or `--force-transcript` when you intend to replace them.

### Comment privacy

The package excludes the original comments workbook by default, but the summary workbook can still contain comments. Review personal information before sharing. Use `--anonymize-comments` to anonymize identity fields in the summary workbook when needed. Use `--include-raw-comments` only when the original workbook must be retained; it adds the unfiltered workbook to the ZIP. ZIP files are not encrypted.

## Scope and safe use

- Process public content, your own content or content you are explicitly authorized to use, and follow platform rules and applicable laws.
- The tool processes local files supplied by the user. It does not sign in or collect content automatically, and it does not bypass login, CAPTCHA or platform controls.
- Comments may contain personal information; limit access and avoid unnecessary redistribution.
- The current CLI does not include the in-development `collect` feature. See the [DATATOOL workflow](docs/DATATOOL_WORKFLOW.md) for export guidance.

## Documentation and support

- [Installation](docs/installation.md) · [Configuration](docs/configuration.md) · [Troubleshooting](docs/troubleshooting.md)
- [DATATOOL workflow](docs/DATATOOL_WORKFLOW.md) · [Platform compatibility](docs/PLATFORM_COMPATIBILITY.md) · [Architecture](docs/architecture.md)
- [Contributing](CONTRIBUTING.md) · [Security and privacy](SECURITY.md) · [Support](SUPPORT.md) · [Code of conduct](CODE_OF_CONDUCT.md)

## Development checks

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m mypy
python -m pytest --cov
python -m build
```

## License

This project is released under the [MIT License](LICENSE).
