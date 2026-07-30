import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/useAuthStore';
import { useActiveTabStore } from '../store/useActiveTabStore';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShoppingCart, Trash2, Package, AlertTriangle, Calendar, TrendingUp, Sparkles, 
  ArrowRight, Check, AlertCircle
} from 'lucide-react';

import { motherApi } from '../api/motherApi';

export default function MotherAgent() {
  const { token } = useAuthStore();
  const { activeTabs, setActiveTab } = useActiveTabStore();
  const activeTab = activeTabs['/mother'] || 'dashboard';

  // API State
  const [toastMessage, setToastMessage] = useState('');
  
  const [budget, setBudget] = useState<any>({ spent: 1417, budget: 3000, status: "Within Budget" });
  const [inventoryHealth, setInventoryHealth] = useState<any>({ health: 79, lowStockCount: 6 });
  const [shoppingList, setShoppingList] = useState<any>({ items: [], totalCount: 28, badge: "Smart Auto-List" });
  const [foodWaste, setFoodWaste] = useState<any>({ amount: "1.2 kg", status: "Stable" });
  const [plannedMeals, setPlannedMeals] = useState<any>({ days: "7 Days", badge: "90% Ingredient match" });
  const [aiAlerts, setAiAlerts] = useState<any>({ count: 20, badge: "Active" });
  
  const [reportText, setReportText] = useState<string>("Pantry Check: Weekly inventory audit completed. | Waste Monitor: Milk carton expired due to negligence. | Budgeting: Spending reached 92% of budget limits.");
  const [insightsText, setInsightsText] = useState<string>("Zepto has a 10% discount on vegetables today. We need Spinach and Onions for the planned chicken curry.");
  const [expiringItems, setExpiringItems] = useState<any[]>([
    { name: "Rohu Fish", status: "Meat & Fish", days: 0 },
    { name: "Spinach", status: "Vegetables", days: 0 },
    { name: "Fresh Chicken", status: "Meat & Fish", days: 0 }
  ]);

  const [addingItem, setAddingItem] = useState(false);

  const fetchDashboardData = async () => {
    try {
      // 1. Fetch Report / Greeting Banner
      const dReport = await motherApi.getReport().catch(() => null);
      if (dReport) setReportText(dReport.report || dReport.text);

      // 2. Fetch Budget
      const dBudget = await motherApi.getBudget().catch(() => null);
      if (dBudget) setBudget(dBudget);

      // 3. Fetch Inventory Health
      const dInv = await motherApi.getPantry().catch(() => null);
      if (dInv) setInventoryHealth(dInv);

      // 4. Fetch Shopping Items
      const dShop = await motherApi.getShoppingList().catch(() => null);
      if (dShop) setShoppingList(dShop);

      // 5. Fetch Waste
      const dWaste = await motherApi.getFoodWaste().catch(() => null);
      if (dWaste) setFoodWaste(dWaste);

      // 6. Fetch Meals
      const dMeals = await motherApi.getMeals().catch(() => null);
      if (dMeals) setPlannedMeals(dMeals);

      // 7. Fetch Alerts
      const dAlerts = await motherApi.getAlerts().catch(() => null);
      if (dAlerts) setAiAlerts(dAlerts);

      // 8. Fetch Insights
      const dInsights = await motherApi.getInsights().catch(() => null);
      if (dInsights) setInsightsText(dInsights.insight || dInsights.text);

      // 9. Fetch Expiring Items
      const dExp = await motherApi.getExpiring().catch(() => null);
      if (dExp) setExpiringItems(dExp);

    } catch (err) {
      console.error("Error fetching Mother Agent data:", err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  const addRiceToShopping = async () => {
    setAddingItem(true);
    try {
      const res = await motherApi.addShoppingItem({
        name: "Rice",
        item: "Rice",
        quantity: "1 bag"
      });

      if (res && res.success) {
        showToast("Successfully added Rice to shopping list!");
        // Increment shopping item count locally for immediate response
        setShoppingList((prev: any) => ({
          ...prev,
          totalCount: (prev?.totalCount || 0) + 1,
          items: prev?.items ? [...prev.items, { id: Date.now(), name: "Rice", quantity: "1 bag", isPriority: false }] : []
        }));
      } else {
        showToast("Failed to add Rice to shopping list.");
      }
    } catch (error) {
      console.error(error);
      showToast("Offline mode: Simulated adding Rice.");
      setShoppingList((prev: any) => ({
        ...prev,
        totalCount: (prev?.totalCount || 0) + 1
      }));
    } finally {
      setAddingItem(false);
    }
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3000);
  };

  return (
    <div className="min-h-full bg-slate-50 text-slate-800 p-8 pb-12 transition-colors duration-300">
      
      {/* Toast Notification */}
      <AnimatePresence>
        {toastMessage && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-20 right-8 z-50 bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-emerald-800 text-xs font-semibold shadow-lg flex items-center space-x-2"
          >
            <Check className="w-4 h-4 text-emerald-600" />
            <span>{toastMessage}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Greeting Banner */}
      <div className="mb-8">
        <h2 className="text-2xl font-black text-slate-900 tracking-tight mb-1">Good morning, Mother 👋</h2>
        <p className="text-sm text-slate-500 font-medium mb-6">Your household is looking healthy today.</p>

        {/* Report Banner */}
        <div className="bg-purple-50/70 border border-purple-100/80 rounded-2xl p-6 relative overflow-hidden shadow-sm">
          <div className="flex items-start space-x-3 relative z-10">
            <div className="p-2 rounded-xl bg-purple-100 text-purple-700 mt-0.5">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] font-bold text-purple-700 tracking-wider uppercase block mb-1">Mother Agent Report</span>
              <p className="text-xs text-purple-900 font-medium leading-relaxed">
                {reportText}
              </p>
            </div>
          </div>
        </div>
      </div>

      {activeTab === 'dashboard' ? (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
          
          {/* Top 6 KPI Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            
            {/* Budget */}
            <div className="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-all">
              <div className="flex justify-between items-start mb-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Weekly Budget</span>
                <TrendingUp className="w-5 h-5 text-indigo-500" />
              </div>
              <div>
                <p className="text-lg font-black text-slate-800">₹{budget?.spent ?? 1417} / ₹{budget?.budget ?? 3000}</p>
                <div className="w-full bg-slate-100 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${((budget?.spent ?? 1417) / (budget?.budget ?? 3000)) * 100}%` }} />
                </div>
                <span className="text-[9px] font-extrabold tracking-wide uppercase px-2 py-0.5 rounded-full mt-2.5 inline-block bg-emerald-50 text-emerald-700 border border-emerald-100">
                  {budget?.status ?? "Within Budget"}
                </span>
              </div>
            </div>

            {/* Inventory */}
            <div className="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-all">
              <div className="flex justify-between items-start mb-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Inventory Health</span>
                <Package className="w-5 h-5 text-indigo-500" />
              </div>
              <div>
                <p className="text-2xl font-black text-slate-800">{inventoryHealth?.health ?? 79}%</p>
                <p className="text-xs text-slate-500 font-semibold mt-1">28 items tracked</p>
                <span className="text-[9px] font-extrabold tracking-wide uppercase px-2 py-0.5 rounded-full mt-2 inline-block bg-rose-50 text-rose-700 border border-rose-100">
                  {inventoryHealth?.lowStockCount ?? 6} Low stock
                </span>
              </div>
            </div>

            {/* Shopping */}
            <div className="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-all">
              <div className="flex justify-between items-start mb-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Shopping Items</span>
                <ShoppingCart className="w-5 h-5 text-indigo-500" />
              </div>
              <div>
                <p className="text-2xl font-black text-slate-800">{shoppingList?.totalCount ?? 28}</p>
                <p className="text-xs text-slate-500 font-semibold mt-1">Recommended to buy</p>
                <span className="text-[9px] font-extrabold tracking-wide uppercase px-2 py-0.5 rounded-full mt-2 inline-block bg-blue-50 text-blue-700 border border-blue-100">
                  {shoppingList?.badge ?? "Smart Auto-List"}
                </span>
              </div>
            </div>

            {/* Waste */}
            <div className="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-all">
              <div className="flex justify-between items-start mb-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Food Waste</span>
                <Trash2 className="w-5 h-5 text-indigo-500" />
              </div>
              <div>
                <p className="text-2xl font-black text-slate-800">{foodWaste?.amount ?? "1.2 kg"}</p>
                <p className="text-xs text-slate-500 font-semibold mt-1">Weekly average</p>
                <span className="text-[9px] font-extrabold tracking-wide uppercase px-2 py-0.5 rounded-full mt-2 inline-block bg-emerald-50 text-emerald-700 border border-emerald-100">
                  {foodWaste?.status ?? "Stable"}
                </span>
              </div>
            </div>

            {/* Meals */}
            <div className="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-all">
              <div className="flex justify-between items-start mb-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Planned Meals</span>
                <Calendar className="w-5 h-5 text-indigo-500" />
              </div>
              <div>
                <p className="text-2xl font-black text-slate-800">{plannedMeals?.days ?? "7 Days"}</p>
                <p className="text-xs text-slate-500 font-semibold mt-1">Fully scheduled</p>
                <span className="text-[9px] font-extrabold tracking-wide uppercase px-2 py-0.5 rounded-full mt-2 inline-block bg-purple-50 text-purple-700 border border-purple-100">
                  {plannedMeals?.badge ?? "90% Ingredient match"}
                </span>
              </div>
            </div>

            {/* Alerts */}
            <div className="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-all">
              <div className="flex justify-between items-start mb-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">AI Alerts</span>
                <AlertTriangle className="w-5 h-5 text-indigo-500" />
              </div>
              <div>
                <p className="text-2xl font-black text-slate-800">{aiAlerts?.count ?? 20}</p>
                <p className="text-xs text-slate-500 font-semibold mt-1">Needs attention</p>
                <span className="text-[9px] font-extrabold tracking-wide uppercase mt-2 inline-block text-rose-600 font-semibold">
                  {aiAlerts?.badge ?? "Active"}
                </span>
              </div>
            </div>

          </div>

          {/* Bottom Split Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Card: AI Insights */}
            <div className="lg:col-span-2 bg-white rounded-3xl p-8 border border-slate-200 shadow-sm flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-black text-slate-800 flex items-center mb-6">
                  <Sparkles className="w-5 h-5 text-indigo-600 mr-2" /> Mother Agent Insight
                </h3>
                <p className="text-sm text-slate-600 leading-relaxed font-medium mb-8">
                  {insightsText}
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <button 
                  onClick={addRiceToShopping}
                  disabled={addingItem}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-bold transition-all shadow-md shadow-indigo-600/20 flex items-center active:scale-95 disabled:opacity-50"
                >
                  <ShoppingCart className="w-4 h-4 mr-2" /> Add Rice to Shopping List
                </button>
                <button 
                  onClick={() => setActiveTab('/mother', 'inventory')}
                  className="px-6 py-2.5 bg-white border border-slate-300 hover:bg-slate-55 text-slate-700 rounded-xl text-sm font-bold transition-all"
                >
                  View Inventory
                </button>
              </div>
            </div>

            {/* Right Card: Needs Attention */}
            <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-black text-slate-800 flex items-center">
                    <AlertCircle className="w-5 h-5 text-rose-500 mr-2" /> Needs Attention
                  </h3>
                  <span className="bg-rose-50 text-rose-600 text-[10px] font-black px-2 py-0.5 rounded-full border border-rose-100">
                    6 items
                  </span>
                </div>

                <div className="space-y-4">
                  {expiringItems.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center pb-3 border-b border-slate-100 last:border-0 last:pb-0">
                      <div>
                        <p className="text-sm font-bold text-slate-800">{item.name}</p>
                        <p className="text-[10px] text-slate-400 font-semibold">{item.status || "Category"}</p>
                      </div>
                      <span className="bg-rose-50 text-rose-600 text-[10px] font-black px-2.5 py-0.5 rounded-full border border-rose-100">
                        {item.days === 0 ? "0 days left" : `${item.days} days left`}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <button 
                onClick={() => setActiveTab('/mother', 'inventory')}
                className="w-full flex items-center justify-center space-x-1.5 py-3 mt-6 bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-slate-800 rounded-2xl text-xs font-bold border border-slate-200 transition-all"
              >
                <span>View Full Pantry</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

          </div>

        </motion.div>
      ) : (
        <div className="flex items-center justify-center h-96 border-2 border-dashed border-slate-200 rounded-3xl bg-white/50">
          <p className="text-slate-400 text-lg font-medium">Work in progress: <span className="capitalize">{activeTab.replace('_', ' ')}</span> view</p>
        </div>
      )}
    </div>
  );
}