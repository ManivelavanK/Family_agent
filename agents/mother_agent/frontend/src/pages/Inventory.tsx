import React, { useState, useEffect } from 'react';
import { inventoryService } from '../services/inventoryService';
import { shoppingService } from '../services/shoppingService';
import { InventoryItem } from '../types/inventory';
import { InventoryTable } from '../components/inventory/InventoryTable';
import { PredictionCard } from '../components/inventory/PredictionCard';
import { Plus, Search, Filter, Loader2, Sparkles, X } from 'lucide-react';

export const Inventory: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');

  // Modals state
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  
  // Form States
  const [name, setName] = useState('');
  const [category, setCategory] = useState<InventoryItem['category']>('Staples');
  const [quantity, setQuantity] = useState(1);
  const [unit, setUnit] = useState('kg');
  const [avgWeeklyCons, setAvgWeeklyCons] = useState(1);
  const [purchaseDate, setPurchaseDate] = useState(new Date().toISOString().split('T')[0]);
  const [expiryDate, setExpiryDate] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const categories: InventoryItem['category'][] = [
    'Staples', 'Vegetables', 'Fruits', 'Dairy', 'Snacks', 'Beverages', 'Cleaning', 'Personal Care', 'Other'
  ];

  const loadInventory = async () => {
    setLoading(true);
    try {
      const data = await inventoryService.getInventory();
      setInventory(data);
      if (data.length > 0) {
        setSelectedItem(data[0]); // Default to first item for prediction preview
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInventory();
  }, []);

  const handleAddToShoppingList = async (item: InventoryItem) => {
    try {
      await shoppingService.addShoppingItem({
        name: item.name,
        quantity: Math.ceil(item.averageWeeklyConsumption * 2),
        unit: item.unit,
        category: item.category,
        estimatedPrice: item.category === 'Staples' ? 250 : 80,
        priority: 'Must Buy',
        aiReason: `Pantry is running low (${item.expectedRemainingDays} days remaining).`,
        checked: false
      });
      alert(`${item.name} has been added to your shopping list!`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteItem = async (id: string) => {
    if (!confirm('Are you sure you want to delete this item?')) return;
    try {
      await inventoryService.deleteInventoryItem(id);
      setInventory(prev => prev.filter(item => item.id !== id));
      if (selectedItem?.id === id) {
        setSelectedItem(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenAddModal = () => {
    setName('');
    setCategory('Staples');
    setQuantity(1);
    setUnit('kg');
    setAvgWeeklyCons(1);
    setPurchaseDate(new Date().toISOString().split('T')[0]);
    setExpiryDate('');
    setAddModalOpen(true);
  };

  const handleOpenEditModal = (item: InventoryItem) => {
    setEditingId(item.id);
    setName(item.name);
    setCategory(item.category);
    setQuantity(item.quantity);
    setUnit(item.unit);
    setAvgWeeklyCons(item.averageWeeklyConsumption);
    setPurchaseDate(item.purchaseDate);
    setExpiryDate(item.expiryDate);
    setEditModalOpen(true);
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const added = await inventoryService.addInventoryItem({
        name,
        category,
        quantity,
        unit,
        averageWeeklyConsumption: avgWeeklyCons,
        purchaseDate,
        expiryDate
      });
      setInventory(prev => [added, ...prev]);
      setSelectedItem(added);
      setAddModalOpen(false);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingId) return;
    setSubmitting(true);
    try {
      const updated = await inventoryService.updateInventoryItem(editingId, {
        name,
        category,
        quantity,
        unit,
        averageWeeklyConsumption: avgWeeklyCons,
        purchaseDate,
        expiryDate
      });
      setInventory(prev => prev.map(item => item.id === editingId ? updated : item));
      setSelectedItem(updated);
      setEditModalOpen(false);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  // Filter computation
  const filteredInventory = inventory.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
    const matchesStatus = selectedStatus === 'All' || item.status === selectedStatus;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header and Add Button */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Pantry & Inventory</h1>
          <p className="text-slate-500 font-medium text-xs mt-1">Manage kitchen assets and track predicted depletion dates.</p>
        </div>
        <button
          onClick={handleOpenAddModal}
          className="flex items-center justify-center gap-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 px-4 text-xs shadow-md shadow-indigo-100 transition-colors self-start sm:self-auto cursor-pointer"
        >
          <Plus className="h-4 w-4" />
          Add Item
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center gap-4 bg-white p-4 rounded-xl border border-slate-100 shadow-2xs">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search className="h-4 w-4" />
          </span>
          <input
            type="text"
            placeholder="Search item name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-4 text-xs font-medium focus:border-indigo-500 focus:outline-none focus:bg-white transition-colors"
          />
        </div>

        {/* Category Filter */}
        <div className="flex items-center gap-2">
          <Filter className="h-4.5 w-4.5 text-slate-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="rounded-lg border border-slate-200 py-2 px-3 text-xs font-semibold text-slate-600 bg-white focus:border-indigo-500 focus:outline-none"
          >
            <option value="All">All Categories</option>
            {categories.map((cat, idx) => (
              <option key={idx} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="rounded-lg border border-slate-200 py-2 px-3 text-xs font-semibold text-slate-600 bg-white focus:border-indigo-500 focus:outline-none"
          >
            <option value="All">All Statuses</option>
            <option value="Sufficient">Sufficient</option>
            <option value="Moderate">Moderate</option>
            <option value="Low Stock">Low Stock</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main List */}
          <div className="lg:col-span-2">
            <InventoryTable
              items={filteredInventory}
              onEdit={handleOpenEditModal}
              onDelete={handleDeleteItem}
              onAddToShoppingList={handleAddToShoppingList}
            />
          </div>

          {/* Side Predictive Dashboard Panel */}
          <div>
            <div className="sticky top-20 space-y-4">
              <div className="flex items-center gap-2 font-bold text-slate-800 text-sm">
                <Sparkles className="h-4 w-4 text-indigo-600 animate-pulse" />
                <span>AI Prediction Insights</span>
              </div>
              {selectedItem ? (
                <PredictionCard
                  item={selectedItem}
                  onAddToShoppingList={handleAddToShoppingList}
                />
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50/50 p-6 text-center text-slate-500">
                  Select an item to view predictive metrics.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add Modal */}
      {addModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-xs">
          <div className="fixed inset-0" onClick={() => setAddModalOpen(false)} />
          <div className="relative w-full max-w-md overflow-hidden rounded-2xl border border-slate-100 bg-white p-6 shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-800 text-sm">Add Grocery Item</h3>
              <button onClick={() => setAddModalOpen(false)} className="text-slate-400 hover:text-slate-650 transition-colors">
                <X className="h-4.5 w-4.5" />
              </button>
            </div>
            <form onSubmit={handleAddSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Item Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as any)}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none bg-white"
                  >
                    {categories.map((cat, idx) => (
                      <option key={idx} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Weekly Consumption</label>
                  <input
                    type="number"
                    step="0.1"
                    value={avgWeeklyCons}
                    onChange={(e) => setAvgWeeklyCons(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Quantity</label>
                  <input
                    type="number"
                    step="0.1"
                    value={quantity}
                    onChange={(e) => setQuantity(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Unit</label>
                  <input
                    type="text"
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Purchase Date</label>
                  <input
                    type="date"
                    value={purchaseDate}
                    onChange={(e) => setPurchaseDate(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Expiry Date</label>
                  <input
                    type="date"
                    value={expiryDate}
                    onChange={(e) => setExpiryDate(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setAddModalOpen(false)}
                  className="rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 font-semibold px-4 py-2 text-xs transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-4 py-2 text-xs shadow-md transition-colors"
                >
                  {submitting ? 'Adding...' : 'Add Item'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-xs">
          <div className="fixed inset-0" onClick={() => setEditModalOpen(false)} />
          <div className="relative w-full max-w-md overflow-hidden rounded-2xl border border-slate-100 bg-white p-6 shadow-xl transition-all">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-800 text-sm">Edit Grocery Item</h3>
              <button onClick={() => setEditModalOpen(false)} className="text-slate-400 hover:text-slate-650 transition-colors">
                <X className="h-4.5 w-4.5" />
              </button>
            </div>
            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Item Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as any)}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none bg-white"
                  >
                    {categories.map((cat, idx) => (
                      <option key={idx} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Weekly Consumption</label>
                  <input
                    type="number"
                    step="0.1"
                    value={avgWeeklyCons}
                    onChange={(e) => setAvgWeeklyCons(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Quantity</label>
                  <input
                    type="number"
                    step="0.1"
                    value={quantity}
                    onChange={(e) => setQuantity(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Unit</label>
                  <input
                    type="text"
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Purchase Date</label>
                  <input
                    type="date"
                    value={purchaseDate}
                    onChange={(e) => setPurchaseDate(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Expiry Date</label>
                  <input
                    type="date"
                    value={expiryDate}
                    onChange={(e) => setExpiryDate(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 p-2 text-xs font-semibold focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setEditModalOpen(false)}
                  className="rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 font-semibold px-4 py-2 text-xs transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-4 py-2 text-xs shadow-md transition-colors"
                >
                  {submitting ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default Inventory;
