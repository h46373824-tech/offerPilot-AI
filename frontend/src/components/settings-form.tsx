"use client";
import { useState } from "react";
export function SettingsForm() {
  const [saved, setSaved] = useState(false);
  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <aside className="card h-fit p-3">
        <button className="w-full rounded-lg bg-teal-50 px-3 py-2 text-left text-sm font-bold text-teal-700">
          个人资料
        </button>
        <button className="w-full rounded-lg px-3 py-2 text-left text-sm">
          通知偏好
        </button>
        <button className="w-full rounded-lg px-3 py-2 text-left text-sm">
          求职偏好
        </button>
        <button className="w-full rounded-lg px-3 py-2 text-left text-sm">
          账户安全
        </button>
      </aside>
      <form
        className="card space-y-5 p-6 lg:col-span-2"
        onSubmit={(e) => {
          e.preventDefault();
          setSaved(true);
        }}
      >
        <div>
          <label className="mb-2 block text-sm font-semibold">姓名</label>
          <input className="field" defaultValue="应届生用户" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-semibold">毕业年份</label>
            <select className="field" defaultValue="2027">
              <option>2027</option>
              <option>2028</option>
            </select>
          </div>
          <div>
            <label className="mb-2 block text-sm font-semibold">最高学历</label>
            <select className="field" defaultValue="本科">
              <option>专科</option>
              <option>本科</option>
              <option>硕士</option>
            </select>
          </div>
        </div>
        <div>
          <label className="mb-2 block text-sm font-semibold">目标城市</label>
          <input className="field" defaultValue="北京、上海、深圳、杭州" />
        </div>
        <label className="flex items-center gap-3 text-sm">
          <input type="checkbox" defaultChecked />
          接收岗位截止提醒和流程通知
        </label>
        <div className="flex items-center gap-3">
          <button className="btn-primary">保存设置</button>
          {saved && <span className="text-sm text-teal-600">保存成功</span>}
        </div>
      </form>
    </div>
  );
}
