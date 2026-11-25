cask "mypaste" do
  version "0.2.0"
  sha256 "6b7de261db133b574b3758640cf74ad00a7026a4abca8855aef6f3344979da9b"

  url "https://github.com/punxch/MyApps/releases/download/mypaste-v0.2.0/mypaste-0.2.0-macos-arm64.dmg"
  name "MyPaste"
  desc "Native clipboard history manager with local network sharing"
  homepage "https://github.com/punxch/MyApps/blob/main/docs/apps/mypaste.md"

  depends_on arch: :arm64
  depends_on macos: :sequoia

  app "MyPaste.app"

  caveats <<~EOS
    Requires macOS 15.4 or later on Apple Silicon.
    This build uses an ad-hoc signature and is not notarized by Apple.
    Enable clipboard history in settings. Automatic paste requires Accessibility permission.
    Quit MyPaste before upgrading; disable login startup before uninstalling.
    Clipboard history and settings are retained when uninstalling.
  EOS
end
