"use client";

import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCheck, RefreshCw } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useHasToken } from "@/lib/auth";
import type { ApiPage, Notification } from "@/lib/types";

export function NotificationMenu() {
  const authenticated = useHasToken();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const notifications = useQuery({
    enabled: authenticated,
    queryKey: ["notifications"],
    queryFn: () =>
      apiFetch<ApiPage<Notification>>("/notifications?page_size=8"),
    refetchInterval: 60_000,
  });
  const unread =
    notifications.data?.items.filter((item) => !item.is_read).length ?? 0;
  const readAll = useMutation({
    mutationFn: () =>
      apiFetch<void>("/notifications/read-all", { method: "PATCH" }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });
  const runReminders = useMutation({
    mutationFn: () =>
      apiFetch<{ created: number }>("/reminders/run", { method: "POST" }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  useEffect(() => {
    const close = (event: MouseEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  return (
    <div className="relative" ref={containerRef}>
      <button
        aria-expanded={open}
        aria-label={`查看通知${unread ? `，${unread} 条未读` : ""}`}
        className="relative rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
        onClick={() => setOpen((value) => !value)}
        type="button"
      >
        <Bell aria-hidden="true" size={20} />
        {unread > 0 && (
          <span className="absolute top-0.5 right-0.5 min-w-4 rounded-full bg-rose-500 px-1 text-center text-[10px] font-bold text-white">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <section className="card absolute top-12 right-0 z-50 w-[min(22rem,calc(100vw-2rem))] overflow-hidden shadow-xl">
          <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3">
            <div>
              <p className="font-bold">通知中心</p>
              <p className="text-xs text-[var(--muted)]">
                截止、面试与 Offer 提醒
              </p>
            </div>
            <div className="flex gap-1">
              <button
                aria-label="立即检查提醒"
                className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
                disabled={!authenticated || runReminders.isPending}
                onClick={() => runReminders.mutate()}
                type="button"
              >
                <RefreshCw
                  aria-hidden="true"
                  className={runReminders.isPending ? "animate-spin" : ""}
                  size={17}
                />
              </button>
              <button
                aria-label="全部标为已读"
                className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
                disabled={!unread || readAll.isPending}
                onClick={() => readAll.mutate()}
                type="button"
              >
                <CheckCheck aria-hidden="true" size={18} />
              </button>
            </div>
          </div>
          {!authenticated ? (
            <p className="p-5 text-sm text-[var(--muted)]">
              登录后查看个人提醒。
            </p>
          ) : notifications.isPending ? (
            <p className="p-5 text-sm text-[var(--muted)]">正在加载通知…</p>
          ) : notifications.isError ? (
            <p className="p-5 text-sm text-rose-600">
              通知加载失败，请稍后重试。
            </p>
          ) : notifications.data?.items.length ? (
            <ul className="max-h-80 divide-y divide-[var(--border)] overflow-y-auto">
              {notifications.data.items.map((item) => (
                <li className="px-4 py-3" key={item.id}>
                  <div className="flex items-start gap-2">
                    <span
                      aria-hidden="true"
                      className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${item.is_read ? "bg-slate-300" : "bg-teal-500"}`}
                    />
                    <div>
                      <p className="text-sm font-semibold">{item.title}</p>
                      <p className="mt-1 text-xs text-[var(--muted)]">
                        {item.content}
                      </p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="p-5 text-sm text-[var(--muted)]">暂无通知。</p>
          )}
        </section>
      )}
    </div>
  );
}
