# Homebrew 安装

## 安装

需要 macOS 和 [Homebrew](https://brew.sh/)。首次安装：

```sh
brew tap vinono/tap
brew install 1d1t
1d1t welcome
```

也可以一步安装：

```sh
brew install vinono/tap/1d1t
```

`1d1t` 是 Tap 中的别名，指向 `one-day-one-thing` Formula；安装后的终端命令为 `1d1t`。
Python 依赖由 Homebrew 管理，无需克隆或保留项目目录。

## 更新与卸载

```sh
brew update
brew upgrade one-day-one-thing
```

```sh
brew uninstall one-day-one-thing
```

卸载不会删除 `~/Library/Application Support/1D1T/` 中的个人记录。

如果此前使用过源码安装器，可用 `type -a 1d1t` 检查当前命令来源。
`~/.local/bin/1d1t` 可能优先于 Homebrew；确认它是旧项目的符号链接后，再移除该链接。

## 维护 Tap

Tap 仓库为 `vinono/homebrew-tap`。公开安装包来自 `vinono/1D1T` 的 GitHub Release，
Formula 固定版本号和 SHA256，`Aliases/1d1t` 指向 `../Formula/one-day-one-thing.rb`。

生成发布包和 Formula：

```sh
python3 scripts/package.py --url https://github.com/vinono/1D1T/releases/download/v0.1.0/1d1t-0.1.0.tar.gz
```

产物在忽略追踪的 `dist/` 中。打包脚本只收集命令入口、Python 源文件和用户文档，
不包含个人数据库、Git 目录或设计素材。同一源码生成相同的 SHA256。
发布后不要替换同版本附件；源码变更应提升版本号并发布新版本。

上传 Release 附件后，将 `dist/homebrew-tap/` 内容同步至 Tap 仓库，并验证：

```sh
brew install vinono/tap/1d1t
brew test vinono/tap/one-day-one-thing
```

发布前的本地安装验证可省略 `--url` 生成本地文件 Formula，再复制至临时本地 Tap。
