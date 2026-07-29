import { create } from 'zustand';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  familyId: string | null;
  token: string | null;
  login: (userData: any, familyId: string, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!localStorage.getItem('token'),
  user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null,
  familyId: localStorage.getItem('familyId'),
  token: localStorage.getItem('token'),
  login: (user, familyId, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('familyId', familyId);
    set({ isAuthenticated: true, user, familyId, token });
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('familyId');
    set({ isAuthenticated: false, user: null, familyId: null, token: null });
  },
}));
