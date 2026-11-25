cask "mymouse" do
  version "0.2.0"
  sha256 "c2167b1b09069b3deb49413bf0ea9d64e6ce833010c27b26e679738ec500d9b7"

  url "https://github.com/punxch/MyApps/releases/download/mymouse-v0.2.0/mymouse-0.2.0-macos-universal.zip"
  name "MyMouse"
  desc "Share keyboard, mouse and clipboard between computers"
  homepage "https://github.com/punxch/MyApps/blob/main/docs/apps/mymouse.md"

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
