import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { budgetApi } from '../services/budgetApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { PieChart, Plus, AlertCircle, CheckCircle2, AlertTriangle, ShieldCheck, X } from 'lucide-react';
import { motion } from 'framer-motion';

export const Budget = () => {
  const { familyId, triggerRefresh } = useFamily();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Form state
  const [category, setCategory] = useState('Food & Groceries');
  const [monthlyLimit, setMonthlyLimit] = useState('');

  const fetchBudgets = async () => {
    setLoading(true);
    try {
      const data = await budgetApi.getBudgetAnalytics(familyId);
      setAnalytics(data || []);
    } catch (err) {
      console.error('Error fetching budget analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgets();
  }, [familyId]);

  const handleCreateBudget = async (e) => {
    e.preventDefault();
    if (!monthlyLimit) return;

    setSubmitting(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      await budgetApi.createBudget({
        family_id: Number(familyId),
        category,
        monthly_limit: parseFloat(monthlyLimit),
      });

      setSuccessMsg(`Budget allocated for ${category}!`);
      setMonthlyLimit('');
      setIsModalOpen(false);
      triggerRefresh();
      fetchBudgets();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create budget');
    } finally {
      setSubmitting(false);
    }
  };

  const totalBudgeted = analytics.reduce((acc, b) => acc + Number(b.monthly_limit || 0), 0);
  const totalSpent = analytics.reduce((acc, b) => acc + Number(b.spent || 0), 0);
  const totalRemaining = totalBudgeted - totalSpent;
  const overallPercentage = totalBudgeted > 0 ? Math.min((totalSpent / totalBudgeted) * 100, 100) : 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
            <PieChart className="w-8 h-8 text-[#0F766E]" />
            <span>Budget Management</span>
          </h1>
          <p className="text-[#627D98] text-sm mt-1">
            Category-level budget allocations, spend limits, and utilization health.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#0F766E] hover:bg-emerald-600 text-white font-medium text-sm shadow-lg shadow-[#0f766e]/15 transition-all hover:scale-[1.02] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Allocate Budget</span>
        </button>
      </div>

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Overall Utilization Card */}
      <GlassCard glow={true} className="p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-[#0F766E]">Monthly Workspace Overview</span>
            <div className="flex items-baseline gap-3 mt-2">
              <span className="text-4xl font-black text-[#102A43]">
                <AnimatedNumber value={totalSpent} />
              </span>
              <span className="text-lg text-[#627D98] font-semibold">
                / <AnimatedNumber value={totalBudgeted} />
              </span>
            </div>
            <p className="text-xs text-[#627D98] mt-1">
              ₹{totalRemaining.toLocaleString('en-IN')} remaining across allocated categories
            </p>
          </div>

          {/* Progress Bar Container */}
          <div className="w-full lg:w-1/2 space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-[#172B4D]">Total Budget Utilization</span>
              <span className={overallPercentage > 85 ? 'text-[#C53030]' : 'text-[#2F855A]'}>
                {overallPercentage.toFixed(1)}%
              </span>
            </div>
            <div className="h-4 w-full bg-[#F7F9FC] rounded-full overflow-hidden p-0.5 border border-[#D9E2EC]">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${overallPercentage}%` }}
                transition={{ duration: 1.2, ease: 'easeOut' }}
                className={`h-full rounded-full ${
                  overallPercentage >= 100
                    ? 'bg-[#C53030] shadow-lg shadow-rose-500/20'
                    : overallPercentage >= 80
                    ? 'bg-[#D97706] shadow-lg shadow-amber-500/20'
                    : 'bg-[#0F766E] shadow-lg shadow-emerald-500/20'
                }`}
              />
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Category Budget Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-[#102A43]">Category Allocations</h3>

        {loading ? (
          <div className="py-12 text-center text-[#627D98]">Loading budget analytics...</div>
        ) : analytics.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {analytics.map((item, idx) => {
              const isOver = item.status === 'Exceeded';
              const isWarn = item.status === 'Warning';
              return (
                <GlassCard key={idx} delay={idx * 0.1}>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="font-bold text-[#102A43] text-base">{item.category}</h4>
                      <span className="text-xs text-[#627D98]">Monthly Limit: ₹{Number(item.monthly_limit).toLocaleString('en-IN')}</span>
                    </div>

                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1 ${
                        isOver
                          ? 'bg-[#C53030]/10 text-[#C53030] border border-[#C53030]/30'
                          : isWarn
                          ? 'bg-[#D97706]/10 text-[#D97706] border border-[#D97706]/30'
                          : 'bg-[#2F855A]/10 text-[#2F855A] border border-[#2F855A]/30'
                      }`}
                    >
                      {isOver ? (
                        <>
                          <AlertCircle className="w-3 h-3" /> Exceeded
                        </>
                      ) : isWarn ? (
                        <>
                          <AlertTriangle className="w-3 h-3" /> Warning
                        </>
                      ) : (
                        <>
                          <ShieldCheck className="w-3 h-3" /> Healthy
                        </>
                      )}
                    </span>
                  </div>

                  {/* Stat Breakdown */}
                  <div className="grid grid-cols-2 gap-2 text-xs mb-4">
                    <div className="p-2.5 rounded-xl bg-white border border-[#D9E2EC]">
                      <span className="text-[#627D98]">Spent</span>
                      <div className="font-bold text-[#172B4D] text-sm mt-0.5">₹{Number(item.spent).toLocaleString('en-IN')}</div>
                    </div>
                    <div className="p-2.5 rounded-xl bg-white border border-[#D9E2EC]">
                      <span className="text-[#627D98]">Remaining</span>
                      <div className={`font-bold text-sm mt-0.5 ${item.remaining < 0 ? 'text-[#C53030]' : 'text-[#2F855A]'}`}>
                        ₹{Number(item.remaining).toLocaleString('en-IN')}
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-[11px] font-semibold text-[#627D98]">
                      <span>Usage</span>
                      <span>{item.percentage_used}%</span>
                    </div>
                    <div className="h-2 w-full bg-[#F7F9FC] rounded-full overflow-hidden border border-[#D9E2EC]">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(item.percentage_used, 100)}%` }}
                        transition={{ duration: 1 }}
                        className={`h-full rounded-full ${
                          isOver ? 'bg-[#C53030]' : isWarn ? 'bg-[#D97706]' : 'bg-[#0F766E]'
                        }`}
                      />
                    </div>
                  </div>
                </GlassCard>
              );
            })}
          </div>
        ) : (
          <div className="py-12 text-center text-[#627D98]">No budget allocations found for this family.</div>
        )}
      </div>

      {/* Add Budget Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-[#0B1F33]/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white border border-[#D9E2EC] rounded-2xl p-6 relative shadow-2xl">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-[#627D98] hover:text-[#102A43] p-1 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-xl font-extrabold text-[#102A43] mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-[#0F766E]" />
              <span>Create Category Budget</span>
            </h3>

            {errorMsg && (
              <div className="mb-4 p-3 rounded-xl bg-[#C53030]/10 border border-[#C53030]/30 text-[#C53030] text-xs">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreateBudget} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm bg-white cursor-pointer"
                >
                  <option value="Food & Groceries">Food & Groceries</option>
                  <option value="Dining">Dining</option>
                  <option value="Utilities">Utilities</option>
                  <option value="Shopping">Shopping</option>
                  <option value="Transportation">Transportation</option>
                  <option value="Entertainment">Entertainment</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Monthly Limit (₹)</label>
                <input
                  type="number"
                  required
                  step="0.01"
                  placeholder="15000"
                  value={monthlyLimit}
                  onChange={(e) => setMonthlyLimit(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm"
                />
              </div>

              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-[#627D98] hover:text-[#102A43] cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-[#0F766E] hover:bg-[#0F766E] text-white shadow-lg shadow-[#0f766e]/15 cursor-pointer"
                >
                  {submitting ? 'Allocating...' : 'Set Budget'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Budget;
