# OfferPilot AI 前端

OfferPilot AI 的 Web 客户端，面向 2027 届校招场景，提供企业与岗位检索、投递跟踪、校招日历、Offer 管理和数据分析等功能。界面中的招聘信息均为 Demo 示例，不代表实时开放状态。

## 技术栈

- Next.js App Router、React、TypeScript（严格模式）
- Tailwind CSS 4、Zustand、TanStack Query、Recharts
- ESLint、Prettier

## 本地开发

```bash
npm ci
npm run dev
```

浏览器访问 <http://localhost:3000>。默认 API 地址为 `http://localhost:8000/api/v1`，可通过 `NEXT_PUBLIC_API_URL` 覆盖。

## 质量检查

```bash
npm run lint
npm run typecheck
npm run format:check
npm run build
```

完整的项目启动、数据库迁移与 Docker 使用说明请参阅仓库根目录的 `README.md`。
