"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart3,
  Bookmark,
  BriefcaseBusiness,
  Building2,
  CalendarDays,
  FileCheck2,
  FileUser,
  LayoutDashboard,
  Menu,
  Moon,
  Search,
  Settings,
  ShieldCheck,
  Siren,
  Sun,
  Trophy,
  X,
} from "lucide-react";
import { useUiStore } from "@/stores/ui";
import { NotificationMenu } from "@/components/notification-menu";
import { apiFetch } from "@/lib/api";
import { useHasToken } from "@/lib/auth";
import type { CurrentUser } from "@/lib/types";

const navigation = [
  ["/dashboard", "数据总览", LayoutDashboard],
  ["/companies", "企业库", Building2],
  ["/jobs", "岗位库", BriefcaseBusiness],
  ["/applications", "投递管理", FileCheck2],
  ["/resumes", "简历中心", FileUser],
  ["/alerts", "岗位订阅", Siren],
  ["/calendar", "校招日历", CalendarDays],
  ["/favorites", "我的收藏", Bookmark],
  ["/offers", "Offer 管理", Trophy],
  ["/analytics", "数据分析", BarChart3],
  ["/admin", "数据治理", ShieldCheck],
  ["/settings", "设置", Settings],
] as const;

const publicPaths = new Set(["/companies", "/jobs"]);

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const authenticated = useHasToken();
  const { dark, toggleDark, mobileOpen, setMobileOpen } = useUiStore();
  const user = useQuery({
    enabled: authenticated,
    queryKey: ["current-user"],
    queryFn: () => apiFetch<CurrentUser>("/auth/me"),
  });

  useEffect(() => {
    if (!mobileOpen) return;

    const previousOverflow = document.body.style.overflow;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMobileOpen(false);
    };

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", closeOnEscape);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [mobileOpen, setMobileOpen]);

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      {mobileOpen && (
        <button
          aria-label="关闭导航遮罩"
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          onClick={() => setMobileOpen(false)}
          type="button"
        />
      )}

      <aside
        aria-label="主导航"
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col overflow-y-auto border-r border-slate-800 bg-[#0b1f38] text-white transition-transform motion-reduce:transition-none ${mobileOpen ? "translate-x-0" : "-translate-x-full"} md:translate-x-0`}
      >
        <div className="flex h-18 shrink-0 items-center justify-between px-5">
          <Link
            className="text-xl font-black tracking-tight"
            href={authenticated ? "/dashboard" : "/jobs"}
            onClick={() => setMobileOpen(false)}
          >
            OfferPilot <span className="text-teal-400">AI</span>
          </Link>
          <button
            aria-label="关闭主导航"
            className="rounded-lg p-1 md:hidden"
            onClick={() => setMobileOpen(false)}
            type="button"
          >
            <X aria-hidden="true" />
          </button>
        </div>

        <div className="mx-4 mb-5 rounded-xl border border-teal-400/20 bg-teal-400/10 p-3 text-xs text-teal-100">
          <b>2027 届校招</b>
          <br />
          官方来源 · 展示核验日期
        </div>

        <nav className="space-y-1 px-3 pb-5">
          {navigation.map(([href, label, Icon]) => {
            if (!authenticated && !publicPaths.has(href)) return null;
            if (href === "/admin" && !user.data?.is_admin) return null;
            const active = pathname === href;

            return (
              <Link
                aria-current={active ? "page" : undefined}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm ${active ? "bg-teal-500 text-white" : "text-slate-300 hover:bg-white/8 hover:text-white"}`}
                href={href}
                key={href}
                onClick={() => setMobileOpen(false)}
              >
                <Icon aria-hidden="true" size={18} />
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="min-w-0 md:pl-64">
        <header className="sticky top-0 z-20 flex h-18 items-center gap-3 border-b border-[var(--border)] bg-[color:var(--card)]/90 px-4 backdrop-blur md:px-7">
          <button
            aria-expanded={mobileOpen}
            aria-label="打开主导航"
            className="rounded-lg p-1 md:hidden"
            onClick={() => setMobileOpen(true)}
            type="button"
          >
            <Menu aria-hidden="true" />
          </button>

          <label className="relative hidden max-w-md flex-1 md:block">
            <span className="sr-only">全局搜索</span>
            <Search
              aria-hidden="true"
              className="absolute top-2.5 left-3 text-slate-400"
              size={18}
            />
            <input
              className="field py-2 pl-10"
              placeholder="搜索企业、岗位或城市"
              type="search"
            />
          </label>

          <div className="ml-auto flex items-center gap-2">
            <button
              aria-label={dark ? "切换浅色模式" : "切换深色模式"}
              className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
              onClick={toggleDark}
              type="button"
            >
              {dark ? (
                <Sun aria-hidden="true" size={20} />
              ) : (
                <Moon aria-hidden="true" size={20} />
              )}
            </button>
            {authenticated ? (
              <>
                <NotificationMenu />
                <div
                  aria-label={`当前用户：${user.data?.full_name ?? "应届生用户"}`}
                  className="ml-1 flex h-9 w-9 items-center justify-center rounded-full bg-teal-600 text-sm font-bold text-white"
                  role="img"
                >
                  {(user.data?.full_name ?? "应届生").slice(0, 1)}
                </div>
              </>
            ) : (
              <Link className="btn-primary py-2" href="/login">
                登录管理求职进度
              </Link>
            )}
          </div>
        </header>

        <main className="p-4 md:p-7">{children}</main>
      </div>
    </div>
  );
}
