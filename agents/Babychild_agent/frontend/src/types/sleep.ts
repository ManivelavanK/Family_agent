export type SleepType = 'Nap' | 'Night Sleep';
export type SleepQuality = 'Excellent' | 'Good' | 'Fair' | 'Poor';

export interface SleepLog {
  id: string;
  type: SleepType;
  startTime: string;
  endTime: string;
  duration: number; // hours
  quality: SleepQuality;
  notes?: string;
}

export interface SleepSummary {
  todayTotal: number; // hours
  weeklyAverage: number; // hours
  qualityStatus: SleepQuality;
  insight: string;
}
