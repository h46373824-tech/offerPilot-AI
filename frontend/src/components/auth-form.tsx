"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { LoaderCircle } from "lucide-react";
import { apiFetch } from "@/lib/api";

type AuthMode = "login" | "register";

export function AuthForm({ mode }: { mode: AuthMode }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const isLogin = mode === "login";

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    const data = new FormData(event.currentTarget);
    const email = String(data.get("email") ?? "");
    const password = String(data.get("password") ?? "");

    try {
      const payload = isLogin
        ? await apiFetch<{ access_token: string }>("/auth/login", {
            body: JSON.stringify({ email, password }),
            method: "POST",
          })
        : await apiFetch<{ access_token: string }>("/auth/register", {
            body: JSON.stringify({
              email,
              full_name: String(data.get("full_name") ?? ""),
              password,
            }),
            method: "POST",
          });

      window.localStorage.setItem("access_token", payload.access_token);
      router.replace("/dashboard");
    } catch (caughtError) {
      setError(
        caughtError instanceof Error ? caughtError.message : "操作失败，请重试",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-[var(--background)] text-[var(--foreground)] lg:grid-cols-2">
      <section className="hidden bg-[#0b1f38] p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="text-2xl font-black">
          OfferPilot <span className="text-teal-400">AI</span>
        </div>
        <div>
          <p className="mb-4 text-sm font-bold tracking-widest text-teal-300 uppercase">
            2027 届校招助手
          </p>
          <h1 className="max-w-xl text-5xl leading-tight font-black">
            让每一次投递
            <br />
            都有清晰航向
          </h1>
          <p className="mt-6 max-w-lg text-slate-300">
            统一管理企业、岗位、投递、面试和 Offer，用数据复盘求职进度。
          </p>
        </div>
        <p className="text-xs text-slate-400">
          平台内置数据为 Demo 示例，不代表实时招聘状态。
        </p>
      </section>

      <section className="flex items-center justify-center p-5">
        <div className="card w-full max-w-md p-7 md:p-9">
          <div className="mb-7 lg:hidden">
            <b className="text-xl">OfferPilot AI</b>
          </div>
          <h2 className="text-2xl font-black">
            {isLogin ? "欢迎回来" : "创建你的账户"}
          </h2>
          <p className="mt-2 text-sm text-[var(--muted)]">
            {isLogin ? "登录后继续管理求职进度" : "开始建立你的校招求职工作台"}
          </p>
          <form
            aria-busy={loading}
            className="mt-7 space-y-4"
            onSubmit={submit}
          >
            {!isLogin && (
              <div>
                <label
                  className="mb-2 block text-sm font-semibold"
                  htmlFor="full_name"
                >
                  姓名
                </label>
                <input
                  autoComplete="name"
                  className="field"
                  id="full_name"
                  name="full_name"
                  placeholder="你的姓名"
                  required
                />
              </div>
            )}
            <div>
              <label
                className="mb-2 block text-sm font-semibold"
                htmlFor="email"
              >
                邮箱
              </label>
              <input
                autoComplete="email"
                className="field"
                id="email"
                name="email"
                placeholder="name@example.com"
                required
                type="email"
              />
            </div>
            <div>
              <label
                className="mb-2 block text-sm font-semibold"
                htmlFor="password"
              >
                密码
              </label>
              <input
                autoComplete={isLogin ? "current-password" : "new-password"}
                className="field"
                id="password"
                minLength={8}
                name="password"
                placeholder="至少 8 位字符"
                required
                type="password"
              />
            </div>
            {error && (
              <p
                className="rounded-lg bg-rose-50 p-3 text-sm text-rose-600 dark:bg-rose-950 dark:text-rose-300"
                role="alert"
              >
                {error}
              </p>
            )}
            <button
              className="btn-primary w-full"
              disabled={loading}
              type="submit"
            >
              {loading && (
                <LoaderCircle
                  aria-hidden="true"
                  className="animate-spin"
                  size={18}
                />
              )}
              {loading ? "请稍候…" : isLogin ? "登录" : "注册并登录"}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-[var(--muted)]">
            {isLogin ? "还没有账户？" : "已有账户？"}{" "}
            <Link
              className="font-bold text-teal-600 dark:text-teal-400"
              href={isLogin ? "/register" : "/login"}
            >
              {isLogin ? "立即注册" : "返回登录"}
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
