"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useUiStore } from "@/stores/ui";

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { retry: 1, staleTime: 30_000 },
        },
      }),
  );
  const dark = useUiStore((state) => state.dark);

  useEffect(() => {
    void useUiStore.persist.rehydrate();
  }, []);

  return (
    <div className={dark ? "dark min-h-screen" : "min-h-screen"}>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </div>
  );
}
