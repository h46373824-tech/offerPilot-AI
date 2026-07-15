"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { useHasToken } from "@/lib/auth";
import type { ApiPage, CurrentUser } from "@/lib/types";

type AuditLog = {
  id: number;
  action: string;
  created_at: string;
};

type ProfilePayload = {
  full_name: string;
  graduation_year: number;
  education_level: string;
  target_cities: string;
  notifications_enabled: boolean;
};

const actionLabels: Record<string, string> = {
  "profile.update": "更新个人设置",
  "resume.upload": "上传简历",
  "resume.update": "更新简历",
  "resume.delete": "删除简历",
  "application.create": "创建投递",
  "application.update": "更新投递",
  "application.delete": "删除投递",
  "interview.create": "创建面试",
  "interview.update": "更新面试",
  "offer.create": "登记 Offer",
  "offer.update": "更新 Offer",
};

export function SettingsForm() {
  const authenticated = useHasToken();
  const user = useQuery({
    enabled: authenticated,
    queryKey: ["current-user"],
    queryFn: () => apiFetch<CurrentUser>("/auth/me"),
  });

  if (!authenticated) {
    return <Notice text="请先登录后管理个人设置。" />;
  }
  if (user.isPending) return <Notice text="正在加载设置…" />;
  if (user.isError || !user.data) {
    return <Notice error text="个人设置加载失败，请刷新重试。" />;
  }

  return <SettingsContent user={user.data} />;
}

function SettingsContent({ user }: { user: CurrentUser }) {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState("");
  const auditLogs = useQuery({
    queryKey: ["audit-logs"],
    queryFn: () => apiFetch<ApiPage<AuditLog>>("/audit-logs?page_size=8"),
  });
  const save = useMutation({
    mutationFn: (payload: ProfilePayload) =>
      apiFetch<CurrentUser>("/auth/me", {
        method: "PATCH",
        body: JSON.stringify(payload),
      }),
    onError: (error) => setMessage((error as Error).message),
    onSuccess: () => {
      setMessage("设置已保存");
      void queryClient.invalidateQueries({ queryKey: ["current-user"] });
      void queryClient.invalidateQueries({ queryKey: ["audit-logs"] });
    },
  });

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <aside className="card h-fit p-4">
        <p className="rounded-lg bg-teal-50 px-3 py-2 text-sm font-bold text-teal-700 dark:bg-teal-950 dark:text-teal-300">
          个人资料与求职偏好
        </p>
        <p className="mt-3 px-3 text-xs leading-5 text-[var(--muted)]">
          这些信息用于个性化岗位订阅与提醒，不会写入公开的 Demo 数据。
        </p>
      </aside>
      <div className="space-y-5 lg:col-span-2">
        <form
          className="card space-y-5 p-6"
          onSubmit={(event) => {
            event.preventDefault();
            setMessage("");
            const data = new FormData(event.currentTarget);
            save.mutate({
              full_name: String(data.get("full_name")),
              graduation_year: Number(data.get("graduation_year")),
              education_level: String(data.get("education_level")),
              target_cities: String(data.get("target_cities")),
              notifications_enabled: data.get("notifications_enabled") === "on",
            });
          }}
        >
          <div>
            <label
              className="mb-2 block text-sm font-semibold"
              htmlFor="full-name"
            >
              姓名
            </label>
            <input
              className="field"
              defaultValue={user.full_name}
              id="full-name"
              name="full_name"
              required
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label
                className="mb-2 block text-sm font-semibold"
                htmlFor="graduation-year"
              >
                毕业年份
              </label>
              <select
                className="field"
                defaultValue={String(user.graduation_year ?? 2027)}
                id="graduation-year"
                name="graduation_year"
              >
                <option>2027</option>
                <option>2028</option>
                <option>2029</option>
              </select>
            </div>
            <div>
              <label
                className="mb-2 block text-sm font-semibold"
                htmlFor="education-level"
              >
                最高学历
              </label>
              <select
                className="field"
                defaultValue={user.education_level ?? "本科"}
                id="education-level"
                name="education_level"
              >
                <option>专科</option>
                <option>本科</option>
                <option>硕士</option>
                <option>博士</option>
              </select>
            </div>
          </div>
          <div>
            <label
              className="mb-2 block text-sm font-semibold"
              htmlFor="target-cities"
            >
              目标城市
            </label>
            <input
              className="field"
              defaultValue={user.target_cities ?? ""}
              id="target-cities"
              name="target_cities"
              placeholder="例如：北京、上海、深圳"
            />
          </div>
          <label className="flex items-center gap-3 text-sm">
            <input
              defaultChecked={user.notifications_enabled}
              name="notifications_enabled"
              type="checkbox"
            />
            接收岗位截止、面试和 Offer 流程提醒
          </label>
          <div className="flex items-center gap-3">
            <button
              className="btn-primary"
              disabled={save.isPending}
              type="submit"
            >
              {save.isPending ? "保存中…" : "保存设置"}
            </button>
            {message && (
              <span
                className={`text-sm ${save.isError ? "text-rose-600" : "text-teal-600"}`}
              >
                {message}
              </span>
            )}
          </div>
        </form>

        <section className="card p-6">
          <h2 className="font-bold">最近操作记录</h2>
          <p className="mb-4 text-xs text-[var(--muted)]">
            关键求职流程变更会记录在个人审计日志中。
          </p>
          {auditLogs.isPending ? (
            <p className="text-sm text-[var(--muted)]">正在加载记录…</p>
          ) : auditLogs.data?.items.length ? (
            <ul className="divide-y divide-[var(--border)]">
              {auditLogs.data.items.map((log) => (
                <li
                  className="flex items-center justify-between gap-4 py-3 text-sm"
                  key={log.id}
                >
                  <span>{actionLabels[log.action] ?? log.action}</span>
                  <time className="shrink-0 text-xs text-[var(--muted)]">
                    {new Date(log.created_at).toLocaleString("zh-CN")}
                  </time>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--muted)]">暂无操作记录。</p>
          )}
        </section>
      </div>
    </div>
  );
}

function Notice({ error = false, text }: { error?: boolean; text: string }) {
  return (
    <div
      className={`card p-8 text-sm ${error ? "text-rose-600" : "text-[var(--muted)]"}`}
    >
      {text}
    </div>
  );
}
