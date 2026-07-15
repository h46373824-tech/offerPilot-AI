"use client";
import { applications, jobs } from "@/data/demo";
import { Badge, EmptyState } from "@/components/status";
import {
  CalendarDays,
  CheckCircle2,
  Clock3,
  MapPin,
  Trophy,
} from "lucide-react";
export function Applications() {
  return (
    <div className="grid gap-4 md:grid-cols-4">
      <div className="space-y-3 md:col-span-3">
        {applications.map((r, i) => (
          <div
            key={r[0] + r[1]}
            className="card flex flex-col justify-between gap-3 p-5 sm:flex-row sm:items-center"
          >
            <div>
              <h3 className="font-bold">{r[1]}</h3>
              <p className="text-sm text-[var(--muted)]">
                {r[0]} · 投递于 {r[3]}
              </p>
            </div>
            <Badge tone={i === 2 ? "teal" : "blue"}>{r[2]}</Badge>
          </div>
        ))}
      </div>
      <div className="card h-fit p-5">
        <h3 className="font-bold">进度概览</h3>
        <div className="mt-4 space-y-3 text-sm">
          <p>
            准备投递 <b className="float-right">5</b>
          </p>
          <p>
            已投递 <b className="float-right">8</b>
          </p>
          <p>
            笔试/面试 <b className="float-right">4</b>
          </p>
          <p>
            已完成 <b className="float-right">2</b>
          </p>
        </div>
      </div>
    </div>
  );
}
export function Calendar() {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {jobs.map((r, i) => (
        <div className="card flex gap-4 p-5" key={r[0]}>
          <div className="flex h-14 w-14 shrink-0 flex-col items-center justify-center rounded-xl bg-teal-50 text-teal-700">
            <b>{r[5].slice(8)}</b>
            <span className="text-xs">{r[5].slice(5, 7)}月</span>
          </div>
          <div>
            <div className="mb-1 flex items-center gap-2">
              <h3 className="font-bold">{r[0]}</h3>
              {i < 2 && <Badge tone="amber">即将截止</Badge>}
            </div>
            <p className="text-sm text-[var(--muted)]">{r[1]}</p>
            <p className="mt-2 flex items-center gap-1 text-xs text-slate-500">
              <MapPin size={13} />
              {r[3]} <Clock3 size={13} className="ml-2" />
              截止 {r[5]}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
export function Favorites() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {jobs.slice(0, 4).map((r) => (
        <div className="card p-5" key={r[0]}>
          <Badge>岗位</Badge>
          <h3 className="mt-3 text-lg font-bold">{r[0]}</h3>
          <p className="mt-1 text-sm text-[var(--muted)]">{r[1]}</p>
          <p className="mt-4 text-xs">
            {r[3]} · {r[4]}
          </p>
          <button className="btn-primary mt-5 w-full">查看详情</button>
        </div>
      ))}
    </div>
  );
}
export function Offers() {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="card border-2 border-teal-500 p-6 lg:col-span-2">
        <div className="flex items-center gap-3 text-teal-600">
          <Trophy />
          <b>Offer 已确认</b>
        </div>
        <h2 className="mt-5 text-2xl font-black">前端开发工程师</h2>
        <p className="mt-1 text-[var(--muted)]">星云科技（Demo） · 北京</p>
        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <Info t="年薪范围" v="Demo 参考" />
          <Info t="预计入职" v="2027-07" />
          <Info t="状态" v="待决定" />
        </div>
      </div>
      <div className="card p-6">
        <h3 className="font-bold">决策清单</h3>
        <div className="mt-4 space-y-3 text-sm">
          <p className="flex gap-2">
            <CheckCircle2 className="text-teal-600" size={18} />
            薪酬与福利
          </p>
          <p className="flex gap-2">
            <CheckCircle2 className="text-teal-600" size={18} />
            发展空间
          </p>
          <p className="flex gap-2">
            <CalendarDays className="text-slate-400" size={18} />
            截止日期提醒
          </p>
        </div>
      </div>
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
export function NotificationsEmpty() {
  return <EmptyState text="暂无新的通知" />;
}
