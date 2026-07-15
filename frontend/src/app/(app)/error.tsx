"use client";

import { useEffect } from "react";
import { ErrorState } from "@/components/status";

export default function ProductError({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  useEffect(() => {
    console.error("OfferPilot 页面渲染失败", error);
  }, [error]);

  return (
    <ErrorState
      action={
        <button className="btn-primary" onClick={unstable_retry} type="button">
          重新加载
        </button>
      }
      text="页面加载失败，请检查网络后重试。"
    />
  );
}
