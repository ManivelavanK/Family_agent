import { MealPlanDay } from '../types/meal';
import { db } from '../data/mockData';
import { IS_MOCK_MODE, apiClient } from './api';

const LATENCY = 600;

export interface AIMealPlanGeneratorInputs {
  familyMembers: number;
  budget: number;
  preferences: string;
  availableIngredients: string[];
}

export interface AIMealPlanResponse {
  mealPlan: MealPlanDay[];
  requiredIngredients: string[];
  availableIngredients: string[];
  missingIngredients: { name: string; quantity: string; cost: number }[];
  estimatedCost: number;
  wasteReductionSuggestion: string;
}

export const mealService = {
  async getMealPlan(): Promise<MealPlanDay[]> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve([...db.mealPlan]);
        }, LATENCY);
      });
    }
    const stored = localStorage.getItem('kinnest_meal_plan');
    if (stored) {
      return JSON.parse(stored);
    }
    // Default fallback to mock database values
    localStorage.setItem('kinnest_meal_plan', JSON.stringify(db.mealPlan));
    return [...db.mealPlan];
  },

  async updateMeal(day: string, type: 'breakfast' | 'lunch' | 'dinner', mealName: string): Promise<MealPlanDay> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const index = db.mealPlan.findIndex(m => m.day === day);
          if (index === -1) {
            reject(new Error('Day not found'));
            return;
          }
          db.mealPlan[index][type] = mealName;
          resolve(db.mealPlan[index]);
        }, LATENCY);
      });
    }
    const mealPlan = await this.getMealPlan();
    const index = mealPlan.findIndex(m => m.day === day);
    if (index !== -1) {
      mealPlan[index][type] = mealName;
      localStorage.setItem('kinnest_meal_plan', JSON.stringify(mealPlan));
      return mealPlan[index];
    }
    throw new Error('Day not found');
  },

  async generateMealPlan(inputs: AIMealPlanGeneratorInputs): Promise<AIMealPlanResponse> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          const mealPlan: MealPlanDay[] = [
            {
              day: 'Monday',
              breakfast: 'Ven Pongal + Chutney',
              lunch: 'Rice + Sambar + Cabbage Poriyal',
              dinner: 'Oats Idli + Tomato Sambar',
              ingredientsAvailability: 'Sufficient',
              missingIngredientsCount: 0
            },
            {
              day: 'Tuesday',
              breakfast: 'Rava Kichadi',
              lunch: 'Rice + Tomato Rasam + Kovakkai Fry',
              dinner: 'Set Dosa + Vadacurry',
              ingredientsAvailability: 'Sufficient',
              missingIngredientsCount: 0
            },
            {
              day: 'Wednesday',
              breakfast: 'Idli + Milagai Podi',
              lunch: 'Rice + Vatha Kuzhambu + Appalam',
              dinner: 'Pesaarattu + Ginger Chutney',
              ingredientsAvailability: 'Missing',
              missingIngredientsCount: 1
            },
            {
              day: 'Thursday',
              breakfast: 'Wheat Rava Upma',
              lunch: 'Rice + Dal + Snakegourd Kootu',
              dinner: 'Chappati + Mixed Veg Kurma',
              ingredientsAvailability: 'Sufficient',
              missingIngredientsCount: 0
            },
            {
              day: 'Friday',
              breakfast: 'Semiya Kichadi',
              lunch: 'Vegetable Pulao + Onion Raitha',
              dinner: 'Idiyappam + Coconut Stew',
              ingredientsAvailability: 'Missing',
              missingIngredientsCount: 2
            },
            {
              day: 'Saturday',
              breakfast: 'Kambu Koozh',
              lunch: 'Curd Rice + Pickle + Potato Roast',
              dinner: 'Dosa + Onion Kara Chutney',
              ingredientsAvailability: 'Sufficient',
              missingIngredientsCount: 0
            },
            {
              day: 'Sunday',
              breakfast: 'Appam + Coconut Milk',
              lunch: 'Millet Biryani + Brinjal Gravy',
              dinner: 'Adai + Avial',
              ingredientsAvailability: 'Sufficient',
              missingIngredientsCount: 0
            }
          ];

          const missingIngredients = [
            { name: 'Organic Milk', quantity: '2 L', cost: 120 },
            { name: 'Tomatoes', quantity: '1.5 kg', cost: 90 },
            { name: 'Coriander Leaves', quantity: '1 bunch', cost: 20 }
          ];

          resolve({
            mealPlan,
            requiredIngredients: ['Rice', 'Dal', 'Tomatoes', 'Onions', 'Milk', 'Coriander', 'Vegetables'],
            availableIngredients: ['Rice', 'Dal', 'Onions', 'Vegetables'],
            missingIngredients,
            estimatedCost: 230,
            wasteReductionSuggestion: 'By planning semiya/rava dishes, you use ingredients currently in stock. Estimated food waste will be reduced by 12%.'
          });
        }, 1800); // Mocking deep planning logic
      });
    }

    // Call live FastAPI /recipe/suggest endpoint to get AI recipe recommendations
    console.log('Generating meal plan with inputs:', inputs);
    const response = await apiClient.get<any>('/recipe/suggest');
    const suggestText = response.data.recipes || '';

    const mealPlan: MealPlanDay[] = [
      {
        day: 'Monday',
        breakfast: 'Pongal',
        lunch: 'Rice + Sambar + Spinach',
        dinner: 'Dosa',
        ingredientsAvailability: 'Sufficient',
        missingIngredientsCount: 0
      },
      {
        day: 'Tuesday',
        breakfast: 'Idli',
        lunch: 'Rice + Kovakkai Fry',
        dinner: 'Roti + Paneer Butter Masala',
        ingredientsAvailability: 'Sufficient',
        missingIngredientsCount: 0
      },
      {
        day: 'Wednesday',
        breakfast: 'Upma',
        lunch: 'Rice + Tomato Rasam',
        dinner: 'Chappati + Veg Kurma',
        ingredientsAvailability: 'Missing',
        missingIngredientsCount: 1
      },
      {
        day: 'Thursday',
        breakfast: 'Oats Idli',
        lunch: 'Vegetable Pulao',
        dinner: 'Set Dosa',
        ingredientsAvailability: 'Sufficient',
        missingIngredientsCount: 0
      },
      {
        day: 'Friday',
        breakfast: 'Puri + Potato Masala',
        lunch: 'Rice + Sambar',
        dinner: 'Idiyappam',
        ingredientsAvailability: 'Missing',
        missingIngredientsCount: 2
      },
      {
        day: 'Saturday',
        breakfast: 'Pesaarattu',
        lunch: 'Curd Rice',
        dinner: 'Dosa + Kara Chutney',
        ingredientsAvailability: 'Sufficient',
        missingIngredientsCount: 0
      },
      {
        day: 'Sunday',
        breakfast: 'Appam + Coconut Milk',
        lunch: 'Millet Biryani',
        dinner: 'Adai + Avial',
        ingredientsAvailability: 'Sufficient',
        missingIngredientsCount: 0
      }
    ];

    const missingIngredients = [
      { name: 'Organic Milk', quantity: '2 L', cost: 120 },
      { name: 'Tomatoes', quantity: '1.5 kg', cost: 90 }
    ];

    return {
      mealPlan,
      requiredIngredients: response.data.available_ingredients || [],
      availableIngredients: response.data.available_ingredients || [],
      missingIngredients,
      estimatedCost: 210,
      wasteReductionSuggestion: suggestText || 'No custom suggestions available.'
    };
  },

  async applyGeneratedMealPlan(mealPlan: MealPlanDay[]): Promise<boolean> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          db.mealPlan = [...mealPlan];
          resolve(true);
        }, LATENCY);
      });
    }
    localStorage.setItem('kinnest_meal_plan', JSON.stringify(mealPlan));
    return true;
  }
};
