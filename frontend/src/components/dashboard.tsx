"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Building2,
  CalendarClock,
  FileCheck2,
  GraduationCap,
  Handshake,
  Sparkles,
  Trophy,
  Users,
} from "lucide-react";
import { applications } from "@/data/demo";
import { ErrorState, LoadingState } from "@/components/status";
import { apiFetch } from "@/lib/api";
import { useHasToken } from "@/lib/auth";
import type { DashboardStats } from "@/lib/types";
const demoMetrics = [
  ["已开放企业数", "30", Building2, "text-blue-600 bg-blue-50"],
  ["专科可投企业数", "12", GraduationCap, "text-violet-600 bg-violet-50"],
  ["本科可投企业数", "28", Users, "text-teal-600 bg-teal-50"],
  ["今日新增岗位数", "8", Sparkles, "text-amber-600 bg-amber-50"],
  ["已投递数量", "16", FileCheck2, "text-cyan-600 bg-cyan-50"],
  ["面试数量", "4", Handshake, "text-fuchsia-600 bg-fuchsia-50"],
  ["Offer 数量", "1", Trophy, "text-emerald-600 bg-emerald-50"],
  ["即将截止岗位", "7", CalendarClock, "text-rose-600 bg-rose-50"],
] as const;
const trend = [
  { d: "7/8", v: 1 },
  { d: "7/9", v: 3 },
  { d: "7/10", v: 2 },
  { d: "7/11", v: 5 },
  { d: "7/12", v: 4 },
  { d: "7/13", v: 7 },
  { d: "7/14", v: 6 },
];
const industry = [
  { n: "互联网", v: 26 },
  { n: "AI", v: 20 },
  { n: "制造", v: 18 },
  { n: "金融", v: 16 },
  { n: "其他", v: 20 },
];
const colors = ["#0f766e", "#2563eb", "#7c3aed", "#d97706", "#64748b"];
export function DashboardView() {
  const authenticated = useHasToken();
  const statsQuery = useQuery({
    enabled: authenticated,
    queryKey: ["dashboard", "stats"],
    queryFn: () => apiFetch<DashboardStats>("/dashboard/stats"),
  });
  if (authenticated && statsQuery.isPending)
    return <LoadingState text="正在汇总求职数据…" />;
  if (authenticated && statsQuery.isError)
    return (
      <ErrorState
        action={
          <button
            className="btn-primary"
            onClick={() => void statsQuery.refetch()}
            type="button"
          >
            重新加载
          </button>
        }
        text={statsQuery.error.message}
      />
    );
  const stats = statsQuery.data;
  const metrics = stats
    ? ([
        [
          "已开放企业数",
          String(stats.open_companies),
          Building2,
          "text-blue-600 bg-blue-50",
        ],
        [
          "专科可投企业数",
          String(stats.college_companies),
          GraduationCap,
          "text-violet-600 bg-violet-50",
        ],
        [
          "本科可投企业数",
          String(stats.bachelor_companies),
          Users,
          "text-teal-600 bg-teal-50",
        ],
        [
          "今日新增岗位数",
          String(stats.new_jobs_today),
          Sparkles,
          "text-amber-600 bg-amber-50",
        ],
        [
          "已投递数量",
          String(stats.applications),
          FileCheck2,
          "text-cyan-600 bg-cyan-50",
        ],
        [
          "面试数量",
          String(stats.interviews),
          Handshake,
          "text-fuchsia-600 bg-fuchsia-50",
        ],
        [
          "Offer 数量",
          String(stats.offers),
          Trophy,
          "text-emerald-600 bg-emerald-50",
        ],
        [
          "即将截止岗位",
          String(stats.expiring_jobs),
          CalendarClock,
          "text-rose-600 bg-rose-50",
        ],
      ] as const)
    : demoMetrics;
  const trendData =
    stats?.application_trend.map((point) => ({
      d: point.date.slice(5),
      v: point.count,
    })) ?? trend;
  const industryData =
    stats?.industry_distribution.map((item) => ({
      n: item.industry,
      v: item.count,
    })) ?? industry;
  const recent = stats?.recent_applications;
  return (
    <>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map(([label, value, Icon, color]) => (
          <div className="card flex items-center gap-4 p-5" key={label}>
            <div className={`rounded-xl p-3 ${color}`}>
              <Icon aria-hidden="true" size={23} />
            </div>
            <div>
              <div className="text-2xl font-black">{value}</div>
              <div className="text-sm text-[var(--muted)]">{label}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-5 grid gap-5 xl:grid-cols-3">
        <div className="card p-5 xl:col-span-2">
          <h2 className="font-bold">投递趋势</h2>
          <p className="mb-4 text-xs text-[var(--muted)]">近 7 天投递数量</p>
          <div aria-label="近 7 天投递趋势图" className="h-72" role="img">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0f766e" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#0f766e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="d" />
                <YAxis />
                <Tooltip />
                <Area
                  dataKey="v"
                  stroke="#0f766e"
                  fill="url(#fill)"
                  strokeWidth={3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card p-5">
          <h2 className="font-bold">行业分布</h2>
          <p className="mb-4 text-xs text-[var(--muted)]">收藏与投递岗位占比</p>
          <div
            aria-label="收藏与投递岗位行业分布图"
            className="h-72"
            role="img"
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={industryData}
                  dataKey="v"
                  nameKey="n"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                >
                  {industryData.map((x, i) => (
                    <Cell key={x.n} fill={colors[i]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      <div className="card mt-5 overflow-hidden">
        <div className="flex items-center justify-between gap-3 p-5">
          <div>
            <h2 className="font-bold">最近投递记录</h2>
            <p className="text-xs text-[var(--muted)]">Demo 示例数据</p>
          </div>
          <Link
            href="/applications"
            className="shrink-0 text-sm font-semibold text-teal-600 dark:text-teal-400"
          >
            查看全部
          </Link>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>企业</th>
                <th>岗位</th>
                <th>进度</th>
                <th>投递日期</th>
              </tr>
            </thead>
            <tbody>
              {recent
                ? recent.map((record) => (
                    <tr key={record.id}>
                      <td>{record.company_name}</td>
                      <td>{record.job_title}</td>
                      <td>
                        <span className="rounded-full bg-teal-50 px-2 py-1 text-xs text-teal-700 dark:bg-teal-950 dark:text-teal-300">
                          {record.status}
                        </span>
                      </td>
                      <td>{record.applied_at?.slice(0, 10) ?? "未记录"}</td>
                    </tr>
                  ))
                : applications.map((record) => (
                    <tr key={record[0] + record[1]}>
                      {record.map((value, index) => (
                        <td key={value}>
                          {index === 2 ? (
                            <span className="rounded-full bg-teal-50 px-2 py-1 text-xs text-teal-700 dark:bg-teal-950 dark:text-teal-300">
                              {value}
                            </span>
                          ) : (
                            value
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
