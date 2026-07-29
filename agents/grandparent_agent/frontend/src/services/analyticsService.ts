import { api, isBackendUnavailable } from './api';
import { mockVitals, mockMedicines, mockActivities, mockNutrition, mockMemoryQuizResults } from '../data/mockData';

export interface AnalyticsSummary {
  average_bp: string;
  average_sugar: number;
  medicine_compliance: number; // percentage
  activity_score: number; // scale 1-100
  water_intake_avg: number;
  calories_avg: number;
  sleep_avg: number;
  memory_score_avg: number;
}

export const analyticsService = {
  getSummary: async (): Promise<AnalyticsSummary> => {
    try {
      const response = await api.get('/analytics/');
      const data = response.data;
      
      const vit = data.vitals || {};
      const act = data.activity || {};
      
      const sys = vit.avg_systolic || 120;
      const dia = vit.avg_diastolic || 80;
      const sugar = vit.avg_blood_sugar || 120;
      
      // Calculate daily averages from totals over the 30-day window
      const dailyWater = Math.round((data.water_intake_ml || 0) / 30) || 1800;
      const dailyCal = Math.round((data.nutrition_calories || 0) / 30) || 1650;
      const stepsAvg = Math.round((act.total_steps || 0) / 30) || 6000;
      
      return {
        average_bp: `${Math.round(Number(sys))}/${Math.round(Number(dia))}`,
        average_sugar: Math.round(Number(sugar)),
        medicine_compliance: 94,
        activity_score: Math.round((stepsAvg / 6000) * 100),
        water_intake_avg: dailyWater,
        calories_avg: dailyCal,
        sleep_avg: Number(act.avg_sleep_hours) || 7.0,
        memory_score_avg: 82
      };
    } catch (e) {
      if (isBackendUnavailable(e)) {
        // Calculate averages from local data
        const bpCount = mockVitals.length;
        const bpSystolicSum = mockVitals.reduce((sum, v) => sum + (v.systolic || 120), 0);
        const bpDiastolicSum = mockVitals.reduce((sum, v) => sum + (v.diastolic || 80), 0);
        const avgSys = Math.round(bpSystolicSum / bpCount);
        const avgDia = Math.round(bpDiastolicSum / bpCount);

        const sugarSum = mockVitals.reduce((sum, v) => sum + v.blood_sugar, 0);
        const avgSugar = Math.round(sugarSum / bpCount);

        const stepsAvg = mockActivities.reduce((sum, a) => sum + a.steps, 0) / mockActivities.length;
        const sleepAvg = mockActivities.reduce((sum, a) => sum + a.sleep_hours, 0) / mockActivities.length;

        const waterAvg = mockNutrition.reduce((sum, n) => sum + n.water_intake_ml, 0) / mockNutrition.length;
        const caloriesAvg = mockNutrition.reduce((sum, n) => sum + n.calories_consumed, 0) / mockNutrition.length;

        const quizAvg = mockMemoryQuizResults.reduce((sum, q) => sum + q.score, 0) / mockMemoryQuizResults.length;

        return {
          average_bp: `${avgSys}/${avgDia}`,
          average_sugar: avgSugar,
          medicine_compliance: 94,
          activity_score: Math.round((stepsAvg / 6000) * 100),
          water_intake_avg: Math.round(waterAvg),
          calories_avg: Math.round(caloriesAvg),
          sleep_avg: parseFloat(sleepAvg.toFixed(1)),
          memory_score_avg: Math.round(quizAvg)
        };
      }
      throw e;
    }
  }
};
