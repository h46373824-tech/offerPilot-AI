"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  Database,
  FileUp,
  RefreshCw,
  Rss,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { EmptyState, ErrorState, LoadingState } from "@/components/status";
import { apiFetch } from "@/lib/api";
import { useHasToken } from "@/lib/auth";
import type {
  ApiPage,
  Company,
  CrawlRun,
  CurrentUser,
  DataQualityStats,
  DataSource,
  ImportBatch,
  ReviewItem,
} from "@/lib/types";

export function AdminConsole() {
  const authenticated = useHasToken();
  const user = useQuery({
    enabled: authenticated,
    queryKey: ["current-user"],
    queryFn: () => apiFetch<CurrentUser>("/auth/me"),
  });

  if (!authenticated) return <AccessNotice text="请先登录本地管理员账号。" />;
  if (user.isPending) return <LoadingState text="正在验证管理员权限…" />;
  if (user.isError || !user.data)
    return <ErrorState text="无法读取当前用户权限。" />;
  if (!user.data.is_admin)
    return <AccessNotice text="当前账号没有数据治理权限。" />;
  return <GovernanceWorkspace />;
}

function GovernanceWorkspace() {
  const client = useQueryClient();
  const [entityType, setEntityType] = useState<"company" | "job">("company");
  const [message, setMessage] = useState("");
  const sources = useQuery({
    queryKey: ["admin", "sources"],
    queryFn: () =>
      apiFetch<ApiPage<DataSource>>("/admin/data-sources?page_size=100"),
  });
  const quality = useQuery({
    queryKey: ["admin", "quality"],
    queryFn: () => apiFetch<DataQualityStats>("/admin/quality"),
  });
  const imports = useQuery({
    queryKey: ["admin", "imports"],
    queryFn: () => apiFetch<ApiPage<ImportBatch>>("/admin/imports?page_size=8"),
  });
  const companies = useQuery({
    queryKey: ["companies", "admin-source-map"],
    queryFn: () =>
      apiFetch<ApiPage<Company>>(
        "/companies?page_size=100&sort_by=name&order=asc",
      ),
  });
  const crawlRuns = useQuery({
    queryKey: ["admin", "crawl-runs"],
    queryFn: () =>
      apiFetch<ApiPage<CrawlRun>>("/admin/crawl-runs?page_size=10"),
  });
  const review = useQuery({
    queryKey: ["admin", "review", entityType],
    queryFn: () =>
      apiFetch<ApiPage<ReviewItem>>(
        `/admin/review?entity_type=${entityType}&page_size=20`,
      ),
  });
  const refresh = () => {
    void client.invalidateQueries({ queryKey: ["admin"] });
    void client.invalidateQueries({ queryKey: ["companies"] });
    void client.invalidateQueries({ queryKey: ["jobs"] });
  };
  const createSource = useMutation({
    mutationFn: (payload: object) =>
      apiFetch<DataSource>("/admin/data-sources", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onError: (error) => setMessage((error as Error).message),
    onSuccess: () => {
      setMessage("数据源已登记");
      refresh();
    },
  });
  const upload = useMutation({
    mutationFn: (formData: FormData) =>
      apiFetch<ImportBatch>("/admin/imports", {
        method: "POST",
        body: formData,
      }),
    onError: (error) => setMessage((error as Error).message),
    onSuccess: (batch) => {
      setMessage(
        `导入完成：新增 ${batch.created_rows}，更新 ${batch.updated_rows}，错误 ${batch.error_rows}`,
      );
      refresh();
    },
  });
  const crawl = useMutation({
    mutationFn: (sourceId: number) =>
      apiFetch<CrawlRun>(`/admin/data-sources/${sourceId}/crawl`, {
        method: "POST",
      }),
    onError: (error) => setMessage((error as Error).message),
    onSuccess: (run) => {
      setMessage(
        run.status === "completed"
          ? `同步完成：新增 ${run.discovered_rows}，更新 ${run.updated_rows}，跳过 ${run.skipped_rows}`
          : `同步失败：${run.error_message ?? "请检查来源配置"}`,
      );
      refresh();
    },
  });
  const decide = useMutation({
    mutationFn: ({
      action,
      id,
      type,
    }: {
      action: "approve" | "reject";
      id: number;
      type: "company" | "job";
    }) =>
      apiFetch<ReviewItem>(`/admin/review/${type}/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ action, recruitment_status: "open" }),
      }),
    onSuccess: refresh,
  });

  if (
    sources.isPending ||
    quality.isPending ||
    imports.isPending ||
    companies.isPending ||
    crawlRuns.isPending
  )
    return <LoadingState text="正在加载本地数据治理信息…" />;
  if (
    sources.isError ||
    quality.isError ||
    imports.isError ||
    companies.isError ||
    crawlRuns.isError ||
    !quality.data
  )
    return <ErrorState text="数据治理信息加载失败。" />;

  return (
    <div className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric
          icon={Database}
          label="企业 / 岗位"
          value={`${quality.data.companies_total} / ${quality.data.jobs_total}`}
        />
        <Metric
          icon={ShieldCheck}
          label="已核验记录"
          value={String(quality.data.verified_records)}
        />
        <Metric
          icon={FileUp}
          label="待核验记录"
          value={String(quality.data.unverified_records)}
          warning={quality.data.unverified_records > 0}
        />
        <Metric
          icon={XCircle}
          label="超过 30 天未复核"
          value={String(quality.data.stale_records)}
          warning={quality.data.stale_records > 0}
        />
      </section>

      <div className="grid gap-5 xl:grid-cols-2">
        <SourcePanel
          mutation={createSource}
          sources={sources.data?.items ?? []}
        />
        <ImportPanel mutation={upload} sources={sources.data?.items ?? []} />
      </div>
      <OfficialSyncPanel
        companies={companies.data?.items ?? []}
        crawlMutation={crawl}
        createMutation={createSource}
        runs={crawlRuns.data?.items ?? []}
        sources={sources.data?.items ?? []}
      />
      {message && (
        <p
          className={`rounded-xl px-4 py-3 text-sm ${createSource.isError || upload.isError || crawl.isError ? "bg-rose-50 text-rose-700 dark:bg-rose-950" : "bg-teal-50 text-teal-700 dark:bg-teal-950"}`}
        >
          {message}
        </p>
      )}

      <section className="card overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] p-5">
          <div>
            <h2 className="font-bold">待核验队列</h2>
            <p className="text-xs text-[var(--muted)]">
              导入记录默认不会成为实时开放数据，必须人工确认。
            </p>
          </div>
          <div className="flex rounded-lg bg-slate-100 p-1 dark:bg-slate-800">
            {(["company", "job"] as const).map((type) => (
              <button
                className={`rounded-md px-3 py-1.5 text-sm ${entityType === type ? "bg-white font-bold shadow-sm dark:bg-slate-700" : "text-[var(--muted)]"}`}
                key={type}
                onClick={() => setEntityType(type)}
                type="button"
              >
                {type === "company" ? "企业" : "岗位"}
              </button>
            ))}
          </div>
        </div>
        {review.isPending ? (
          <div className="p-5">
            <LoadingState text="正在加载审核队列…" />
          </div>
        ) : review.data?.items.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>名称</th>
                  <th>来源</th>
                  <th>当前状态</th>
                  <th>更新时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {review.data.items.map((item) => (
                  <tr key={`${item.entity_type}-${item.id}`}>
                    <td>
                      <b>{item.name}</b>
                      {item.company_name && (
                        <span className="block text-xs text-[var(--muted)]">
                          {item.company_name}
                        </span>
                      )}
                    </td>
                    <td>{item.source_name}</td>
                    <td>{item.recruitment_status}</td>
                    <td>
                      {new Date(item.updated_at).toLocaleDateString("zh-CN")}
                    </td>
                    <td>
                      <div className="flex gap-3">
                        <button
                          className="text-sm font-semibold text-teal-600"
                          disabled={decide.isPending}
                          onClick={() =>
                            decide.mutate({
                              action: "approve",
                              id: item.id,
                              type: item.entity_type,
                            })
                          }
                          type="button"
                        >
                          <CheckCircle2 className="inline" size={15} /> 核验通过
                        </button>
                        <button
                          className="text-sm font-semibold text-rose-600"
                          disabled={decide.isPending}
                          onClick={() =>
                            decide.mutate({
                              action: "reject",
                              id: item.id,
                              type: item.entity_type,
                            })
                          }
                          type="button"
                        >
                          关闭
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-5">
            <EmptyState text="当前没有待核验记录" />
          </div>
        )}
      </section>

      <div className="grid gap-5 xl:grid-cols-2">
        <CoveragePanel quality={quality.data} />
        <ImportHistory batches={imports.data?.items ?? []} />
      </div>
    </div>
  );
}

function SourcePanel({
  mutation,
  sources,
}: {
  mutation: ReturnType<typeof useMutation<DataSource, Error, object>>;
  sources: DataSource[];
}) {
  return (
    <section className="card p-5">
      <h2 className="font-bold">授权数据源</h2>
      <p className="mb-4 text-xs text-[var(--muted)]">
        必须记录授权或合法使用依据，不能填写模糊的“网络公开”。
      </p>
      <form
        className="space-y-3"
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          mutation.mutate({
            name: data.get("name"),
            source_type: "authorized_csv",
            base_url: data.get("base_url") || null,
            authorization_note: data.get("authorization_note"),
          });
          event.currentTarget.reset();
        }}
      >
        <input
          className="field"
          name="name"
          placeholder="数据源名称"
          required
        />
        <input
          className="field"
          name="base_url"
          placeholder="来源主页（可选）"
          type="url"
        />
        <textarea
          className="field min-h-24"
          name="authorization_note"
          placeholder="授权范围、用途与有效期"
          required
        />
        <button className="btn-primary" disabled={mutation.isPending}>
          {mutation.isPending ? "登记中…" : "登记数据源"}
        </button>
      </form>
      <div className="mt-5 flex flex-wrap gap-2">
        {sources.map((source) => (
          <span
            className="rounded-full bg-slate-100 px-3 py-1 text-xs dark:bg-slate-800"
            key={source.id}
          >
            {source.name} · {source.is_active ? "启用" : "停用"}
          </span>
        ))}
      </div>
    </section>
  );
}

function OfficialSyncPanel({
  companies,
  crawlMutation,
  createMutation,
  runs,
  sources,
}: {
  companies: Company[];
  crawlMutation: ReturnType<typeof useMutation<CrawlRun, Error, number>>;
  createMutation: ReturnType<typeof useMutation<DataSource, Error, object>>;
  runs: CrawlRun[];
  sources: DataSource[];
}) {
  const sourceNames = new Map(
    sources.map((source) => [source.id, source.name]),
  );
  const crawlerSources = sources.filter((source) => source.feed_url);

  return (
    <section className="card overflow-hidden">
      <div className="border-b border-[var(--border)] p-5">
        <div className="flex items-start gap-3">
          <span className="rounded-xl bg-teal-50 p-3 text-teal-600 dark:bg-teal-950">
            <Rss aria-hidden="true" size={22} />
          </span>
          <div>
            <h2 className="font-bold">企业官方招聘自动同步</h2>
            <p className="mt-1 text-xs leading-5 text-[var(--muted)]">
              仅配置已确认可自动访问的企业官方页面、RSS、Atom 或 JSON
              Feed。系统遵守
              robots.txt，不登录、不绕过验证码；新岗位先进入待核验队列。
            </p>
          </div>
        </div>
      </div>
      <div className="grid gap-6 p-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.25fr)]">
        <form
          className="space-y-3"
          onSubmit={(event) => {
            event.preventDefault();
            const data = new FormData(event.currentTarget);
            const keywords = String(data.get("link_keywords") ?? "")
              .split(/[，,]/)
              .map((item) => item.trim())
              .filter(Boolean);
            createMutation.mutate({
              name: data.get("name"),
              source_type: "official_recruitment",
              base_url: data.get("feed_url"),
              authorization_note: data.get("authorization_note"),
              company_id: Number(data.get("company_id")),
              feed_url: data.get("feed_url"),
              parser_mode: data.get("parser_mode"),
              link_keywords: keywords,
              is_crawl_enabled: true,
              crawl_interval_minutes: Number(
                data.get("crawl_interval_minutes"),
              ),
            });
            event.currentTarget.reset();
          }}
        >
          <h3 className="text-sm font-bold">新增官方来源</h3>
          <input
            className="field"
            name="name"
            placeholder="来源名称"
            required
          />
          <select className="field" defaultValue="" name="company_id" required>
            <option disabled value="">
              绑定企业
            </option>
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
          <input
            className="field"
            name="feed_url"
            placeholder="https://企业官方招聘页或 Feed"
            required
            type="url"
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <select className="field" defaultValue="auto" name="parser_mode">
              <option value="auto">自动识别格式</option>
              <option value="html_links">HTML 招聘链接</option>
              <option value="rss">RSS</option>
              <option value="atom">Atom</option>
              <option value="json_feed">JSON Feed</option>
            </select>
            <select
              className="field"
              defaultValue="360"
              name="crawl_interval_minutes"
            >
              <option value="60">每小时</option>
              <option value="360">每 6 小时</option>
              <option value="720">每 12 小时</option>
              <option value="1440">每天</option>
            </select>
          </div>
          <input
            className="field"
            name="link_keywords"
            placeholder="HTML 关键词（逗号分隔，可留空）"
          />
          <textarea
            className="field min-h-20"
            name="authorization_note"
            placeholder="说明官方来源、使用依据及已检查的网站条款"
            required
          />
          <label className="flex items-start gap-2 text-xs text-[var(--muted)]">
            <input className="mt-0.5" required type="checkbox" />
            我已确认该官方来源允许上述自动访问方式，并对配置负责。
          </label>
          <button
            className="btn-primary"
            disabled={createMutation.isPending || !companies.length}
          >
            {createMutation.isPending ? "保存中…" : "保存并启用定时同步"}
          </button>
        </form>

        <div>
          <h3 className="mb-3 text-sm font-bold">已配置来源</h3>
          {crawlerSources.length ? (
            <ul className="space-y-3">
              {crawlerSources.map((source) => (
                <li
                  className="rounded-xl border border-[var(--border)] p-4"
                  key={source.id}
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0">
                      <b>{source.name}</b>
                      <p className="mt-1 truncate text-xs text-[var(--muted)]">
                        {source.feed_url}
                      </p>
                      <p className="mt-1 text-xs text-[var(--muted)]">
                        {source.last_crawled_at
                          ? `上次同步：${new Date(source.last_crawled_at).toLocaleString("zh-CN")}`
                          : "尚未同步"}
                        {source.last_crawl_status
                          ? ` · ${source.last_crawl_status === "completed" ? "成功" : "失败"}`
                          : ""}
                      </p>
                    </div>
                    <button
                      className="inline-flex items-center gap-1 text-sm font-semibold text-teal-600 disabled:opacity-50"
                      disabled={crawlMutation.isPending}
                      onClick={() => crawlMutation.mutate(source.id)}
                      type="button"
                    >
                      <RefreshCw
                        aria-hidden="true"
                        className={
                          crawlMutation.isPending ? "animate-spin" : ""
                        }
                        size={15}
                      />
                      立即同步
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState text="尚未配置官方招聘来源" />
          )}
          {runs.length > 0 && (
            <div className="mt-5">
              <h3 className="mb-2 text-sm font-bold">最近同步记录</h3>
              <ul className="divide-y divide-[var(--border)] text-xs">
                {runs.slice(0, 5).map((run) => (
                  <li className="flex justify-between gap-3 py-2" key={run.id}>
                    <span>
                      {run.source_id
                        ? (sourceNames.get(run.source_id) ??
                          `来源 #${run.source_id}`)
                        : "已删除来源"}
                    </span>
                    <span
                      className={
                        run.status === "failed"
                          ? "text-rose-600"
                          : "text-teal-600"
                      }
                    >
                      {run.status === "completed"
                        ? `新增 ${run.discovered_rows} / 更新 ${run.updated_rows}`
                        : `失败：${run.error_message ?? "未知错误"}`}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function ImportPanel({
  mutation,
  sources,
}: {
  mutation: ReturnType<typeof useMutation<ImportBatch, Error, FormData>>;
  sources: DataSource[];
}) {
  return (
    <section className="card p-5">
      <h2 className="font-bold">CSV 导入</h2>
      <p className="mb-4 text-xs text-[var(--muted)]">
        仅在本机处理 UTF-8 CSV；同名企业、同企业同名岗位会更新并重新进入核验。
      </p>
      <form
        className="space-y-3"
        onSubmit={(event) => {
          event.preventDefault();
          mutation.mutate(new FormData(event.currentTarget));
        }}
      >
        <select className="field" name="source_id" required defaultValue="">
          <option disabled value="">
            选择授权数据源
          </option>
          {sources
            .filter((source) => source.is_active)
            .map((source) => (
              <option key={source.id} value={source.id}>
                {source.name}
              </option>
            ))}
        </select>
        <select className="field" name="entity_type" defaultValue="company">
          <option value="company">企业 CSV</option>
          <option value="job">岗位 CSV</option>
        </select>
        <input
          accept=".csv,text/csv"
          className="field"
          name="file"
          required
          type="file"
        />
        <button
          className="btn-primary"
          disabled={mutation.isPending || !sources.length}
        >
          {mutation.isPending ? "导入中…" : "导入并进入审核"}
        </button>
      </form>
      <div className="mt-4 flex gap-4 text-sm">
        <button
          className="font-semibold text-teal-600"
          onClick={() => downloadTemplate("company")}
          type="button"
        >
          下载企业模板
        </button>
        <button
          className="font-semibold text-teal-600"
          onClick={() => downloadTemplate("job")}
          type="button"
        >
          下载岗位模板
        </button>
      </div>
    </section>
  );
}

function CoveragePanel({ quality }: { quality: DataQualityStats }) {
  return (
    <section className="card p-5">
      <h2 className="font-bold">来源覆盖</h2>
      <p className="mb-4 text-xs text-[var(--muted)]">
        Demo 记录 {quality.demo_records} 条，不计入已核验实时数据。
      </p>
      {quality.source_coverage.length ? (
        <ul className="space-y-3">
          {quality.source_coverage.map((source) => (
            <li
              className="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3 text-sm dark:bg-slate-800"
              key={source.source_id}
            >
              <span>{source.source_name}</span>
              <b>
                {source.companies} 家企业 · {source.jobs} 个岗位
              </b>
            </li>
          ))}
        </ul>
      ) : (
        <EmptyState text="尚未导入授权数据" />
      )}
    </section>
  );
}

function ImportHistory({ batches }: { batches: ImportBatch[] }) {
  return (
    <section className="card p-5">
      <h2 className="font-bold">最近导入</h2>
      <p className="mb-4 text-xs text-[var(--muted)]">
        导入批次和错误数量保存在本地数据库。
      </p>
      {batches.length ? (
        <ul className="divide-y divide-[var(--border)]">
          {batches.map((batch) => (
            <li className="py-3 text-sm" key={batch.id}>
              <div className="flex justify-between gap-3">
                <b>{batch.filename}</b>
                <span>{batch.status}</span>
              </div>
              <p className="mt-1 text-xs text-[var(--muted)]">
                共 {batch.total_rows} · 新增 {batch.created_rows} · 更新{" "}
                {batch.updated_rows} · 错误 {batch.error_rows}
              </p>
            </li>
          ))}
        </ul>
      ) : (
        <EmptyState text="暂无导入记录" />
      )}
    </section>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
  warning = false,
}: {
  icon: typeof Database;
  label: string;
  value: string;
  warning?: boolean;
}) {
  return (
    <div className="card flex items-center gap-4 p-5">
      <span
        className={`rounded-xl p-3 ${warning ? "bg-amber-50 text-amber-600 dark:bg-amber-950" : "bg-teal-50 text-teal-600 dark:bg-teal-950"}`}
      >
        <Icon aria-hidden="true" size={22} />
      </span>
      <div>
        <p className="text-xs text-[var(--muted)]">{label}</p>
        <p className="text-2xl font-black">{value}</p>
      </div>
    </div>
  );
}

function AccessNotice({ text }: { text: string }) {
  return <div className="card p-8 text-sm text-[var(--muted)]">{text}</div>;
}

function downloadTemplate(type: "company" | "job") {
  const csv =
    type === "company"
      ? "name,industry,company_type,education_requirement,work_cities,accepts_college,accepts_bachelor,website,open_date,deadline\n"
      : "title,company_name,category,work_cities,education_requirement,description,requirements,application_url,published_at,deadline\n";
  const url = URL.createObjectURL(
    new Blob([`\ufeff${csv}`], { type: "text/csv;charset=utf-8" }),
  );
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${type}-import-template.csv`;
  anchor.click();
  URL.revokeObjectURL(url);
}
