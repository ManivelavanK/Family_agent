import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { incomeApi } from '../services/incomeApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { TrendingUp, Plus, DollarSign, Wallet, Building, CheckCircle, X } from 'lucide-react';

export const Income = () => {
  const { familyId, triggerRefresh } = useFamily();
  const [loading, setLoading] = useState(true);
  const [incomes, setIncomes] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Form State
  const [source, setSource] = useState('');
  const [amount, setAmount] = useState('');
  const [incomeType, setIncomeType] = useState('Primary Salary');

  const fetchIncomeData = async () => {
    setLoading(true);
    try {
      const data = await incomeApi.getIncome(familyId);
      setIncomes(data || []);
    } catch (err) {
      console.error('Error fetching income data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncomeData();
  }, [familyId]);

  const handleAddIncome = async (e) => {
    e.preventDefault();
    if (!source || !amount) return;

    setSubmitting(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      await incomeApi.createIncome({
        family_id: Number(familyId),
        source,
        amount: parseFloat(amount),
        income_type: incomeType,
      });

      setSuccessMsg('Income source successfully recorded!');
      setSource('');
      setAmount('');
      setIsModalOpen(false);
      triggerRefresh();
      fetchIncomeData();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to add income');
    } finally {
      setSubmitting(false);
    }
  };

  const totalIncome = incomes.reduce((acc, curr) => acc + Number(curr.amount || 0), 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-[#0F766E]" />
            <span>Income Streams</span>
          </h1>
          <p className="text-[#627D98] text-sm mt-1">
            Family earnings, salaries, investments, and recurring cash inflows.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#0F766E] hover:bg-emerald-600 text-white font-medium text-sm shadow-lg shadow-[#0f766e]/15 transition-all hover:scale-[1.02] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Add Income Stream</span>
        </button>
      </div>

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard glow={true}>
          <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Total Monthly Income</div>
          <div className="text-3xl font-black text-[#2F855A] mt-1">
            <AnimatedNumber value={totalIncome} />
          </div>
          <p className="text-xs text-[#627D98] mt-2">{incomes.length} active income streams</p>
        </GlassCard>

        <GlassCard>
          <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Primary Stream</div>
          <div className="text-2xl font-bold text-[#102A43] mt-1 truncate">
            {incomes.length > 0 ? incomes[0].source : 'None recorded'}
          </div>
          <p className="text-xs text-[#627D98] mt-2">
            ₹{incomes.length > 0 ? Number(incomes[0].amount).toLocaleString('en-IN') : 0} per month
          </p>
        </GlassCard>

        <GlassCard>
          <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Stream Count</div>
          <div className="text-3xl font-black text-[#102A43] mt-1">{incomes.length}</div>
          <p className="text-xs text-[#627D98] mt-2">Diversified family cash flow</p>
        </GlassCard>
      </div>

      {/* Income List */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-bold text-[#102A43] mb-4">Active Income Ledger</h3>

        {loading ? (
          <div className="py-12 text-center text-[#627D98]">Loading income records...</div>
        ) : incomes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {incomes.map((inc) => (
              <div
                key={inc.id}
                className="p-4 rounded-xl bg-white border border-[#D9E2EC] flex items-center justify-between hover:border-[#0F766E]/40 transition-all"
              >
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-[#0F766E]/10 text-[#0F766E]">
                    <Building className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-[#172B4D]">{inc.source}</h4>
                    <span className="text-xs text-[#627D98]">{inc.income_type}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-base font-extrabold text-[#2F855A]">
                    +₹{Number(inc.amount).toLocaleString('en-IN')}
                  </div>
                  <span className="text-[10px] text-[#627D98]">Monthly</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-12 text-center text-[#627D98]">No income records found for this family.</div>
        )}
      </GlassCard>

      {/* Add Income Modal */}
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
              <span>Record Income Stream</span>
            </h3>

            {errorMsg && (
              <div className="mb-4 p-3 rounded-xl bg-[#C53030]/10 border border-[#C53030]/30 text-[#C53030] text-xs">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleAddIncome} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Source Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Salary - Tech Corp"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Income Type</label>
                <select
                  value={incomeType}
                  onChange={(e) => setIncomeType(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm bg-white cursor-pointer"
                >
                  <option value="Primary Salary">Primary Salary</option>
                  <option value="Secondary Salary">Secondary Salary</option>
                  <option value="Freelance / Business">Freelance / Business</option>
                  <option value="Investments / Dividends">Investments / Dividends</option>
                  <option value="Rental Income">Rental Income</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Monthly Amount (₹)</label>
                <input
                  type="number"
                  required
                  step="0.01"
                  placeholder="75000"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
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
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-[#0F766E] hover:bg-emerald-600 text-white shadow-lg shadow-[#0f766e]/15 cursor-pointer"
                >
                  {submitting ? 'Saving...' : 'Add Income Stream'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Income;
