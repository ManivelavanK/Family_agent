import { api, isBackendUnavailable } from './api';
import { Reminder } from '../types';
import { mockReminders } from '../data/mockData';

const getLocalReminders = (): Reminder[] => {
  const local = localStorage.getItem('grandparent_reminders');
  if (!local) {
    localStorage.setItem('grandparent_reminders', JSON.stringify(mockReminders));
    return mockReminders;
  }
  return JSON.parse(local);
};

const saveLocalReminders = (data: Reminder[]) => {
  localStorage.setItem('grandparent_reminders', JSON.stringify(data));
};

export const reminderService = {
  getReminders: async (): Promise<Reminder[]> => {
    try {
      const response = await api.get('/reminder/');
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return getLocalReminders();
      }
      throw e;
    }
  },
  addReminder: async (rem: Omit<Reminder, 'id' | 'completed'>): Promise<Reminder> => {
    try {
      // Backend expects ReminderCreate which matches Omit<Reminder, 'id' | 'completed'>
      const response = await api.post('/reminder/add', rem);
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalReminders();
        const newRem: Reminder = { ...rem, id: `rem-${Date.now()}`, completed: false };
        current.push(newRem);
        saveLocalReminders(current);
        return newRem;
      }
      throw e;
    }
  },
  toggleReminder: async (id: string): Promise<Reminder> => {
    // Backend reminder model represents active background cron/alarm triggers and doesn't support completing/toggling,
    // so we handle toggling completed status locally.
    const current = getLocalReminders();
    const idx = current.findIndex(r => r.id === id);
    if (idx !== -1) {
      current[idx].completed = !current[idx].completed;
      saveLocalReminders(current);
      return current[idx];
    }
    throw new Error("Reminder not found");
  },
  deleteReminder: async (id: string): Promise<void> => {
    try {
      await api.delete(`/reminder/${id}`);
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalReminders();
        const filtered = current.filter(r => r.id !== id);
        saveLocalReminders(filtered);
        return;
      }
      throw e;
    }
  }
};
