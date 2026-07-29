import { api, isBackendUnavailable } from './api';
import { Nutrition } from '../types';
import { mockNutrition } from '../data/mockData';

const getLocalNutrition = (): Nutrition[] => {
  const local = localStorage.getItem('grandparent_nutrition');
  if (!local) {
    localStorage.setItem('grandparent_nutrition', JSON.stringify(mockNutrition));
    return mockNutrition;
  }
  return JSON.parse(local);
};

const saveLocalNutrition = (data: Nutrition[]) => {
  localStorage.setItem('grandparent_nutrition', JSON.stringify(data));
};

export const nutritionService = {
  getNutrition: async (): Promise<Nutrition[]> => {
    try {
      const response = await api.get('/nutrition/');
      // Map individual meal logs from backend and group them by date
      const logsByDate: { [dateStr: string]: Nutrition } = {};
      
      response.data.forEach((item: any) => {
        const dateStr = item.timestamp.includes('T') ? item.timestamp.split('T')[0] : item.timestamp.split(' ')[0];
        if (!logsByDate[dateStr]) {
          logsByDate[dateStr] = {
            id: dateStr,
            date: dateStr,
            meals: [],
            calories_consumed: 0,
            water_intake_ml: 0,
            food_notes: ''
          };
        }
        
        if (item.meal_type) {
          const mealDesc = item.description ? `${item.meal_type} (${item.description})` : item.meal_type;
          logsByDate[dateStr].meals.push(mealDesc);
        }
        logsByDate[dateStr].calories_consumed += item.calories || 0;
        logsByDate[dateStr].water_intake_ml += item.water_ml || 0;
        if (item.description) {
          if (logsByDate[dateStr].food_notes) {
            logsByDate[dateStr].food_notes += '; ';
          }
          logsByDate[dateStr].food_notes += item.description;
        }
      });
      
      return Object.values(logsByDate);
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return getLocalNutrition();
      }
      throw e;
    }
  },
  addNutrition: async (nut: Nutrition): Promise<Nutrition> => {
    try {
      const backendNut = {
        meal_type: nut.meals.join(', ') || 'Mixed Meal',
        description: nut.food_notes || 'Logged via Dashboard',
        calories: nut.calories_consumed || 0,
        water_ml: nut.water_intake_ml || 0
      };
      const response = await api.post('/nutrition/add', backendNut);
      const item = response.data;
      const dateStr = item.timestamp.includes('T') ? item.timestamp.split('T')[0] : item.timestamp.split(' ')[0];
      return {
        id: String(item.id),
        date: dateStr,
        meals: [item.meal_type],
        calories_consumed: item.calories,
        water_intake_ml: item.water_ml,
        food_notes: item.description
      };
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalNutrition();
        const newNut = { ...nut, id: `n-${Date.now()}` };
        current.push(newNut);
        saveLocalNutrition(current);
        return newNut;
      }
      throw e;
    }
  }
};
