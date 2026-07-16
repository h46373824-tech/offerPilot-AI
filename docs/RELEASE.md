# GitHub 发布清单

## 代码与数据

- [ ] `dev` 分支 CI 全绿并通过人工复核
- [ ] `.env`、Token、简历、数据库、日志和测试账号未进入 Git 历史
- [ ] 正式招聘数据均有来源 URL、核验日期和状态说明
- [ ] 过期、结束或官方显示零岗位的项目未作为开放岗位发布
- [ ] 数据删除、更正和来源停用流程可用
- [ ] 从全新 Docker 数据卷完成迁移、种子和端到端测试

## GitHub 仓库设置

- [ ] 选择并添加明确的 `LICENSE`；选择前不得宣传为开源项目
- [ ] 将 `dev` 或 `main` 设置为默认分支并启用分支保护
- [ ] 要求 Pull Request、CI 状态检查和至少一次审核
- [ ] 启用 Dependabot alerts、secret scanning 与 push protection
- [ ] 仓库公开后启用 CodeQL default setup（JavaScript/TypeScript、Python）
- [ ] 启用 private vulnerability reporting
- [ ] 设置仓库描述、Topics、社交预览图和维护者联系方式

## 首次发布

- [ ] 使用语义化版本，例如 `v0.5.0`
- [ ] Release notes 明确本地部署定位、Demo 数据和正式数据覆盖范围
- [ ] 不使用“全网”“实时”“全部企业”等无法持续证明的宣传语
- [ ] 验证 README 中的克隆、启动、迁移、测试和停止命令
- [ ] 公布已知限制：官方页面结构变化、单实例调度、人工核验时效
