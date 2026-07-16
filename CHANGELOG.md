# Changelog

本项目的主要变更记录在此文件中。版本号遵循
[Semantic Versioning](https://semver.org/)。

## [1.0.1] - 2026-07-16

### Added

- 无需登录的企业库、岗位库、Dashboard 和官方投递链接。
- 登录后的收藏、投递、面试、Offer、通知、简历和岗位提醒工作流。
- 14 家已核验官方招聘来源及每日 05:00（Asia/Shanghai）本地同步调度。
- 30 家 Demo 企业和 60 个 Demo 岗位，全部带有明确 Demo 标识。
- FastAPI、SQLAlchemy 2、Alembic、PostgreSQL、Redis 与 Docker Compose 本地运行环境。
- GitHub Actions CI、CodeQL、Dependabot、Secret Scanning 和分支保护。
- Apache License 2.0、贡献指南、安全策略和完整项目文档。

### Changed

- 前端、后端包元数据和 OpenAPI 版本统一为 `1.0.1`。
- GitHub 发布材料、支持版本声明和公开仓库元数据升级为稳定版状态。

### Fixed

- 保留空的 `frontend/public` 目录，确保干净检出后 Docker 构建成功。
- 初始 Alembic 迁移改为确定性 schema，确保全新数据库可依次升级到 `0004`。
- 将 TypeScript 保持在 Next.js ESLint 工具链兼容的 5.9 系列，修复依赖自动更新导致的 CI 失败。

### Security

- 官方来源同步包含 robots.txt、SSRF、响应超时、大小与批量限制保护。
- 敏感配置只从环境变量读取，仓库不跟踪真实 `.env`、Token 或用户数据。
- GitHub 启用 Secret Scanning、Push Protection 和 CodeQL。

[1.0.1]: https://github.com/h46373824-tech/offerPilot-AI/releases/tag/v1.0.1
