export type FeedingType = 'Bottle' | 'Breastfeeding' | 'Solid Food' | 'Water' | 'Formula';

export interface FeedingRecord {
  id: string;
  time: string;
  type: FeedingType;
  quantity: string; // e.g. "120 ml" or "20 mins" or "1 bowl"
  duration?: string; // e.g. "15 mins"
  notes?: string;
}

export interface FeedingAnalysis {
  averageFeedingInterval: string; // e.g. "3.5 hours"
  predictedNextFeed: string; // e.g. "1:30 PM"
  hydrationStatus: 'Normal' | 'Monitor' | 'Dehydrated';
  confidence: string; // e.g. "94%"
  recommendation: string;
}
