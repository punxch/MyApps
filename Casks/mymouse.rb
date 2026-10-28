cask "mymouse" do
  version "0.1.2"
  sha256 "cdeacb5c400d96d0d88137c76628c20a46a8585ea6f1edb5f95ff3ff2db03470"

  url "https://github.com/punxch/MyApps/releases/download/mymouse-v0.1.2/mymouse-0.1.2-macos-universal.zip"
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
