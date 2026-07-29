import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { crossAgentApi } from '../services/crossAgentApi';
import { GlassCard } from '../components/ui/GlassCard';
import { Users, ShoppingBag, ArrowDown, CheckCircle, RefreshCw, Plus, Package } from 'lucide-react';

export const FamilyIntelligence = () => {
  const { familyId, triggerRefresh } = useFamily();
  const [loading, setLoading] = useState(true);
  const [motherStatus, setMotherStatus] = useState('offline');
  const [inventory, setInventory] = useState(null);
  const [shoppingList, setShoppingList] = useState(null);
  const [recording, setRecording] = useState(false);
  const [recordMsg, setRecordMsg] = useState('');

  const fetchFamilyAgentData = async () => {
    setLoading(true);
    try {
      const [healthRes, invRes, shopRes] = await Promise.allSettled([
        crossAgentApi.getMotherHealth(),
        crossAgentApi.getMotherInventory(),
        crossAgentApi.getMotherShoppingList(),
      ]);

      if (healthRes.status === 'fulfilled') setMotherStatus(healthRes.value?.mother_agent || 'offline');
      if (invRes.status === 'fulfilled') setInventory(invRes.value?.inventory);
      if (shopRes.status === 'fulfilled') setShoppingList(shopRes.value?.shopping_list);
    } catch (err) {
      console.error('Error fetching family agent integration data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFamilyAgentData();
  }, []);

  const handleRecordGroceryExpense = async (item) => {
    setRecording(true);
    setRecordMsg('');
    try {
      await crossAgentApi.recordExpenseFromMother({
        family_id: Number(familyId),
        category: 'Food & Groceries',
        amount: item.estimated_cost || 500,
        merchant: item.item_name || 'MotherAgent Restock',
      });
      setRecordMsg(`Recorded expense for ${item.item_name} (₹${item.estimated_cost}) into Father Agent ledger!`);
      triggerRefresh();
    } catch (err) {
      console.error('Failed to record cross-agent expense:', err);
    } finally {
      setRecording(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Users className="w-8 h-8 text-pink-400" />
            <span>KinNest Cross-Agent Family Intelligence</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Father Agent (Finance) $\longleftrightarrow$ Mother Agent (Household & Inventory) Service Protocol.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-2 border ${
              motherStatus === 'online'
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                motherStatus === 'online' ? 'bg-emerald-400 animate-ping' : 'bg-slate-500'
              }`}
            />
            <span>Mother Agent: {motherStatus}</span>
          </span>
        </div>
      </div>

      {recordMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 shrink-0" />
          <span>{recordMsg}</span>
        </div>
      )}

      {/* Agent Diagram Flow Card */}
      <GlassCard glow={true} className="p-6 bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900">
        <h3 className="text-base font-bold text-white mb-4">Inter-Agent Architecture Protocol</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div className="p-4 rounded-xl bg-slate-900/90 border border-blue-500/30">
            <div className="font-extrabold text-blue-400 text-sm">Father Agent</div>
            <div className="text-xs text-slate-400 mt-1">Finance Orchestrator & Safe-to-Spend</div>
          </div>
          <div className="flex items-center justify-center text-slate-500 font-bold">
            <span className="hidden md:inline">⇄ REST JSON ⇄</span>
            <span className="md:hidden">↓ REST JSON ↓</span>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/90 border border-pink-500/30">
            <div className="font-extrabold text-pink-400 text-sm">Mother Agent</div>
            <div className="text-xs text-slate-400 mt-1">Household Inventory & Grocery Manager</div>
          </div>
        </div>
      </GlassCard>

      {/* Mother Agent Shopping List & Cross-Agent Action */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard className="p-6">
          <h3 className="text-base font-bold text-white mb-3 flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-pink-400" />
            <span>Mother Agent Active Shopping List</span>
          </h3>

          {loading ? (
            <div className="py-8 text-center text-slate-400">Querying Mother Agent...</div>
          ) : shoppingList?.items && shoppingList.items.length > 0 ? (
            <div className="space-y-3">
              {shoppingList.items.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between"
                >
                  <div>
                    <h4 className="font-bold text-white text-sm">{item.item_name}</h4>
                    <span className="text-xs text-slate-400">
                      Need: {item.quantity_needed} {item.unit} • Est: ₹{item.estimated_cost}
                    </span>
                  </div>

                  <button
                    onClick={() => handleRecordGroceryExpense(item)}
                    disabled={recording}
                    className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-500/20 flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Sync Expense</span>
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 text-center">
              Mother Agent shopping list active or default items loaded.
            </div>
          )}
        </GlassCard>

        {/* Inventory Stock Levels */}
        <GlassCard className="p-6">
          <h3 className="text-base font-bold text-white mb-3 flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-400" />
            <span>Mother Agent Pantry & Inventory</span>
          </h3>

          {loading ? (
            <div className="py-8 text-center text-slate-400">Loading stock levels...</div>
          ) : inventory?.items && inventory.items.length > 0 ? (
            <div className="space-y-3">
              {inventory.items.map((item, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-white text-sm">{item.item_name}</h4>
                    <span className="text-xs text-slate-400">{item.category}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-200">{item.quantity} {item.unit}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 text-center">
              Household inventory connected via REST protocol.
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
};

export default FamilyIntelligence;
