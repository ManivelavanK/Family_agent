export interface HealthLog {
  id: string;
  timestamp: string;
  temperature?: number; // °C
  weight?: number; // kg
  height?: number; // cm
  medicine?: string;
  symptoms: string[];
  doctorNotes?: string;
  attachments?: string[];
}

export interface HealthSummary {
  status: string;
  alertsCount: number;
  recentInsight: string;
}
