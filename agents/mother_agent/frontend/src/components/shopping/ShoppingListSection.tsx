import React from 'react';
import { ShoppingItem } from '../../types/shopping';
import { Sparkles, Trash2 } from 'lucide-react';

interface ShoppingListSectionProps {
  title: string;
  items: ShoppingItem[];
  variant: 'must' | 'consider' | 'available';
  onToggleCheck: (id: string, checked: boolean) => void;
  onDeleteItem: (id: string) => void;
}

export const ShoppingListSection: React.FC<ShoppingListSectionProps> = ({
  title,
  items,
  variant,
  onToggleCheck,
  onDeleteItem
}) => {
  const getHeaderStyle = () => {
    switch (variant) {
      case 'must':
        return 'text-rose-600 bg-rose-50 border-rose-100';
      case 'consider':
        return 'text-amber-600 bg-amber-50 border-amber-100';
      case 'available':
        return 'text-emerald-600 bg-emerald-50 border-emerald-100';
    }
  };

  const getDotStyle = () => {
    switch (variant) {
      case 'must': return 'bg-rose-500';
      case 'consider': return 'bg-amber-500';
      case 'available': return 'bg-emerald-500';
    }
  };

  if (items.length === 0) return null;

  return (
    <div className="mb-6">
      <div className={`inline-flex items-center gap-2 border px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-4 ${getHeaderStyle()}`}>
        <span className={`h-2.5 w-2.5 rounded-full ${getDotStyle()}`} />
        {title} ({items.length})
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <div 
            key={item.id} 
            className={`
              flex flex-col md:flex-row md:items-center justify-between rounded-xl border border-slate-100 p-4 transition-all hover:shadow-xs
              ${item.checked ? 'bg-slate-50/70 border-slate-200/60 opacity-70' : 'bg-white'}
            `}
          >
            <div className="flex items-start gap-3">
              <input 
                type="checkbox"
                checked={item.checked}
                onChange={(e) => onToggleCheck(item.id, e.target.checked)}
                className="mt-1 h-4 w-4 rounded-sm border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
              />
              <div>
                <div className="flex items-center gap-2.5">
                  <span className={`font-semibold text-slate-800 ${item.checked ? 'line-through text-slate-400' : ''}`}>
                    {item.name}
                  </span>
                  <span className="text-xs bg-slate-100 text-slate-500 font-medium px-2 py-0.5 rounded-md">
                    {item.quantity} {item.unit}
                  </span>
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                    {item.category}
                  </span>
                </div>

                {item.aiReason && !item.checked && (
                  <div className="mt-1.5 flex items-start gap-1 text-[11px] font-medium text-indigo-600">
                    <Sparkles className="h-3 w-3 mt-0.5 shrink-0" />
                    <span>{item.aiReason}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="mt-3 md:mt-0 flex items-center justify-between md:justify-end gap-4 border-t border-slate-55 pt-3 md:border-none md:pt-0">
              <span className="text-sm font-bold text-slate-800">
                ₹{item.estimatedPrice}
              </span>
              <button 
                onClick={() => onDeleteItem(item.id)}
                className="rounded-lg p-1.5 hover:bg-rose-50 text-slate-400 hover:text-rose-600 transition-colors"
                title="Remove Item"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
export default ShoppingListSection;
