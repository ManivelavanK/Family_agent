import React, { useState, useEffect } from 'react';
import { shoppingService, AISmartListResponse } from '../services/shoppingService';
import { ShoppingItem } from '../types/shopping';
import { ShoppingListSection } from '../components/shopping/ShoppingListSection';
import { SmartListModal } from '../components/shopping/SmartListModal';
import { Sparkles, Plus, Loader2, DollarSign } from 'lucide-react';

export const ShoppingList: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [shoppingList, setShoppingList] = useState<ShoppingItem[]>([]);
  
  // Smart list modal
  const [smartModalOpen, setSmartModalOpen] = useState(false);
  const [smartLoading, setSmartLoading] = useState(false);
  const [smartResult, setSmartResult] = useState<AISmartListResponse | null>(null);

  // Manual Add Form
  const [itemName, setItemName] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [unit, setUnit] = useState('kg');
  const [category, setCategory] = useState('Staples');
  const [price, setPrice] = useState(100);
  const [priority, setPriority] = useState<ShoppingItem['priority']>('Must Buy');
  const [adding, setAdding] = useState(false);

  const loadShoppingList = async () => {
    setLoading(true);
    try {
      const data = await shoppingService.getShoppingList();
      setShoppingList(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadShoppingList();
  }, []);

  const handleToggleCheck = async (id: string, checked: boolean) => {
    try {
      // Optimistic update
      setShoppingList(prev => prev.map(item => item.id === id ? { ...item, checked } : item));
      await shoppingService.updateShoppingItem(id, { checked });
    } catch (err) {
      console.error(err);
      loadShoppingList(); // rollback
    }
  };

  const handleDeleteItem = async (id: string) => {
    try {
      setShoppingList(prev => prev.filter(item => item.id !== id));
      await shoppingService.deleteShoppingItem(id);
    } catch (err) {
      console.error(err);
      loadShoppingList(); // rollback
    }
  };

  const handleManualAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!itemName.trim()) return;
    setAdding(true);
    try {
      const newItem = await shoppingService.addShoppingItem({
        name: itemName,
        quantity,
        unit,
        category,
        estimatedPrice: price,
        priority,
        checked: false
      });
      setShoppingList(prev => [newItem, ...prev]);
      setItemName('');
      setQuantity(1);
      setUnit('kg');
      setPrice(100);
    } catch (err) {
      console.error(err);
    } finally {
      setAdding(false);
    }
  };

  const handleTriggerSmartList = async () => {
    setSmartModalOpen(true);
    setSmartLoading(true);
    try {
      const result = await shoppingService.generateShoppingList();
      setSmartResult(result);
    } catch (err) {
      console.error(err);
    } finally {
      setSmartLoading(false);
    }
  };

  const handleAddAllSmartItems = async () => {
    if (!smartResult) return;
    try {
      await shoppingService.addAllToShoppingList(smartResult.items);
      setSmartModalOpen(false);
      setSmartResult(null);
      loadShoppingList(); // Reload lists
    } catch (err) {
      console.error(err);
    }
  };

  // Group items by priorities
  const mustBuyItems = shoppingList.filter(item => item.priority === 'Must Buy' && !item.checked);
  const considerItems = shoppingList.filter(item => item.priority === 'Consider Buying' && !item.checked);
  const alreadyAvailableItems = shoppingList.filter(item => item.priority === 'Already Available' || item.checked);

  // Stats calculation
  const totalCost = shoppingList.reduce((sum, item) => sum + (item.checked ? 0 : item.estimatedPrice), 0);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Smart Shopping List</h1>
          <p className="text-slate-500 font-medium text-xs mt-1">Review must-buy list and let the Mother Agent suggest needed goods.</p>
        </div>
        <button
          onClick={handleTriggerSmartList}
          className="flex items-center justify-center gap-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 px-4 text-xs shadow-md shadow-indigo-100 transition-colors cursor-pointer"
        >
          <Sparkles className="h-4 w-4 animate-pulse" />
          Generate Smart Shopping List
        </button>
      </div>

      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main List Sections */}
          <div className="lg:col-span-2 space-y-6">
            <ShoppingListSection
              title="Must Buy"
              items={mustBuyItems}
              variant="must"
              onToggleCheck={handleToggleCheck}
              onDeleteItem={handleDeleteItem}
            />

            <ShoppingListSection
              title="Consider Buying"
              items={considerItems}
              variant="consider"
              onToggleCheck={handleToggleCheck}
              onDeleteItem={handleDeleteItem}
            />

            <ShoppingListSection
              title="Already Available / Completed"
              items={alreadyAvailableItems}
              variant="available"
              onToggleCheck={handleToggleCheck}
              onDeleteItem={handleDeleteItem}
            />

            {shoppingList.length === 0 && (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white py-12 px-4 text-center">
                <span className="text-4xl">🛒</span>
                <h3 className="mt-4 text-lg font-bold text-slate-800">Your shopping list is empty</h3>
                <p className="mt-1 text-sm text-slate-500">Add custom items below or trigger the AI generator above.</p>
              </div>
            )}
          </div>

          {/* Sidebar Actions & Stats */}
          <div className="space-y-6">
            {/* Stats Card */}
            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-xs">
              <h3 className="font-bold text-slate-800 text-sm mb-4">Total Budget Projection</h3>
              <div className="flex items-center gap-3 bg-slate-50 rounded-xl p-4 border border-slate-100 mb-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                  <DollarSign className="h-5 w-5" />
                </div>
                <div>
                  <span className="block text-[10px] font-bold text-slate-450 uppercase tracking-wider">Estimated Total</span>
                  <span className="text-xl font-bold text-slate-900">₹{totalCost}</span>
                </div>
              </div>
              <p className="text-[10px] text-slate-400 font-semibold leading-normal">
                Estimated pricing does not include discounts. Items marked check/available are excluded from calculations.
              </p>
            </div>

            {/* Quick Add Custom Item */}
            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-xs">
              <h3 className="font-bold text-slate-800 text-sm mb-4">Quick Add Item</h3>
              <form onSubmit={handleManualAdd} className="space-y-3">
                <div>
                  <input
                    type="text"
                    placeholder="Item Name (e.g. Milk)"
                    value={itemName}
                    onChange={(e) => setItemName(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 p-2.5 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    placeholder="Qty"
                    value={quantity}
                    onChange={(e) => setQuantity(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-200 p-2.5 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    min={1}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Unit (e.g. kg)"
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 p-2.5 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    placeholder="Price (₹)"
                    value={price}
                    onChange={(e) => setPrice(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-200 p-2.5 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    min={1}
                    required
                  />
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as any)}
                    className="w-full rounded-lg border border-slate-200 p-2.5 text-xs font-semibold focus:border-indigo-500 focus:outline-none bg-white"
                  >
                    <option value="Must Buy">Must Buy</option>
                    <option value="Consider Buying">Consider Buying</option>
                    <option value="Already Available">Already Available</option>
                  </select>
                </div>
                <button
                  type="submit"
                  disabled={adding}
                  className="flex w-full items-center justify-center gap-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 text-xs transition-all shadow-xs cursor-pointer"
                >
                  <Plus className="h-4 w-4" />
                  Add to List
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Smart List Generator Modal */}
      <SmartListModal
        isOpen={smartModalOpen}
        onClose={() => setSmartModalOpen(false)}
        loading={smartLoading}
        recommendedItems={smartResult ? smartResult.items : []}
        estimatedTotal={smartResult ? smartResult.estimatedTotal : 0}
        onAddAll={handleAddAllSmartItems}
      />
    </div>
  );
};
export default ShoppingList;
