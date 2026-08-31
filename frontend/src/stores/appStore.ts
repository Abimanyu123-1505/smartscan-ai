import { create } from "zustand";
import type { Case } from "../types";

interface Notification {
  id: string;
  type: "info" | "success" | "warning" | "error";
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

interface AppState {
  // Active case context
  activeCase: Case | null;
  setActiveCase: (c: Case | null) => void;

  // Command palette
  commandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;

  // Notifications
  notifications: Notification[];
  addNotification: (n: Omit<Notification, "id" | "timestamp" | "read">) => void;
  markAllRead: () => void;
  clearNotifications: () => void;

  // Sidebar collapse
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (v: boolean) => void;

  // Global search query
  globalQuery: string;
  setGlobalQuery: (q: string) => void;
}

let nid = 0;

export const useAppStore = create<AppState>((set) => ({
  activeCase: null,
  setActiveCase: (c) => set({ activeCase: c }),

  commandPaletteOpen: false,
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),

  notifications: [],
  addNotification: (n) =>
    set((state) => ({
      notifications: [
        {
          ...n,
          id: String(++nid),
          timestamp: new Date(),
          read: false,
        },
        ...state.notifications,
      ].slice(0, 50),
    })),
  markAllRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
    })),
  clearNotifications: () => set({ notifications: [] }),

  sidebarCollapsed: false,
  setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),

  globalQuery: "",
  setGlobalQuery: (q) => set({ globalQuery: q }),
}));
