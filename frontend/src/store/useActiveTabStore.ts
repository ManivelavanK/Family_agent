import { create } from 'zustand';

interface ActiveTabState {
  activeTabs: Record<string, string>; // e.g. { '/father': 'overview', '/mother': 'shopping' }
  setActiveTab: (route: string, tabId: string) => void;
}

export const useActiveTabStore = create<ActiveTabState>((set) => ({
  activeTabs: {
    '/father': 'overview',
    '/mother': 'shopping',
    '/grandparent': 'medication',
    '/children': 'tasks',
    '/baby': 'feeding',
    '/planner': 'events',
  },
  setActiveTab: (route, tabId) =>
    set((state) => ({
      activeTabs: { ...state.activeTabs, [route]: tabId },
    })),
}));
