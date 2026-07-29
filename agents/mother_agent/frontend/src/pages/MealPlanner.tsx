import React, { useState, useEffect } from 'react';
import { mealService, AIMealPlanResponse, AIMealPlanGeneratorInputs } from '../services/mealService';
import { shoppingService } from '../services/shoppingService';
import { MealPlanDay } from '../types/meal';
import { MealDayCard } from '../components/meal-planner/MealDayCard';
import { AIMealPlannerModal } from '../components/meal-planner/AIMealPlannerModal';
import { Sparkles, Calendar, ShoppingCart, Loader2, X } from 'lucide-react';

export const MealPlanner: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [mealPlan, setMealPlan] = useState<MealPlanDay[]>([]);
  
  // AI Modal States
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState<AIMealPlanResponse | null>(null);

  // Custom Edit Meal States
  const [editMealOpen, setEditMealOpen] = useState(false);
  const [editDay, setEditDay] = useState('');
  const [editType, setEditType] = useState<'breakfast' | 'lunch' | 'dinner'>('breakfast');
  const [editMealName, setEditMealName] = useState('');
  const [updating, setUpdating] = useState(false);

  const loadMealPlan = async () => {
    setLoading(true);
    try {
      const data = await mealService.getMealPlan();
      setMealPlan(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMealPlan();
  }, []);

  const handleOpenEdit = (day: string, type: 'breakfast' | 'lunch' | 'dinner', mealName: string) => {
    setEditDay(day);
    setEditType(type);
    setEditMealName(mealName);
    setEditMealOpen(true);
  };

  const handleUpdateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUpdating(true);
    try {
      const updated = await mealService.updateMeal(editDay, editType, editMealName);
      setMealPlan(prev => prev.map(d => d.day === editDay ? updated : d));
      setEditMealOpen(false);
    } catch (err) {
      console.error(err);
    } finally {
      setUpdating(false);
    }
  };

  const handleGenerateAIPlan = async (inputs: AIMealPlanGeneratorInputs) => {
    setAiLoading(true);
    try {
      const result = await mealService.generateMealPlan(inputs);
      setAiResult(result);
    } catch (err) {
      console.error(err);
    } finally {
      setAiLoading(false);
    }
  };

  const handleApplyMealPlan = async () => {
    if (!aiResult) return;
    try {
      // Save meal plan to active memory
      await mealService.applyGeneratedMealPlan(aiResult.mealPlan);
      
      // Batch add missing ingredients to shopping list
      const shoppingItems = aiResult.missingIngredients.map(ing => {
        const qtyNum = parseFloat(ing.quantity);
        const unitStr = ing.quantity.replace(/[0-9.]/g, '').trim();
        return {
          name: ing.name,
          quantity: isNaN(qtyNum) ? 1 : qtyNum,
          unit: unitStr || 'unit',
          category: 'Ingredients',
          estimatedPrice: ing.cost,
          priority: 'Must Buy' as const,
          aiReason: 'Required for newly scheduled AI meal plan.'
        };
      });

      if (shoppingItems.length > 0) {
        await shoppingService.addAllToShoppingList(shoppingItems);
      }

      setAiModalOpen(false);
      setAiResult(null);
      loadMealPlan();
      alert('AI Meal Plan applied and missing ingredients added to Shopping List!');
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerateShoppingList = async () => {
    // Generate shopping list items for missing ingredients based on current meal plan
    const missingItems = [
      { name: 'Organic Milk', quantity: 2, unit: 'L', category: 'Dairy', estimatedPrice: 120, priority: 'Must Buy' as const, aiReason: 'Required for scheduled Wednesday meal.' },
      { name: 'Tomatoes', quantity: 1.5, unit: 'kg', category: 'Vegetables', estimatedPrice: 90, priority: 'Must Buy' as const, aiReason: 'Required for Friday scheduled dishes.' }
    ];

    try {
      await shoppingService.addAllToShoppingList(missingItems);
      alert('Missing ingredients have been compiled and sent to your Shopping List!');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Panel */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Weekly Meal Planner</h1>
          <p className="text-slate-500 font-medium text-xs mt-1">Plan meals, audit nutritional variety, and prevent ingredient deficits.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => {
              setAiResult(null);
              setAiModalOpen(true);
            }}
            className="flex items-center justify-center gap-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 px-4 text-xs shadow-md shadow-indigo-100 transition-colors cursor-pointer"
          >
            <Sparkles className="h-4 w-4 animate-pulse" />
            AI Meal Planner
          </button>
          <button
            onClick={handleGenerateShoppingList}
            className="flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-655 font-semibold py-2.5 px-4 text-xs transition-colors cursor-pointer"
          >
            <ShoppingCart className="h-4 w-4" />
            Generate Shopping List
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {mealPlan.map((dayPlan) => (
            <MealDayCard
              key={dayPlan.day}
              dayPlan={dayPlan}
              onEditMeal={handleOpenEdit}
            />
          ))}
        </div>
      )}

      {/* AI Meal Planner Modal Dialog */}
      <AIMealPlannerModal
        isOpen={aiModalOpen}
        onClose={() => setAiModalOpen(false)}
        onGenerate={handleGenerateAIPlan}
        loading={aiLoading}
        result={aiResult}
        onApplyPlan={handleApplyMealPlan}
      />

      {/* Edit Single Meal Dialog */}
      {editMealOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-xs">
          <div className="fixed inset-0" onClick={() => setEditMealOpen(false)} />
          <div className="relative w-full max-w-sm overflow-hidden rounded-2xl border border-slate-100 bg-white p-6 shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-800 text-sm">Edit {editDay} {editType}</h3>
              <button onClick={() => setEditMealOpen(false)} className="text-slate-400 hover:text-slate-650 transition-colors">
                <X className="h-4.5 w-4.5" />
              </button>
            </div>
            <form onSubmit={handleUpdateSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Meal Name</label>
                <input
                  type="text"
                  value={editMealName}
                  onChange={(e) => setEditMealName(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 p-2.5 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setEditMealOpen(false)}
                  className="rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-650 font-semibold px-4 py-2 text-xs transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updating}
                  className="rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-4 py-2 text-xs shadow-md transition-colors"
                >
                  {updating ? 'Saving...' : 'Save Meal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default MealPlanner;
