# Skill 可行性分析

## 结论

本项目已转换为“热门平台数据采集Skill”，推荐可行性为：

- 数据整理、转写和打包：高，约 8/10。
- 浏览器内完整自动采集：中等，约 5/10。
- 跨智能体复用：高，但应以 CLI 作为稳定核心，以不同智能体的 Skill/Tool 格式作为适配层。

最合适的架构不是把所有逻辑复制进 `SKILL.md`，而是让 Skill 调用本仓库提供的确定性 CLI。

## 推荐 Skill 结构

标准 Skill 名称：`collect-popular-platform-data`

```text
collect-popular-platform-data/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── run_packager.py
└── references/
    ├── datatool-workflow.md
    ├── input-schema.md
    └── privacy-guardrails.md
```

职责划分：

- `SKILL.md`：触发条件、核心步骤、何时要求用户登录或确认授权。
- `scripts/run_packager.py`：检测并调用 `social-content-packager`，不复制打包实现。
- `references/datatool-workflow.md`：DATATOOL 安装和页面操作说明。
- `references/input-schema.md`：文件命名与元数据结构。
- `references/privacy-guardrails.md`：公开内容、个人数据和账号凭据边界。

## 适合触发 Skill 的请求

- “把这个公开视频、文案和评论整理成数据包。”
- “使用 DATATOOL 导出评论并生成中文 Excel。”
- “提取视频口播文案并和评论一起打包。”
- “校验这个社交内容归档包是否完整。”

## Agent 工作流

1. 确认目标是公开内容、本人内容或已获授权内容。
2. 运行 `social-content-packager doctor` 检查依赖。
3. 通过 `init` 创建任务目录。
4. 引导用户安装 DATATOOL、完成登录和验证码。
5. 使用真实浏览器打开目标页面；每次交互前读取最新页面状态。
6. 导出视频、封面和评论到标准输入目录。
7. 可选运行 `transcribe`，提醒用户人工复核。
8. 运行 `validate`，修正占位元数据、评论表头或无效媒体。
9. 运行 `package`，按用途选择评论脱敏或显式包含原始工作簿。
10. 运行 `verify`，复核 ZIP 文件集合、大小和 SHA-256。
11. 只交付最终数据包，不传播账号 profile、Cookie 或临时下载地址。

## 不能放入 Skill 的内容

- DATATOOL 扩展安装包或付费账号。
- 浏览器 profile、Cookie、访问令牌或账号密码。
- 采集到的视频、评论或其他用户数据。
- 针对验证码、登录或反爬机制的绕过逻辑。
- 易过期的 CDN 签名链接。

## 主要限制

### 浏览器扩展依赖

Skill 无法保证自动安装或控制所有浏览器扩展。Codex 所在环境必须允许有头浏览器、持久 profile 和扩展加载。部分智能体平台只提供无头浏览器，无法完成这一步。

### 人工登录与授权

扫码、验证码、二次验证、付费升级和平台授权应由用户完成。Skill 需要在这些环节暂停，而不是尝试绕过。

### 页面与扩展更新

平台 DOM、DATATOOL 菜单和导出格式都可能变化。Skill 应优先使用可访问性快照和可见按钮名称，不应长期依赖固定 CSS 选择器。

### 数据合规

评论包含用户生成内容和可能的个人信息。Skill 必须在采集前确认用途，在交付时提示限制传播，并默认排除账号信息和浏览器状态。

## Codex 与其他智能体

- Codex：可使用标准 `SKILL.md`、`agents/openai.yaml`、脚本和参考资料。
- 其他支持 Skill 的智能体：可以复用 CLI 和参考文档，但可能需要适配其目录结构和触发元数据。
- 不支持 Skill 的智能体：仍可通过 shell 调用 CLI。
- 更稳定的跨平台方案：后续可把 `init`、`transcribe`、`package`、`verify` 暴露为本地 MCP Server 工具。

## 推荐演进路线

1. 稳定当前 CLI 和输入格式。
2. 收集至少三个不同平台的真实、授权样本进行兼容性测试。
3. 在 AGENSI 与 AgentPowers 完成真实上传和平台安全审核。
4. 如需跨智能体调用，再增加本地 MCP Server；不要把浏览器登录状态放进 MCP 配置。
