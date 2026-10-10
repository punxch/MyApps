# 软件配置

每个软件对应一个 `apps/<id>.json`。示例：

```json
{
  "schema_version": 1,
  "id": "alpha",
  "enabled": true,
  "scoop": {
    "template": "templates/alpha.scoop.json",
    "assets": {
      "64bit": "alpha-{version}-windows-x64.zip",
      "arm64": "alpha-{version}-windows-arm64.zip"
    }
  },
  "homebrew": {
    "kind": "cask",
    "template": "templates/alpha.cask.rb",
    "assets": {
      "arm64": "alpha-{version}-macos-arm64.dmg",
      "x64": "alpha-{version}-macos-x64.dmg"
    }
  }
}
```

`id` 必须与配置文件名一致：小写字母开头，可以包含数字及单个连字符分隔的段，例如 `my-app`。软件名同时决定 Release 标签前缀、生成文件名和 Homebrew token。

| 字段 | 约束 |
| --- | --- |
| `schema_version` | 固定为 `1` |
| `enabled` | 布尔值；示例默认 `false`，填好真实信息后启用 |
| `scoop` / `homebrew` | 至少配置一个，可以只提供单端 |
| `template` | 仓库内 `templates/` 下的路径 |
| `assets` | 架构到 Release 附件文件名的映射 |
| `homebrew.kind` | `cask` 或 `formula` |

附件命名必须包含 `{version}`，允许 ASCII 字母、数字、点、短横线及下划线，以字母或数字开头。没有模糊匹配或“任意一个 zip”回退，以免拿错包。各架构的文件名必须不同。

Scoop 支持 `64bit`、`32bit`、`arm64`；Homebrew 支持 `arm64`、`x64`，或单独的 `universal`。配置了几个架构，就必须在同一个软件版本 Release 中上传几个对应附件。

## Scoop 安装规则

`templates/alpha.scoop.json` 是普通 Scoop 清单的一部分，至少提供 `description`、`homepage`、`license`。替换示例许可证网址，确认它确实指向自己的软件授权条款。

可以按真实包结构添加 `bin`、`shortcuts`、`extract_dir`、`persist`、`installer`、`uninstaller`、`pre_install`、`post_install` 等字段。EXE / MSI 安装程序要自行配置其静默参数、卸载方式；不能直接把 ZIP 文件名改成 EXE 就期待自动安装。

版本及下载字段 `version`、`url`、`hash` 由更新器生成；`checkver`、`autoupdate` 不使用。可在 `architecture` 下提供各架构安装规则，但不要放 `url` / `hash`：

```json
"architecture": {
  "64bit": { "extract_dir": "alpha-x64" },
  "arm64": { "extract_dir": "alpha-arm64" }
}
```

生成结果在 `bucket/<id>.json`。修改安装方式请编辑模板，再运行同步，不要直接修改生成结果。

## Homebrew 安装规则

图形应用用 Cask，命令行程序可用 Formula；两个示例都分发预编译二进制，不要求公开源代码。

所有占位符必须处于 Ruby 双引号字符串中：

| 占位符 | 内容 |
| --- | --- |
| `@@VERSION@@` | 当前软件版本 |
| `@@REPOSITORY@@` | 实际 owner/repository，可选 |
| `@@URL_ARM64@@` / `@@SHA256_ARM64@@` | Apple Silicon 包 |
| `@@URL_X64@@` / `@@SHA256_X64@@` | Intel 包 |
| `@@URL_UNIVERSAL@@` / `@@SHA256_UNIVERSAL@@` | Universal 包 |

每个配置架构都必须出现对应 URL 和 SHA256 占位符；不能用 `:no_check`。删除某个架构时也要删掉其模板分支与占位符，必要时加 `depends_on arch: :arm64` 或 `depends_on arch: :x86_64` 限制支持范围。

Cask 的 `cask "alpha"` 必须匹配软件 ID。DMG / ZIP 包内是应用时使用 `app "Alpha.app"`；PKG 使用 `pkg "Alpha.pkg"` 并根据软件情况补充 `uninstall`。文件名和实际包内路径必须由你确认。

Formula 的类名使用 ID 各段首字母大写拼接，例如 `my-app` → `MyApp`。CLI 示例 `beta.formula.rb` 使用 `bin.install "beta"`，要求解压后存在这个文件。按真实软件修改安装和测试逻辑。

Universal 配置：

```json
"homebrew": {
  "kind": "cask",
  "template": "templates/alpha.cask.rb",
  "assets": { "universal": "alpha-{version}-macos-universal.dmg" }
}
```

对应模板：

```ruby
cask "alpha" do
  version "@@VERSION@@"
  sha256 "@@SHA256_UNIVERSAL@@"
  url "@@URL_UNIVERSAL@@"
  name "Alpha"
  desc "Your application description"
  homepage "https://github.com/@@REPOSITORY@@"
  depends_on :macos
  app "Alpha.app"
end
```

## 版本和状态

稳定版本只接受 `X.Y.Z` 或 `X.Y.Z.N`，例如 `1.10.0`、`2.0.0.1`；数字段不能有前导零。比较按数值进行，所以 `1.10.0` 大于 `1.9.0`。不要同时发布 `1.2.3` 和 `1.2.3.0`，它们按同一版本处理。

`.release-state/<id>.json` 记录已经进入清单的版本、仓库、附件 ID / 大小 / 更新时间 / GitHub digest，以及实际下载计算的 SHA256。保留并提交这些文件，才能检测同版本附件更改与阻止回退。不要手工修改它们。

首次发布前可以自由修改配置。已发布后，安装规则可通过重新同步修订；新增架构、改变附件名称等需要发布新版本。切换 Cask / Formula 或删除平台时，应同时删除不再使用的旧生成文件；停用软件只需将 `enabled` 设为 `false`，它不会自动删除已有安装清单。

删除软件时，将其配置、对应生成清单、模板与状态文件一起删除。至少保留一个软件配置。测试使用独立夹具，重命名或替换实际示例不会破坏测试数据。
