# Welcome 实际输出图

文件：`terminal-welcome.png`。README 与落地页统一使用此图。
图中文字来自 `python3 -m oneDayOneThing welcome` 在 TTY 中的实际 ANSI 输出；外框由
`scripts/render_welcome.m` 绘制。图片不包含安装成功等非 Welcome 内容。

在仓库根目录重新生成：

```sh
script -q /private/tmp/1d1t-welcome.capture env -u NO_COLOR TERM=xterm-256color COLUMNS=80 python3 -m oneDayOneThing welcome
clang -fobjc-arc -framework AppKit scripts/render_welcome.m -o /private/tmp/render-1d1t-welcome
/private/tmp/render-1d1t-welcome /private/tmp/1d1t-welcome.capture assets/terminal-welcome.png
clang -fobjc-arc -framework AppKit scripts/render_brand.m -o /private/tmp/render-1d1t-brand
/private/tmp/render-1d1t-brand /private/tmp/1d1t-welcome.capture oneDayOneThing/assets/logo.png assets/1d1t-icon.png
```

实心格字形定义在 `oneDayOneThing/terminal.py`。两张品牌图从同一份 Welcome
输出读取字形，因此修改字形后可按上面命令一起更新。32px favicon 使用 `> ■`
提示符简写，以保证小尺寸可辨认。

品牌标语：
**One day. One thing.**
**Take a day. Feel the love in everything.**

采用统一的银盐冷灰配色（Silver Gelatin：黑白灰阶与银白 Logo）。

## 配色规范

- 背景：深冷黑 / 暗室沉静底色（#0C0C0C）
- Logo 与重点字符：明亮银白（ANSI 97，图中 #F8F8F8）
- 正文与命令：中性灰阶（ANSI 37 / 90，图中约 #CFCFCF / #8F8F8F）
- 标语：两行对齐排版
  - One day. One thing.
  - Take a day. Feel the love in everything.
