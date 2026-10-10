# 创建仓库和发布

## 将模板上传到 punxch/MyApps

先在本机完成 GitHub CLI 登录；不要把令牌写进文件或提交进仓库：

```sh
gh auth login
```

如果解压后的目录没有 Git 历史，先初始化；已有 Git 仓库可跳过初始化和首次提交：

```sh
git init -b main
git add .
git commit -m "Initial Scoop and Homebrew repository template"
```

当目标仓库尚未存在时，在本目录执行：

```sh
gh repo create punxch/MyApps --public --source . --remote origin --push
gh api --method PATCH repos/punxch/MyApps -F is_template=true
```

如果仓库已存在，先检查其内容与默认分支，再决定如何合并，避免覆盖历史。此处不提供强制推送命令。

在 GitHub 仓库的 Actions 页面确认 **Template CI** 成功；Scoop 原生测试在生成真实清单前会跳过。仓库设置要允许同步工作流的 `contents: write`，默认分支不能阻止机器人直接提交。

本模板预设公开二进制分发。源代码可保存在私有仓库；公开的 Release 附件任何人都可以下载。

## 发布多个软件

分别创建 `alpha-v1.2.0`、`beta-v3.4.0`，每个 Release 只放对应软件的跨平台附件。软件共享同一仓库的 Releases 列表，但不会共享版本号。

以 alpha 为例，在项目外准备好安装包，执行：

```sh
gh release create alpha-v1.2.0 --repo punxch/MyApps --draft --title "Alpha 1.2.0" --notes "本版本的更新说明"
gh release upload alpha-v1.2.0 --repo punxch/MyApps ./dist/alpha-1.2.0-windows-x64.zip ./dist/alpha-1.2.0-windows-arm64.zip ./dist/alpha-1.2.0-macos-arm64.dmg ./dist/alpha-1.2.0-macos-x64.dmg
gh release edit alpha-v1.2.0 --repo punxch/MyApps --draft=false
```

`dist` 是你自行准备的构建产物目录，不在模板里提供。还没有正确配置 `apps/alpha.json` 和对应模板时，不要发布。

不要在发布后补齐必需附件。若发布时遗漏了附件，补齐后手动重跑同步；清单此前若已成功更新，则不要再替换同版本附件，应发布新版本。工作流不会自动标记 GitHub Release 为 immutable；你也可按自己的发布流程开启不可变 Release。

## 与软件构建工作流衔接

通过 `GITHUB_TOKEN` 创建的 Release 不会触发另一个 `release` 工作流。若构建就在本仓库，给已有构建 / 发布工作流增加后续 job：

```yaml
jobs:
  publish:
    # 此处保留你自己的构建、上传全部附件、发布 Release 步骤。
    # 此示意不是完整可执行的工作流；publish job 需由你实现。
    # ...

  update_manifests:
    needs: publish
    permissions:
      contents: write
    uses: ./.github/workflows/sync-releases.yml
    with:
      tag: alpha-v1.2.0
```

也可以不传 `tag`，由工作流同步所有启用软件的最高稳定版本。`workflow_call` 用于本仓库调用；不要把这个更新工作流直接作为其他仓库的通用库调用，运行上下文属于调用方仓库。

构建在私有源码仓库时，先将二进制附件发布到公开的 `punxch/MyApps`，然后显式调度目标仓库工作流：

```sh
gh workflow run sync-releases.yml --repo punxch/MyApps -f tag=alpha-v1.2.0
```

跨仓库上传和调度需要对目标仓库有相应权限的 GitHub App / 细粒度令牌（上传需要 Contents write，调度需要 Actions write），放在源仓库 Secrets 中。源仓库自己的 `GITHUB_TOKEN` 通常无权写另一个仓库。本模板未创建或配置这些凭据。

Release 发布事件默认全量对账，以补偿多个软件短时间连续发布时事件排队合并。手动传入 `tag` 则只处理匹配的软件；每 6 小时的定时对账作为兜底。

## 失败处理

| 现象 | 处理 |
| --- | --- |
| 找不到附件 | 检查精确文件名、版本、架构和上传是否完成，再重跑 |
| 同版本附件发生变化 | 发布更高版本，不覆盖旧安装包 |
| 无清单生成 | 确认配置启用、标签为软件 ID 加 `-v` 和数值版本，且不是草稿 / 预发布 |
| 推送被拒绝 | 检查 Actions 写权限、默认分支规则；若是并发人工提交，重新运行同步 |
| 模板与清单不一致 | 同步重新生成，并同时提交模板与输出 |
| 下载 404 / 403 | 确认仓库与 Release 附件公开，检查 GitHub API 限流 |
| Ruby / Homebrew 解析失败 | 检查自定义安装模板，在 macOS 上运行原生验证 |
| 安装时找不到应用 / 可执行文件 | 校正模板中的真实包内路径与安装命令 |

清单提交使用 `GITHUB_TOKEN`，不会再自动触发 push CI。同步任务内检查生成器与 Ruby 语法，但无法在 Linux 上完成 Windows / macOS 应用安装；请在 Actions 页面运行 **Template CI** / **Scoop tests** 并在实际目标系统验收真实软件。
