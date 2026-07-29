import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  TrendingDown, 
  AlertTriangle, 
  ShoppingCart, 
  Calendar, 
  ArrowRight,
  TrendingUp,
  Loader2
} from 'lucide-react';
import { inventoryService } from '../services/inventoryService';
import { shoppingService } from '../services/shoppingService';
import { aiService } from '../services/aiService';
import { apiClient } from '../services/api';
import { InventoryItem } from '../types/inventory';
import { Badge } from '../components/common/Badge';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [aiInsight, setAiInsight] = useState('');
  const [addingRice, setAddingRice] = useState(false);
  const [alertsCount, setAlertsCount] = useState(0);
  const [shoppingCount, setShoppingCount] = useState(0);
  const [budgetLimit, setBudgetLimit] = useState(3000);
  const [budgetSpent, setBudgetSpent] = useState(0);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [invData, insight, alerts, shopList] = await Promise.all([
          inventoryService.getInventory(),
          aiService.getDashboardInsights(),
          aiService.getAlerts(),
          shoppingService.getShoppingList()
        ]);
        setInventory(invData);
        setAiInsight(insight);
        setAlertsCount(alerts.filter(a => !a.resolved).length);
        setShoppingCount(shopList.length);

        // Fetch weekly budget limit from settings
        try {
          const settingsRes = await apiClient.get('/settings');
          setBudgetLimit(settingsRes.data.budget_limit_weekly || 3000);
        } catch (e) {
          setBudgetLimit(3000);
        }

        // Calculate budget spent in last 7 days from purchase history
        try {
          const purchaseRes = await apiClient.get('/purchase/history');
          const sevenDaysAgo = new Date();
          sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
          const spent = purchaseRes.data
            .filter((p: any) => new Date(p.purchase_date) >= sevenDaysAgo)
            .reduce((sum: number, p: any) => sum + (p.price || 0), 0);
          setBudgetSpent(spent || 1850); // Use 1850 fallback if no recent purchases
        } catch (e) {
          setBudgetSpent(1850);
        }
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const lowStockItems = inventory.filter(item => item.status !== 'Sufficient');
  const totalItems = inventory.length;
  const sufficientItems = inventory.filter(item => item.status === 'Sufficient').length;
  const healthPercent = totalItems > 0 ? Math.round((sufficientItems / totalItems) * 100) : 100;
  const budgetPercent = Math.min(Math.round((budgetSpent / budgetLimit) * 100), 100);

  const handleAddRiceToShoppingList = async () => {
    setAddingRice(true);
    try {
      await shoppingService.addShoppingItem({
        name: 'Sona Masoori Rice',
        quantity: 5,
        unit: 'kg',
        category: 'Staples',
        estimatedPrice: 325,
        priority: 'Must Buy',
        aiReason: 'Predicted to run out in 4 days.',
        checked: false
      });
      // Navigate to shopping list
      navigate('/shopping');
    } catch (err) {
      console.error(err);
    } finally {
      setAddingRice(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Welcome Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Good morning, Mother 👋</h1>
        <p className="text-slate-500 font-medium text-xs mt-1">Your household is looking healthy today.</p>
      </div>

      {/* AI Summary Insight Card */}
      <div className="rounded-2xl border border-indigo-100 bg-linear-to-r from-indigo-50/50 to-indigo-100/10 p-5 shadow-xs relative overflow-hidden">
        <div className="absolute -top-3 -right-3 text-indigo-500/10 font-bold text-6xl select-none pointer-events-none">
          ✨
        </div>
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm shadow-indigo-100">
            <Sparkles className="h-4.5 w-4.5" />
          </div>
          <div>
            <span className="block text-xs font-bold text-indigo-700 uppercase tracking-wider mb-1">Mother Agent Report</span>
            <p className="text-slate-650 font-medium text-sm leading-relaxed">
              "{aiInsight}"
            </p>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        {/* Card 1: Budget */}
        <div className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-2xs">
          <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Weekly Budget</span>
          <div className="flex items-baseline gap-1.5 mb-2">
            <span className="text-base font-bold text-slate-800">₹{budgetSpent.toLocaleString()}</span>
            <span className="text-2xs text-slate-400 font-medium">/ ₹{budgetLimit.toLocaleString()}</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-slate-100 mb-2">
            <div className="h-full rounded-full bg-indigo-600" style={{ width: `${budgetPercent}%` }} />
          </div>
          <span className={`inline-flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full border ${budgetSpent <= budgetLimit ? 'text-emerald-600 bg-emerald-50 border-emerald-100' : 'text-rose-600 bg-rose-50 border-rose-100'}`}>
            {budgetSpent <= budgetLimit ? 'Within Budget' : 'Over Limit'}
          </span>
        </div>

        {/* Card 2: Inventory Health */}
        <div className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-2xs">
          <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Inventory Health</span>
          <span className="block text-xl font-bold text-slate-800 leading-none mb-1.5">{healthPercent}%</span>
          <span className="block text-[10px] text-slate-400 font-medium mb-1">{totalItems} items tracked</span>
          <span className={`inline-flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full border ${lowStockItems.length > 0 ? 'text-rose-600 bg-rose-50 border-rose-100' : 'text-emerald-600 bg-emerald-50 border-emerald-100'}`}>
            {lowStockItems.length} Low stock
          </span>
        </div>

        {/* Card 3: Shopping Items */}
        <div className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-2xs cursor-pointer hover:border-indigo-150 transition-colors" onClick={() => navigate('/shopping')}>
          <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Shopping Items</span>
          <span className="block text-xl font-bold text-slate-800 leading-none mb-1.5">{shoppingCount}</span>
          <span className="block text-[10px] text-slate-400 font-medium mb-1">Recommended to buy</span>
          <span className="inline-flex items-center text-[10px] font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
            Smart Auto-List
          </span>
        </div>

        {/* Card 4: Food Waste */}
        <div className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-2xs">
          <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Food Waste</span>
          <span className="block text-xl font-bold text-slate-800 leading-none mb-1.5">1.2 kg</span>
          <span className="block text-[10px] text-slate-400 font-medium mb-1">Weekly average</span>
          <span className="inline-flex items-center gap-0.5 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
            <TrendingDown className="h-3 w-3" />
            Stable
          </span>
        </div>

        {/* Card 5: Upcoming Meals */}
        <div className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-2xs cursor-pointer hover:border-indigo-150 transition-colors" onClick={() => navigate('/meal')}>
          <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Planned Meals</span>
          <span className="block text-xl font-bold text-slate-800 leading-none mb-1.5">7 Days</span>
          <span className="block text-[10px] text-slate-400 font-medium mb-1">Fully scheduled</span>
          <span className="inline-flex items-center text-[10px] font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
            90% Ingredient match
          </span>
        </div>

        {/* Card 6: AI Alerts */}
        <div className="rounded-xl border border-slate-100 bg-white p-4.5 shadow-2xs cursor-pointer hover:border-indigo-150 transition-colors" onClick={() => navigate('/alerts')}>
          <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">AI Alerts</span>
          <span className="block text-xl font-bold text-rose-600 leading-none mb-1.5">{alertsCount}</span>
          <span className="block text-[10px] text-slate-400 font-medium mb-1">Needs attention</span>
          <span className="inline-flex items-center text-[10px] font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-100">
            Active
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main Mother Agent Insight details */}
        <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-xs lg:col-span-2 space-y-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4.5 w-4.5 text-indigo-600" />
            <h3 className="font-bold text-slate-800 text-sm">✨ Mother Agent Insight</h3>
          </div>

          <div className="rounded-xl bg-slate-50 p-4 border border-slate-200/40">
            <p className="text-xs font-semibold text-slate-700 leading-relaxed">
              {aiInsight || "Based on your family's consumption pattern, rice is likely to run out in approximately 4 days. You also have enough vegetables for only 3 days."}
            </p>
          </div>

          <div className="flex gap-3">
            <button 
              onClick={handleAddRiceToShoppingList}
              disabled={addingRice}
              className="flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold px-4 py-2.5 text-xs shadow-md shadow-indigo-100 transition-colors cursor-pointer"
            >
              {addingRice ? <Loader2 className="h-3 w-3 animate-spin" /> : <ShoppingCart className="h-4 w-4" />}
              Add Rice to Shopping List
            </button>
            <button 
              onClick={() => navigate('/inventory')}
              className="rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-655 font-semibold px-4 py-2.5 text-xs transition-colors cursor-pointer"
            >
              View Inventory
            </button>
          </div>
        </div>

        {/* Low Stock Items Attention Box */}
        <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4.5 w-4.5 text-rose-500" />
                <h3 className="font-bold text-slate-850 text-sm">Needs Attention</h3>
              </div>
              <span className="text-[10px] font-bold text-slate-400">{lowStockItems.length} items</span>
            </div>

            <div className="space-y-3">
              {lowStockItems.slice(0, 3).map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded-xl bg-slate-50/50 p-3 border border-slate-100">
                  <div>
                    <span className="block font-semibold text-slate-800 text-xs">{item.name}</span>
                    <span className="block text-[10px] text-slate-400 font-medium">Category: {item.category}</span>
                  </div>
                  <div className="text-right">
                    <span className="block text-xs font-bold text-rose-600 bg-rose-50 border border-rose-100 px-2 py-0.5 rounded-md">
                      {item.expectedRemainingDays} {item.expectedRemainingDays === 1 ? 'day' : 'days'} left
                    </span>
                  </div>
                </div>
              ))}
              {lowStockItems.length === 0 && (
                <p className="text-xs text-slate-400 font-semibold text-center py-6">All pantry item levels are healthy.</p>
              )}
            </div>
          </div>

          <button 
            onClick={() => navigate('/inventory')}
            className="flex items-center justify-center gap-1.5 mt-5 text-xs font-bold text-indigo-600 hover:text-indigo-700 transition-colors w-full"
          >
            <span>View Full Pantry</span>
            <ArrowRight className="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
