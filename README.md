# MyApps：Scoop + Homebrew 发布仓库模板

基于 [ScoopInstaller/BucketTemplate](https://github.com/ScoopInstaller/BucketTemplate)，为 `punxch/MyApps` 准备。一个公开 GitHub 仓库同时存放 Windows Scoop 清单、macOS Homebrew Cask / Formula，以及多个软件的 Release 安装包。软件源代码可以留在其他私有仓库。

每个软件独立使用 `软件名-v版本` 标签，例如 `alpha-v1.2.0`、`beta-v3.4.0`。发布后，GitHub Actions 下载配置中的附件、计算 SHA256，并把双端清单和版本状态一起提交到默认分支。

> `alpha` 和 `beta` 是默认禁用的配置示例，尚无真实安装包。首次配置和发布成功前，安装命令不能安装它们。本模板不编译、签名或公证软件。

## 已接入的软件

| 软件 | 平台 | 安装 |
| --- | --- | --- |
| [Dota2 IME](docs/apps/dota2ime.md) | Windows x64 | `scoop install myapps/dota2ime` |

软件的二进制发布在本仓库 Releases，应用源码不在本仓库。`alpha`、`beta` 继续作为禁用的配置示例。

## 仓库结构

| 路径 | 用途 |
| --- | --- |
| `apps/*.json` | 每个软件的开关、支持平台、架构和附件命名 |
| `templates/*.scoop.json` | Scoop 安装规则；保留快捷方式、持久化、安装脚本等自定义字段 |
| `templates/*.cask.rb` | macOS 图形软件安装规则 |
| `templates/*.formula.rb` | macOS 命令行软件安装规则 |
| `bucket/`、`Casks/`、`Formula/` | 发布后生成的可安装清单 |
| `.release-state/` | 已发布版本、附件指纹和实际 SHA256 |
| `scripts/sync_releases.py` | Python 3.11+ 更新器，仅使用标准库 |
| `.github/workflows/` | 发布同步、跨平台检查、Scoop 官方测试 |
| `bin/` | 保留的 Scoop Bucket Template 辅助工具 |

## 首次使用

1. 将本目录推送到公开仓库 `punxch/MyApps`，默认分支建议 `main`；具体命令见 [发布指南](docs/PUBLISHING.md)。
2. 在 GitHub 仓库 Settings → General 勾选 **Template repository**，即可供以后复用。
3. 在 Settings → Actions → General 启用工作流，允许本模板使用的 Actions。同步工作流声明 `contents: write`；组织策略也必须允许它写入仓库。
4. 默认分支需要允许 `github-actions[bot]` 提交。本模板直接提交清单，没有自动 PR 模式；如果分支规则强制 PR，需要改用 PR 发布流程。本模板不会修改你的分支保护。
5. 编辑一个 `apps/*.json` 及其安装规则模板，填入真实软件信息后将 `enabled` 改成 `true`。
6. 提交配置，再按下面的流程发布第一个版本。

本模板使用公开附件下载地址，不包含私有 Release 的客户端鉴权。闭源软件可以公开分发二进制文件；模板的许可证不改变软件自身的许可证。

复用到其他新仓库时，在首次发布前执行：

```powershell
python scripts/configure.py your-name/your-repository
```

它只替换模板中预设的仓库地址；工作流在运行时自动读取实际 GitHub 仓库。已有发布状态的仓库迁移不能使用这个初始化命令。

## 添加软件

`alpha` 展示 Windows ZIP + macOS DMG 图形应用；`beta` 展示 Windows ZIP + macOS tar.gz 命令行应用。复制配置和模板，将文件名、`id`、Cask 名称 / Formula 类名、软件主页、许可证、包内路径改成真实值。

例如 `alpha-v1.2.0` 需要四个附件：

- `alpha-1.2.0-windows-x64.zip`
- `alpha-1.2.0-windows-arm64.zip`
- `alpha-1.2.0-macos-arm64.dmg`
- `alpha-1.2.0-macos-x64.dmg`

Windows ZIP 示例要求解压根目录有 `Alpha.exe`；DMG 示例要求包含 `Alpha.app`。如果目录结构不同，修改对应模板。没有某个架构的包，就从配置删除该架构；Homebrew 模板也要相应调整。支持只发布 Windows、只发布 macOS，以及 macOS Universal 包。

详细字段、安装类型和架构示例见 [配置说明](docs/CONFIGURATION.md)。不要把安装包放进 Git 历史；把它们作为 Release 附件上传。

## 日常发布

1. 为目标软件创建草稿 Release，标签为 `alpha-v1.2.0`。
2. 上传该软件这个版本的全部已配置附件。
3. 确认上传完成，再发布 Release。
4. 在 Actions 查看 **Sync release manifests**；成功后，双端清单会更新到同一次提交。

每个软件使用独立版本，不要求其他软件同时更新。更新器分页读取 Releases，并为每个软件选择数值最高的稳定版本，不依赖全仓库的 `latest`。支持 `X.Y.Z` 和 `X.Y.Z.N`；草稿、预发布、`-beta` 等标签不会进入稳定清单。

重复运行会复用已记录的校验和；如果同版本附件被替换、重命名或其指纹变化，更新器会拒绝接受它，要求发布新版本。也不会用旧 Release 降级已有清单。不要手动修改生成清单或删除 `.release-state` 来绕过这个检查。

缺少任意配置附件、下载失败或校验失败时，本批更新不会提交，也不会只提交 Windows 或 macOS 一端。额外的未配置附件（如更新日志、校验文件）会被忽略。

除了 Release 发布事件，还支持 Actions 页面手动运行、其他工作流调用，以及每 6 小时扫描补偿遗漏事件。定时运行可能延迟，且公开仓库长时间不活动时 GitHub 可能停用定时工作流。

**构建工作流用 `GITHUB_TOKEN` 创建 Release 时，不会因此触发另一个 Release 工作流。** 请在构建结束后显式调用本模板的可复用工作流，或使用手动调度；示例见 [发布指南](docs/PUBLISHING.md)。

## 用户安装

以下命令在真实软件首次发布并生成清单后使用。

Windows：

```powershell
scoop bucket add myapps https://github.com/punxch/MyApps
scoop install myapps/alpha
scoop update
scoop update alpha
```

macOS 图形软件：

```sh
brew tap punxch/myapps https://github.com/punxch/MyApps
brew install --cask punxch/myapps/alpha
brew update
brew upgrade --cask punxch/myapps/alpha
```

macOS 命令行软件：

```sh
brew install punxch/myapps/beta
```

仓库不必以 `homebrew-` 开头；首次 `brew tap` 时给出完整仓库 URL 即可。自行处理真实软件的签名、公证和更新兼容性，模板不会绕过系统验证。

## 本地检查与维护

```sh
python -m unittest discover -s tests -v
python scripts/sync_releases.py --check
python scripts/sync_releases.py --repository punxch/MyApps --all --dry-run
python scripts/sync_releases.py --repository punxch/MyApps --tag alpha-v1.2.0
```

`--check` 离线检查配置与已生成文件；`--dry-run` 仍需联网并下载新附件以计算实际校验和，但不写文件。手动同步后需要自己提交生成结果。未启用的软件不会自动生成清单。

修改已发布软件的安装规则后，运行同步重新生成，或在 Actions 手动运行同步；普通配置提交不自动运行发布同步，离线 CI 会提示清单是否已与模板不一致。更改架构或附件名称需要发布新版本。

CI 在 Windows、macOS 和 Linux 上运行生成器测试；macOS 使用 Homebrew 读取生成的 Cask / Formula；有真实 Scoop 清单时运行官方 Bucket 测试。测试夹具仅在临时目录生成，不冒充可安装软件。

机器人使用 `GITHUB_TOKEN` 提交不会再触发 push CI，所以同步工作流内直接执行生成器测试、结果一致性检查和 Ruby 语法检查。完整原生平台检查可在 Actions 手动运行，真实应用的安装验收仍需用真实附件完成。

## 模板来源与许可

保留上游 Unlicense 许可证及 Scoop 辅助工具；改造范围、上游版本和被停用的单端更新工作流见 [UPSTREAM.md](UPSTREAM.md)。闭源软件的授权条款由软件自己的许可证决定。

参考：[Scoop 清单规范](https://github.com/ScoopInstaller/Scoop/wiki/App-Manifests)、[Homebrew 自定义 Tap](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)、[Cask Cookbook](https://docs.brew.sh/Cask-Cookbook)、[GitHub 工作流触发规则](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow)。
