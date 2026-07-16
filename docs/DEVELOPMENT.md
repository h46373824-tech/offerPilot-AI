# OfferPilot AI 开发指南

## 1. 开发基线

- 主开发分支：`dev`
- 前端：Node.js 22、npm、Next.js App Router、TypeScript strict
- 后端：Python 3.11+，推荐 3.12
- 数据：PostgreSQL 17、Redis 7
- 容器：Docker Compose v2

仓库只保留根目录一个 Git 仓库。`frontend/.git`、`backend/.git` 或其他嵌套仓库都不允许存在。不要删除或重建根目录 `.git`，也不要覆盖已有历史。

开始修改前：

```powershell
cd C:\Users\Lenovo\offerPilot-AI
git branch --show-current
git status --short
```

分支应为 `dev`。工作区有他人改动时必须保留并避开，不要使用 `git reset --hard` 或未确认的清理命令。

## 2. 快速启动

### 2.1 完整 Docker 环境

本项目按本地部署维护。Windows 首次启动推荐：

```powershell
.\scripts\setup-local.ps1 -AdminEmail "admin@offerpilot.example.com"
```

脚本只在仓库根目录创建被忽略的 `.env`，并将业务数据保存在本项目 Docker 卷中。

```powershell
Copy-Item .env.example .env
docker compose up --build
```

启动后：

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8000`
- Swagger：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`

backend 容器会自动运行迁移、幂等 Demo 种子和固定核验日期的正式基线种子。查看状态：

```bash
docker compose ps
docker compose logs -f backend frontend
```

将已注册账号提升为本地管理员：

```powershell
.\scripts\promote-admin.ps1 -Email "your-email@example.com"
```

### 2.2 数据服务使用 Docker，应用本地运行

```bash
docker compose up -d postgres redis
```

后端本地运行：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
$env:DATABASE_URL = "postgresql+psycopg://offerpilot:change_me@localhost:5432/offerpilot"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:SECRET_KEY = "replace-with-a-long-local-random-secret"
$env:CORS_ORIGINS = "http://localhost:3000"
alembic upgrade head
python -m app.db.seed
python -m app.db.seed_official
uvicorn app.main:app --reload --port 8000
```

也可以在 `backend/.env` 中配置这些变量，但该文件不得提交。

前端本地运行：

```powershell
cd frontend
Set-Content -Encoding utf8 -Path .env.local -Value "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
npm ci
npm run dev
```

## 3. 环境变量与密钥

以根目录 `.env.example` 为唯一可提交模板。规则：

1. `.env` 与 `.env.local` 不提交；
2. `SECRET_KEY` 使用足够长的随机值；
3. `NEXT_PUBLIC_*` 会暴露给浏览器，绝不能存放密钥；
4. 生产环境从平台 Secret Manager 注入配置；
5. 日志和错误消息不得打印连接串、密码、Token；
6. 添加新变量时同时更新 `.env.example`、README 和相关配置模型。

生成本地随机密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 4. 前端开发

### 4.1 路由

业务页面位于 `frontend/src/app/(app)/`，共享应用壳由该路由组的 `layout.tsx` 提供。认证页面位于 `app/login` 与 `app/register`。

新增页面时：

1. 在 App Router 下创建语义清晰的目录和 `page.tsx`；
2. 需要全局导航时更新 Shell；
3. 服务端组件优先，仅在需要状态、事件或浏览器 API 时使用 `"use client"`；
4. 为加载、空数据和失败分别提供反馈；
5. 在 375px、768px 和桌面宽度检查布局；
6. 确保浅色与深色主题均可读。

### 4.2 远程数据

- 所有 API 地址从 `NEXT_PUBLIC_API_URL` 获得；
- 复用 `src/lib/api.ts`，不要在页面散落完整 URL；
- 用 TanStack Query 管理远程数据，不把远程实体复制到 Zustand；
- Query Key 必须包含分页、搜索、筛选和排序参数；
- Mutation 成功后精确失效或更新相关缓存；
- 区分网络错误、后端错误、空数组和初次加载；
- 用户切换或退出时清除带用户范围的缓存。

### 4.3 UI 状态

Zustand 只保存跨组件 UI 状态，例如深色模式和移动导航。可从 URL 推导的搜索、筛选与分页应优先放在 URL Search Params 中，便于刷新、分享和返回。

### 4.4 可访问性

- 输入框必须有关联 label；
- 仅图标按钮必须有 `aria-label`；
- 键盘可以打开和关闭移动导航；
- 焦点状态清晰；
- 不只用颜色表达状态；
- 图表旁提供文本摘要或可访问表格；
- 动画尊重 `prefers-reduced-motion`。

### 4.5 前端检查

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm run format:check
npm run build
```

修复格式：

```bash
npm run format
```

不要手工修改 `package-lock.json`；依赖变化通过 npm 命令产生 lockfile，并与 `package.json` 一起提交。

## 5. 后端开发

### 5.1 新增资源或接口

推荐顺序：

1. 在 `models/` 定义或修改 SQLAlchemy 模型；
2. 在 `schemas/` 定义请求、更新和响应 Schema；
3. 生成并检查 Alembic 迁移；
4. 在 `api/v1/routes/` 新增路由；
5. 在 v1 router 中注册路由；
6. 加入认证、资源归属和异常处理；
7. 编写成功、未认证、越权、不存在和校验失败测试；
8. 更新 OpenAPI 说明与 `docs/API.md`。

### 5.2 类型与代码风格

- 公共函数、依赖、路由和返回值都写类型；
- 使用 SQLAlchemy 2 `Mapped[...]` 与 `mapped_column`；
- 使用 Pydantic v2 API；
- 不用裸 `except` 吞掉异常；
- 不在路由中拼接原始 SQL；
- 排序字段使用 `Literal` 或显式映射白名单；
- 一个请求的相关写入放在同一事务；
- 404/409/422 等错误使用稳定、可理解的信息。

### 5.3 用户数据隔离

任何个人资源都必须：

1. 依赖 `CurrentUser`；
2. 查询包含 `resource.user_id == current_user.id`；
3. 创建关联资源时验证父资源也属于当前用户；
4. 不允许客户端覆盖 `user_id`；
5. 越权访问按不存在处理，避免枚举其他用户资源。

特别注意面试和 Offer 的 `application_id`：必须验证所引用投递属于当前用户。

### 5.4 事务与 Session

- 每个请求通过依赖获得独立 Session；
- 成功写入后 `commit`，需要响应数据库默认值时 `refresh`；
- 写入过程中发生异常应 rollback；
- 不在请求结束后继续使用 ORM 实例；
- 批量导入使用分批事务，避免一次事务占用过多内存和锁。

### 5.5 后端检查

```bash
cd backend
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy app
pytest
```

自动格式化：

```bash
ruff format .
ruff check . --fix
```

检查自动修复结果，不要让工具改变无关文件。

## 6. 数据库变更流程

修改模型后：

```bash
cd backend
alembic revision --autogenerate -m "clear migration description"
alembic upgrade head
alembic current
```

迁移必须人工审查。特别检查非空列、默认值、索引、唯一约束、外键删除行为和 downgrade。迁移应尽量小且单一目的。

不要通过删除现有迁移或重建 Git 历史解决冲突。已经共享的迁移发生分叉时使用 Alembic merge，并由团队确认顺序。

种子：

```bash
python -m app.db.seed
python -m app.db.seed_official
```

Demo 种子必须保留明确标识。正式基线只能来自可溯源的官方页面，保留核验日期和官方链接，不得宣传为全网实时覆盖。

## 7. 测试策略

### 7.1 后端测试

现有测试覆盖：

- 健康检查；
- 注册、登录和当前用户；
- 企业和岗位公开读取、受保护写入；
- 企业创建、搜索和基础分页响应。

新增功能至少测试：

- 正常路径；
- 无 Token、无效 Token；
- 资源不存在；
- 跨用户访问；
- 重复数据或状态冲突；
- 参数边界和 422；
- 删除后的关联行为。

测试默认使用隔离 SQLite 数据库，快速但不能覆盖全部 PostgreSQL 语义。涉及大小写搜索、JSON、并发、约束或迁移的功能应补 PostgreSQL 集成测试。

运行第二阶段 PostgreSQL 集成测试：

```bash
TEST_POSTGRES_URL=postgresql+psycopg://user:password@localhost:5432/test_db \
  pytest tests/integration -m integration
```

### 7.2 前端测试

第二阶段已加入 Playwright 关键路径；继续优先补充：

- API 客户端与错误映射单元测试；
- 登录/注册表单交互测试；
- 搜索、筛选、分页和空状态组件测试；
- Playwright 关键路径：注册 → Dashboard → 岗位订阅，以及访客移动端正式数据浏览与官方投递跳转；
- 深色模式、移动导航与可访问性检查。

运行 E2E（先启动 `docker compose up --build -d --wait`）：

```bash
cd frontend
npx playwright install chromium
npm run test:e2e -- --project=chromium
```

### 7.3 手工冒烟

每次交付至少确认：

1. `docker compose up --build` 成功；
2. 四个服务状态正常；
3. `/health` 与 `/docs` 可访问；
4. 注册与登录成功；
5. 未登录可查询企业和岗位，个人与管理操作返回 401/403；
6. 默认列表仅展示 30 天内核验的正式数据与官方投递入口；
7. 手机宽度可打开和关闭导航；
8. 深色模式在刷新后保留；
9. 页面区分 Demo、核验日期和过期数据。
10. 管理员可登记官方测试 Feed、查看同步结果，自动发现岗位保持待核验并显示官方投递入口。

## 8. Git 工作流

建议流程：

```bash
git status --short
git diff --check
git diff
git add <明确文件>
git commit -m "type: concise description"
```

常用类型：`feat`、`fix`、`docs`、`test`、`refactor`、`chore`。

提交前：

- 确认位于 `dev`；
- 确认没有 `.env`、数据库、日志、备份、Token 或简历文件；
- 确认没有 `frontend/.git`；
- 运行前后端质量检查；
- 检查 `git diff --check`；
- 不提交无关格式化或他人的临时文件；
- 默认不自行 push，由仓库维护者确认远端操作。

## 9. CI

`.github/workflows/ci.yml` 对 `dev`、`main` push 和 Pull Request 运行。CI 使用 Node.js 22、Python 3.12；前端执行 lint、类型检查和生产构建，后端执行 Ruff、mypy、SQLite API 测试与 PostgreSQL 17 集成测试，随后完整构建 Compose 并执行 Playwright Chromium E2E。Prettier 仍作为提交前本地检查。

CI 失败时先在对应子目录复现单个命令。不要通过移除规则、全局 ignore 或降低 TypeScript/mypy 严格度来绕过问题。

## 10. 调试与常见问题

### 10.1 数据库连接失败

- 容器内主机名：`postgres`；
- 宿主机主机名：`localhost`；
- 检查端口 5432 是否被其他 PostgreSQL 占用；
- 检查 `.env` 用户名、密码和数据库名是否与 Compose 一致；
- 运行 `docker compose logs postgres`。

### 10.2 Redis 连接失败

核心 MVP 请求目前不应依赖 Redis 缓存才能工作，但容器启动会等待其健康。运行：

```bash
docker compose exec redis redis-cli ping
```

预期返回 `PONG`。

### 10.3 前端构建时 API 地址不正确

`NEXT_PUBLIC_API_URL` 是构建期变量。修改后需重新运行 `npm run build` 或 `docker compose build frontend`。

### 10.4 Alembic 找不到应用模块

应在 `backend` 目录运行命令，并确认虚拟环境已安装项目：

```bash
pip install -e ".[dev]"
alembic current
```

### 10.5 Windows PowerShell 无法激活虚拟环境

若执行策略阻止脚本，可在当前进程临时调整，或直接使用 `.venv\Scripts\python.exe -m ...`。遵循所在组织的终端安全策略，不要全局降低安全限制。

### 10.6 需要清空本地数据

`docker compose down -v` 会永久删除本项目数据卷。只在确认无需保留数据后使用；团队共享和生产环境禁止这样操作。

## 11. 完成定义

一个变更只有同时满足以下条件才算完成：

- 行为符合 PRD 和数据合规策略；
- 代码、迁移、测试和文档同步；
- 前后端质量检查通过；
- 新增页面包含响应式与三类数据状态；
- 新增接口包含认证、资源归属和异常路径；
- 没有密钥、个人数据或伪实时招聘内容；
- Docker 启动路径仍可用；
- Git diff 仅包含本任务需要的修改。
