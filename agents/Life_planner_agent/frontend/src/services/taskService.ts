import api from './api';
import type { StandardResponse, Task } from './api';

export const taskService = {
  getTasks: async (planId = 1): Promise<Task[]> => {
    try {
      const res = await api.get<StandardResponse<Task[]>>(`/plans/${planId}/tasks`);
      return res.data.data;
    } catch {
      return [];
    }
  },
  createTask: async (task: Partial<Task>, planId = 1): Promise<Task> => {
    try {
      const res = await api.post<StandardResponse<Task>>(`/plans/${planId}/tasks`, task);
      return res.data.data;
    } catch {
      await api.post('/plans', { id: 1, title: 'Primary Family Plan', plan_type: 'EVENT' }).catch(() => {});
      const res = await api.post<StandardResponse<Task>>(`/plans/${planId}/tasks`, task);
      return res.data.data;
    }
  },
  updateTask: async (id: number, task: Partial<Task>): Promise<Task> => {
    const res = await api.put<StandardResponse<Task>>(`/tasks/${id}`, task);
    return res.data.data;
  },
  deleteTask: async (id: number): Promise<any> => {
    const res = await api.delete<StandardResponse<any>>(`/tasks/${id}`);
    return res.data;
  }
};
