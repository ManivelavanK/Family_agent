import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { memoryApi } from '../services/memoryApi';
import { GlassCard } from '../components/ui/GlassCard';
import { Brain, Plus, Search, CheckCircle, X } from 'lucide-react';

export const FinancialMemory = () => {
  const { familyId } = useFamily();
  const [loading, setLoading] = useState(true);
  const [memories, setMemories] = useState([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  // Form State
  const [category, setCategory] = useState('Savings Preferences');
  const [key, setKey] = useState('');
  const [content, setContent] = useState('');

  const fetchMemories = async () => {
    setLoading(true);
    try {
      const res = await memoryApi.getMemories(familyId, search);
      setMemories(res?.memories || []);
    } catch (err) {
      console.error('Error loading financial memories:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, [familyId, search]);

  const handleStoreMemory = async (e) => {
    e.preventDefault();
    if (!key || !content) return;

    setSubmitting(true);
    try {
      await memoryApi.storeMemory({
        family_id: Number(familyId),
        category,
        key,
        content,
      });

      setSuccessMsg('Financial preference stored in persistent memory!');
      setKey('');
      setContent('');
      setIsModalOpen(false);
      fetchMemories();
    } catch (err) {
      console.error('Failed to store memory:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Brain className="w-8 h-8 text-purple-400" />
            <span>Financial Memory System</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Persistent storage of family financial decisions, preferences, and long-term priorities.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-sm shadow-lg shadow-purple-500/25 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          <span>Remember Preference</span>
        </button>
      </div>

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Memory Search */}
      <GlassCard className="p-4">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search financial memories (e.g. phone, vacation, priority)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl glass-input text-xs"
          />
        </div>
      </GlassCard>

      {/* Memory Grid */}
      {loading ? (
        <div className="py-12 text-center text-slate-400">Searching financial memories...</div>
      ) : memories.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {memories.map((mem) => (
            <GlassCard key={mem.id || mem.key} className="p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {mem.category || 'General'}
                </span>
              </div>
              <h4 className="font-bold text-white text-base mt-2">{mem.key}</h4>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">{mem.content}</p>
            </GlassCard>
          ))}
        </div>
      ) : (
        <div className="py-12 text-center text-slate-400">No financial memories recorded for family #{familyId}.</div>
      )}

      {/* Add Memory Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 relative shadow-2xl">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white p-1"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-xl font-extrabold text-white mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-purple-400" />
              <span>Store Financial Preference</span>
            </h3>

            <form onSubmit={handleStoreMemory} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm bg-slate-900"
                >
                  <option value="Savings Preferences">Savings Preferences</option>
                  <option value="Spending Rules">Spending Rules</option>
                  <option value="Investment Goals">Investment Goals</option>
                  <option value="Household Commitments">Household Commitments</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Memory Title / Key</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Phone Purchase Budget Priority"
                  value={key}
                  onChange={(e) => setKey(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Memory Content / Detail</label>
                <textarea
                  required
                  rows={3}
                  placeholder="e.g. Prefer to maintain emergency fund of 50,000 before buying non-essential gadgets."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm"
                />
              </div>

              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-500/25"
                >
                  {submitting ? 'Saving...' : 'Remember'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FinancialMemory;
