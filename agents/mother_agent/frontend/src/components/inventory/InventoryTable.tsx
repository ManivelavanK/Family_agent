import React from 'react';
import { InventoryItem } from '../../types/inventory';
import { Badge } from '../common/Badge';
import { ShoppingCart, Edit, Trash2 } from 'lucide-react';

interface InventoryTableProps {
  items: InventoryItem[];
  onEdit: (item: InventoryItem) => void;
  onDelete: (id: string) => void;
  onAddToShoppingList: (item: InventoryItem) => void;
}

export const InventoryTable: React.FC<InventoryTableProps> = ({
  items,
  onEdit,
  onDelete,
  onAddToShoppingList
}) => {
  const getStatusVariant = (status: InventoryItem['status']) => {
    switch (status) {
      case 'Sufficient': return 'success';
      case 'Moderate': return 'warning';
      case 'Low Stock': return 'error';
      default: return 'info';
    }
  };

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white py-12 px-4 text-center">
        <span className="text-4xl">📦</span>
        <h3 className="mt-4 text-lg font-bold text-slate-800">No grocery items found</h3>
        <p className="mt-1 text-sm text-slate-500">Try adjusting your filters or add a new inventory item above.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Desktop Table view */}
      <div className="hidden md:block overflow-x-auto rounded-xl border border-slate-100 bg-white shadow-xs">
        <table className="w-full border-collapse text-left text-sm text-slate-500">
          <thead className="bg-slate-55/60 text-xs font-semibold uppercase tracking-wider text-slate-600 border-b border-slate-100">
            <tr>
              <th scope="col" className="px-6 py-4">Item</th>
              <th scope="col" className="px-6 py-4">Category</th>
              <th scope="col" className="px-6 py-4 text-right">Quantity</th>
              <th scope="col" className="px-6 py-4 text-center">Expected Remaining</th>
              <th scope="col" className="px-6 py-4">Status</th>
              <th scope="col" className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-6 py-4 font-semibold text-slate-900">{item.name}</td>
                <td className="px-6 py-4 text-slate-600 font-medium">{item.category}</td>
                <td className="px-6 py-4 text-right font-medium text-slate-950">
                  {item.quantity} <span className="text-slate-400 font-normal">{item.unit}</span>
                </td>
                <td className="px-6 py-4 text-center font-medium text-slate-800">
                  {item.expectedRemainingDays} {item.expectedRemainingDays === 1 ? 'day' : 'days'}
                </td>
                <td className="px-6 py-4">
                  <Badge variant={getStatusVariant(item.status)}>{item.status}</Badge>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex justify-end gap-2">
                    {item.status !== 'Sufficient' && (
                      <button
                        onClick={() => onAddToShoppingList(item)}
                        className="rounded-lg p-1.5 hover:bg-indigo-50 text-indigo-600 transition-colors"
                        title="Add to Shopping List"
                      >
                        <ShoppingCart className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      onClick={() => onEdit(item)}
                      className="rounded-lg p-1.5 hover:bg-slate-100 text-slate-500 hover:text-slate-700 transition-colors"
                      title="Edit Item"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => onDelete(item.id)}
                      className="rounded-lg p-1.5 hover:bg-rose-50 text-rose-500 hover:text-rose-700 transition-colors"
                      title="Delete Item"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card list view */}
      <div className="grid grid-cols-1 gap-4 md:hidden">
        {items.map((item) => (
          <div key={item.id} className="rounded-xl border border-slate-100 bg-white p-5 shadow-xs flex flex-col justify-between gap-4">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-semibold text-slate-900 leading-tight">{item.name}</h4>
                <span className="text-xs text-slate-400 font-medium">{item.category}</span>
              </div>
              <Badge variant={getStatusVariant(item.status)}>{item.status}</Badge>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs border-y border-slate-50 py-3">
              <div>
                <span className="block text-slate-400 font-medium">Quantity</span>
                <span className="text-sm font-semibold text-slate-800">{item.quantity} {item.unit}</span>
              </div>
              <div>
                <span className="block text-slate-400 font-medium">Remaining</span>
                <span className="text-sm font-semibold text-slate-800">{item.expectedRemainingDays} days</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-indigo-600">AI Confidence: {item.aiConfidence}%</span>
              <div className="flex gap-2">
                {item.status !== 'Sufficient' && (
                  <button
                    onClick={() => onAddToShoppingList(item)}
                    className="flex items-center justify-center rounded-lg p-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 transition-colors"
                  >
                    <ShoppingCart className="h-4 w-4" />
                  </button>
                )}
                <button
                  onClick={() => onEdit(item)}
                  className="flex items-center justify-center rounded-lg p-2 bg-slate-50 hover:bg-slate-100 text-slate-500 hover:text-slate-700 transition-colors"
                >
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={() => onDelete(item.id)}
                  className="flex items-center justify-center rounded-lg p-2 bg-rose-50 hover:bg-rose-100 text-rose-600 transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
export default InventoryTable;
