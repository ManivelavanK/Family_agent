import { api } from './api';

export const motherApi = {
  getReport: (): Promise<any> => api.get('/api/mother/report'),
  getBudget: (): Promise<any> => api.get('/api/mother/budget'),
  getPantry: (): Promise<any> => api.get('/api/mother/pantry'),
  getShoppingList: (): Promise<any> => api.get('/api/mother/shopping'),
  addShoppingItem: (data: any): Promise<any> => api.post('/api/mother/shopping', data),
  getFoodWaste: (): Promise<any> => api.get('/api/mother/waste'),
  getMeals: (): Promise<any> => api.get('/api/mother/meals'),
  getAlerts: (): Promise<any> => api.get('/api/mother/alerts'),
  getInsights: (): Promise<any> => api.get('/api/mother/insights'),
  getExpiring: (): Promise<any> => api.get('/api/mother/pantry/expiring'),
};
