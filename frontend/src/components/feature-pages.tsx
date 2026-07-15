"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarDays, Clock3, MapPin, Trash2, Trophy } from "lucide-react";
import {
  Badge,
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/status";
import { apiFetch } from "@/lib/api";
import { useHasToken } from "@/lib/auth";
import type {
  ApiPage,
  Application,
  Favorite,
  Interview,
  Job,
  Offer,
  Resume,
} from "@/lib/types";

const applicationLabels: Record<string, string> = {
  planned: "准备投递",
  applied: "已投递",
  written_test: "笔试",
  interview: "面试",
  offer: "Offer",
  rejected: "未通过",
  withdrawn: "已撤回",
  completed: "已完成",
};
const nextStatuses: Record<string, string[]> = {
  planned: ["applied", "withdrawn"],
  applied: ["written_test", "interview", "rejected", "withdrawn"],
  written_test: ["interview", "rejected", "withdrawn"],
  interview: ["offer", "rejected", "withdrawn"],
  offer: ["completed", "withdrawn"],
};

function LoginRequired() {
  return (
    <EmptyState
      action={
        <Link className="btn-primary" href="/login">
          前往登录
        </Link>
      }
      text="登录后即可管理你的个人求职记录"
    />
  );
}

function useJobs(enabled: boolean) {
  return useQuery({
    enabled,
    queryKey: ["jobs"],
    queryFn: () => apiFetch<ApiPage<Job>>("/jobs?page_size=100"),
  });
}

export function Applications() {
  const authenticated = useHasToken();
  const client = useQueryClient();
  const [message, setMessage] = useState("");
  const apps = useQuery({
    enabled: authenticated,
    queryKey: ["applications"],
    queryFn: () =>
      apiFetch<ApiPage<Application>>("/applications?page_size=100"),
  });
  const jobs = useQuery({
    enabled: authenticated,
    queryKey: ["jobs"],
    queryFn: () => apiFetch<ApiPage<Job>>("/jobs?page_size=100"),
  });
  const resumes = useQuery({
    enabled: authenticated,
    queryKey: ["resumes"],
    queryFn: () => apiFetch<ApiPage<Resume>>("/resumes?page_size=100"),
  });
  const refresh = () => {
    void client.invalidateQueries({ queryKey: ["applications"] });
    void client.invalidateQueries({ queryKey: ["dashboard"] });
  };
  const create = useMutation({
    mutationFn: (payload: object) =>
      apiFetch<Application>("/applications", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      setMessage("投递记录已创建");
      refresh();
    },
  });
  const update = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      apiFetch<Application>(`/applications/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
    onSuccess: refresh,
  });
  const remove = useMutation({
    mutationFn: (id: number) =>
      apiFetch<void>(`/applications/${id}`, { method: "DELETE" }),
    onSuccess: refresh,
  });
  const jobMap = useMemo(
    () => new Map(jobs.data?.items.map((job) => [job.id, job]) ?? []),
    [jobs.data],
  );
  if (!authenticated) return <LoginRequired />;
  if (apps.isPending || jobs.isPending)
    return <LoadingState text="正在加载投递记录…" />;
  if (apps.isError) return <ErrorState text={apps.error.message} />;
  return (
    <div className="space-y-5">
      <form
        className="card grid gap-3 p-5 md:grid-cols-4"
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          create.mutate({
            job_id: Number(data.get("job_id")),
            resume_id: data.get("resume_id")
              ? Number(data.get("resume_id"))
              : null,
            status: "planned",
            channel: data.get("channel"),
          });
          event.currentTarget.reset();
        }}
      >
        <label>
          <span className="mb-1 block text-xs text-[var(--muted)]">岗位</span>
          <select className="field" name="job_id" required>
            <option value="">选择岗位</option>
            {jobs.data?.items.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span className="mb-1 block text-xs text-[var(--muted)]">
            简历版本
          </span>
          <select className="field" name="resume_id">
            <option value="">暂不关联</option>
            {resumes.data?.items.map((resume) => (
              <option key={resume.id} value={resume.id}>
                {resume.name} {resume.version}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span className="mb-1 block text-xs text-[var(--muted)]">渠道</span>
          <input
            className="field"
            name="channel"
            placeholder="企业官网 / 内推"
          />
        </label>
        <button className="btn-primary self-end" disabled={create.isPending}>
          新增投递
        </button>
      </form>
      {(message || create.error) && (
        <p
          className={`text-sm ${create.error ? "text-rose-600" : "text-teal-600"}`}
        >
          {create.error?.message ?? message}
        </p>
      )}
      {apps.data?.items.length ? (
        <div className="space-y-3">
          {apps.data.items.map((item) => {
            const job = jobMap.get(item.job_id);
            return (
              <div
                className="card flex flex-col justify-between gap-4 p-5 lg:flex-row lg:items-center"
                key={item.id}
              >
                <div>
                  <h3 className="font-bold">
                    {job?.title ?? `岗位 #${item.job_id}`}
                  </h3>
                  <p className="text-sm text-[var(--muted)]">
                    {item.channel || "未记录渠道"} ·{" "}
                    {item.applied_at?.slice(0, 10) ?? "尚未投递"}
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge>{applicationLabels[item.status] ?? item.status}</Badge>
                  {nextStatuses[item.status]?.length ? (
                    <select
                      aria-label="更新投递状态"
                      className="field w-auto py-2"
                      defaultValue=""
                      onChange={(e) => {
                        if (e.target.value)
                          update.mutate({
                            id: item.id,
                            status: e.target.value,
                          });
                      }}
                    >
                      <option value="">推进状态</option>
                      {nextStatuses[item.status].map((status) => (
                        <option key={status} value={status}>
                          {applicationLabels[status]}
                        </option>
                      ))}
                    </select>
                  ) : null}
                  <button
                    aria-label="删除投递记录"
                    className="rounded-lg p-2 text-rose-500 hover:bg-rose-50"
                    onClick={() => remove.mutate(item.id)}
                    type="button"
                  >
                    <Trash2 size={17} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState text="还没有投递记录，请从上方添加" />
      )}
    </div>
  );
}

export function Calendar() {
  const authenticated = useHasToken();
  const client = useQueryClient();
  const interviews = useQuery({
    enabled: authenticated,
    queryKey: ["interviews"],
    queryFn: () => apiFetch<ApiPage<Interview>>("/interviews?page_size=100"),
  });
  const apps = useQuery({
    enabled: authenticated,
    queryKey: ["applications"],
    queryFn: () =>
      apiFetch<ApiPage<Application>>("/applications?page_size=100"),
  });
  const create = useMutation({
    mutationFn: (payload: object) =>
      apiFetch<Interview>("/interviews", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () =>
      void client.invalidateQueries({ queryKey: ["interviews"] }),
  });
  const update = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      apiFetch<Interview>(`/interviews/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
    onSuccess: () =>
      void client.invalidateQueries({ queryKey: ["interviews"] }),
  });
  if (!authenticated) return <LoginRequired />;
  if (interviews.isPending || apps.isPending)
    return <LoadingState text="正在整理校招日历…" />;
  return (
    <div className="space-y-5">
      <form
        className="card grid gap-3 p-5 md:grid-cols-4"
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          create.mutate({
            application_id: Number(data.get("application_id")),
            interview_type: data.get("interview_type"),
            scheduled_at: new Date(
              String(data.get("scheduled_at")),
            ).toISOString(),
            location: data.get("location"),
          });
          event.currentTarget.reset();
        }}
      >
        <select className="field" name="application_id" required>
          <option value="">选择投递记录</option>
          {apps.data?.items.map((item) => (
            <option key={item.id} value={item.id}>
              投递 #{item.id}
            </option>
          ))}
        </select>
        <input
          className="field"
          name="interview_type"
          placeholder="面试类型"
          required
        />
        <input
          className="field"
          name="scheduled_at"
          type="datetime-local"
          required
        />
        <div className="flex gap-2">
          <input
            className="field"
            name="location"
            placeholder="地点/会议链接"
          />
          <button className="btn-primary">添加</button>
        </div>
      </form>
      {create.error && (
        <p className="text-sm text-rose-600">{create.error.message}</p>
      )}
      <div className="grid gap-4 lg:grid-cols-2">
        {interviews.data?.items.map((item) => (
          <div className="card flex gap-4 p-5" key={item.id}>
            <div className="flex h-14 w-14 shrink-0 flex-col items-center justify-center rounded-xl bg-teal-50 text-teal-700">
              <CalendarDays />
              <span className="text-xs">面试</span>
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <h3 className="font-bold">{item.interview_type}</h3>
                <Badge tone={item.status === "scheduled" ? "amber" : "teal"}>
                  {item.status}
                </Badge>
              </div>
              <p className="mt-2 flex items-center gap-1 text-xs text-[var(--muted)]">
                <Clock3 size={13} />
                {new Date(item.scheduled_at).toLocaleString("zh-CN")}
              </p>
              <p className="mt-1 flex items-center gap-1 text-xs text-[var(--muted)]">
                <MapPin size={13} />
                {item.location || "待确定"}
              </p>
              {item.status === "scheduled" && (
                <div className="mt-3 flex gap-2">
                  <button
                    className="text-xs font-semibold text-teal-600"
                    onClick={() =>
                      update.mutate({ id: item.id, status: "completed" })
                    }
                  >
                    标记完成
                  </button>
                  <button
                    className="text-xs font-semibold text-rose-600"
                    onClick={() =>
                      update.mutate({ id: item.id, status: "cancelled" })
                    }
                  >
                    取消
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      {!interviews.data?.total && <EmptyState text="暂无面试安排" />}
    </div>
  );
}

export function Favorites() {
  const authenticated = useHasToken();
  const client = useQueryClient();
  const jobs = useJobs(authenticated);
  const favorites = useQuery({
    enabled: authenticated,
    queryKey: ["favorites"],
    queryFn: () => apiFetch<ApiPage<Favorite>>("/favorites?page_size=100"),
  });
  const remove = useMutation({
    mutationFn: (jobId: number) =>
      apiFetch<void>(`/favorites/${jobId}`, { method: "DELETE" }),
    onSuccess: () => void client.invalidateQueries({ queryKey: ["favorites"] }),
  });
  const jobMap = new Map(jobs.data?.items.map((job) => [job.id, job]) ?? []);
  if (!authenticated) return <LoginRequired />;
  if (favorites.isPending || jobs.isPending)
    return <LoadingState text="正在加载收藏…" />;
  if (!favorites.data?.total)
    return (
      <EmptyState
        action={
          <Link className="btn-primary" href="/jobs">
            浏览岗位
          </Link>
        }
        text="暂无收藏岗位"
      />
    );
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {favorites.data.items.map((favorite) => {
        const job = jobMap.get(favorite.job_id);
        return (
          <div className="card p-5" key={favorite.id}>
            <Badge>岗位</Badge>
            <h3 className="mt-3 text-lg font-bold">
              {job?.title ?? `岗位 #${favorite.job_id}`}
            </h3>
            <p className="mt-1 text-sm text-[var(--muted)]">
              {job?.work_cities ?? "城市待核验"}
            </p>
            <p className="mt-4 text-xs">
              {job?.education_requirement ?? "学历要求待核验"}
            </p>
            <button
              className="mt-5 text-sm font-semibold text-rose-600"
              onClick={() => remove.mutate(favorite.job_id)}
            >
              取消收藏
            </button>
          </div>
        );
      })}
    </div>
  );
}

export function Offers() {
  const authenticated = useHasToken();
  const client = useQueryClient();
  const offers = useQuery({
    enabled: authenticated,
    queryKey: ["offers"],
    queryFn: () => apiFetch<ApiPage<Offer>>("/offers?page_size=100"),
  });
  const apps = useQuery({
    enabled: authenticated,
    queryKey: ["applications"],
    queryFn: () =>
      apiFetch<ApiPage<Application>>("/applications?page_size=100"),
  });
  const create = useMutation({
    mutationFn: (payload: object) =>
      apiFetch<Offer>("/offers", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => void client.invalidateQueries({ queryKey: ["offers"] }),
  });
  const update = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      apiFetch<Offer>(`/offers/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
    onSuccess: () => void client.invalidateQueries({ queryKey: ["offers"] }),
  });
  if (!authenticated) return <LoginRequired />;
  if (offers.isPending || apps.isPending)
    return <LoadingState text="正在加载 Offer…" />;
  return (
    <div className="space-y-5">
      <form
        className="card grid gap-3 p-5 md:grid-cols-4"
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          create.mutate({
            application_id: Number(data.get("application_id")),
            received_at: data.get("received_at"),
            response_deadline: data.get("response_deadline") || null,
            compensation: data.get("compensation"),
          });
          event.currentTarget.reset();
        }}
      >
        <select className="field" name="application_id" required>
          <option value="">选择投递记录</option>
          {apps.data?.items.map((item) => (
            <option key={item.id} value={item.id}>
              投递 #{item.id}
            </option>
          ))}
        </select>
        <input className="field" name="received_at" type="date" required />
        <input className="field" name="response_deadline" type="date" />
        <div className="flex gap-2">
          <input className="field" name="compensation" placeholder="薪酬备注" />
          <button className="btn-primary">记录</button>
        </div>
      </form>
      {create.error && (
        <p className="text-sm text-rose-600">{create.error.message}</p>
      )}
      <div className="grid gap-4 lg:grid-cols-2">
        {offers.data?.items.map((item) => (
          <div className="card border-l-4 border-teal-500 p-6" key={item.id}>
            <div className="flex items-center gap-3 text-teal-600">
              <Trophy />
              <b>Offer #{item.id}</b>
              <Badge tone={item.status === "accepted" ? "teal" : "amber"}>
                {item.status}
              </Badge>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <Info t="薪酬" v={item.compensation || "待补充"} />
              <Info t="收到日期" v={item.received_at} />
              <Info t="回复期限" v={item.response_deadline || "未设置"} />
            </div>
            {item.status === "pending" && (
              <div className="mt-4 flex gap-3">
                <button
                  className="btn-primary"
                  onClick={() =>
                    update.mutate({ id: item.id, status: "accepted" })
                  }
                >
                  接受
                </button>
                <button
                  className="text-sm font-semibold text-rose-600"
                  onClick={() =>
                    update.mutate({ id: item.id, status: "declined" })
                  }
                >
                  婉拒
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      {!offers.data?.total && <EmptyState text="暂无 Offer 记录" />}
    </div>
  );
}

function Info({ t, v }: { t: string; v: string }) {
  return (
    <div className="rounded-xl bg-slate-50 p-3 dark:bg-slate-800">
      <p className="text-xs text-[var(--muted)]">{t}</p>
      <b>{v}</b>
    </div>
  );
}
