import React from 'react';
import { InventoryItem } from '../../types/inventory';
import { Sparkles, Calendar, TrendingDown, ShoppingCart } from 'lucide-react';

interface PredictionCardProps {
  item: InventoryItem;
  onAddToShoppingList: (item: InventoryItem) => void;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({ item, onAddToShoppingList }) => {
  return (
    <div className="rounded-2xl border border-slate-100 bg-linear-to-b from-indigo-50/30 to-indigo-100/10 p-6 shadow-xs relative overflow-hidden">
      {/* Sparkles background icon decoration */}
      <div className="absolute -top-3 -right-3 text-indigo-500/10 font-bold text-7xl select-none pointer-events-none">
        ✨
      </div>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4.5 w-4.5 text-indigo-600 animate-pulse" />
          <h3 className="font-bold text-slate-800 text-base">{item.name}</h3>
        </div>
        <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
          AI Confidence: {item.aiConfidence}%
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4 border-b border-indigo-50 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white shadow-xs border border-indigo-50 text-indigo-600">
            <span className="font-bold text-sm">{item.quantity}</span>
            <span className="text-[10px] text-slate-400 font-normal ml-0.5">{item.unit}</span>
          </div>
          <div>
            <span className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider">Current Stock</span>
            <span className="text-xs font-bold text-slate-700">In Kitchen</span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white shadow-xs border border-indigo-50 text-indigo-600">
            <TrendingDown className="h-4.5 w-4.5" />
          </div>
          <div>
            <span className="block text-[10px] font-medium text-slate-400 uppercase tracking-wider">Weekly Usage</span>
            <span className="text-xs font-bold text-slate-700">{item.averageWeeklyConsumption} {item.unit} / week</span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-slate-400" />
          <span className="text-sm font-medium text-slate-600">Estimated Depletion</span>
        </div>
        <span className="text-base font-bold text-slate-900 bg-rose-50 border border-rose-100 text-rose-700 px-3 py-1 rounded-lg">
          {item.predictedRemainingDays} {item.predictedRemainingDays === 1 ? 'day' : 'days'}
        </span>
      </div>

      {item.recommendation && (
        <div className="rounded-xl bg-white border border-indigo-50 p-3.5 shadow-xs mb-4">
          <span className="block text-[10px] font-bold text-indigo-600 uppercase tracking-wider mb-1">Recommendation</span>
          <p className="text-xs text-slate-600 leading-normal font-medium">{item.recommendation}</p>
        </div>
      )}

      <button
        onClick={() => onAddToShoppingList(item)}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 text-xs shadow-md shadow-indigo-100 active:scale-98 transition-all"
      >
        <ShoppingCart className="h-4 w-4" />
        Add to Shopping List
      </button>
    </div>
  );
};
export default PredictionCard;
