import { api } from './api';

export const plannerApi = {
  getGoals: (): Promise<any> => api.get('/planner/goals'),
  createGoal: (data: any): Promise<any> => api.post('/planner/goals', data),
  getHabits: (): Promise<any> => api.get('/planner/habits'),
  createHabit: (data: any): Promise<any> => api.post('/planner/habits', data),
  getPlans: (): Promise<any> => api.get('/plans'),
  getTasks: (): Promise<any> => api.get('/tasks'),
  getRoutines: (): Promise<any> => api.get('/routines'),
  getReflections: (): Promise<any> => api.get('/reflections'),
};
