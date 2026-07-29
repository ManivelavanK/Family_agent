import api from './api';
import type { StandardResponse, Habit, HabitLog } from './api';

export const habitService = {
  getHabits: async (familyId = 'default_family'): Promise<Habit[]> => {
    const res = await api.get<StandardResponse<Habit[]>>(`/planner/habits?family_id=${familyId}`);
    return res.data.data;
  },
  createHabit: async (habit: Partial<Habit>): Promise<Habit> => {
    const res = await api.post<StandardResponse<Habit>>('/planner/habits', habit);
    return res.data.data;
  },
  updateHabit: async (id: number, habit: Partial<Habit>, familyId = 'default_family'): Promise<Habit> => {
    const res = await api.put<StandardResponse<Habit>>(`/planner/habits/${id}?family_id=${familyId}`, habit);
    return res.data.data;
  },
  logHabit: async (id: number, date: string, completed: boolean, familyId = 'default_family'): Promise<HabitLog> => {
    const res = await api.post<StandardResponse<HabitLog>>(`/planner/habits/${id}/log?family_id=${familyId}`, { date, completed });
    return res.data.data;
  },
  deleteHabit: async (id: number, familyId = 'default_family'): Promise<any> => {
    const res = await api.delete<StandardResponse<any>>(`/planner/habits/${id}?family_id=${familyId}`);
    return res.data;
  }
};
