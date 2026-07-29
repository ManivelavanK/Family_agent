export interface GrowthDataPoint {
  ageMonths: number;
  weightKg: number;
  heightCm: number;
  headCircumferenceCm: number;
  weightPercentile: number;
  heightPercentile: number;
}

export interface GrowthSummary {
  currentWeight: string;
  monthlyGain: string;
  whoPercentileText: string;
  insight: string;
}
