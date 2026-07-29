import { db } from '../data/mockData';
import { FeedingRecord, FeedingAnalysis } from '../types/feeding';

const LATENCY = 600;

export const feedingService = {
  async getFeedingHistory(): Promise<FeedingRecord[]> {
    return new Promise((resolve) => {
      setTimeout(() => resolve([...db.feedingHistory]), LATENCY);
    });
  },

  async getFeedingAnalysis(): Promise<FeedingAnalysis> {
    return new Promise((resolve) => {
      setTimeout(() => resolve({ ...db.feedingAnalysis }), LATENCY);
    });
  },

  async logFeeding(record: Omit<FeedingRecord, 'id'>): Promise<FeedingRecord> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newRecord: FeedingRecord = { ...record, id: `f_${Date.now()}` };
        db.feedingHistory.unshift(newRecord);
        resolve(newRecord);
      }, LATENCY);
    });
  },
};
