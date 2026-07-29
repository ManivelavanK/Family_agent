import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { expenseApi } from '../services/expenseApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { Receipt, Plus, Search, Filter, Calendar, Tag, FileText, CheckCircle, AlertCircle, X } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const CATEGORY_COLORS = {
  Groceries: '#10b981',
  Dining: '#f59e0b',
  Utilities: '#3b82f6',
  Shopping: '#8b5cf6',
  Transportation: '#ec4899',
  Entertainment: '#06b6d4',
  Healthcare: '#ef4444',
  Other: '#64748b',
};

export const Expenses = () => {
  const { familyId, triggerRefresh } = useFamily();
  const [loading, setLoading] = useState(true);
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState(null);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Form State
  const [category, setCategory] = useState('Food & Groceries');
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [expenseDate, setExpenseDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [listData, summaryData] = await Promise.all([
        expenseApi.getExpenses(familyId),
        expenseApi.getExpenseSummary(familyId),
      ]);
      setExpenses(listData || []);
      setSummary(summaryData || null);
    } catch (err) {
      console.error('Error fetching expenses:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [familyId]);

  const handleAddExpense = async (e) => {
    e.preventDefault();
    if (!amount || !description) return;

    setSubmitting(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      await expenseApi.createExpense({
        family_id: Number(familyId),
        category,
        description,
        amount: parseFloat(amount),
        expense_date: expenseDate,
      });

      setSuccessMsg('Expense recorded in financial ledger!');
      setDescription('');
      setAmount('');
      setIsModalOpen(false);
      triggerRefresh();
      fetchData();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create expense');
    } finally {
      setSubmitting(false);
    }
  };

  // Filter expenses
  const filteredExpenses = expenses.filter((item) => {
    const matchesSearch =
      item.description?.toLowerCase().includes(search.toLowerCase()) ||
      item.category?.toLowerCase().includes(search.toLowerCase());
    const matchesCat = selectedCategory === 'ALL' || item.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  const pieChartData = summary?.categories?.map((cat) => ({
    name: cat.category,
    value: cat.total,
    color: CATEGORY_COLORS[cat.category] || '#3b82f6',
  })) || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
            <Receipt className="w-8 h-8 text-[#0F766E]" />
            <span>Expense Ledger</span>
          </h1>
          <p className="text-[#627D98] text-sm mt-1">
            Real-time breakdown of all household financial transactions.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#102A43] hover:bg-[#243B53] text-white font-medium text-sm shadow-lg shadow-[#102A43]/15 transition-all hover:scale-[1.02] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Add Expense</span>
        </button>
      </div>

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Summary Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard>
          <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Total Spent This Month</div>
          <div className="text-3xl font-black text-[#102A43] mt-1">
            <AnimatedNumber value={summary?.total_spent ?? 0} />
          </div>
          <p className="text-xs text-[#627D98] mt-2">{summary?.expense_count ?? 0} transactions recorded</p>
        </GlassCard>

        <GlassCard>
          <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Average Expense</div>
          <div className="text-3xl font-black text-[#0F766E] mt-1">
            <AnimatedNumber value={summary?.average_expense ?? 0} />
          </div>
          <p className="text-xs text-[#627D98] mt-2">Average transaction cost</p>
        </GlassCard>

        <GlassCard>
          <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Highest Category</div>
          <div className="text-2xl font-bold text-[#D4A72C] mt-1 truncate">
            {summary?.highest_category || 'N/A'}
          </div>
          <p className="text-xs text-[#627D98] mt-2">
            ₹{summary?.highest_category_amount?.toLocaleString('en-IN') || 0} total spent
          </p>
        </GlassCard>
      </div>

      {/* Analytics & Table Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Category Breakdown Chart */}
        {pieChartData.length > 0 && (
          <GlassCard className="lg:col-span-4 p-6 flex flex-col justify-between">
            <div>
              <h3 className="text-base font-bold text-[#102A43] mb-2">Category Distribution</h3>
              <p className="text-xs text-[#627D98] mb-4">Monthly expense breakdown</p>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#D9E2EC', borderRadius: '0.5rem', color: '#172B4D' }}
                    formatter={(val) => [`₹${val}`, 'Total']}
                  />
                  <Legend verticalAlign="bottom" height={36} iconSize={10} wrapperStyle={{ fontSize: '11px', color: '#627D98' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        )}

        {/* Transactions Table */}
        <GlassCard className={`${pieChartData.length > 0 ? 'lg:col-span-8' : 'lg:col-span-12'} p-6`}>
          {/* Controls Header */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-3 text-[#627D98]" />
              <input
                type="text"
                placeholder="Search transactions..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-xl glass-input text-xs"
              />
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Filter className="w-4 h-4 text-[#627D98]" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="glass-input px-3 py-2 rounded-xl text-xs bg-white cursor-pointer"
              >
                <option value="ALL">All Categories</option>
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
          </div>

          {loading ? (
            <div className="py-12 text-center text-[#627D98]">Loading ledger...</div>
          ) : filteredExpenses.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-[#D9E2EC] text-xs text-[#627D98] uppercase tracking-wider">
                    <th className="pb-3">Description</th>
                    <th className="pb-3">Category</th>
                    <th className="pb-3">Date</th>
                    <th className="pb-3 text-right">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#D9E2EC]/60">
                  {filteredExpenses.map((exp) => (
                    <tr key={exp.id} className="hover:bg-[#F7F9FC] transition-colors">
                      <td className="py-3 font-semibold text-[#172B4D] flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-[#0F766E]/10 text-[#0F766E] flex items-center justify-center shrink-0">
                          <FileText className="w-4 h-4" />
                        </div>
                        <span>{exp.description}</span>
                      </td>
                      <td className="py-3">
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-[#F7F9FC] text-[#172B4D] border border-[#D9E2EC]">
                          {exp.category}
                        </span>
                      </td>
                      <td className="py-3 text-xs text-[#627D98]">{exp.expense_date}</td>
                      <td className="py-3 text-right font-bold text-[#C53030]">
                        -₹{Number(exp.amount).toLocaleString('en-IN')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 text-center text-[#627D98]">No expenses matching criteria.</div>
          )}
        </GlassCard>
      </div>

      {/* Add Expense Modal */}
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
              <span>Record New Expense</span>
            </h3>

            {errorMsg && (
              <div className="mb-4 p-3 rounded-xl bg-[#C53030]/10 border border-[#C53030]/30 text-[#C53030] text-xs">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleAddExpense} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Description</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Weekly Grocery Restock"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm"
                />
              </div>

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
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Amount (₹)</label>
                <input
                  type="number"
                  required
                  step="0.01"
                  placeholder="2500"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Date</label>
                <input
                  type="date"
                  required
                  value={expenseDate}
                  onChange={(e) => setExpenseDate(e.target.value)}
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
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-[#102A43] hover:bg-[#243B53] text-white shadow-lg shadow-[#102A43]/15 cursor-pointer"
                >
                  {submitting ? 'Recording...' : 'Submit Expense'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Expenses;
