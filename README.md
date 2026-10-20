# social-content-data-packager

把公开或已获授权的社交内容导出文件整理成可校验的 ZIP 数据包。它是一个在本机运行的 Python 命令行工具。

简体中文 | [English](README.en.md)

[![License: MIT](https://img.shields.io/github/license/yangjing6213-dev/social-content-data-packager?style=flat-square)](https://github.com/yangjing6213-dev/social-content-data-packager/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-%233670A0.svg?style=flat-square&logo=python&logoColor=ffdd54)](https://www.python.org/) [![OpenPyXL](https://img.shields.io/badge/OpenPyXL-3.x-2F6FEB?style=flat-square)](https://openpyxl.readthedocs.io/)
[![FFmpeg](https://img.shields.io/badge/ffmpeg-%23007808.svg?style=flat-square&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/) [![Whisper optional](https://img.shields.io/badge/Whisper-optional-412991?style=flat-square&logo=openai&logoColor=white)](https://pypi.org/project/openai-whisper/)

项目接收已经导出的本地文件，例如视频、封面、页面文案和评论；检查文件后生成中文 Excel、ZIP 数据包和 SHA-256 完整性清单。视频转写是可选功能，由本地 Whisper 处理。

登录平台、导出内容和确认授权由使用者完成。已有符合下方目录要求的文件即可开始，不需要本项目自动采集。

## 功能一览

| 命令 | 用途 |
| --- | --- |
| `init` | 创建任务目录和元数据模板。 |
| `validate` | 检查必需元数据、评论表头，并用 FFprobe 确认视频含有效视频流。 |
| `package` | 生成中文 Excel、ZIP 数据包和 SHA-256 文件清单。 |
| `verify` | 独立检查 ZIP 文件、路径、文件大小和 SHA-256。 |
| `transcribe` | 可选：用本地 Whisper 生成完整视频口播的 TXT、分段 JSON 和 SRT。 |

`package --transcribe-video` 可以先转写，再生成数据包。转写结果是自动识别内容，不是作者官方字幕；分享或分析前请人工检查。

## 使用流程

1. 用 DATATOOL 或其他方式取得公开或已授权的内容导出文件。
2. 创建任务目录：

   ```bash
   social-content-packager init "我的任务"
   ```

3. 将文件放入 `我的任务/输入/`。`元数据.json` 和 `视频素材.mp4` 为必需文件；评论工作簿、封面和已有转写文件可选。元数据可参考[示例](examples/元数据示例.json)。
4. 填写并检查元数据，然后验证输入：

   ```bash
   social-content-packager validate "我的任务"
   ```

5. 生成数据包：

   ```bash
   social-content-packager package "我的任务"
   ```

   命令会显示 ZIP 文件的完整路径。

6. 将上一步显示的路径交给校验命令：

   ```bash
   social-content-packager verify "此处替换为上一步显示的 ZIP 路径"
   ```

例如，任务目录通常包含：

```text
我的任务/
├── 输入/
│   ├── 元数据.json                  必需
│   ├── 视频素材.mp4                 必需
│   ├── 原始评论.xlsx                可选
│   ├── 封面图片.webp                可选，也支持 jpg/jpeg/png
│   └── 视频文案（分段数据）.json     可选
└── 输出/                            生成的数据包
```

## 安装

需要 Python 3.10 或更高版本。`pip install -e .` 会安装必需的 OpenPyXL。输入视频并运行 `validate` 或 `package` 前，需安装 FFmpeg 和 FFprobe。

```bash
git clone https://github.com/yangjing6213-dev/social-content-data-packager.git
cd social-content-data-packager
python -m venv .venv
```

激活虚拟环境，按你的系统选择一条命令：

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

然后安装并检查本机工具：

```bash
python -m pip install -e .
social-content-packager doctor
```

`doctor` 会检查 FFmpeg 和 FFprobe 是否可用。安装视频工具的方法见[安装说明](docs/installation.md)。

### 可选：本地视频转写

安装可选依赖后，可以在打包时一并转写：

```bash
python -m pip install -e ".[transcribe]"
social-content-packager package "我的任务" --transcribe-video --model small --language zh
```

也可以单独运行 `social-content-packager transcribe "我的任务"`。若任务目录已有转写文件，程序默认不会覆盖；确认替换时再使用 `--force` 或 `--force-transcript`。

### 评论隐私

默认数据包不包含原始评论工作簿，但汇总 Excel 仍可能含评论内容。分享前请检查个人信息；需要时可用 `--anonymize-comments` 脱敏汇总表中的身份字段。只有确需保留原表时才使用 `--include-raw-comments`，它会把未经净化的原始工作簿放进 ZIP。ZIP 文件本身不加密。

## 使用边界

- 仅处理公开内容、本人所有的内容或已明确授权的内容，并遵守平台规则和适用法律。
- 本工具处理使用者提供的本地文件，不负责登录或自动采集，也不提供绕过登录、验证码或平台限制的功能。
- 评论可能包含个人信息；请限制访问并避免不必要的二次传播。
- 当前命令行不包含开发中的 `collect` 自动采集功能。平台导出步骤见 [DATATOOL 工作流](docs/DATATOOL_WORKFLOW.md)。

## 文档与支持

- [安装说明](docs/installation.md) · [配置说明](docs/configuration.md) · [排障指南](docs/troubleshooting.md)
- [DATATOOL 工作流](docs/DATATOOL_WORKFLOW.md) · [平台兼容说明](docs/PLATFORM_COMPATIBILITY.md) · [架构说明](docs/architecture.md)
- [贡献指南](CONTRIBUTING.md) · [安全与隐私](SECURITY.md) · [支持渠道](SUPPORT.md) · [行为准则](CODE_OF_CONDUCT.md)

## 开发检查

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m mypy
python -m pytest --cov
python -m build
```

## 许可证

本项目采用 [MIT 许可证](LICENSE)。
