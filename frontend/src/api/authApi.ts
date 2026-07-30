import { api } from './api';

export const authApi = {
  login: (data: any): Promise<any> => api.post('/orchestrator/auth/login', data),
  register: (data: any): Promise<any> => api.post('/orchestrator/auth/register', data),
  setupFamily: (data: any): Promise<any> => api.post('/orchestrator/auth/family/setup', data),
  connectFamily: (data: any): Promise<any> => api.post('/orchestrator/auth/family/connect', data),
  createWorkspace: (data: any): Promise<any> => api.post('/orchestrator/auth/workspace/create', data),
  joinWorkspace: (data: any): Promise<any> => api.post('/orchestrator/auth/workspace/join', data),
};
