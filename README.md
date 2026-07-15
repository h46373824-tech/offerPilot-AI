# OfferPilot AI

面向 2027 届校招的求职信息与流程管理平台。OfferPilot AI 将企业与岗位检索、收藏、投递、面试、Offer、校招日历和数据复盘集中到一个工作台中，帮助求职者建立清晰、可追踪的校招流程。

> **数据声明**：仓库内置的 30 家企业和 60 个岗位全部是功能演示数据，均带有 `Demo` / `is_demo` / `demo_unverified` 标记，不代表真实企业、实时招聘状态或有效投递机会。任何求职决策均应以企业官方渠道的最新信息为准。

## 当前阶段

本仓库已完成第四阶段本地官方来源同步：管理员可以为企业登记明确允许自动访问的官方招聘页或 RSS/Atom/JSON Feed，按来源定时同步最新岗位，查看运行记录并人工核验。项目仅按本地部署设计，不依赖云服务；不会登录招聘网站、绕过验证码或把自动发现内容直接声明为实时开放。

## 功能清单

### 前端

- 登录、注册与 JWT 登录态接入
- Dashboard：企业与学历统计、今日新增、投递/面试/Offer 数量、即将截止岗位、投递趋势、行业分布、最近投递
- 企业库与岗位库：关键词搜索、筛选入口和空状态
- 投递管理、校招日历、收藏、Offer 管理、数据分析、设置页面均使用当前用户 API 数据
- 简历中心：PDF/DOC/DOCX 上传、版本、默认简历、下载、删除及投递关联
- 岗位订阅：关键词/城市/类别条件、运行频率、启停、手动匹配
- 通知中心：截止、面试与 Offer 提醒、未读数、立即检查和全部已读
- 本地数据治理：授权来源、企业/岗位 CSV 导入、待核验队列、来源覆盖与质量指标
- 企业官方招聘源定时同步、手动立即同步、运行历史和岗位官方投递直达链接
- 桌面端侧边导航、顶部导航及移动端抽屉导航
- 深色模式，偏好保存在浏览器本地
- 通用加载、空数据和错误状态组件
- 响应式中文界面

### 后端

- FastAPI 健康检查和自动生成的 OpenAPI 文档
- 用户注册、登录、JWT Bearer 认证和当前用户接口
- 企业与岗位 CRUD，支持分页、搜索、筛选和排序
- 收藏分页、投递/面试/Offer 完整 CRUD、受控状态流转、通知分页与批量已读接口
- 用户资料与偏好更新、简历文件 API、岗位订阅 CRUD/预览/运行、提醒生成和个人审计日志
- 管理员专属数据源、导入批次、审核和数据质量 API；普通用户不能修改全局企业/岗位目录
- 本地后台调度器支持 HTML 招聘链接、RSS、Atom 与 JSON Feed，包含 robots.txt、SSRF、超时、大小和批量上限保护
- Dashboard 聚合统计接口
- SQLAlchemy 2 数据模型与 Alembic 初始迁移
- 关键认证和企业接口的基础测试

### 数据与工程

- 11 个核心数据表：用户、企业、岗位、投递、收藏、面试、Offer、通知、简历、岗位订阅和审计日志
- 30 家企业、60 个岗位的明确标记演示种子数据，覆盖互联网、人工智能、通信、半导体、新能源、制造业、银行、央企国企、医药和物流
- Docker Compose 编排 frontend、backend、PostgreSQL 和 Redis
- PostgreSQL、Redis 与后端健康检查
- TypeScript 严格模式、ESLint、Prettier、Ruff、mypy 和 pytest
- GitHub Actions 对前后端执行 lint、类型检查、测试和构建

## 技术栈

| 层级 | 技术 |
| --- | --- |
| Web | Next.js App Router、React、TypeScript、Tailwind CSS |
| 前端状态与数据 | Zustand、TanStack Query |
| 图表 | Recharts |
| API | Python、FastAPI、Pydantic |
| 数据访问 | SQLAlchemy 2、Alembic、psycopg |
| 认证 | JWT（HS256）、Argon2 密码哈希 |
| 数据服务 | PostgreSQL、Redis |
| 工程 | Docker Compose、ESLint、Prettier、Ruff、mypy、pytest、GitHub Actions |

## 目录结构

```text
offerPilot-AI/
├── .github/workflows/       # CI 工作流
├── backend/
│   ├── alembic/             # 数据库迁移
│   ├── app/
│   │   ├── api/             # API 路由与依赖
│   │   ├── core/            # 配置与安全
│   │   ├── db/              # 会话与种子数据
│   │   ├── models/          # SQLAlchemy 模型
│   │   └── schemas/         # Pydantic Schema
│   ├── data/uploads/        # 本地开发附件目录（不提交）
│   └── tests/               # 单元/API 与 PostgreSQL 集成测试
├── database/                # 数据库相关扩展目录
├── docker/                  # Docker 扩展配置目录
├── docs/                    # 产品、架构、数据库、API 与开发文档
├── frontend/
│   ├── e2e/                 # Playwright 关键路径测试
│   ├── public/
│   └── src/
│       ├── app/             # Next.js App Router 页面
│       ├── components/      # UI 与业务组件
│       ├── data/            # 前端演示数据
│       ├── lib/             # API 客户端
│       └── stores/          # Zustand Store
├── scripts/                 # 项目辅助脚本目录
├── .env.example
├── docker-compose.yml
└── README.md
```

## 环境要求

推荐使用 Docker 启动完整环境：

- Docker Desktop 或 Docker Engine 24+
- Docker Compose v2
- 至少 4 GB 可用内存

本地开发还需要：

- Node.js 22（最低需满足当前 Next.js 版本要求）与 npm
- Python 3.11+（CI 和容器使用 Python 3.12）
- PostgreSQL 17 或兼容版本
- Redis 7
- Git

## 使用 Docker 启动

Windows 本地首次部署推荐使用初始化脚本，它会生成随机数据库密码和 JWT 密钥，并启动全部服务：

```powershell
cd C:\Users\Lenovo\offerPilot-AI
.\scripts\setup-local.ps1 -AdminEmail "admin@offerpilot.example.com"
```

随后使用相同邮箱注册，即可看到“数据治理”入口。若账号已经存在，可执行：

```powershell
.\scripts\promote-admin.ps1 -Email "your-email@example.com"
```

以下为手动启动方式：

1. 进入仓库并创建本地环境变量文件：

   ```powershell
   cd C:\Users\Lenovo\offerPilot-AI
   Copy-Item .env.example .env
   ```

   macOS / Linux 可使用 `cp .env.example .env`。

2. 修改 `.env`，至少替换 `POSTGRES_PASSWORD` 与 `SECRET_KEY`。生成随机密钥的一种方式：

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

3. 构建并启动：

   ```bash
   docker compose up --build
   ```

   backend 容器会在启动时执行 `alembic upgrade head`，并在空数据库中写入演示种子数据。种子脚本是幂等的：检测到企业数据后不会重复插入。

4. 访问服务：

   | 服务 | 地址 |
   | --- | --- |
   | 前端 | http://localhost:3000 |
   | 后端 | http://localhost:8000 |
   | Swagger UI | http://localhost:8000/docs |
   | ReDoc | http://localhost:8000/redoc |
   | 健康检查 | http://localhost:8000/health |

5. 首次使用请在注册页创建本地账号。仓库不提供硬编码的默认密码。

后台运行可使用 `docker compose up --build -d`，查看日志可使用 `docker compose logs -f`，停止服务使用 `docker compose down`。若执行 `docker compose down -v`，PostgreSQL 和 Redis 持久卷也会被删除，请仅在确认不再需要本地数据时使用。

## 本地开发启动

### 1. 准备数据服务

可以只通过 Docker 启动 PostgreSQL 和 Redis：

```bash
docker compose up -d postgres redis
```

复制环境变量模板，并确认本地连接地址使用 `localhost`：

```powershell
Copy-Item .env.example .env
```

后端设置从进程环境或当前目录的 `.env` 读取。进入 `backend` 运行命令时，可将根目录 `.env` 复制为 `backend/.env`，或在终端显式设置 `DATABASE_URL`、`REDIS_URL`、`SECRET_KEY` 和 `CORS_ORIGINS`。

### 2. 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

macOS / Linux 激活虚拟环境使用 `source .venv/bin/activate`。

### 3. 启动前端

新开一个终端：

```powershell
cd frontend
Set-Content -Encoding utf8 -Path .env.local -Value "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
npm ci
npm run dev
```

`frontend/.env.local` 中需要存在：

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 环境变量

| 变量 | 用途 | 本地示例 |
| --- | --- | --- |
| `POSTGRES_DB` | PostgreSQL 数据库名 | `offerpilot` |
| `POSTGRES_USER` | PostgreSQL 用户 | `offerpilot` |
| `POSTGRES_PASSWORD` | PostgreSQL 密码 | 必须自行修改 |
| `DATABASE_URL` | SQLAlchemy 连接串 | `postgresql+psycopg://...@localhost:5432/offerpilot` |
| `REDIS_URL` | Redis 连接串 | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT 签名密钥 | 长随机值，禁止提交 |
| `CORS_ORIGINS` | 允许的前端来源，多个值用逗号分隔 | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | 浏览器请求的 API 前缀 | `http://localhost:8000/api/v1` |
| `UPLOAD_DIR` | 简历附件存储目录 | `data/uploads` |
| `MAX_UPLOAD_BYTES` | 单个附件最大字节数 | `10485760` |
| `MAX_IMPORT_BYTES` | 单个 CSV 最大字节数 | `5242880` |
| `ADMIN_EMAILS` | 首次注册时自动授予本地管理员权限的邮箱 | `admin@offerpilot.example.com` |
| `CRAWLER_ENABLED` | 是否启动本地官方来源调度器 | `true` |
| `CRAWLER_TICK_SECONDS` | 扫描到期来源的间隔秒数 | `60` |
| `CRAWLER_TIMEOUT_SECONDS` | 单次官方请求超时 | `10` |
| `CRAWLER_MAX_RESPONSE_BYTES` | 单个响应最大字节数 | `2097152` |
| `CRAWLER_MAX_ITEMS_PER_RUN` | 单来源单次最多处理岗位数 | `100` |
| `CRAWLER_USER_AGENT` | robots.txt 检查与请求使用的客户端标识 | `OfferPilotAI/0.4 ...` |

`.env` 和 `.env.local` 已加入 `.gitignore`。生产环境必须使用密钥管理服务，不得采用模板默认值。

## 配置本地官方招聘同步

1. 使用 `ADMIN_EMAILS` 中的邮箱注册，进入 `http://localhost:3000/admin`。
2. 先在企业库建立目标企业，再在“企业官方招聘自动同步”中绑定企业并填写具体官方招聘页或官方 Feed。
3. 选择解析格式和最低 15 分钟的同步间隔，记录使用依据并确认网站条款后启用。
4. 点击“立即同步”验证配置；新发现岗位会出现在岗位库和待核验队列，状态为“待核验”。
5. 核验后用户可点击“前往官方投递”，新窗口将打开来源提供的官方 URL。

每家企业页面结构和许可不同，因此仓库不会预置或猜测真实企业抓取规则。若 robots.txt 禁止、地址指向内网、需要登录/验证码、响应超限或格式不受支持，本次运行会安全失败并记录原因。当前调度器适用于本地单个 backend 进程；不要把同一数据库连接到多个同时运行的调度实例。

## 数据库迁移与种子数据

本地执行：

```bash
cd backend
alembic upgrade head
python -m app.db.seed
```

Docker 环境手动执行：

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
```

创建新迁移：

```bash
cd backend
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```

迁移文件必须随模型变更一起提交并经过审查。详细约定见 [数据库文档](docs/DATABASE.md) 和 [开发指南](docs/DEVELOPMENT.md)。

## 质量检查与测试

前端：

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm run format:check
npm run build
```

后端：

```bash
cd backend
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy app tests
pytest
```

PostgreSQL 集成测试：

```bash
cd backend
TEST_POSTGRES_URL=postgresql+psycopg://... pytest tests/integration -m integration
```

浏览器端到端测试（需先启动完整 Docker 环境）：

```bash
cd frontend
npx playwright install chromium
npm run test:e2e -- --project=chromium
```

后端快速测试默认使用隔离的 SQLite 数据库。CI 另外启动 PostgreSQL 17 执行集成测试，并在完整 Compose 环境上运行 Playwright。

## API 快速体验

注册会返回 Bearer Token：

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"strong-pass-123","full_name":"校招同学"}'
```

后续请求携带：

```text
Authorization: Bearer <access_token>
```

完整端点与示例见 [API 文档](docs/API.md)。

## 数据合规与边界

- 内置企业和岗位只用于 UI、筛选、统计和流程演示，不得宣传为“正在招聘”或“实时开放”。
- 平台不实现验证码绕过、反爬规避、登录态盗用或其他违反网站条款的采集能力。
- 外部数据接入前必须确认授权、来源、许可、用途、保留期限与更新频率。
- 展示外部招聘信息时必须保存来源、最后核验时间和演示/已核验状态；用户应在投递前访问企业官方渠道复核。
- 不将简历、联系方式、Token、密钥等敏感信息写入日志、种子数据或仓库。

详细策略见 [数据来源与合规](docs/DATA-SOURCES.md)。

## 常见问题

### `docker compose up --build` 后前端暂时不可访问

首次构建会安装依赖，并等待 PostgreSQL、Redis 和后端健康检查通过。使用 `docker compose ps` 和 `docker compose logs -f backend frontend` 检查状态。

### 后端提示无法连接 PostgreSQL

容器内数据库主机名应为 `postgres`；宿主机本地开发应使用 `localhost`。同时检查 `.env` 中的用户名、密码、数据库名是否一致，并确认 `docker compose ps postgres` 显示 healthy。

### 前端请求出现 CORS 或网络错误

确认后端运行在 8000 端口，`NEXT_PUBLIC_API_URL` 为 `http://localhost:8000/api/v1`，且 `CORS_ORIGINS` 包含浏览器实际访问的前端 Origin。修改构建期公开变量后需要重新构建前端。

### 为什么企业或岗位显示 Demo / 待核验？

这是有意的安全设计。种子数据不代表真实或实时招聘，`deadline` 也仅用于功能演示。请勿依据演示数据直接投递。

### 如何清空本地 Docker 数据重新初始化？

确认无需保留本地数据后运行 `docker compose down -v`，再运行 `docker compose up --build`。该操作会永久删除本项目的 Docker 数据卷。

### 为什么注册后没有默认投递记录？

用户业务记录按账号隔离。种子脚本只提供演示企业与岗位，不创建带默认密码的用户；请通过页面或 API 创建个人记录。

## 后续路线图

- 来源级 ETag/Last-Modified 增量请求、允许域名配置与结构化企业适配器
- Redis 分布式任务锁、重试退避、限流和定时提醒
- 简历恶意文件扫描、对象存储、加密和短期签名下载地址
- 更细粒度的角色权限、刷新 Token、会话撤销和 HttpOnly Cookie 方案
- 扩展端到端、可访问性测试与覆盖率门禁
- 可观测性、备份恢复、生产部署模板
- 在可信数据和用户授权范围内探索简历匹配、投递复盘等 AI 辅助能力

本项目当前目标是单机本地运行，因此对象存储和生产部署模板不是启动前置条件；本地 PostgreSQL 卷仍应按需要定期备份。

## 项目文档

- [产品需求文档](docs/PRD.md)
- [系统架构](docs/ARCHITECTURE.md)
- [数据库设计](docs/DATABASE.md)
- [API 参考](docs/API.md)
- [开发指南](docs/DEVELOPMENT.md)
- [数据来源与合规](docs/DATA-SOURCES.md)

## 许可与责任

当前仓库未声明开源许可证。在获得仓库所有者明确授权前，请勿假定可以复制、分发或商用。平台提供的是求职管理工具，不能替代企业官方招聘信息、录用通知或专业意见。
