cask "adb-status" do
  version "0.2.2"
  sha256 "0705ccaebe31b9f776f878107fe90e79a5b8e01a08138f52622fbac07737c910"

  url "https://github.com/punxch/MyApps/releases/download/adb-status-v0.2.2/adb-status-0.2.2-macos-arm64.zip"
  name "ADB Status"
  desc "Floating Android device connection and battery monitor"
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
