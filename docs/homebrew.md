# Homebrew 本地安装与发布

Homebrew Formula 名称为 `one-day-one-thing`，安装后的命令仍为 `1d1t`。
采用完整英文名以符合 Homebrew 的 Ruby 类命名规则。

## 本地安装

在项目根目录执行（需要已安装 Homebrew）：

```sh
python3 scripts/package.py
brew tap-new local/oned1t  # 只需首次执行
cp dist/homebrew-tap/Formula/one-day-one-thing.rb "$(brew --repository)/Library/Taps/local/homebrew-oned1t/Formula/"
brew install local/oned1t/one-day-one-thing
brew test local/oned1t/one-day-one-thing
1d1t welcome
```

打包脚本只收集 Python 源文件、命令入口和用户文档；不包含个人数据库、Git 目录或设计素材。
生成的压缩包和 Formula 位于忽略追踪的 `dist/`，本地 Formula 使用该压缩包的绝对 file URL。
安装后程序位于 Homebrew Cellar，不依赖原项目；重新安装需要保留压缩包。
更新本地包后重新复制 Formula，并执行 `brew reinstall local/oned1t/one-day-one-thing`。

若之前运行过本项目安装器，`~/.local/bin/1d1t` 可能优先于 Homebrew。
用 `type -a 1d1t` 检查；只有确认旧入口是本项目的符号链接后才移除该链接。

卸载命令：`brew uninstall one-day-one-thing`。用户数据不会删除。

## 公开分发（尚未发布）

1. 确定 GitHub 仓库、发布可见性及许可证。
2. 创建版本标签，将 `dist/1d1t-0.1.0.tar.gz` 作为对应 Release 附件上传。
3. 用 `python3 scripts/package.py --url '实际附件的 HTTPS URL'` 生成公开 Formula。
4. 将 Formula 放入公开 `homebrew-tap` 仓库的 `Formula/`，补充项目 homepage。
5. 从公开 URL 安装并运行 `brew test`，再提供用户安装命令。

同一源码的归档使用固定时间戳，SHA256 可复现。发布后不要更换同版本附件；改动应提升版本号。
目前 `brew install 1d1t` 不是可用的公共安装命令。
