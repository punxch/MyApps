# MyMouse

MyMouse 在 Windows 和 macOS 电脑之间共享键盘、鼠标及文本/图片剪贴板，提供图形配置界面、托盘/菜单栏入口和命令行工具。

本仓库只分发编译后的软件及安装清单，不包含 MyMouse 源代码。仓库模板的 Unlicense 不适用于 MyMouse 应用。

## 支持的平台

| 系统 | 架构 | 发布附件 |
| --- | --- | --- |
| Windows 10/11 | x64 | `mymouse-版本-windows-x64.zip` |
| macOS 12 Monterey 及以上 | Apple Silicon 和 Intel（Universal） | `mymouse-版本-macos-universal.zip` |

## 安装

Windows 使用 Scoop：

```powershell
scoop bucket add myapps https://github.com/punxch/MyApps
scoop install myapps/mymouse
```

在开始菜单打开 **MyMouse**。`mymouse` 命令可用于命令行操作。

macOS 使用 Homebrew：

```sh
brew tap punxch/myapps https://github.com/punxch/MyApps
brew install --cask punxch/myapps/mymouse
```

打开“应用程序”中的 **MyMouse**，也可以使用 `mymouse` 命令。

手动安装：从 [Releases](https://github.com/punxch/MyApps/releases) 下载对应 ZIP。Windows 完整解压后运行 `mymouse_settings.exe`，不要只复制 EXE；Mac 将 `MyMouse.app` 移到“应用程序”后打开。

Windows 包未做发行者代码签名；Mac 包使用临时本地签名，尚未取得 Developer ID 签名和 Apple 公证。macOS 如阻止打开，请在确认下载来源后按 [Apple 的应用打开说明](https://support.apple.com/en-us/102445) 操作。安装清单不会关闭系统安全检查。

## 首次使用

1. 在两台电脑上启动 MyMouse，在设备页发现对端，或输入对端地址。默认共享端口为 TCP 24810，局域网发现使用 UDP 5353；按系统提示允许所需的本地网络连接。
2. 比对当次配对显示的八位校验码，双方确认后再开始共享。
3. 在布局页将对端屏幕放到本机屏幕旁，保存后从相接的边缘移动鼠标跨屏。
4. Mac 需为实际后台程序授予“辅助功能”“输入监控”权限；按应用诊断页引导检查。重新构建或更新后可能需要重新授权。
5. 剪贴板同步在两端设置页分别启用，连接后从下一次复制开始同步；支持纯文本和图片，不支持文件传输。

默认 **F6** 切换光标锁定；**Ctrl + Alt + Shift + Esc** 紧急释放远程控制。关闭配置窗口会隐藏到托盘/菜单栏，共享仍可继续；要完全退出，请使用托盘/菜单栏的“退出”。

macOS 登录自启是当前用户登录后的启动项。保留 FileVault；每次重启先在 Mac 本机解锁并登录桌面，再使用共享，不提供登录前控制。

## 更新与卸载

Windows 的 Scoop 安装步骤会将本安装目录已有的登录自启项迁移到 `current\mymouse.exe` 并启用后台模式，无需先打开新版界面。未启用自启的用户不会被自动启用；其他安装目录和自定义命令不会被修改。

升级前先从托盘/菜单栏完全退出应用，升级后重新打开：

```powershell
scoop update
scoop update mymouse
```

```sh
brew update
brew upgrade --cask punxch/myapps/mymouse
```

卸载前先在设置中关闭登录自启，并完全退出应用；然后执行 `scoop uninstall mymouse` 或 `brew uninstall --cask punxch/myapps/mymouse`。配置、配对身份和系统权限保留，不会随着卸载被自动删除。使用自定义配置目录的用户应分别关闭对应配置的自启。

默认配置目录：Windows `%APPDATA%\MyMouse\MyMouse\config`；macOS `~/Library/Application Support/dev.MyMouse.MyMouse`。分享诊断信息时使用应用的脱敏诊断功能，不要公开原始配置或身份文件。

## 验证范围

发布前检查双端自动测试、原生 Release 打包、包内组件与架构和校验和。自动测试中的模拟输入不代表 Windows ↔ Mac 实体键鼠、剪贴板、锁屏、自启及不同 DPI 场景已全部验收；这些仍需真实设备验证。
