class Beta < Formula
  desc "Example command-line application; replace before enabling"
  homepage "https://github.com/@@REPOSITORY@@"
  version "@@VERSION@@"

  on_macos do
    if Hardware::CPU.arm?
      url "@@URL_ARM64@@"
      sha256 "@@SHA256_ARM64@@"
    else
      url "@@URL_X64@@"
      sha256 "@@SHA256_X64@@"
    end
  end

  depends_on :macos

  def install
    bin.install "beta"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/beta --version")
  end
end
