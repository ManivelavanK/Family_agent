import React, { createContext, useContext, useState, useEffect } from 'react';
import { financeApi } from '../services/financeApi';

const FamilyContext = createContext(null);

export const FamilyProvider = ({ children }) => {
  const [familyId, setFamilyId] = useState(1);
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [isCheckingBackend, setIsCheckingBackend] = useState(true);
  const [refreshCount, setRefreshCount] = useState(0);

  const checkConnection = async () => {
    setIsCheckingBackend(true);
    try {
      const data = await financeApi.checkHealth();
      if (data && data.status === 'HEALTHY') {
        setIsBackendConnected(true);
      } else {
        setIsBackendConnected(false);
      }
    } catch (err) {
      console.warn('Backend connection check failed:', err.message);
      setIsBackendConnected(false);
    } finally {
      setIsCheckingBackend(false);
    }
  };

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 15000); // Poll health every 15s
    return () => clearInterval(interval);
  }, []);

  const triggerRefresh = () => {
    setRefreshCount((prev) => prev + 1);
  };

  return (
    <FamilyContext.Provider
      value={{
        familyId,
        setFamilyId,
        isBackendConnected,
        isCheckingBackend,
        checkConnection,
        refreshCount,
        triggerRefresh,
      }}
    >
      {children}
    </FamilyContext.Provider>
  );
};

export const useFamily = () => {
  const context = useContext(FamilyContext);
  if (!context) {
    throw new Error('useFamily must be used within a FamilyProvider');
  }
  return context;
};
