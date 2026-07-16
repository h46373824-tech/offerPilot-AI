# GitHub 发布清单

## 代码与数据

- [x] `dev` 分支 CI 全绿并通过人工复核
- [x] `.env`、Token、简历、数据库、日志和测试账号未进入 Git 历史
- [x] 正式招聘数据均有来源 URL、核验日期和状态说明
- [x] 过期、结束或官方显示零岗位的项目未作为开放岗位发布
- [x] 数据删除、更正和来源停用流程可用
- [x] 从全新 Docker 数据卷完成迁移、种子和端到端测试

## GitHub 仓库设置

- [x] 添加 Apache License 2.0 `LICENSE` 并在 README 声明
- [x] GitHub 仓库已公开，`dev` 已设为默认分支并启用分支保护
- [x] 已要求 Pull Request、至少一次审核、会话解决和五项 CI/CodeQL 状态检查
- [x] 启用 Dependabot alerts、Dependabot 安全更新、secret scanning 与 push protection
- [x] 仓库内置 CodeQL advanced setup（JavaScript/TypeScript、Python）和依赖审查工作流
- [x] 仓库公开后确认 CodeQL 工作流具有 `security-events: write` 并成功上传结果
- [x] 启用 dependency graph 和 private vulnerability reporting
- [x] 设置仓库描述、Topics、社交预览图和维护者联系方式

## 首次发布

- [x] 使用语义化版本 `v1.0.1`
- [x] Release notes 明确本地部署定位、Demo 数据和正式数据覆盖范围
- [x] 不使用“全网”“实时”“全部企业”等无法持续证明的宣传语
- [x] 验证 README 中的克隆、启动、迁移、测试和停止命令
- [x] 公布已知限制：官方页面结构变化、单实例调度、人工核验时效

发布材料：

- [v1.0.1 发布说明](releases/v1.0.1.md)
- [社交预览图](assets/social-preview-v1.0.1.jpg)
- [维护者信息](../MAINTAINERS.md)
