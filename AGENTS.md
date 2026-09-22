# 1D1T

## Agent skills

### Issue tracker
开发任务和规格使用本地 Markdown，见 `docs/agents/issue-tracker.md`。

### Triage labels
使用默认状态词，见 `docs/agents/triage-labels.md`。

### Domain docs
使用单一领域词汇表 `CONTEXT.md`；阅读规则见 `docs/agents/domain.md`。

## Development

CLI 是第一版的用户入口。通过命令输入输出测试行为，测试数据放在临时目录。
第一版保持离线、无第三方运行依赖。贡献记录不引入完成率或评分。
持久化格式发生变化时，保留已有数据，并考虑未来 macOS App 的读取需求。
