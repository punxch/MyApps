# Dota2 IME

Windows x64 的 Dota 2 输入法兼容与管理工具。此仓库仅分发编译后的程序和 Scoop 清单，不公开应用源码。

## 安装和升级

```powershell
scoop bucket add myapps https://github.com/punxch/MyApps
scoop install myapps/dota2ime
```

安装后，从开始菜单打开 **Dota2 IME**，或运行 `dota2ime`。升级时先关闭程序，再执行：

```powershell
scoop update
scoop update dota2ime
```

不使用 Scoop 时，可在 [Releases](https://github.com/punxch/MyApps/releases) 下载 `dota2ime-版本-windows-x64.zip`，解压后运行 `dota2ime.exe`。ZIP 同时包含使用说明、校验和和第三方组件声明。

## 0.4.0

- 为已安装的简体中文 TSF 输入法提供 Dota 2 兼容名称设置，并支持恢复原名。
- 查看输入法启用状态，启用或停用已安装配置、设置默认、调整顺序。
- 可在程序运行期间开启 Ctrl+Alt+Space 快捷切换，默认关闭。
- 缺少 Microsoft WebView2 时，在确认后调用内嵌的微软引导器联网补装。

改兼容名称前先退出 Dota 2，修改时由程序请求 Windows UAC 确认。兼容名称会持久保存；普通浏览和刷新列表不会修改输入法设置。

程序为便携 EXE，当前版本没有应用代码签名。小狼毫有此前的游戏实测记录；其他输入法以及全部游戏场景尚未全部验收。当前仅提供 Windows x64 版本。

## 卸载和数据

```powershell
scoop uninstall dota2ime
```

卸载会移除程序，不会自动还原输入法兼容名称、语言设置或删除共享 WebView2。需要恢复时，应先在应用中使用“恢复原名”，并调整输入法管理设置。备份保留在 Windows 注册表，不会随 Scoop 卸载清除。

## 分发文件

发布附件包含 Windows x64 ZIP、独立 EXE、SHA256SUMS.txt，以及微软组件的声明和来源记录。独立 EXE 与 ZIP 内的程序完全相同；使用 ZIP 可一并获得完整分发说明。

应用以闭源二进制方式分发。MyApps 仓库模板的 Unlicense 不对应用二进制重新授权；内嵌 Microsoft WebView2 引导器及共享 Runtime 适用微软的独立条款，详见发布附件 `THIRD_PARTY_NOTICES.md`。
