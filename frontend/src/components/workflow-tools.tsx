"use client";

import Link from "next/link";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BellRing, Download, FileText, Play, Star, Trash2 } from "lucide-react";
import {
  Badge,
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/status";
import { apiDownload, apiFetch } from "@/lib/api";
import { useHasToken } from "@/lib/auth";
import type { ApiPage, JobAlert, Resume } from "@/lib/types";

function LoginRequired() {
  return (
    <EmptyState
      action={
        <Link className="btn-primary" href="/login">
          前往登录
        </Link>
      }
      text="登录后可使用此功能"
    />
  );
}

export function ResumesManager() {
  const authenticated = useHasToken();
  const client = useQueryClient();
  const [feedback, setFeedback] = useState("");
  const resumes = useQuery({
    enabled: authenticated,
    queryKey: ["resumes"],
    queryFn: () => apiFetch<ApiPage<Resume>>("/resumes?page_size=100"),
  });
  const upload = useMutation({
    mutationFn: (data: FormData) =>
      apiFetch<Resume>("/resumes", { method: "POST", body: data }),
    onSuccess: () => {
      setFeedback("简历上传成功");
      void client.invalidateQueries({ queryKey: ["resumes"] });
    },
  });
  const update = useMutation({
    mutationFn: ({ id, isDefault }: { id: number; isDefault: boolean }) =>
      apiFetch<Resume>(`/resumes/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_default: isDefault }),
      }),
    onSuccess: () => void client.invalidateQueries({ queryKey: ["resumes"] }),
  });
  const remove = useMutation({
    mutationFn: (id: number) =>
      apiFetch<void>(`/resumes/${id}`, { method: "DELETE" }),
    onSuccess: () => void client.invalidateQueries({ queryKey: ["resumes"] }),
  });
  if (!authenticated) return <LoginRequired />;
  if (resumes.isPending) return <LoadingState text="正在加载简历版本…" />;
  if (resumes.isError) return <ErrorState text={resumes.error.message} />;
  return (
    <div className="space-y-5">
      <form
        className="card grid gap-3 p-5 md:grid-cols-[1fr_150px_1fr_auto]"
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          upload.mutate(data);
          event.currentTarget.reset();
        }}
      >
        <label>
          <span className="mb-1 block text-xs text-[var(--muted)]">
            版本名称
          </span>
          <input
            className="field"
            name="name"
            placeholder="后端方向简历"
            required
          />
        </label>
        <label>
          <span className="mb-1 block text-xs text-[var(--muted)]">版本号</span>
          <input className="field" name="version" placeholder="v2.1" />
        </label>
        <label>
          <span className="mb-1 block text-xs text-[var(--muted)]">
            附件（PDF/DOC/DOCX，≤10MB）
          </span>
          <input
            accept=".pdf,.doc,.docx"
            className="field"
            name="file"
            type="file"
            required
          />
        </label>
        <button className="btn-primary self-end" disabled={upload.isPending}>
          {upload.isPending ? "上传中…" : "上传简历"}
        </button>
      </form>
      {(feedback || upload.error) && (
        <p
          className={`text-sm ${upload.error ? "text-rose-600" : "text-teal-600"}`}
        >
          {upload.error?.message ?? feedback}
        </p>
      )}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {resumes.data?.items.map((resume) => (
          <article className="card p-5" key={resume.id}>
            <div className="flex items-start justify-between">
              <div className="rounded-xl bg-teal-50 p-3 text-teal-700">
                <FileText />
              </div>
              {resume.is_default && <Badge>默认简历</Badge>}
            </div>
            <h3 className="mt-4 font-bold">{resume.name}</h3>
            <p className="mt-1 text-sm text-[var(--muted)]">
              {resume.version || "未命名版本"} ·{" "}
              {(resume.file_size / 1024).toFixed(1)} KB
            </p>
            <p className="mt-1 truncate text-xs text-[var(--muted)]">
              {resume.original_filename}
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              <button
                className="text-sm font-semibold text-teal-600"
                onClick={() =>
                  void apiDownload(
                    `/resumes/${resume.id}/download`,
                    resume.original_filename,
                  )
                }
              >
                <Download className="inline" size={15} /> 下载
              </button>
              {!resume.is_default && (
                <button
                  className="text-sm font-semibold text-amber-600"
                  onClick={() =>
                    update.mutate({ id: resume.id, isDefault: true })
                  }
                >
                  <Star className="inline" size={15} /> 设为默认
                </button>
              )}
              <button
                className="text-sm font-semibold text-rose-600"
                onClick={() => remove.mutate(resume.id)}
              >
                <Trash2 className="inline" size={15} /> 删除
              </button>
            </div>
          </article>
        ))}
      </div>
      {!resumes.data?.total && <EmptyState text="暂无简历版本" />}
    </div>
  );
}

export function AlertsManager() {
  const authenticated = useHasToken();
  const client = useQueryClient();
  const [message, setMessage] = useState("");
  const alerts = useQuery({
    enabled: authenticated,
    queryKey: ["job-alerts"],
    queryFn: () => apiFetch<ApiPage<JobAlert>>("/job-alerts?page_size=100"),
  });
  const refresh = () =>
    void client.invalidateQueries({ queryKey: ["job-alerts"] });
  const create = useMutation({
    mutationFn: (payload: object) =>
      apiFetch<JobAlert>("/job-alerts", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: refresh,
  });
  const toggle = useMutation({
    mutationFn: ({ id, active }: { id: number; active: boolean }) =>
      apiFetch<JobAlert>(`/job-alerts/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: active }),
      }),
    onSuccess: refresh,
  });
  const remove = useMutation({
    mutationFn: (id: number) =>
      apiFetch<void>(`/job-alerts/${id}`, { method: "DELETE" }),
    onSuccess: refresh,
  });
  const run = useMutation({
    mutationFn: (id: number) =>
      apiFetch<{ matched: number; notifications_created: number }>(
        `/job-alerts/${id}/run`,
        { method: "POST" },
      ),
    onSuccess: (result) =>
      setMessage(
        `匹配 ${result.matched} 个已核验岗位，新增 ${result.notifications_created} 条通知`,
      ),
  });
  if (!authenticated) return <LoginRequired />;
  if (alerts.isPending) return <LoadingState text="正在加载岗位订阅…" />;
  return (
    <div className="space-y-5">
      <form
        className="card grid gap-3 p-5 md:grid-cols-5"
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          create.mutate({
            name: data.get("name"),
            criteria: {
              keyword: data.get("keyword"),
              city: data.get("city"),
              category: data.get("category"),
            },
            frequency: data.get("frequency"),
          });
          event.currentTarget.reset();
        }}
      >
        <input className="field" name="name" placeholder="订阅名称" required />
        <input className="field" name="keyword" placeholder="岗位关键词" />
        <input className="field" name="city" placeholder="目标城市" />
        <input className="field" name="category" placeholder="岗位类别" />
        <div className="flex gap-2">
          <select className="field" name="frequency" defaultValue="daily">
            <option value="daily">每天</option>
            <option value="weekly">每周</option>
            <option value="instant">即时</option>
          </select>
          <button className="btn-primary">创建</button>
        </div>
      </form>
      {(message || create.error || run.error) && (
        <p
          className={`text-sm ${create.error || run.error ? "text-rose-600" : "text-teal-600"}`}
        >
          {create.error?.message ?? run.error?.message ?? message}
        </p>
      )}
      <div className="grid gap-4 lg:grid-cols-2">
        {alerts.data?.items.map((alert) => (
          <article className="card p-5" key={alert.id}>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <BellRing className="text-teal-600" />
                <div>
                  <h3 className="font-bold">{alert.name}</h3>
                  <p className="text-xs text-[var(--muted)]">
                    {alert.frequency} · 下次运行{" "}
                    {alert.next_run_at?.slice(0, 10) ?? "待安排"}
                  </p>
                </div>
              </div>
              <Badge tone={alert.is_active ? "teal" : "slate"}>
                {alert.is_active ? "运行中" : "已停用"}
              </Badge>
            </div>
            <p className="mt-4 rounded-lg bg-slate-50 p-3 text-sm dark:bg-slate-800">
              {Object.entries(alert.criteria)
                .filter(([, value]) => value)
                .map(([key, value]) => `${key}: ${String(value)}`)
                .join(" · ") || "不限条件"}
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <button
                className="text-sm font-semibold text-teal-600"
                disabled={!alert.is_active}
                onClick={() => run.mutate(alert.id)}
              >
                <Play className="inline" size={15} /> 立即匹配
              </button>
              <button
                className="text-sm font-semibold text-amber-600"
                onClick={() =>
                  toggle.mutate({ id: alert.id, active: !alert.is_active })
                }
              >
                {alert.is_active ? "暂停" : "启用"}
              </button>
              <button
                className="text-sm font-semibold text-rose-600"
                onClick={() => remove.mutate(alert.id)}
              >
                删除
              </button>
            </div>
          </article>
        ))}
      </div>
      {!alerts.data?.total && <EmptyState text="暂无岗位订阅" />}
    </div>
  );
}
