import React, { createContext, useContext, useState, useCallback } from 'react';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  // Global refresh token — bumping this triggers re-fetches across all components
  const [refreshToken, setRefreshToken] = useState(0);
  const [studentId] = useState(1); // Single-student mode for MVP

  const triggerRefresh = useCallback(() => {
    setRefreshToken(t => t + 1);
  }, []);

  return (
    <AppContext.Provider value={{ refreshToken, triggerRefresh, studentId }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used inside AppProvider');
  return ctx;
}
