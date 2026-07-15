"use client";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
const data = [
  { name: "互联网", 投递: 8, 面试: 3 },
  { name: "AI", 投递: 5, 面试: 2 },
  { name: "金融", 投递: 4, 面试: 1 },
  { name: "制造", 投递: 3, 面试: 1 },
  { name: "其他", 投递: 2, 面试: 0 },
];
export function Analytics() {
  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <div className="card p-5 lg:col-span-2">
        <h2 className="font-bold">行业转化表现</h2>
        <p className="mb-5 text-xs text-[var(--muted)]">
          投递与进入面试数量对比
        </p>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="投递" fill="#0f766e" radius={[6, 6, 0, 0]} />
              <Bar dataKey="面试" fill="#60a5fa" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="space-y-4">
        <Stat t="简历通过率" v="36%" d="较上月 +4.2%" />
        <Stat t="面试转化率" v="25%" d="建议加强项目表达" />
        <Stat t="平均推进周期" v="12 天" d="从投递到首次沟通" />
      </div>
    </div>
  );
}
function Stat({ t, v, d }: { t: string; v: string; d: string }) {
  return (
    <div className="card p-5">
      <p className="text-sm text-[var(--muted)]">{t}</p>
      <p className="mt-2 text-3xl font-black">{v}</p>
      <p className="mt-2 text-xs text-teal-600">{d}</p>
    </div>
  );
}
