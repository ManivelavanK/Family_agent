import { db } from '../data/mockData';
import { GrowthDataPoint, GrowthSummary } from '../types/growth';

const LATENCY = 600;

export const growthService = {
  async getGrowthData(): Promise<GrowthDataPoint[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve([...db.growthData]), LATENCY);
    });
  },

  async getGrowthSummary(): Promise<GrowthSummary> {
    return new Promise((resolve) => {
      setTimeout(() => resolve({ ...db.growthSummary }), LATENCY);
    });
  },
};
