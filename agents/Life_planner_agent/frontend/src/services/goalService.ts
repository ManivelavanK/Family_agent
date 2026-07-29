import api from './api';
import type { StandardResponse, Goal } from './api';

export const goalService = {
  getGoals: async (familyId = 'default_family'): Promise<Goal[]> => {
    const res = await api.get<StandardResponse<Goal[]>>(`/planner/goals?family_id=${familyId}`);
    return res.data.data;
  },
  createGoal: async (goal: Partial<Goal>): Promise<Goal> => {
    const res = await api.post<StandardResponse<Goal>>('/planner/goals', goal);
    return res.data.data;
  },
  updateGoal: async (id: number, goal: Partial<Goal>, familyId = 'default_family'): Promise<Goal> => {
    const res = await api.put<StandardResponse<Goal>>(`/planner/goals/${id}?family_id=${familyId}`, goal);
    return res.data.data;
  },
  deleteGoal: async (id: number, familyId = 'default_family'): Promise<any> => {
    const res = await api.delete<StandardResponse<any>>(`/planner/goals/${id}?family_id=${familyId}`);
    return res.data;
  }
};
