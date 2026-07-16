# Database

数据库结构由 `backend/app/models` 中的 SQLAlchemy 2 模型定义，由 Alembic 管理迁移。开发环境使用 PostgreSQL 17；自动化测试使用 SQLite。

- 升级：`cd backend && alembic upgrade head`
- 回滚：`cd backend && alembic downgrade -1`
- Demo 数据：`cd backend && python -m app.db.seed`

种子脚本只写入明确标记为 `is_demo=true`、`demo_only` 的 30 家企业和 60 个岗位。
