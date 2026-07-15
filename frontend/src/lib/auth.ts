"use client";

import { useSyncExternalStore } from "react";

function subscribe(onStoreChange: () => void) {
  window.addEventListener("storage", onStoreChange);
  return () => window.removeEventListener("storage", onStoreChange);
}

export function useHasToken() {
  return useSyncExternalStore(
    subscribe,
    () => Boolean(window.localStorage.getItem("access_token")),
    () => false,
  );
}
