"use client";

import Link from "next/link";
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
const metrics = [
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
              <AreaChart data={trend}>
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
                  data={industry}
                  dataKey="v"
                  nameKey="n"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                >
                  {industry.map((x, i) => (
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
              {applications.map((r) => (
                <tr key={r[0] + r[1]}>
                  {r.map((v, i) => (
                    <td key={v}>
                      {i === 2 ? (
                        <span className="rounded-full bg-teal-50 px-2 py-1 text-xs text-teal-700 dark:bg-teal-950 dark:text-teal-300">
                          {v}
                        </span>
                      ) : (
                        v
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
