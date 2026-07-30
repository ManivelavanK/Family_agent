import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { orchestratorApi } from '../api/orchestratorApi';

interface FamilyContextType {
  familyStatus: any;
  agents: any[];
  loading: boolean;
  refresh: () => Promise<void>;
}

const FamilyContext = createContext<FamilyContextType | undefined>(undefined);

export const FamilyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, familyId } = useAuthStore();
  const [familyStatus, setFamilyStatus] = useState<any>(null);
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    if (!token || !familyId) return;
    setLoading(true);
    try {
      const [statusData, agentsData] = await Promise.all([
        orchestratorApi.getStatus(),
        orchestratorApi.getAgents(),
      ]);
      setFamilyStatus(statusData);
      setAgents(agentsData);
    } catch (error) {
      console.error('Failed to sync family status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, [token, familyId]);

  return (
    <FamilyContext.Provider value={{ familyStatus, agents, loading, refresh }}>
      {children}
    </FamilyContext.Provider>
  );
};

export const useFamily = () => {
  const context = useContext(FamilyContext);
  if (!context) throw new Error('useFamily must be used within a FamilyProvider');
  return context;
};
