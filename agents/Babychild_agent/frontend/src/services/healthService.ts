import { db } from '../data/mockData';
import { HealthLog } from '../types/health';

const LATENCY = 600;

export const healthService = {
  async getHealthLogs(): Promise<HealthLog[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve([...db.healthLogs]), LATENCY);
    });
  },

  async logHealthRecord(record: Omit<HealthLog, 'id'>): Promise<HealthLog> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newRecord: HealthLog = { ...record, id: `h_${Date.now()}` };
        db.healthLogs.unshift(newRecord);
        resolve(newRecord);
      }, LATENCY);
    });
  },
};
