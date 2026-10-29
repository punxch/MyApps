# ADB Status

ADB Status 是原生 macOS ADB 状态浮窗，显示 Android 设备连接状态、可用设备数量及电量。支持 macOS 11 及以上的 Apple Silicon Mac。

本仓库分发编译后的应用与 Homebrew Cask，源码保留在独立仓库。当前发布版本为 0.2.3；附件为 `adb-status-0.2.3-macos-arm64.zip`，不包含 adb 或 Intel Mac 程序。

## 安装

```sh
brew tap punxch/myapps https://github.com/punxch/MyApps
brew install --cask punxch/myapps/adb-status
```

从“应用程序”打开 **ADB Status**。手动安装时，从 [ADB Status 0.2.3](https://github.com/punxch/MyApps/releases/tag/adb-status-v0.2.3) 下载 ZIP，解压后将 **ADB Status.app** 拖入“应用程序”。Homebrew 自身有独立的系统要求；无法使用 Homebrew 时可手动安装。

应用使用临时本地签名，尚未经过 Apple Developer ID 签名或公证。如果 macOS 阻止打开，请确认下载来源后参考 [Apple 的应用打开说明](https://support.apple.com/en-us/102445)。

## ADB 配置

需自行安装 Android SDK Platform Tools，并在设备上启用 USB 调试、确认授权。应用按以下顺序查找可执行的 `adb`：

1. `ANDROID_HOME/platform-tools/adb`
2. `ANDROID_SDK_ROOT/platform-tools/adb`
3. `~/Library/Android/sdk/platform-tools/adb`
4. `/opt/homebrew/bin/adb`、`/usr/local/bin/adb`
5. `PATH` 中的 adb

Finder 启动一般不继承终端环境变量，建议使用标准 SDK 或 Homebrew 路径。

## 使用

- 绿色表示至少一台设备处于 ADB `device` 状态；只有一台可用设备时，浮窗同时显示电量。
- 红色表示未连接、等待授权、设备离线或检测失败；灰色表示首次检测中。
- 左键拖动浮窗，位置自动保存；右键查看设备详情、重新检测或退出。
- 设备详情和悬停提示依次显示机型名称、序列号、ADB 状态及电量，例如 `Pixel 8 Pro · usb —  device · 电量 83%`。机型名称来自 `adb devices -l` 的 `model` 字段，下划线显示为空格；缺失或为空时显示“未知”。
- USB、无线设备和模拟器均计入。电量读取失败时显示“未知”，不影响连接状态。
- 浮窗在所有桌面及其他应用的全屏空间显示，不显示 Dock 图标，也不会主动获取键盘焦点。

“已连接”表示 ADB 可用，不代表 Android 已完成启动。应用可以启动 ADB 服务，退出时不会关闭共享的 ADB server。本版本没有开机启动或内置自动更新功能。

## 更新和卸载

先右键浮窗并选择“退出 ADB Status”，再执行：

```sh
brew update
brew upgrade --cask punxch/myapps/adb-status
```

卸载使用 `brew uninstall --cask punxch/myapps/adb-status`，手动安装则删除应用。窗口位置设置会保留。

## 验证范围

发布前运行项目自动测试、Clippy、release 构建，并检查包内路径、arm64 架构、最低系统版本、签名和 SHA256。真实设备插拔、授权、多显示器、桌面切换及全屏显示仍需在实际使用环境验收。
