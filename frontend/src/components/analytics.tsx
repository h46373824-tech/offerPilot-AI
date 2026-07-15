"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ErrorState, LoadingState } from "@/components/status";
import { apiFetch } from "@/lib/api";
import { useHasToken } from "@/lib/auth";
import type { ApiPage, Application, DashboardStats } from "@/lib/types";

const statusLabels: Record<string, string> = {
  saved: "待投递",
  applied: "已投递",
  screening: "筛选中",
  interview: "面试中",
  offer: "已获 Offer",
  rejected: "未通过",
  withdrawn: "已撤回",
};

export function Analytics() {
  const authenticated = useHasToken();
  const dashboard = useQuery({
    enabled: authenticated,
    queryKey: ["dashboard-stats"],
    queryFn: () => apiFetch<DashboardStats>("/dashboard/stats"),
  });
  const applications = useQuery({
    enabled: authenticated,
    queryKey: ["applications"],
    queryFn: () =>
      apiFetch<ApiPage<Application>>("/applications?page_size=100"),
  });
  const statusData = useMemo(() => {
    const counts = new Map<string, number>();
    for (const item of applications.data?.items ?? []) {
      counts.set(item.status, (counts.get(item.status) ?? 0) + 1);
    }
    return Array.from(counts, ([status, count]) => ({
      name: statusLabels[status] ?? status,
      数量: count,
    }));
  }, [applications.data]);

  if (!authenticated) {
    return (
      <div className="card p-8 text-sm text-[var(--muted)]">
        登录后查看基于个人投递数据生成的分析。
      </div>
    );
  }
  if (dashboard.isPending || applications.isPending) {
    return <LoadingState text="正在计算个人求职分析…" />;
  }
  if (dashboard.isError || applications.isError || !dashboard.data) {
    return <ErrorState text="分析数据加载失败，请稍后重试。" />;
  }

  const applicationCount = dashboard.data.applications;
  const interviewRate = applicationCount
    ? Math.round((dashboard.data.interviews / applicationCount) * 100)
    : 0;
  const offerRate = applicationCount
    ? Math.round((dashboard.data.offers / applicationCount) * 100)
    : 0;

  return (
    <div className="space-y-5">
      <div className="grid gap-5 lg:grid-cols-3">
        <div className="card p-5 lg:col-span-2">
          <h2 className="font-bold">投递流程分布</h2>
          <p className="mb-5 text-xs text-[var(--muted)]">
            按当前投递状态实时统计
          </p>
          {statusData.length ? (
            <div className="h-80">
              <ResponsiveContainer height="100%" width="100%">
                <BarChart data={statusData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="数量" fill="#0f766e" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex h-80 items-center justify-center text-sm text-[var(--muted)]">
              创建投递后将在这里显示流程分布。
            </div>
          )}
        </div>
        <div className="space-y-4">
          <Stat
            description={`${dashboard.data.interviews} 场面试`}
            title="面试转化率"
            value={`${interviewRate}%`}
          />
          <Stat
            description={`${dashboard.data.offers} 个 Offer`}
            title="Offer 转化率"
            value={`${offerRate}%`}
          />
          <Stat
            description="来自个人投递记录"
            title="累计投递"
            value={String(applicationCount)}
          />
        </div>
      </div>
      <section className="card p-5">
        <h2 className="font-bold">Demo 企业行业覆盖</h2>
        <p className="mb-4 text-xs text-[var(--muted)]">
          用于辅助理解当前示例岗位池，不代表实时市场规模。
        </p>
        <div className="flex flex-wrap gap-2">
          {dashboard.data.industry_distribution.map((item) => (
            <span
              className="rounded-full bg-slate-100 px-3 py-1.5 text-sm dark:bg-slate-800"
              key={item.industry}
            >
              {item.industry} · {item.count}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}

function Stat({
  description,
  title,
  value,
}: {
  description: string;
  title: string;
  value: string;
}) {
  return (
    <div className="card p-5">
      <p className="text-sm text-[var(--muted)]">{title}</p>
      <p className="mt-2 text-3xl font-black">{value}</p>
      <p className="mt-2 text-xs text-teal-600">{description}</p>
    </div>
  );
}
