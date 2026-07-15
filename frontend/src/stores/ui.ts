"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

type UiState = {
  dark: boolean;
  mobileOpen: boolean;
  toggleDark: () => void;
  setMobileOpen: (open: boolean) => void;
};

type PersistedUiState = Pick<UiState, "dark">;

export const useUiStore = create<UiState>()(
  persist<UiState, [], [], PersistedUiState>(
    (set) => ({
      dark: false,
      mobileOpen: false,
      toggleDark: () => set((state) => ({ dark: !state.dark })),
      setMobileOpen: (mobileOpen) => set({ mobileOpen }),
    }),
    {
      name: "offerpilot-ui",
      partialize: (state) => ({ dark: state.dark }),
      skipHydration: true,
    },
  ),
);
