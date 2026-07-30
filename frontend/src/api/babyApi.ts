import { api } from './api';

export const babyApi = {
  getSummary: (babyId: number = 1): Promise<any> => api.get(`/api/v1/baby/dashboard/summary/${babyId}`),
  getAlerts: (babyId: number = 1): Promise<any> => api.get(`/api/v1/baby/dashboard/alerts/${babyId}`),
  getRecommendations: (babyId: number = 1): Promise<any> => api.get(`/api/v1/baby/dashboard/recommendations/${babyId}`),
  logFeeding: (data: any): Promise<any> => api.post('/api/v1/baby/feeding', data),
  logSleep: (data: any): Promise<any> => api.post('/api/v1/baby/sleep', data),
};
