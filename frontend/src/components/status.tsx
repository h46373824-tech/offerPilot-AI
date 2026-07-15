import { AlertCircle, Inbox, LoaderCircle } from "lucide-react";

type StatusStateProps = {
  text?: string;
  action?: React.ReactNode;
};

export function LoadingState({ text = "正在加载数据…" }: StatusStateProps) {
  return (
    <div
      aria-busy="true"
      aria-live="polite"
      className="card flex min-h-40 items-center justify-center gap-2 p-6 text-center text-[var(--muted)]"
      role="status"
    >
      <LoaderCircle aria-hidden="true" className="animate-spin" size={20} />
      <span>{text}</span>
    </div>
  );
}

export function EmptyState({ text = "暂无数据", action }: StatusStateProps) {
  return (
    <div
      className="card flex min-h-40 flex-col items-center justify-center gap-3 p-6 text-center text-[var(--muted)]"
      role="status"
    >
      <Inbox aria-hidden="true" size={28} />
      <span>{text}</span>
      {action}
    </div>
  );
}

export function ErrorState({
  text = "数据加载失败",
  action,
}: StatusStateProps) {
  return (
    <div
      className="card flex min-h-40 flex-col items-center justify-center gap-3 p-6 text-center text-rose-600 dark:text-rose-400"
      role="alert"
    >
      <AlertCircle aria-hidden="true" size={28} />
      <span>{text}</span>
      {action}
    </div>
  );
}

export function Badge({
  children,
  tone = "teal",
}: {
  children: React.ReactNode;
  tone?: "teal" | "amber" | "blue" | "slate";
}) {
  const colors = {
    teal: "bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300",
    amber: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
    blue: "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
    slate: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300",
  };

  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${colors[tone]}`}
    >
      {children}
    </span>
  );
}
