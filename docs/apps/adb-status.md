# ADB Status

ADB Status 是原生 ADB 状态浮窗，显示 Android 设备连接状态、可用设备数量及电量，支持拖放 APK 安装。支持 Windows 10/11 x64 和 macOS 11 及以上的 Apple Silicon Mac。

本仓库分发编译后的应用、Scoop 清单与 Homebrew Cask，源码保留在独立仓库。当前发布版本为 [0.3.0](https://github.com/punxch/MyApps/releases/tag/adb-status-v0.3.0)，提供 `adb-status-0.3.0-windows-x64.zip` 和 `adb-status-0.3.0-macos-arm64.zip`。Windows 包为单个 EXE，内嵌固定版本 37.0.1 的备用 ADB；Mac 包需另行安装 adb，不提供 Intel 版。

## 安装

### Windows：Scoop

在 PowerShell 中执行：

```powershell
scoop bucket add myapps https://github.com/punxch/MyApps
scoop install myapps/adb-status
```

从开始菜单打开 **ADB Status**，或执行 `adb-status`。已添加过 bucket 时跳过第一行。手动安装则从 Release 下载 Windows ZIP，解压后运行 **ADB Status.exe**；无需安装 Rust、PowerShell 运行库或单独下载 ADB，不包含 USB 驱动。Windows 包尚未进行发行者代码签名。

### macOS：Homebrew

```sh
brew tap punxch/myapps https://github.com/punxch/MyApps
brew install --cask punxch/myapps/adb-status
```

从“应用程序”打开 **ADB Status**。手动安装时，从 Release 下载 macOS ZIP，解压后将 **ADB Status.app** 拖入“应用程序”。Homebrew 自身有独立的系统要求；无法使用 Homebrew 时可手动安装。

应用使用临时本地签名，尚未经过 Apple Developer ID 签名或公证。如果 macOS 阻止打开，请确认下载来源后参考 [Apple 的应用打开说明](https://support.apple.com/en-us/102445)。

## ADB 配置

在设备上启用 USB 调试并确认授权。Mac 需自行安装 Android SDK Platform Tools；Windows 优先使用已有的 `adb.exe`，找不到时才使用内嵌备用版。应用按以下顺序查找已有 ADB：

1. `ANDROID_HOME/platform-tools/adb`
2. `ANDROID_SDK_ROOT/platform-tools/adb`
3. Mac：`~/Library/Android/sdk/platform-tools/adb`；Windows：`%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe`
4. Mac：`/opt/homebrew/bin/adb`、`/usr/local/bin/adb`；Windows：应用所在目录的 `adb.exe`
5. `PATH` 中的 adb（Windows 为 `adb.exe`）

Finder 启动一般不继承终端环境变量，建议使用标准 SDK 或 Homebrew 路径。

Windows 首次需要备用 ADB 时，将 EXE 内嵌的 ADB、配套 DLL、上游许可声明和版本文件释放到 `%LOCALAPPDATA%\adb-status\runtime\adb\37.0.1\`，运行时无需联网下载。每次启动首次使用备用版时校验固定 SHA256，复用相同文件并修复缺失或损坏文件；已找到外部 ADB 时不会释放备用版，也不会因外部 ADB 执行失败而切换来源。应用不安装驱动、不修改系统 `PATH`，也不关闭共享 ADB 服务。

## 使用

- 绿色表示至少一台设备处于 ADB `device` 状态；只有一台可用设备时，浮窗同时显示电量。
- 红色表示未连接、等待授权、设备离线或检测失败；灰色表示首次检测中。
- 左键拖动浮窗，位置自动保存；右键查看设备详情、重新检测或退出。
- 设备详情和悬停提示依次显示机型名称、序列号、ADB 状态及电量，例如 `Pixel 8 Pro · usb —  device · 电量 83%`。机型名称来自 `adb devices -l` 的 `model` 字段，下划线显示为空格；缺失或为空时显示“未知”。
- USB、无线设备和模拟器均计入。电量读取失败时显示“未知”，不影响连接状态。
- Mac 浮窗在所有桌面及其他应用的全屏空间显示，不显示 Dock 图标；Windows 浮窗在当前虚拟桌面置顶，不显示任务栏按钮，按显示器 DPI 缩放。两端启动和拖动均不会主动获取键盘焦点。

### 拖放 APK 安装

将一个本地 `.apk` 文件拖到浮窗上，预览文字变为“安装apk”；拖出则恢复。松开鼠标后，应用重新枚举设备，并对所有处于 `device` 状态的设备并行执行 `adb install -r`，覆盖安装并保留应用数据；未授权和离线设备不参与。

安装期间显示进度，完成结果显示约 8 秒后恢复连接状态，每台设备的结果保留在悬停提示和设备详情中。一次只接受一个 APK；目录、多文件、非 APK 或安装期间的再次拖放均不会触发新任务。每台设备最多等待 5 分钟，退出时会终止本工具的安装客户端。应用不会自动卸载旧应用或允许降级，安装仍需满足 Android 的包名、签名和版本规则；已经在设备上提交的安装不会因退出应用而回滚。

“已连接”表示 ADB 可用，不代表 Android 已完成启动。应用可以启动 ADB 服务，退出时不会关闭共享的 ADB server。本版本没有开机启动或内置自动更新功能。

## 更新和卸载

先右键浮窗并选择“退出 ADB Status”，再按平台执行。

Windows：

```powershell
scoop update
scoop update adb-status
```

macOS：

```sh
brew update
brew upgrade --cask punxch/myapps/adb-status
```

Windows 使用 `scoop uninstall adb-status`；Mac 使用 `brew uninstall --cask punxch/myapps/adb-status`；手动安装则删除应用。窗口位置设置会保留；Windows 设置和备用 ADB 缓存位于 `%LOCALAPPDATA%\adb-status\`，卸载时也会保留。

## 验证范围

发布前在 macOS 和 Windows 原生环境运行项目自动测试、Clippy、release 构建，检查包内路径、架构和 SHA256；Mac 另检查最低系统版本和签名，Windows 检查单 EXE 包及内嵌 ADB 的固定摘要。自动测试包括模拟 ADB 的 APK 安装、路径处理、失败、超时、取消与 Windows 备用缓存验证。真实设备插拔、授权、APK 拖放及安装、多显示器、桌面切换及全屏显示仍需在实际使用环境验收。
