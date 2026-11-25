# MyPaste

MyPaste 是原生剪贴板历史工具，提供底部卡片面板、搜索、收藏分组、富文本与图片保存、文件引用、截图编辑和局域网同步。

本仓库分发 MyPaste 的编译后软件及安装清单，应用源码保留在独立仓库。应用沿用 MIT License，许可文件随发布包提供。

## 支持的平台

| 系统 | 架构 | 发布附件 |
| --- | --- | --- |
| Windows 10 1607 及以上 / Windows 11 | x64 | `mypaste-版本-windows-x64.zip` |
| macOS 15.4 及以上 | Apple Silicon（arm64） | `mypaste-版本-macos-arm64.dmg` |

Windows 使用原生 Win32，Mac 使用原生 AppKit。Windows 的截图编辑器需要 Microsoft Edge WebView2 Runtime，Mac 使用系统自带的 WebKit。

## 安装

Windows：

```powershell
scoop bucket add myapps https://github.com/punxch/MyApps
scoop install myapps/mypaste
```

从开始菜单打开 **MyPaste**。手动安装时从 [Releases](https://github.com/punxch/MyApps/releases) 下载 ZIP，完整解压后运行 `MyPaste-windows-x86_64/MyPaste.exe`。

Mac：

```sh
brew tap punxch/myapps https://github.com/punxch/MyApps
brew install --cask punxch/myapps/mypaste
```

从“应用程序”打开 **MyPaste**。手动安装时下载 DMG，将 **MyPaste** 拖入 **Applications**。

Windows 包未做发行者代码签名。Mac 包使用临时本地签名，尚未取得 Developer ID 签名和 Apple 公证。如果 macOS 阻止打开，请确认下载来源后参考 [Apple 的应用打开说明](https://support.apple.com/en-us/102445)。更新后可能需要重新授予系统权限。

## 首次使用

1. 在欢迎窗口或设置中启用“记录剪贴板历史”，保存后开始记录；暂停期间的内容不会补录。
2. Windows 默认 **Ctrl + Shift + V**，Mac 默认 **⌘ + Shift + V**，用于呼出或收起卡片面板。
3. 双击或 Enter 粘贴，Shift + Enter 粘贴纯文本；可搜索、收藏、分组和拖动排序。
4. Mac 的自动粘贴需要“辅助功能”权限；如系统提示读取剪贴板或本地网络权限，按实际使用的功能授权。
5. 首次配对时，在同一局域网的两台设备上打开“局域网同步”。两台未配对的设备互为唯一候选时会自动连接，发现多台设备时在“设备与传输”中选择目标。可右键单条卡片共享，也可开启默认关闭的“自动同步”以共享新记录的内容。收到的内容单独显示在“局域网同步”页。

应用常驻托盘或菜单栏，要完全退出请使用其“退出”菜单。历史可记录文本、HTML/RTF、图片和文件引用。

## 截图与编辑

按 **F1** 开始截图，可拖选区域或单击高亮窗口。选择区域后可添加画笔、形状、文字、马赛克等标注，或使用图层面板调整顺序。支持复制、保存 PNG、钉图、滚动长截图和 GIF 录制。Mac 首次截图时需在“系统设置 → 隐私与安全性 → 屏幕与系统音频录制”中允许 MyPaste。

## 数据、更新和卸载

默认数据目录为 Windows `%LOCALAPPDATA%\MyPaste`、Mac `~/Library/Application Support/MyPaste/`。历史、原始内容和缩略图保存在本地，没有额外的应用层加密。备份时先完全退出，再复制整个数据目录。Windows 配对私钥由当前用户账户保护。更换电脑时请重新配对。

从 0.1.0 升级时，旧版 Mac 若仅在钥匙串中保存配对身份，需在“设备与传输”中退出原组后重新配对。如果该 Mac 是组管理员，其他成员也需要退出并重新组建共享组。退出会清除该设备的共享列表，普通剪贴板历史和已保存的文件副本仍可使用。

升级前从托盘/菜单栏退出应用，完成升级后重新打开：

```powershell
scoop update
scoop update mypaste
```

```sh
brew update
brew upgrade --cask punxch/myapps/mypaste
```

卸载前关闭应用内的登录启动，并完全退出；然后运行 `scoop uninstall mypaste` 或 `brew uninstall --cask punxch/myapps/mypaste`。历史和设置保留，不会自动删除。移动手动安装目录后，应关闭再重新启用登录启动，以更新路径。

## 验证范围

双端构建运行核心测试、静态检查及项目提供的隔离原生检查，再核验实际 ZIP / DMG 的内容、架构、许可文件和 SHA256。模拟与隔离测试不替代真实输入法、物理快捷键、多显示器、系统权限及不同目标应用的兼容性验收。原生剪贴板测试在 Windows 无法创建隔离窗口站时会明确跳过，不会改为访问用户剪贴板。
