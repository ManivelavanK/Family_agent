import { api, isBackendUnavailable } from './api';
import { Vitals } from '../types';
import { mockVitals } from '../data/mockData';

// Helper to load/save from localStorage
const getLocalVitals = (): Vitals[] => {
  const local = localStorage.getItem('grandparent_vitals');
  if (!local) {
    localStorage.setItem('grandparent_vitals', JSON.stringify(mockVitals));
    return mockVitals;
  }
  return JSON.parse(local);
};

const saveLocalVitals = (data: Vitals[]) => {
  localStorage.setItem('grandparent_vitals', JSON.stringify(data));
};

export const vitalsService = {
  getVitals: async (): Promise<Vitals[]> => {
    try {
      const response = await api.get('/vitals/');
      // Map backend response fields to frontend Vitals structure
      return response.data.map((item: any) => ({
        id: String(item.id),
        timestamp: item.timestamp,
        blood_pressure: `${item.blood_pressure_systolic}/${item.blood_pressure_diastolic}`,
        systolic: item.blood_pressure_systolic,
        diastolic: item.blood_pressure_diastolic,
        blood_sugar: item.blood_sugar,
        heart_rate: item.heart_rate,
        temperature: item.temperature,
        status: (item.blood_pressure_systolic > 140 || item.blood_pressure_diastolic > 90 || item.blood_sugar > 180) ? 'Warning' : 'Normal'
      }));
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return getLocalVitals();
      }
      throw e;
    }
  },
  addVitals: async (vital: Vitals): Promise<Vitals> => {
    try {
      const backendVital = {
        blood_pressure_systolic: vital.systolic || 120,
        blood_pressure_diastolic: vital.diastolic || 80,
        blood_sugar: vital.blood_sugar,
        heart_rate: vital.heart_rate,
        temperature: vital.temperature
      };
      const response = await api.post('/vitals/add', backendVital);
      const item = response.data;
      return {
        id: String(item.id),
        timestamp: item.timestamp,
        blood_pressure: `${item.blood_pressure_systolic}/${item.blood_pressure_diastolic}`,
        systolic: item.blood_pressure_systolic,
        diastolic: item.blood_pressure_diastolic,
        blood_sugar: item.blood_sugar,
        heart_rate: item.heart_rate,
        temperature: item.temperature,
        status: (item.blood_pressure_systolic > 140 || item.blood_pressure_diastolic > 90 || item.blood_sugar > 180) ? 'Warning' : 'Normal'
      };
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalVitals();
        const newVital = { ...vital, id: `v-${Date.now()}`, timestamp: new Date().toISOString(), status: 'Normal' };
        current.push(newVital);
        saveLocalVitals(current);
        return newVital;
      }
      throw e;
    }
  },
  deleteVitals: async (id: string): Promise<void> => {
    // Backend doesn't support deleting vitals logs, so we handle it locally.
    const current = getLocalVitals();
    const filtered = current.filter(v => v.id !== id);
    saveLocalVitals(filtered);
  }
};
