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

如果 Homebrew 提示 `untrusted tap`，先信任此 Formula，再重试安装：

```sh
brew trust --formula vinono/tap/one-day-one-thing
brew install 1d1t
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

## 打包与发版维护

### 1. 仅打包生成 Formula

```sh
python3 scripts/package.py
```

执行后将自动完成：
1. 读取当前版本号并生成发布归档包 `dist/1d1t-<version>.tar.gz`；
2. 计算其 SHA256 校验和；
3. 自动匹配 GitHub Release 下载 URL；
4. 更新根目录的 `Formula/one-day-one-thing.rb` 及软链接 `Aliases/1d1t`；
5. 同时同步输出到 `dist/homebrew-tap/`（供独立 Tap 仓库同步使用）。

### 2. 准备版本提交与 Tap 更新

当准备发布新版本时，可执行：

```sh
python3 scripts/release.py 0.1.2
```

支持按版本号升级：
- `python3 scripts/release.py patch` （如 `0.1.1` -> `0.1.2`）
- `python3 scripts/release.py minor` （如 `0.1.1` -> `0.2.0`）

该命令会：
1. **测试前检**：自动运行全部单元测试；
2. **版本更新**：同步更新 `oneDayOneThing/__init__.py`、`README.md` 与发布日志；
3. **打包归档**：构建源码包并计算 SHA256；
4. **主库更新**：更新根目录 Tap，并在 1D1T 仓库生成对应 commit 和 `v<version>` tag；
5. **Tap 联动**：自动更新同级或指定的 `homebrew-tap` 仓库中的 Formula，并生成对应的 bump commit。

添加 `--push` 会推送主仓库的提交和标签，但不会创建 GitHub Release，也不会推送 Tap：
```sh
python3 scripts/release.py patch --push
```

随后上传并核验 `dist/1d1t-<version>.tar.gz` 为 GitHub Release 附件；确认下载 URL 和 SHA256 无误后，再推送 `homebrew-tap` 的提交并执行实际 Homebrew 安装测试。发布后不要替换同版本附件；源码变更应提升版本号。
