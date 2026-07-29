export interface MealPlanDay {
  day: 'Monday' | 'Tuesday' | 'Wednesday' | 'Thursday' | 'Friday' | 'Saturday' | 'Sunday';
  breakfast: string;
  lunch: string;
  dinner: string;
  ingredientsAvailability: 'Sufficient' | 'Missing';
  missingIngredientsCount: number;
}
