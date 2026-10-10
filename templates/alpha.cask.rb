cask "alpha" do
  version "@@VERSION@@"
  sha256 arm: "@@SHA256_ARM64@@", intel: "@@SHA256_X64@@"

  on_arm do
    url "@@URL_ARM64@@"
  end
  on_intel do
    url "@@URL_X64@@"
  end

  name "Alpha"
  desc "Example desktop application; replace before enabling"
  homepage "https://github.com/@@REPOSITORY@@"

  depends_on :macos

  app "Alpha.app"
end
