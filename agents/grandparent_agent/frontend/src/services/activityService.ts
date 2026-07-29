import { api, isBackendUnavailable } from './api';
import { Activity } from '../types';
import { mockActivities } from '../data/mockData';

const getLocalActivities = (): Activity[] => {
  const local = localStorage.getItem('grandparent_activities');
  if (!local) {
    localStorage.setItem('grandparent_activities', JSON.stringify(mockActivities));
    return mockActivities;
  }
  return JSON.parse(local);
};

const saveLocalActivities = (data: Activity[]) => {
  localStorage.setItem('grandparent_activities', JSON.stringify(data));
};

export const activityService = {
  getActivities: async (): Promise<Activity[]> => {
    try {
      const response = await api.get('/activity/');
      return response.data.map((item: any) => ({
        id: String(item.id),
        date: item.date,
        steps: item.steps,
        sleep_hours: item.sleep_hours,
        exercise_type: item.activity_type || 'Walking',
        exercise_duration_minutes: item.duration_minutes || 0,
        calories_burned: Math.round((item.steps * 0.04) + ((item.duration_minutes || 0) * 5))
      }));
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return getLocalActivities();
      }
      throw e;
    }
  },
  addActivity: async (act: Activity): Promise<Activity> => {
    try {
      const backendAct = {
        date: act.date || new Date().toISOString().split('T')[0],
        steps: act.steps || 0,
        sleep_hours: act.sleep_hours || 0.0,
        activity_type: act.exercise_type || 'Walking',
        duration_minutes: act.exercise_duration_minutes || 0
      };
      const response = await api.post('/activity/add', backendAct);
      const item = response.data;
      return {
        id: String(item.id),
        date: item.date,
        steps: item.steps,
        sleep_hours: item.sleep_hours,
        exercise_type: item.activity_type || 'Walking',
        exercise_duration_minutes: item.duration_minutes || 0,
        calories_burned: Math.round((item.steps * 0.04) + (item.duration_minutes * 5))
      };
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalActivities();
        const newAct = { ...act, id: `a-${Date.now()}` };
        current.push(newAct);
        saveLocalActivities(current);
        return newAct;
      }
      throw e;
    }
  }
};
