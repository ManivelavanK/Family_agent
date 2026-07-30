import { api } from './api';

export const orchestratorApi = {
  getAgents: (): Promise<any> => api.get('/orchestrator/agents'),
  getStatus: (): Promise<any> => api.get('/orchestrator/status'),
  getContext: (): Promise<any> => api.get('/orchestrator/context'),
  getContextCategory: (category: string): Promise<any> => api.get(`/orchestrator/context/${category}`),
  updateContextCategory: (category: string, data: any): Promise<any> => api.post(`/orchestrator/context/${category}`, data),
  getWorkflows: (): Promise<any> => api.get('/orchestrator/workflows'),
  triggerWorkflow: (data: any): Promise<any> => api.post('/orchestrator/workflows', data),
  cancelWorkflow: (id: string): Promise<any> => api.delete(`/orchestrator/workflows/${id}`),
  getEvents: (): Promise<any> => api.get('/orchestrator/events'),
  triggerEvent: (data: any): Promise<any> => api.post('/orchestrator/events', data),
  getTasks: (): Promise<any> => api.get('/orchestrator/tasks'),
  createTask: (data: any): Promise<any> => api.post('/orchestrator/tasks', data),
  cancelTask: (id: string): Promise<any> => api.delete(`/orchestrator/tasks/${id}`),
  retryTask: (id: string): Promise<any> => api.post(`/orchestrator/tasks/${id}/retry`),
};
