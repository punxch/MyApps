# 上游来源

基础项目：[ScoopInstaller/BucketTemplate](https://github.com/ScoopInstaller/BucketTemplate)

- 本模板基于提交 `dd0ce8ae6a9e55bf12793f744c2fcc80a2178c27`，获取日期：2026-10-10。
- 保留上游 `LICENSE`（Unlicense）、`bin/` 辅助工具、`bucket/app-name.json.template`、`Scoop-Bucket.Tests.ps1`、编辑器配置及贡献模板。
- 修改 `bin/auto-pr.ps1` 的默认仓库为 `punxch/MyApps:main`；修改换行和忽略规则。
- 原始工作流存档在 `docs/upstream-workflows/`，不在 Actions 执行目录内。
- 活跃工作流改为跨平台 CI、官方 Scoop 测试，以及一个统一的双端 Release 更新器。
- Scoop 测试入口将官方格式检查限定到 `bucket/`；该目录使用 CRLF，其余跨平台文件使用 LF。Scoop CI 校验全部已发布清单，不仅检查最后一次提交中变动的文件。

没有启用上游 Excavator / 自动提交类更新工作流，因为本模板用同一个 Release 数据源同时维护 Scoop 和 Homebrew。也不在生成的 Scoop 清单里写 `checkver` / `autoupdate`，避免另一套更新任务独立改动 Windows 版本。

本交付是上游文件的改造副本，不是通过 GitHub 的 “Use this template” 按钮在线创建，因此不会自动显示 GitHub 的 “generated from” 标识；可在仓库设置中将它设为新的 Template repository。
