# 本地数据格式 v1

默认目录为 `~/Library/Application Support/1D1T/`，新建目录权限为 0700。
`focus.sqlite3` 为 SQLite 数据库，`PRAGMA user_version = 1`。
CLI 拒绝打开未知版本，避免旧版本意外写坏新格式。

`focus_days` 表：

| 字段 | 含义 |
| --- | --- |
| day | 主键，重点所属本地日期，`YYYY-MM-DD` |
| title | 单行重点文字，非空 |
| created_at | UTC ISO 8601 创建时间 |
| done_at | UTC ISO 8601 完成操作时间；NULL 表示待完成 |
| note | 可选完成说明；待完成时为 NULL |
| source_day | 沿用来源日期；普通添加时为 NULL |

贡献统计依照 `day` 和非空 `done_at`，不能把 `done_at` 转成日期来统计，
因为补记操作可能在另一天发生。一天只有一条重点，因此完成记录数等于完成天数。
日期一旦保存不会随系统时区改变。

写操作使用 `BEGIN IMMEDIATE` 事务，锁等待最多 10 秒，避免两个终端同时添加时覆盖。
使用 SQLite 默认 rollback journal；备份时等待所有命令退出后复制数据目录。
未来 App 更改格式时应在事务内迁移并增加 `user_version`。
