# ENHE GitHub Open Source Standard

版本：1.2
生效日期：2026-08-08
适用仓库：`social-content-data-packager`

## 仓库标准

保留现有 `src/`、`tests/`、`examples/` 架构，不为套模板强制重构。源代码、测试和文档应可
从锁定或可追溯的 Python 依赖安装复现；媒体、评论、浏览器状态、构建产物和本地环境不入库。
中文主入口为 `README.md`，英文入口为 `README.en.md`，二者必须同步关键事实。现有
`README.zh-CN.md` 保留为兼容性文档，不作为新标准主文件。

README 首屏只使用可验证 badge，不要求 Logo 或 Cover。当前项目的旧 Cover 位于
`docs/assets/project-cover.png`，但来源和再分发许可未确认；它不属于本次 Release Candidate，README
也不得引用它。不得把视觉计划、生成提示词、本地参考路径或未确认素材纳入公开候选。

## Visual Assets Decision Policy

ENHE GitHub Open Source Standard v1.2 使用 `VISUAL_ASSET_POLICY = OPTIONAL_BY_PROJECT`。当前项目属于
Python CLI / 数据打包工具，核心功能可由文字、命令和真实流程解释，因此作出长期项目决定：

```text
CURRENT_PROJECT_VISUAL_ASSETS_REQUIRED = NO
CURRENT_PROJECT_VISUAL_POLICY_REASON = CLI_AND_DATA_PACKAGING_TOOL
VISUAL_ASSETS_STATUS = NOT_REQUIRED_FOR_CURRENT_RELEASE
```

当前稳定版本允许纯文字 README 首屏；Logo、Cover 缺失不阻断 Release Candidate，也不得被错误标记为
安全或质量失败。如果未来增加 GUI、品牌页或产品展示需求，再以独立可选任务判断是否补充视觉资产。
任何未来资产仍必须有可追溯来源、明确再分发权、真实内容、隐私复核和有效 README 引用。禁止来源不明
图片、空白或纯色占位图、失效链接、虚假界面/用户数据/Star/下载量/Benchmark、未授权第三方品牌、
水印、乱码文字和未经复核的旧素材。视觉政策不降低 Secret、隐私、License、测试、构建、文档、CI
或 GitHub 平台合规标准。

## 安全与合规

只处理公开或明确授权的导出数据。禁止凭据、个人数据、未授权第三方代码/素材、登录或验证码
绕过、恶意行为及虚假 GitHub 互动。浏览器采集只能使用用户创建的独立 CDP profile。发布前扫描
工作树、暂存区、所有 refs 和历史 blob；发现历史秘密时先轮换并完成历史清理评估。

## Git 标准

保留无关的工作树改动；提交前检查 status、diff、暂存文件和大文件。使用单一逻辑目的的
Conventional Commit 前缀，禁止常规 force-push `main`。大于 50 MiB 的对象必须有明确处理方案，
100 MiB 单文件不得直接进入普通 Git。

## Release 标准

版本按 Semantic Versioning 思路维护 `CHANGELOG.md`，稳定版本才创建 `vX.Y.Z` 标签。先运行真实
存在的 test、lint、typecheck（如适用）、build、依赖审计、Secret/历史/大文件扫描和文档检查，
并在本地保留发布前审计报告。任何关键检查失败、证据缺失、许可证/授权不清、目标或
账号不明确时写 `READY_TO_PUBLISH=NO` 并停止。

GitHub 写入默认禁止。只有报告为 `READY_TO_PUBLISH=YES` 且用户在当前发布上下文明确输入
`APPROVE_GITHUB_PUBLISH`，才可执行逐项列明的批准动作；403、429、账号限制、滥用检测、速率限制
或仓库限制必须立即停止，不得换账号、Token、IP 或高频重试。

## 文档与持续维护

任何公共 API、安装、配置、CLI 行为或安全边界变化都必须同步 README、相关 `docs/`、治理文件
和 `CHANGELOG.md`。所有 Codex Agent 开始工作前必须读取 `AGENTS.md`、`README.md`、
`README.en.md`、`CONTRIBUTING.md` 和 `SECURITY.md`。每次准备发布还必须复核 README 链接、
活动图片引用、使用流程、视觉资产适用性、`.gitignore` 和 `.env.example`。

## v1.2 状态字段

发布报告必须单独记录：`README_MAIN`、`README_EN`、`USAGE_WORKFLOW`、`README_LINKS`、
`README_IMAGES`、`CURRENT_PROJECT_VISUAL_ASSETS_REQUIRED` 和 `VISUAL_ASSETS_STATUS`。可选视觉资产缺失
应标记 `NOT_REQUIRED_FOR_CURRENT_RELEASE`，不得标记为失败；任何未处理的 Secret、隐私、许可证、
版权、账号或平台风险仍使 `READY_TO_PUBLISH=NO`。
