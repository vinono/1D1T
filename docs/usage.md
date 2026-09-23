# 使用指南

[← 返回项目首页](../README.md)

## 安装

macOS 用户通过 Homebrew 安装，Python 依赖会自动安装：

```sh
brew tap vinono/tap
brew install 1d1t
1d1t --help
```

首次安装若提示 `untrusted tap`，运行 `brew trust --formula vinono/tap/one-day-one-thing` 后重试。
更新与卸载见 [Homebrew 指南](homebrew.md)。

### 从源码运行

需要 Python 3.9 或更新版本，无第三方 Python 运行依赖：

```sh
git clone https://github.com/vinono/1D1T.git
cd 1D1T
./bin/1d1t
```

可选运行 `python3 scripts/install.py`，在 `~/.local/bin/1d1t` 创建指向项目的链接。
安装器不覆盖已有命令，也不修改 shell 配置。请保留项目目录，并将 `~/.local/bin` 加入 PATH。
如果已通过 Homebrew 安装，无需再创建此链接。

## 日常使用

```sh
1d1t add "完成博客首页"
1d1t today                         # 直接运行 1d1t 也可以
1d1t edit "完成首页移动端布局"
1d1t done "布局和手机适配完成"      # 说明可省略
1d1t calendar
1d1t stats --week
1d1t stats --month
1d1t history
```

每天只能有一个重点，重复 `add` 不会覆盖。已完成的重点不能追加或直接修改。
误点完成可以使用 `1d1t undo`：恢复待完成状态，并清除本次完成说明。
重复 `done` 保留第一次的完成记录。

昨天没完成时，不会自动顺延：

```sh
1d1t carry                        # 主动沿用昨天的未完成重点；昨天记录不变
```

昨天做完但忘记记录时：

```sh
1d1t done --date 昨天
1d1t done "补记说明" --date 2026-09-21
```

只能补记过去已有的重点，不能创建过去的事项或提前完成未来事项。
补记计入重点原本的日期。`edit` 和 `undo` 仅作用于今天。
日期使用运行命令时系统的本地日期，周一为一周开始。

```sh
1d1t calendar --year 2026          # 全年，窄终端自动分段
1d1t history --limit 100           # 默认最近 30 条，按日期倒序
```

贡献日历默认显示最近 12 周（含本周截至今天）。亮绿色 `■` 表示有完成记录，
灰色 `▪` 表示无完成记录，青色 `□` 标出尚无完成记录的今天，未来日期留空；一天最多一个格子。
终端使用统一的 `> ▪ 1D1T` 标识、细分隔线和命令提示，无需特殊字体。
重定向输出时自动去掉颜色，设置 `NO_COLOR=1` 也可关闭颜色。

## 数据

默认文件：`~/Library/Application Support/1D1T/focus.sqlite3`。
从任意工作目录运行都使用同一份数据，项目更新或移除命令链接不会删除记录。
所有命令退出后，可以复制整个 `1D1T` 数据目录进行备份。

临时试用或独立数据集：

```sh
1d1t --data-dir /tmp/1d1t-demo add "试用一下"
1d1t --data-dir /tmp/1d1t-demo today
```

也支持 `ONED1T_DATA_DIR` 环境变量，命令行 `--data-dir` 优先。
后续 macOS App 可读取同一份 SQLite 数据；当前版本不包含 App 或同步功能。
数据格式见 [docs/storage.md](storage.md)。

## 开发验证

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q oneDayOneThing scripts
```

测试通过 CLI 的参数和输出验证行为，使用临时数据库；跨日测试在程序入口注入日期。

## 欢迎界面与 Homebrew

`1d1t welcome` 显示绿色文字 Logo、`ONE DAY. ONE THING.` 和
`Take a day. Feel the love in everything.`，以及常用命令。
本地安装器完成安装时也显示欢迎界面；没有任何历史记录时，直接运行 `1d1t` 显示欢迎界面与今日状态。
显式 `today` 及日常数据命令保持简洁，窄终端使用紧凑 Logo，`NO_COLOR` 仍然有效。

Homebrew Tap 使用 `1d1t` 别名指向 `one-day-one-thing` Formula，安装后的命令为 `1d1t`。
具体安装、更新、卸载和公开发布步骤见 [Homebrew 文档](homebrew.md)。
