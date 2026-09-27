class OneDayOneThing < Formula
  desc "One focus per day, with a terminal contribution calendar"
  homepage "https://github.com/vinono/1D1T"
  url "https://github.com/vinono/1D1T/releases/download/v0.1.1/1d1t-0.1.1.tar.gz"
  version "0.1.1"
  sha256 "015adfa0ab4073eeaac70baaca1b5813dba0e945cc1fe987d0809cebcbba18bc"

  depends_on "python@3.13"

  def install
    libexec.install "oneDayOneThing", "bin"
    (bin/"1d1t").write <<~SH
      #!/bin/sh
      exec "#{Formula["python@3.13"].opt_bin}/python3.13" "#{libexec}/bin/1d1t" "$@"
    SH
  end

  def caveats
    <<~EOS
      Run `1d1t welcome` to see the logo and quick start.
      Your records remain in ~/Library/Application Support/1D1T/.
    EOS
  end

  test do
    ENV["ONE_DAY_ONE_THING_DATA_DIR"] = (testpath/"data").to_s
    assert_match "One day. One thing.", shell_output("#{bin}/1d1t welcome")
    assert_match "Take a day. Feel the love in everything.", shell_output("#{bin}/1d1t welcome")
    assert_match "brew test focus", shell_output("#{bin}/1d1t add 'brew test focus'")
    assert_match "Completed", shell_output("#{bin}/1d1t done")
    assert_match "1 completed", shell_output("#{bin}/1d1t stats --week")
    assert_match "1 completed", shell_output("#{bin}/1d1t calendar")
    assert_match "brew test focus", shell_output("#{bin}/1d1t history")
    assert_match "Pending", shell_output("#{bin}/1d1t undo")
  end
end
