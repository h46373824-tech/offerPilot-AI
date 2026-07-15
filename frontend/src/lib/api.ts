const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

type ApiErrorBody = {
  detail?: string | Array<{ msg?: string }>;
};

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const token =
    typeof window === "undefined"
      ? null
      : window.localStorage.getItem("access_token");
  const headers = new Headers(init?.headers);
  const isFormData =
    typeof FormData !== "undefined" && init?.body instanceof FormData;

  if (init?.body && !isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, headers });
  } catch {
    throw new Error("网络连接失败，请确认后端服务已经启动");
  }

  if (!response.ok) {
    const body = (await response
      .json()
      .catch(() => null)) as ApiErrorBody | null;
    const detail = body?.detail;
    const validationMessage = Array.isArray(detail)
      ? detail[0]?.msg
      : undefined;

    throw new Error(
      (typeof detail === "string" ? detail : validationMessage) ??
        (response.status === 401
          ? "登录状态已失效，请重新登录"
          : "请求失败，请稍后重试"),
    );
  }

  if (response.status === 204) return undefined as T;

  return response.json() as Promise<T>;
}
