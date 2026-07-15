# OfferPilot AI API 文档

## 1. 基本信息

| 项目 | 值 |
| --- | --- |
| 本地服务地址 | `http://localhost:8000` |
| API v1 前缀 | `/api/v1` |
| OpenAPI JSON | `/openapi.json` |
| Swagger UI | `/docs` |
| ReDoc | `/redoc` |
| 数据格式 | JSON |
| 认证方式 | `Authorization: Bearer <JWT>` |

除 `GET /health`、注册和两种登录端点外，业务接口均需要有效 JWT。企业和岗位读取对登录用户开放，写操作及 `/api/v1/admin/*` 仅允许本地管理员。

> API 返回的种子企业与岗位是 Demo 数据，不代表真实或实时招聘。客户端必须保留 `is_demo`、`data_source`、`recruitment_status` 和 `last_verified_at` 的语义。

## 2. 通用约定

### 2.1 请求头

```http
Content-Type: application/json
Authorization: Bearer eyJ...
```

### 2.2 时间格式

- 日期：ISO 8601 `YYYY-MM-DD`；
- 日期时间：ISO 8601，建议携带时区，例如 `2026-09-30T10:00:00+08:00`；
- 服务端内部统计使用 UTC；
- 不确定的发布时间、截止时间和核验时间应为 `null`，不得伪造。

### 2.3 分页响应

所有分页列表使用统一结构：

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 0
}
```

通用参数：

| 参数 | 默认值 | 约束 | 说明 |
| --- | --- | --- | --- |
| `page` | 1 | `>= 1` | 页码 |
| `page_size` | 20 | 1–100 | 每页条数 |
| `order` | `desc` | `asc` / `desc` | 排序方向 |

### 2.4 错误响应

业务错误通常使用：

```json
{
  "detail": "错误说明"
}
```

Pydantic 参数校验失败使用 FastAPI 标准 422 结构。主要状态码：

| 状态码 | 含义 |
| --- | --- |
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 204 | 删除成功，无响应体 |
| 401 | 缺少、无效或过期认证 |
| 404 | 资源不存在，或资源不属于当前用户 |
| 409 | 冲突，例如邮箱已注册 |
| 422 | 请求参数或 JSON 校验失败 |
| 500 | 未处理的服务器错误 |

## 3. 认证

### 3.1 注册

`POST /api/v1/auth/register`

请求：

```json
{
  "email": "student@example.com",
  "password": "strong-pass-123",
  "full_name": "校招同学"
}
```

规则：邮箱必须合法；密码长度 8–128；姓名长度 1–100；邮箱按小写保存且唯一。

成功响应 `201`：

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

邮箱已存在返回 `409`。

### 3.2 登录

`POST /api/v1/auth/login`

```json
{
  "email": "student@example.com",
  "password": "strong-pass-123"
}
```

成功返回与注册相同的 Token 结构。凭据错误返回 `401`。

### 3.3 Swagger OAuth2 登录

`POST /api/v1/auth/token`

该端点接收 `application/x-www-form-urlencoded`，供 Swagger UI 的 **Authorize** 按钮和标准 OAuth2 Password Form 使用。把邮箱填入 `username` 字段：

```text
username=student@example.com&password=strong-pass-123
```

成功返回相同的 Token 结构。浏览器应用使用 JSON `/auth/login` 即可。

### 3.4 当前用户

`GET /api/v1/auth/me`

成功响应：

```json
{
  "id": 1,
  "email": "student@example.com",
  "full_name": "校招同学",
  "is_active": true,
  "created_at": "2026-07-15T01:00:00Z"
}
```

## 4. 健康检查

`GET /health`，无需认证。

```json
{
  "status": "ok",
  "service": "offerpilot-api"
}
```

该接口表示 API 进程可以响应；PostgreSQL 和 Redis 另由 Compose 健康检查验证。

## 5. 企业接口

### 5.1 端点

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/companies` | 分页查询企业 |
| POST | `/api/v1/companies` | 创建企业 |
| GET | `/api/v1/companies/{item_id}` | 查询单个企业 |
| PATCH | `/api/v1/companies/{item_id}` | 部分更新企业 |
| DELETE | `/api/v1/companies/{item_id}` | 删除企业 |

### 5.2 列表参数

| 参数 | 值/说明 |
| --- | --- |
| `search` | 模糊匹配企业名称或工作城市 |
| `industry` | 精确匹配行业 |
| `company_type` | 精确匹配企业性质 |
| `education` | 模糊匹配学历要求 |
| `recruitment_status` | 精确匹配招聘/核验状态 |
| `accepts_college` | 布尔值，筛选专科是否可投 |
| `accepts_bachelor` | 布尔值，筛选本科是否可投 |
| `is_demo` | 布尔值，区分 Demo 与正式数据 |
| `sort_by` | `name`、`created_at`、`deadline` |
| `order` | `asc`、`desc` |
| `page` / `page_size` | 分页参数 |

示例：

```http
GET /api/v1/companies?search=上海&industry=半导体&page=1&page_size=20&sort_by=deadline&order=asc
```

### 5.3 创建企业

```json
{
  "name": "示例企业（Demo）",
  "industry": "人工智能",
  "company_type": "民营企业",
  "website": null,
  "campus_website": null,
  "logo_url": null,
  "recruitment_status": "demo_unverified",
  "open_date": null,
  "deadline": null,
  "education_requirement": "本科及以上",
  "accepts_college": false,
  "accepts_bachelor": true,
  "major_requirement": "Demo，仅用于功能展示",
  "work_cities": "北京、上海",
  "data_source": "demo_seed_not_realtime",
  "last_verified_at": null,
  "is_demo": true
}
```

成功返回 `201` 和完整企业对象（含 `id`、`created_at`、`updated_at`）。`PATCH` 只需发送要修改的字段。删除成功返回 `204`。

## 6. 岗位接口

### 6.1 端点

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/jobs` | 分页查询岗位 |
| POST | `/api/v1/jobs` | 创建岗位 |
| GET | `/api/v1/jobs/{item_id}` | 查询单个岗位 |
| PATCH | `/api/v1/jobs/{item_id}` | 部分更新岗位 |
| DELETE | `/api/v1/jobs/{item_id}` | 删除岗位 |

### 6.2 列表参数

| 参数 | 值/说明 |
| --- | --- |
| `search` | 模糊匹配岗位标题、描述或企业名称 |
| `category` | 精确匹配岗位类别 |
| `city` | 模糊匹配工作城市 |
| `education` | 模糊匹配学历要求 |
| `company_id` | 按企业 ID 筛选 |
| `recruitment_status` | 精确匹配招聘/核验状态 |
| `is_demo` | 布尔值，区分 Demo 与正式数据 |
| `sort_by` | `title`、`published_at`、`deadline`、`created_at` |
| `order` | `asc`、`desc` |
| `page` / `page_size` | 分页参数 |

示例：

```http
GET /api/v1/jobs?search=开发&city=深圳&education=本科&sort_by=deadline&order=asc
```

### 6.3 创建岗位

```json
{
  "title": "软件开发工程师（Demo）",
  "company_id": 1,
  "category": "技术研发",
  "work_cities": "北京",
  "education_requirement": "本科及以上",
  "major_requirement": "计算机相关专业，Demo 字段",
  "description": "用于展示产品功能，不代表真实岗位。",
  "requirements": "实际要求请以企业官方渠道为准。",
  "application_url": null,
  "published_at": null,
  "deadline": null,
  "recruitment_status": "demo_unverified",
  "data_source": "demo_seed_not_realtime",
  "last_verified_at": null,
  "is_demo": true
}
```

`company_id` 不存在时返回 `404`。成功返回 `201`。

## 7. 收藏

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/favorites` | 当前用户收藏分页列表 |
| POST | `/api/v1/favorites` | 收藏岗位 |
| DELETE | `/api/v1/favorites/{job_id}` | 按岗位取消收藏 |

新增请求：

```json
{
  "job_id": 1
}
```

同一用户重复收藏同一岗位时返回现有记录，不创建重复数据；岗位不存在返回 `404`。

列表接受 `page` 与 `page_size`，使用统一分页响应。单条字段包括 `id`、`user_id`、`job_id` 和 `created_at`。

## 8. 投递记录

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/applications` | 当前用户投递分页列表 |
| GET | `/api/v1/applications/{item_id}` | 获取自己的单条投递 |
| POST | `/api/v1/applications` | 创建投递 |
| PATCH | `/api/v1/applications/{item_id}` | 更新自己的投递 |
| DELETE | `/api/v1/applications/{item_id}` | 删除自己的投递 |

列表支持：

| 参数 | 说明 |
| --- | --- |
| `page` / `page_size` | 分页 |
| `status` | 精确匹配投递状态 |
| `job_id` | 按岗位筛选 |
| `sort_by` | `created_at`、`applied_at`、`status` |
| `order` | `asc`、`desc` |

创建请求：

```json
{
  "job_id": 1,
  "status": "applied",
  "applied_at": "2026-07-15T09:30:00+08:00",
  "channel": "企业官网",
  "notes": "已使用前端方向简历"
}
```

更新请求可以只包含变化字段：

```json
{
  "status": "interview",
  "notes": "已收到一面通知"
}
```

只能读取和修改当前用户记录。不属于当前用户的 ID 按不存在处理并返回 `404`。

## 9. 面试记录

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/interviews` | 当前用户面试分页列表 |
| GET | `/api/v1/interviews/{item_id}` | 获取自己的单条面试 |
| POST | `/api/v1/interviews` | 创建面试记录 |
| PATCH | `/api/v1/interviews/{item_id}` | 部分更新自己的面试 |
| DELETE | `/api/v1/interviews/{item_id}` | 删除自己的面试 |

创建请求：

```json
{
  "application_id": 1,
  "interview_type": "技术一面",
  "scheduled_at": "2026-07-20T14:00:00+08:00",
  "status": "scheduled",
  "location": "线上",
  "notes": "准备项目复盘"
}
```

列表支持 `page`、`page_size`、`status`、`sort_by`（`scheduled_at`、`created_at`、`status`）和 `order`。更新时可以修改面试类型、计划时间、状态、地点和备注，不能修改 `application_id`。创建时后端会验证关联投递属于当前用户。

## 10. Offer 记录

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/offers` | 当前用户 Offer 分页列表 |
| GET | `/api/v1/offers/{item_id}` | 获取自己的单条 Offer |
| POST | `/api/v1/offers` | 创建 Offer 记录 |
| PATCH | `/api/v1/offers/{item_id}` | 部分更新自己的 Offer |
| DELETE | `/api/v1/offers/{item_id}` | 删除自己的 Offer |

创建请求：

```json
{
  "application_id": 1,
  "status": "pending",
  "compensation": "用户私密备注",
  "location": "上海",
  "received_at": "2026-10-01",
  "response_deadline": "2026-10-10",
  "notes": "待比较发展方向"
}
```

列表支持 `page`、`page_size`、`status`、`sort_by`（`created_at`、`received_at`、`response_deadline`）和 `order`。更新时可修改状态、薪酬文本、地点、收到日期、回复截止日期和备注，不能修改 `application_id`。创建时后端会验证关联投递属于当前用户。`compensation` 和 `notes` 属于用户敏感信息，不应被写入日志或跨用户返回。

## 11. 通知

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/notifications` | 当前用户通知分页列表 |
| PATCH | `/api/v1/notifications/read-all` | 把当前用户全部未读通知标为已读 |
| PATCH | `/api/v1/notifications/{item_id}/read` | 标记通知为已读 |

列表可使用 `page`、`page_size`，并用 `unread_only=true` 只返回未读通知：

```http
GET /api/v1/notifications?unread_only=true
```

通知响应：

```json
{
  "id": 1,
  "title": "截止日期提醒",
  "content": "请前往官方渠道复核岗位截止日期。",
  "notification_type": "deadline",
  "is_read": false,
  "created_at": "2026-07-15T01:00:00Z"
}
```

客户端不能直接创建任意通知。第二阶段由提醒和岗位订阅接口生成通知；外部消息发送与后台定时调度属于后续任务系统。

## 12. 简历

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/resumes` | 当前用户简历列表 |
| POST | `/api/v1/resumes` | `multipart/form-data` 上传简历 |
| GET | `/api/v1/resumes/{id}` | 简历元数据 |
| GET | `/api/v1/resumes/{id}/download` | 下载附件 |
| PATCH | `/api/v1/resumes/{id}` | 修改名称、版本或默认状态 |
| POST | `/api/v1/resumes/{id}/default` | 设为默认简历 |
| DELETE | `/api/v1/resumes/{id}` | 删除元数据与附件 |

上传字段为 `file`、`name`、可选 `version` 和 `is_default`。仅允许 PDF、DOC、DOCX，默认最大 10 MB；附件使用不可预测的内部存储键，下载前会验证资源归属。投递的 `resume_id` 只能关联当前用户的简历。

## 13. 岗位订阅

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET/POST | `/api/v1/job-alerts` | 列表/创建订阅 |
| GET/PATCH/DELETE | `/api/v1/job-alerts/{id}` | 详情/更新/删除 |
| GET | `/api/v1/job-alerts/{id}/preview` | 预览匹配岗位 |
| POST | `/api/v1/job-alerts/{id}/run` | 执行匹配并生成通知 |

`criteria` 支持 `keyword`、`city`、`category`、`education`、`industry`，`frequency` 为 `instant`、`daily` 或 `weekly`。运行结果只将 `is_demo=false`、已核验且开放的岗位生成通知，Demo 岗位可用于界面浏览但不会被包装成实时匹配结果。

## 14. 提醒与审计

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/v1/reminders/run` | 为当前用户检查并生成提醒 |
| GET | `/api/v1/audit-logs` | 当前用户关键操作日志分页列表 |

提醒覆盖收藏岗位截止、48 小时内面试和 3 天内 Offer 决策截止，并按关联资源去重。审计详情只保存最小化动作摘要，不返回密码、Token 或简历正文。

## 15. 本地数据治理（管理员）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET/POST | `/api/v1/admin/data-sources` | 数据源列表/登记授权来源 |
| PATCH | `/api/v1/admin/data-sources/{id}` | 更新来源或停用 |
| POST | `/api/v1/admin/data-sources/{id}/crawl` | 立即同步一个已配置官方来源 |
| GET | `/api/v1/admin/crawl-runs` | 同步运行记录与错误摘要 |
| POST | `/api/v1/admin/imports` | 上传 UTF-8 企业或岗位 CSV |
| GET | `/api/v1/admin/imports` | 导入批次与错误摘要 |
| GET | `/api/v1/admin/review` | 企业/岗位待核验队列 |
| PATCH | `/api/v1/admin/review/{entity_type}/{id}` | 核验通过或关闭记录 |
| GET | `/api/v1/admin/quality` | 质量、过期记录和来源覆盖统计 |

导入使用 `multipart/form-data`，字段为 `source_id`、`entity_type=company|job`、`file`。新增和更新记录一律设为非 Demo、`unverified` 且清空核验时间，不会直接显示为实时开放。企业按名称去重；岗位按关联企业与岗位名去重。

本地管理员可通过 `ADMIN_EMAILS` 在首次注册时授予，或运行 `python -m app.db.promote_admin <email>` 提升已有账号。

官方来源还可设置 `company_id`、`feed_url`、`parser_mode`、`link_keywords`、`is_crawl_enabled` 和 `crawl_interval_minutes`。启用同步必须绑定企业并提供官方 URL，间隔最短 15 分钟。同步响应包含 `status`、`discovered_rows`、`updated_rows`、`skipped_rows` 和 `error_message`；自动发现岗位始终以 `unverified`、`last_verified_at=null` 写入，其 `application_url` 由官方来源提供。

## 16. Dashboard

`GET /api/v1/dashboard/stats`

响应结构：

```json
{
  "open_companies": 0,
  "college_companies": 0,
  "bachelor_companies": 0,
  "new_jobs_today": 0,
  "applications": 3,
  "interviews": 1,
  "offers": 0,
  "expiring_jobs": 4,
  "application_trend": [
    {"date": "2026-07-15", "count": 1}
  ],
  "industry_distribution": [
    {"industry": "人工智能", "count": 3}
  ],
  "recent_applications": [
    {
      "id": 1,
      "job_id": 1,
      "job_title": "软件开发工程师（Demo）",
      "company_name": "示例企业（Demo）",
      "status": "applied",
      "applied_at": "2026-07-15T01:30:00+00:00"
    }
  ]
}
```

口径：

- `open_companies`、学历可投企业、今日新增和即将截止只统计 `is_demo = false` 且 `recruitment_status = open` 的记录；仅加载种子数据时这些实时语义指标均为 0；
- 投递、面试、Offer、趋势和最近记录仅统计当前用户；
- `expiring_jobs` 统计当前 UTC 时间起 14 天内截止的岗位；
- `application_trend` 返回最近 7 天（含当天）；
- `industry_distribution` 对数据库企业按行业聚合，最多返回 10 个行业；
- `recent_applications` 最多返回 5 条，并包含岗位名称和企业名称。

种子企业是 Demo 数据，因此 `open_companies` 不能解释为真实开放企业数。

## 17. curl 示例

注册并保存返回的 Token 后：

```bash
curl http://localhost:8000/api/v1/companies?page=1&page_size=10 \
  -H "Authorization: Bearer <access_token>"
```

```bash
curl http://localhost:8000/api/v1/dashboard/stats \
  -H "Authorization: Bearer <access_token>"
```

PowerShell 可使用：

```powershell
$token = "<access_token>"
Invoke-RestMethod `
  -Uri "http://localhost:8000/api/v1/dashboard/stats" `
  -Headers @{ Authorization = "Bearer $token" }
```

## 18. 兼容性与演进

- 新增可选字段通常可以保持 v1 兼容；
- 删除字段、改名、改变类型或状态语义需要新版本或明确迁移期；
- OpenAPI 是机器可读契约，本文档解释业务语义，两者必须同步；
- 所有列表已统一分页；新增列表端点也应遵守同一结构，并对页大小设置上限；
- 生产化前应补充限流、幂等键、批量操作、请求 ID、刷新 Token 和更细粒度权限。
