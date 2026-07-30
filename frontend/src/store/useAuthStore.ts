import { create } from 'zustand';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  familyId: string | null;
  login: (userData: any, familyId: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  familyId: null,
  login: (user, familyId) => set({ isAuthenticated: true, user, familyId }),
  logout: () => set({ isAuthenticated: false, user: null, familyId: null }),
}));