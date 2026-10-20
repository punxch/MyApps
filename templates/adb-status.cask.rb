cask "adb-status" do
  version "@@VERSION@@"
  sha256 "@@SHA256_ARM64@@"

  url "@@URL_ARM64@@"
  name "ADB Status"
  desc "Floating Android device connection and battery monitor"
  homepage "https://github.com/@@REPOSITORY@@/blob/main/docs/apps/adb-status.md"

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
