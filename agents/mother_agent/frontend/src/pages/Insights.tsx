import React, { useState, useEffect } from 'react';
import { spendingAnalytics } from '../data/mockData';
import { IS_MOCK_MODE, apiClient } from '../services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import { Sparkles, Trash2, Check, Loader2, ArrowRight } from 'lucide-react';

const CATEGORY_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#EF4444', '#06B6D4'];

export const Insights: React.FC = () => {
  const [wasteStatus, setWasteStatus] = useState<'pending' | 'applying' | 'applied'>('pending');
  const [loading, setLoading] = useState(true);
  const [categoryData, setCategoryData] = useState(spendingAnalytics.categoryData);
  const [wasteData, setWasteData] = useState(spendingAnalytics.wasteData);
  const [monthlyData] = useState(spendingAnalytics.monthlyData);

  useEffect(() => {
    async function loadInsights() {
      setLoading(true);
      try {
        if (!IS_MOCK_MODE) {
          // Load consumption data for category breakdown
          const consumptionRes = await apiClient.get<any[]>('/analytics/consumption');
          const items = consumptionRes.data;

          // Build category totals from consumption
          const catTotals: Record<string, number> = {};
          items.forEach((item: any) => {
            // Use item name prefix to infer category
            const cat = item.item_name?.includes('Rice') || item.item_name?.includes('Atta') || item.item_name?.includes('Oil') || item.item_name?.includes('Salt') || item.item_name?.includes('Sugar')
              ? 'Staples'
              : item.item_name?.includes('Milk') || item.item_name?.includes('Curd') || item.item_name?.includes('Paneer') || item.item_name?.includes('Egg')
              ? 'Dairy'
              : item.item_name?.includes('Tomato') || item.item_name?.includes('Onion') || item.item_name?.includes('Spinach') || item.item_name?.includes('Carrot') || item.item_name?.includes('Potato')
              ? 'Vegetables'
              : item.item_name?.includes('Biscuit') || item.item_name?.includes('Coffee') || item.item_name?.includes('Tea') || item.item_name?.includes('Juice')
              ? 'Snacks & Beverages'
              : 'Others';
            catTotals[cat] = (catTotals[cat] || 0) + (item.total_quantity || 0);
          });

          if (Object.keys(catTotals).length > 0) {
            const builtCategoryData = Object.entries(catTotals).map(([name, value], i) => ({
              name,
              value: Math.round(value * 100),  // scale to rupee equivalent
              color: CATEGORY_COLORS[i % CATEGORY_COLORS.length]
            }));
            setCategoryData(builtCategoryData);
          }

          // Load waste analytics
          const wasteRes = await apiClient.get<any>('/analytics/waste');
          if (wasteRes.data) {
            setWasteData(prev => ({
              ...prev,
              estimatedWaste: Math.round(prev.purchased * (wasteRes.data.waste_rate_percentage / 100)),
              insight: `Detected ${wasteRes.data.total_expired_items_count} expired items. ${prev.insight}`
            }));
          }
        }
      } catch (err) {
        console.error('Failed to load analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadInsights();
  }, []);

  const handleApplyWasteRecommendation = () => {
    setWasteStatus('applying');
    setTimeout(() => {
      setWasteStatus('applied');
    }, 1200);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Household Insights & Analytics</h1>
        <p className="text-slate-500 font-medium text-xs mt-1">Audit grocery spending trends, waste logs, and optimization guidelines.</p>
      </div>

      {loading && !IS_MOCK_MODE ? (
        <div className="flex h-40 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      ) : (
        <>
          {/* Main charts grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Spending Chart */}
            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-2xs space-y-4">
              <h3 className="font-bold text-slate-800 text-sm">Grocery Spending Trend (₹)</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="month" tick={{ fontSize: 10, fontWeight: 600, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 10, fontWeight: 600, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ background: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px', border: 'none' }} cursor={{ fill: '#f1f5f9' }} />
                    <Bar dataKey="spending" fill="#4f46e5" radius={[4, 4, 0, 0]} barSize={24} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <span className="block text-[10px] text-slate-400 font-semibold leading-normal">
                Monthly aggregate calculations are updated automatically from linked family debit accounts.
              </span>
            </div>

            {/* Category breakdown pie chart */}
            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-2xs space-y-4">
              <h3 className="font-bold text-slate-800 text-sm">Category Breakdown</h3>
              <div className="h-64 w-full flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ background: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '11px', border: 'none' }} />
                    <Legend iconSize={8} iconType="circle" wrapperStyle={{ fontSize: '11px', fontWeight: 650, color: '#475569' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Food Waste Monitor section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-2xs space-y-4 lg:col-span-2">
              <div className="flex items-center gap-2">
                <Trash2 className="h-4.5 w-4.5 text-rose-500" />
                <h3 className="font-bold text-slate-800 text-sm">Food Waste Monitor</h3>
              </div>

              <div className="grid grid-cols-3 gap-4 border-b border-slate-50 pb-4">
                <div className="rounded-xl bg-slate-50 p-4 border border-slate-100">
                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Purchased Value</span>
                  <span className="text-lg font-bold text-slate-800">₹{wasteData.purchased}</span>
                </div>
                <div className="rounded-xl bg-slate-50 p-4 border border-slate-100">
                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Consumed Value</span>
                  <span className="text-lg font-bold text-slate-800">₹{wasteData.consumed}</span>
                </div>
                <div className="rounded-xl bg-rose-50 p-4 border border-rose-100">
                  <span className="block text-[10px] font-bold text-rose-600 uppercase tracking-wider mb-1">Estimated Waste</span>
                  <span className="text-lg font-bold text-rose-700">₹{wasteData.estimatedWaste}</span>
                </div>
              </div>

              <div className="rounded-xl bg-indigo-50/50 p-4 border border-indigo-100/50 space-y-4">
                <div className="flex items-start gap-3">
                  <Sparkles className="h-4.5 w-4.5 text-indigo-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="block text-xs font-bold text-indigo-700 uppercase tracking-wider mb-1">AI Reduction Recommendation</span>
                    <p className="text-xs text-slate-655 font-semibold leading-relaxed">
                      {wasteData.insight}
                    </p>
                  </div>
                </div>

                <div className="flex justify-end border-t border-indigo-100/50 pt-3">
                  {wasteStatus === 'pending' && (
                    <button
                      onClick={handleApplyWasteRecommendation}
                      className="rounded-lg bg-indigo-650 hover:bg-indigo-700 text-white font-bold px-4 py-2 text-xs transition-colors cursor-pointer"
                    >
                      Apply Recommendation
                    </button>
                  )}
                  {wasteStatus === 'applying' && (
                    <button
                      disabled
                      className="flex items-center gap-1 rounded-lg bg-indigo-400 text-white font-bold px-4 py-2 text-xs"
                    >
                      <Loader2 className="h-3 w-3 animate-spin" />
                      Applying Adjustments...
                    </button>
                  )}
                  {wasteStatus === 'applied' && (
                    <span className="flex items-center gap-1 text-xs font-bold text-emerald-650 bg-emerald-55/20 border border-emerald-200 px-3 py-1.5 rounded-lg">
                      <Check className="h-3.5 w-3.5" />
                      Recommendation Applied (Weekly Tomatoes capped at 1.5kg)
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* AI Insight report cards */}
            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-2xs space-y-4 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4.5 w-4.5 text-indigo-600 animate-pulse" />
                  <h3 className="font-bold text-slate-800 text-sm">Monthly Spend Audit</h3>
                </div>
                <div className="space-y-3">
                  <div className="rounded-xl bg-slate-50 p-3.5 border border-slate-100">
                    <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Staples vs Last Month</span>
                    <span className="text-xs font-bold text-emerald-600">↓ Decreased by 7%</span>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-3.5 border border-slate-100">
                    <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Vegetables vs Last Month</span>
                    <span className="text-xs font-bold text-rose-600">↑ Increased by 18%</span>
                  </div>
                </div>
              </div>

              <button
                className="flex items-center justify-center gap-1 text-xs font-bold text-indigo-600 hover:text-indigo-700 transition-colors pt-4 border-t border-slate-50"
                onClick={() => alert('Exporting full pantry analytics report...')}
              >
                <span>Export Analytics Report</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
export default Insights;
