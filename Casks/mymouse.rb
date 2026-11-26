cask "mymouse" do
  version "0.2.1"
  sha256 "847b92966dd852b316c0610e47ef88f1560222e8a2ca2f147f28331481dde0d8"

  url "https://github.com/punxch/MyApps/releases/download/mymouse-v0.2.1/mymouse-0.2.1-macos-universal.zip"
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
