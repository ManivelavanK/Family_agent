import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  familyId: string | null;
  token: string | null;
  login: (userData: any, familyId: string, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      familyId: null,
      token: null,
      login: (user, familyId, token) => set({ isAuthenticated: true, user, familyId, token }),
      logout: () => set({ isAuthenticated: false, user: null, familyId: null, token: null }),
    }),
    {
      name: 'kinnest-auth-storage', // unique name
    }
  )
);