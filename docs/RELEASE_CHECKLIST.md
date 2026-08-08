# 发布检查清单

1. 更新版本号和 `CHANGELOG.md`。
2. 运行 Ruff、Mypy、覆盖率测试、依赖审计和构建。
3. 使用真实 FFprobe 对授权测试视频运行 `validate`。
4. 完成 `init -> validate -> package -> verify` 端到端检查。
5. 检查 Git 历史和构建产物中没有凭据或真实采集数据。
6. 为候选版本创建签名或带说明的 Git tag，并等待 GitHub Actions 通过。
7. 平台上传包必须带版本号、哈希、许可和支持说明。
8. 只有取得平台上传与安全审核结果后，才声明该平台兼容。
