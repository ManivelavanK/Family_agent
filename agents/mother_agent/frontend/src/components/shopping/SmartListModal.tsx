import React from 'react';
import { ShoppingItem } from '../../types/shopping';
import { Sparkles, Loader2, Check } from 'lucide-react';

interface SmartListModalProps {
  isOpen: boolean;
  onClose: () => void;
  loading: boolean;
  recommendedItems: Omit<ShoppingItem, 'id' | 'checked'>[];
  estimatedTotal: number;
  onAddAll: () => void;
}

export const SmartListModal: React.FC<SmartListModalProps> = ({
  isOpen,
  onClose,
  loading,
  recommendedItems,
  estimatedTotal,
  onAddAll
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-xs">
      <div 
        className="fixed inset-0" 
        onClick={loading ? undefined : onClose}
      />

      <div className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-slate-100 bg-white p-6 shadow-xl transition-all">
        {/* Sparkles background icon decoration */}
        <div className="absolute -top-3 -right-3 text-indigo-500/10 font-bold text-7xl select-none pointer-events-none">
          ✨
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <Loader2 className="h-10 w-10 animate-spin text-indigo-600 mb-4" />
            <h3 className="text-lg font-bold text-slate-800">✨ Mother Agent is analyzing...</h3>
            <p className="mt-2 text-xs font-semibold text-indigo-600 uppercase tracking-widest animate-pulse">Checking inventory, consumption trends, budgets & meal plans...</p>
          </div>
        ) : (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="h-5 w-5 text-indigo-600 animate-pulse" />
              <h3 className="text-lg font-bold text-slate-800">AI Generated Shopping List</h3>
            </div>

            <p className="text-xs text-slate-500 font-medium mb-4">
              Based on your family size (4 members), diet preferences (South Indian), scheduled meal planning, and predicted depletion models.
            </p>

            <div className="max-h-60 overflow-y-auto border-y border-slate-100 py-3 space-y-3">
              {recommendedItems.map((item, idx) => (
                <div key={idx} className="flex justify-between rounded-xl bg-slate-50 p-3.5 border border-slate-200/40">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-800 text-sm">{item.name}</span>
                      <span className="text-[10px] bg-indigo-50 text-indigo-700 font-bold px-1.5 py-0.5 rounded-md border border-indigo-100">
                        {item.quantity} {item.unit}
                      </span>
                    </div>
                    <span className="block text-[11px] font-medium text-indigo-600 mt-1">
                      {item.aiReason}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="block text-sm font-bold text-slate-800">₹{item.estimatedPrice}</span>
                    <span className="text-[10px] text-slate-400 font-medium">{item.category}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between mt-5 mb-6 bg-indigo-50/50 rounded-xl p-4 border border-indigo-100/50">
              <div>
                <span className="block text-xs font-semibold text-indigo-700 uppercase tracking-wider">Estimated Total Cost</span>
                <span className="text-xs text-slate-500 font-medium">Within your remaining budget</span>
              </div>
              <span className="text-2xl font-bold text-slate-900">₹{estimatedTotal}</span>
            </div>

            <div className="flex justify-end gap-3">
              <button 
                onClick={onClose}
                className="rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 font-semibold px-4 py-2.5 text-xs transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={onAddAll}
                className="flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-5 py-2.5 text-xs shadow-md shadow-indigo-100 transition-colors"
              >
                <Check className="h-4 w-4" />
                Add All to List
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
export default SmartListModal;
