import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  familyId: string | null;
  token: string | null;
  role: string | null;
  username: string | null;  // email used as username
  hasFamilySetup: boolean;
  login: (userData: any, familyId: string | null, token: string, role?: string | null, username?: string | null) => void;
  setFamilyConnected: (familyId: string, role: string, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      familyId: null,
      token: null,
      role: null,
      username: null,
      hasFamilySetup: false,
      login: (user, familyId, token, role = null, username = null) =>
        set({
          isAuthenticated: true,
          user,
          familyId: familyId || null,
          token,
          role: role || 'Pending',
          username,
          hasFamilySetup: !!(familyId && familyId.length > 0 && role && role !== 'Pending'),
        }),
      setFamilyConnected: (familyId, role, token) =>
        set({ familyId, role, token, hasFamilySetup: true }),
      logout: () =>
        set({ isAuthenticated: false, user: null, familyId: null, token: null, role: null, username: null, hasFamilySetup: false }),
    }),
    { name: 'kinnest-auth-storage' }
  )
);