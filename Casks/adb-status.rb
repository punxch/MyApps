cask "adb-status" do
  version "0.3.0"
  sha256 "0bbe1c6d1ba8fd4a435ebe4f5f5fafd3f6850bdfe42f62fcf3d6f3452ba7b352"

  url "https://github.com/punxch/MyApps/releases/download/adb-status-v0.3.0/adb-status-0.3.0-macos-arm64.zip"
  name "ADB Status"
  desc "Floating Android device monitor and APK installer"
  homepage "https://github.com/punxch/MyApps/blob/main/docs/apps/adb-status.md"

  depends_on arch: :arm64
  depends_on macos: :big_sur

  app "ADB Status.app"

  caveats <<~EOS
    Requires Android SDK Platform Tools (adb), installed separately.
    This build uses an ad-hoc signature and is not notarized by Apple.
    Right-click the floating window to quit before upgrading or uninstalling.
    Window position settings are retained when uninstalling.
  EOS
end
