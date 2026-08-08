# DATATOOL 工作流

## 1. 安装与登录

1. 打开 [DATATOOL 官方网站](https://www.datatool.vip/?from=extension)。
2. 按照[官方扩展安装指南](https://www.datatool.vip/downloader/install-plugin/en-us)选择 Chrome、Edge、Firefox 或手动安装方式。
3. 在正常浏览器窗口打开扩展并登录 DATATOOL。
4. 打开目标平台并完成平台登录。验证码、扫码或风险确认必须由用户本人完成。

官方商店：

- [Chrome Web Store](https://chromewebstore.google.com/detail/datatool-downloader/dcembjiicioienepbaldihjhmkedagee)
- [Microsoft Edge Add-ons](https://microsoftedge.microsoft.com/addons/detail/datatool-downloader/fnojafohdfhmnkbjonengkcfclhkbkcm)
- [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/datatool-downloader/)

## 2. 选择内容

- 优先使用单条公开内容链接进行测试。
- 确认内容允许下载、研究或归档。
- 不要采集私密账号、未成年人敏感信息、登录后无权访问的内容或超出合理用途的数据。

## 3. 导出素材

在目标内容页面使用 DATATOOL：

1. 下载视频，测试时建议先选择 720P 或 1080P。
2. 下载封面图片。
3. 导出页面正文或自行填入 `元数据.json`。
4. 导出评论；需要回复时选择“包含子评论”。

不同站点提供的按钮、文件格式和清晰度可能不同。DATATOOL 的账号等级也可能影响可用功能。

## 4. 整理输入目录

将 DATATOOL 导出的文件重命名后放入任务目录：

```text
输入/
├── 元数据.json
├── 视频素材.mp4
├── 原始评论.xlsx
└── 封面图片.webp
```

封面也可以是 `封面图片.jpg`、`封面图片.jpeg` 或 `封面图片.png`。

项目不会读取 DATATOOL 账号、浏览器 Cookie 或登录 profile。

## 5. 完整视频口播转写

安装 FFmpeg 和 Whisper 后，推荐在打包时一次完成整段视频音轨转写：

```bash
social-content-packager package "任务目录" --transcribe-video --model small --language zh
```

该命令处理完整的 `视频素材.mp4` 音轨，提取从头到尾的口播和对白，再生成数据包。它不会把标题、页面简介当成视频内容，也不会识别只有画面显示而没有读出的文字；后者需要 OCR。

如果视频包含品牌名或专业词，在 `--initial-prompt` 中提供关键词。已有转写文件默认不会被覆盖，确认替换时使用 `--force-transcript`。自动识别后应结合视频硬字幕或人工听写检查：

- 人名和品牌名
- 数字、金额和日期
- 网址、命令和 API 名称
- 否定词及风险提示

只生成转写文件供人工校对时运行：

```bash
social-content-packager transcribe "任务目录" --model small --language zh
```

独立转写命令确认覆盖时使用 `--force`。

## 6. 打包

不需要自动转写，或输入目录已有有效转写分段时，先验证输入：

```bash
social-content-packager validate "任务目录"
```

验证通过后打包：

```bash
social-content-packager package "任务目录"
```

存在有效转写分段时，生成的 ZIP 包含统一工作簿、媒体、完整口播文案、SRT、
分段 JSON 和 SHA-256 清单。没有转写时不会生成空的视频文案文件，且
`使用说明.txt` 会明确记录本次未提取完整视频口播。原始评论
工作簿默认不进入数据包；确需保留时使用 `--include-raw-comments`，对外分享时
优先使用 `--anonymize-comments`。校验清单不包含自身哈希，因为文件无法稳定
记录自己的最终哈希。

最后独立校验：

```bash
social-content-packager verify "生成的数据包.zip"
```

## 已知限制

- 页面评论数与导出数可能不同，常见原因包括评论删除、审核、分页或接口未返回。
- DATATOOL 可能将回复扁平化，不一定提供父评论编号。
- 平台页面结构和扩展界面会更新，按钮名称可能变化。
- 某些浏览器会限制扩展下载能力；请查看 DATATOOL 官方安装页和 FAQ。
- 本项目不自动处理验证码、扫码登录、风控确认或付费升级。
- CDN 临时地址可能过期，应以已经下载到本地的媒体文件为准。
