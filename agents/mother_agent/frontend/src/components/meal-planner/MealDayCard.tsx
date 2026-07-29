import React from 'react';
import { MealPlanDay } from '../../types/meal';
import { Coffee, Sun, Sunset, CheckCircle, AlertTriangle } from 'lucide-react';

interface MealDayCardProps {
  dayPlan: MealPlanDay;
  onEditMeal: (day: string, type: 'breakfast' | 'lunch' | 'dinner', currentMeal: string) => void;
}

export const MealDayCard: React.FC<MealDayCardProps> = ({ dayPlan, onEditMeal }) => {
  const isSufficient = dayPlan.ingredientsAvailability === 'Sufficient';

  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-xs flex flex-col justify-between gap-4">
      {/* Day Title and Ingredients availability indicator */}
      <div className="flex items-center justify-between border-b border-slate-50 pb-3">
        <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider">{dayPlan.day}</h3>
        <div className={`flex items-center gap-1 text-[11px] font-semibold ${isSufficient ? 'text-emerald-600' : 'text-amber-600'}`}>
          {isSufficient ? (
            <>
              <CheckCircle className="h-3.5 w-3.5" />
              <span>Sufficient</span>
            </>
          ) : (
            <>
              <AlertTriangle className="h-3.5 w-3.5 animate-pulse" />
              <span>{dayPlan.missingIngredientsCount} missing</span>
            </>
          )}
        </div>
      </div>

      {/* Meal details list */}
      <div className="space-y-3">
        {/* Breakfast */}
        <div 
          onClick={() => onEditMeal(dayPlan.day, 'breakfast', dayPlan.breakfast)}
          className="flex items-center gap-3 p-1.5 rounded-lg hover:bg-slate-50 cursor-pointer group transition-colors"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-orange-50 text-orange-600 group-hover:bg-orange-100 transition-colors">
            <Coffee className="h-3.5 w-3.5" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider">Breakfast</span>
            <span className="block text-xs font-semibold text-slate-700 truncate">{dayPlan.breakfast}</span>
          </div>
        </div>

        {/* Lunch */}
        <div 
          onClick={() => onEditMeal(dayPlan.day, 'lunch', dayPlan.lunch)}
          className="flex items-center gap-3 p-1.5 rounded-lg hover:bg-slate-50 cursor-pointer group transition-colors"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-yellow-50 text-yellow-600 group-hover:bg-yellow-100 transition-colors">
            <Sun className="h-3.5 w-3.5" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider">Lunch</span>
            <span className="block text-xs font-semibold text-slate-700 truncate">{dayPlan.lunch}</span>
          </div>
        </div>

        {/* Dinner */}
        <div 
          onClick={() => onEditMeal(dayPlan.day, 'dinner', dayPlan.dinner)}
          className="flex items-center gap-3 p-1.5 rounded-lg hover:bg-slate-50 cursor-pointer group transition-colors"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 group-hover:bg-indigo-100 transition-colors">
            <Sunset className="h-3.5 w-3.5" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider">Dinner</span>
            <span className="block text-xs font-semibold text-slate-700 truncate">{dayPlan.dinner}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
export default MealDayCard;
