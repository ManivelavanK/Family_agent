import { db } from '../data/mockData';
import { Vaccination } from '../types/vaccination';

const LATENCY = 600;

export const vaccinationService = {
  async getVaccinations(): Promise<Vaccination[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve([...db.vaccinations]), LATENCY);
    });
  },

  async markCompleted(id: string): Promise<boolean> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const idx = db.vaccinations.findIndex((v) => v.id === id);
        if (idx !== -1) {
          db.vaccinations[idx].status = 'Completed';
          db.vaccinations[idx].completedDate = new Date().toISOString();
        }
        resolve(true);
      }, LATENCY);
    });
  },
};
