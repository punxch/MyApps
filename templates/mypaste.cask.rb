cask "mypaste" do
  version "@@VERSION@@"
  sha256 "@@SHA256_ARM64@@"

  url "@@URL_ARM64@@"
  name "MyPaste"
  desc "Native clipboard history manager with local network sharing"
  homepage "https://github.com/@@REPOSITORY@@/blob/main/docs/apps/mypaste.md"

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
