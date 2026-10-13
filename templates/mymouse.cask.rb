cask "mymouse" do
  version "@@VERSION@@"
  sha256 "@@SHA256_UNIVERSAL@@"

  url "@@URL_UNIVERSAL@@"
  name "MyMouse"
  desc "Share keyboard, mouse and clipboard between computers"
  homepage "https://github.com/@@REPOSITORY@@/blob/main/docs/apps/mymouse.md"

  depends_on macos: :monterey

  app "MyMouse.app"
  binary "#{appdir}/MyMouse.app/Contents/Resources/mymouse"

  caveats <<~EOS
    This build uses an ad-hoc signature and is not notarized by Apple.
    Grant Accessibility and Input Monitoring permissions when setting up sharing.
    Disable login startup and quit MyMouse from the menu bar before uninstalling.
    Quit before upgrading, then reopen the app. User settings and pairing data are retained.
  EOS
end
