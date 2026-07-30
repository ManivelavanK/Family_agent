import { api } from './api';

export const fatherApi = {
  getMetrics: (): Promise<any> => api.get('/api/father/metrics'),
  updateMetrics: (data: any): Promise<any> => api.post('/api/father/metrics', data),
  getLedger: (): Promise<any> => api.get('/api/father/ledger'),
  getGoals: (): Promise<any> => api.get('/api/father/goals'),
  getBills: (): Promise<any> => api.get('/api/father/bills'),
  getRequests: (): Promise<any> => api.get('/api/father/requests'),
  createRequest: (data: any): Promise<any> => api.post('/api/father/requests', data),
  updateRequest: (reqId: string, data: any): Promise<any> => api.patch(`/api/father/requests/${reqId}`, data),
  consult: (data: any): Promise<any> => api.post('/api/father/consult', data),
};
