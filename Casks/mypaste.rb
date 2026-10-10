cask "mypaste" do
  version "0.1.0"
  sha256 "3ee8452fde32f2b4452a3946f04f35a27e224d41128258a1ac51c2867a302e2f"

  url "https://github.com/punxch/MyApps/releases/download/mypaste-v0.1.0/mypaste-0.1.0-macos-arm64.dmg"
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
