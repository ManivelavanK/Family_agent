import React, { useState } from 'react';
import { Sparkles, Loader2, Check, HelpCircle } from 'lucide-react';
import { AIMealPlanResponse, AIMealPlanGeneratorInputs } from '../../services/mealService';

interface AIMealPlannerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (inputs: AIMealPlanGeneratorInputs) => Promise<void>;
  loading: boolean;
  result: AIMealPlanResponse | null;
  onApplyPlan: () => void;
}

export const AIMealPlannerModal: React.FC<AIMealPlannerModalProps> = ({
  isOpen,
  onClose,
  onGenerate,
  loading,
  result,
  onApplyPlan
}) => {
  const [familyMembers, setFamilyMembers] = useState(4);
  const [budget, setBudget] = useState(3000);
  const [preferences, setPreferences] = useState('South Indian Vegetarian');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate({
      familyMembers,
      budget,
      preferences,
      availableIngredients: [] // Passed down from active inventory implicitly in service
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-xs">
      <div 
        className="fixed inset-0" 
        onClick={loading ? undefined : onClose}
      />

      <div className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-slate-100 bg-white p-6 shadow-xl transition-all">
        {/* Sparkles background icon decoration */}
        <div className="absolute -top-3 -right-3 text-indigo-500/10 font-bold text-7xl select-none pointer-events-none">
          ✨
        </div>

        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="h-5 w-5 text-indigo-600 animate-pulse" />
          <h3 className="text-lg font-bold text-slate-800">AI Weekly Meal Planner</h3>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <Loader2 className="h-10 w-10 animate-spin text-indigo-600 mb-4" />
            <h3 className="text-lg font-bold text-slate-800">✨ Mother Agent is modeling meal charts...</h3>
            <p className="mt-2 text-xs font-semibold text-indigo-600 uppercase tracking-widest animate-pulse">Running recipe simulations, nutrient checks, and waste profiles...</p>
          </div>
        ) : !result ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-xs text-slate-500 font-medium">
              Specify your parameters below. The agent will balance your weekly budget against available pantry items to optimize meal schedules.
            </p>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Family Members</label>
                <input 
                  type="number"
                  value={familyMembers}
                  onChange={(e) => setFamilyMembers(Number(e.target.value))}
                  className="w-full rounded-xl border border-slate-200 p-3 text-sm focus:border-indigo-500 focus:outline-none"
                  min={1}
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Weekly Budget (₹)</label>
                <input 
                  type="number"
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                  className="w-full rounded-xl border border-slate-200 p-3 text-sm focus:border-indigo-500 focus:outline-none"
                  min={100}
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Dietary Preferences</label>
              <select 
                value={preferences}
                onChange={(e) => setPreferences(e.target.value)}
                className="w-full rounded-xl border border-slate-200 p-3 text-sm focus:border-indigo-500 focus:outline-none bg-white"
              >
                <option value="South Indian Vegetarian">South Indian Vegetarian</option>
                <option value="North Indian Vegetarian">North Indian Vegetarian</option>
                <option value="Mixed Indian Diet">Mixed Indian Diet</option>
                <option value="Low Carb / Keto Friendly">Low Carb / Keto Friendly</option>
              </select>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button 
                type="button"
                onClick={onClose}
                className="rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 font-semibold px-4 py-2.5 text-xs transition-colors"
              >
                Cancel
              </button>
              <button 
                type="submit"
                className="rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-5 py-2.5 text-xs shadow-md shadow-indigo-100 transition-colors"
              >
                Generate Weekly Plan
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <p className="text-xs text-slate-500 font-medium">
              Weekly meal plan generated successfully. Ingredients have been analyzed against current kitchen inventory.
            </p>

            <div className="max-h-60 overflow-y-auto border border-slate-100 rounded-xl divide-y divide-slate-100 bg-slate-50/50 p-1">
              <div className="p-3 bg-white rounded-lg border border-indigo-100/40 mb-2">
                <span className="block text-[10px] font-bold text-indigo-600 uppercase tracking-wider">AI Waste Reduction Tip</span>
                <p className="text-xs text-slate-600 mt-1 font-medium leading-normal">{result.wasteReductionSuggestion}</p>
              </div>

              <div className="p-3">
                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Missing Ingredients (₹{result.estimatedCost} Total)</span>
                <div className="space-y-2">
                  {result.missingIngredients.map((ing, idx) => (
                    <div key={idx} className="flex justify-between text-xs font-semibold text-slate-700">
                      <span>{ing.name} ({ing.quantity})</span>
                      <span className="text-slate-500">₹{ing.cost}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button 
                onClick={onClose}
                className="rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 font-semibold px-4 py-2.5 text-xs transition-colors"
              >
                Back
              </button>
              <button 
                onClick={onApplyPlan}
                className="flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-5 py-2.5 text-xs shadow-md shadow-indigo-100 transition-colors"
              >
                <Check className="h-4 w-4" />
                Apply Plan & Add Missing to Shopping List
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
export default AIMealPlannerModal;
