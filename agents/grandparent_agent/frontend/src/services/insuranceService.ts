import { api, isBackendUnavailable } from './api';
import { Insurance } from '../types';
import { mockInsurance } from '../data/mockData';

const getLocalInsurance = (): Insurance[] => {
  const local = localStorage.getItem('grandparent_insurance');
  if (!local) {
    localStorage.setItem('grandparent_insurance', JSON.stringify(mockInsurance));
    return mockInsurance;
  }
  return JSON.parse(local);
};

const saveLocalInsurance = (data: Insurance[]) => {
  localStorage.setItem('grandparent_insurance', JSON.stringify(data));
};

export const insuranceService = {
  getInsurance: async (): Promise<Insurance[]> => {
    try {
      const response = await api.get('/insurance/');
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return getLocalInsurance();
      }
      throw e;
    }
  },
  addInsurance: async (ins: Omit<Insurance, 'id'>): Promise<Insurance> => {
    try {
      const response = await api.post('/insurance/add', ins);
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalInsurance();
        const newIns: Insurance = { ...ins, id: `i-${Date.now()}` };
        current.push(newIns);
        saveLocalInsurance(current);
        return newIns;
      }
      throw e;
    }
  },
  updateInsurance: async (id: string, ins: Partial<Insurance>): Promise<Insurance> => {
    try {
      const response = await api.put(`/insurance/${id}`, ins);
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalInsurance();
        const idx = current.findIndex(i => i.id === id);
        if (idx !== -1) {
          current[idx] = { ...current[idx], ...ins } as Insurance;
          saveLocalInsurance(current);
          return current[idx];
        }
        throw new Error("Policy not found");
      }
      throw e;
    }
  },
  deleteInsurance: async (id: string): Promise<void> => {
    try {
      await api.delete(`/insurance/${id}`);
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalInsurance();
        const filtered = current.filter(i => i.id !== id);
        saveLocalInsurance(filtered);
        return;
      }
      throw e;
    }
  }
};
