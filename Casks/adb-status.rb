cask "adb-status" do
  version "0.2.3"
  sha256 "6d7180a02d680fe53e62d04aa6d82dc11190caa829a986a518f108b369c01c79"

  url "https://github.com/punxch/MyApps/releases/download/adb-status-v0.2.3/adb-status-0.2.3-macos-arm64.zip"
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
