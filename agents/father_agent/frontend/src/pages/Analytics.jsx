import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { expenseApi } from '../services/expenseApi';
import { budgetApi } from '../services/budgetApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { BarChart3, TrendingUp, PieChart as PieChartIcon, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';

export const Analytics = () => {
  const { familyId } = useFamily();
  const [loading, setLoading] = useState(true);
  const [expenseSummary, setExpenseSummary] = useState(null);
  const [budgetAnalytics, setBudgetAnalytics] = useState([]);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const [expRes, budRes] = await Promise.all([
          expenseApi.getExpenseSummary(familyId),
          budgetApi.getBudgetAnalytics(familyId),
        ]);
        setExpenseSummary(expRes);
        setBudgetAnalytics(budRes || []);
      } catch (err) {
        console.error('Error loading analytics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [familyId]);

  // Comparison Bar Chart data (Limit vs Spent)
  const comparisonData = budgetAnalytics.map((b) => ({
    category: b.category,
    Limit: Number(b.monthly_limit),
    Spent: Number(b.spent),
  }));

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-blue-400" />
            <span>Financial Analytics</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Deep dive into spending patterns, category trends, and budget adherence.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-400">Synthesizing financial analytics...</div>
      ) : (
        <>
          {/* Top Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard>
              <span className="text-xs font-semibold text-slate-400 uppercase">Total Spent</span>
              <div className="text-2xl font-black text-white mt-1">
                <AnimatedNumber value={expenseSummary?.total_spent ?? 0} />
              </div>
              <p className="text-xs text-slate-400 mt-1">Current month total</p>
            </GlassCard>

            <GlassCard>
              <span className="text-xs font-semibold text-slate-400 uppercase">Transactions</span>
              <div className="text-2xl font-black text-blue-400 mt-1">
                {expenseSummary?.expense_count ?? 0}
              </div>
              <p className="text-xs text-slate-400 mt-1">Ledger items</p>
            </GlassCard>

            <GlassCard>
              <span className="text-xs font-semibold text-slate-400 uppercase">Avg Expense</span>
              <div className="text-2xl font-black text-emerald-400 mt-1">
                <AnimatedNumber value={expenseSummary?.average_expense ?? 0} />
              </div>
              <p className="text-xs text-slate-400 mt-1">Per transaction average</p>
            </GlassCard>

            <GlassCard>
              <span className="text-xs font-semibold text-slate-400 uppercase">Highest Category</span>
              <div className="text-xl font-bold text-amber-400 mt-1 truncate">
                {expenseSummary?.highest_category || 'N/A'}
              </div>
              <p className="text-xs text-slate-400 mt-1">
                ₹{expenseSummary?.highest_category_amount?.toLocaleString('en-IN') || 0}
              </p>
            </GlassCard>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Budget vs Actual Spent Comparison Bar Chart */}
            <GlassCard className="lg:col-span-8 p-6">
              <h3 className="text-base font-bold text-white mb-2">Budget Limit vs Actual Spending</h3>
              <p className="text-xs text-slate-400 mb-6">Comparison by category</p>

              {comparisonData.length > 0 ? (
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={comparisonData}>
                      <XAxis dataKey="category" stroke="#64748b" fontSize={11} />
                      <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `₹${v}`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '0.5rem', color: '#fff' }}
                        formatter={(val) => [`₹${val}`]}
                      />
                      <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
                      <Bar dataKey="Limit" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Spent" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="py-12 text-center text-slate-400">No budget data available for comparison.</div>
              )}
            </GlassCard>

            {/* Category Summary List */}
            <GlassCard className="lg:col-span-4 p-6">
              <h3 className="text-base font-bold text-white mb-4">Category Summary</h3>
              <div className="space-y-3">
                {expenseSummary?.categories && expenseSummary.categories.length > 0 ? (
                  expenseSummary.categories.map((cat, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                      <span className="text-sm font-semibold text-slate-200">{cat.category}</span>
                      <span className="text-sm font-bold text-white">₹{Number(cat.total).toLocaleString('en-IN')}</span>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-slate-400 text-xs">No category totals available.</div>
                )}
              </div>
            </GlassCard>
          </div>
        </>
      )}
    </div>
  );
};

export default Analytics;
