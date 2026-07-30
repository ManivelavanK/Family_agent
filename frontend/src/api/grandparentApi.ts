import { api } from './api';

export const grandparentApi = {
  getVitals: (): Promise<any> => api.get('/api/grandparent/vitals'),
  getMedications: (): Promise<any> => api.get('/api/grandparent/medications'),
  getVisits: (): Promise<any> => api.get('/api/grandparent/visits'),
  getActivity: (): Promise<any> => api.get('/api/grandparent/activity'),
  triggerEmergency: (): Promise<any> => api.post('/api/grandparent/emergency'),
};
