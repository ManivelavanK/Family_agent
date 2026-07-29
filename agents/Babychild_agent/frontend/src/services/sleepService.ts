import { db } from '../data/mockData';
import { SleepLog, SleepSummary } from '../types/sleep';

const LATENCY = 600;

export const sleepService = {
  async getSleepLogs(): Promise<SleepLog[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve([...db.sleepLogs]), LATENCY);
    });
  },

  async getSleepSummary(): Promise<SleepSummary> {
    return new Promise((resolve) => {
      setTimeout(() => resolve({ ...db.sleepSummary }), LATENCY);
    });
  },

  async logSleep(log: Omit<SleepLog, 'id'>): Promise<SleepLog> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newLog: SleepLog = { ...log, id: `s_${Date.now()}` };
        db.sleepLogs.unshift(newLog);
        resolve(newLog);
      }, LATENCY);
    });
  },
};
