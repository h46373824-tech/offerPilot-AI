import Link from "next/link";
import { EmptyState } from "@/components/status";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[var(--background)] p-5 text-[var(--foreground)]">
      <div className="w-full max-w-lg">
        <EmptyState
          action={
            <Link className="btn-primary" href="/dashboard">
              返回数据总览
            </Link>
          }
          text="没有找到你访问的页面。"
        />
      </div>
    </main>
  );
}
