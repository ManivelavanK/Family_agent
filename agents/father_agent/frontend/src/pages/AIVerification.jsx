import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Bot, Cpu, Database, Play, CheckCircle2, AlertTriangle, Layers, Activity, Brain } from 'lucide-react';
import { expenseApi } from '../services/expenseApi';
import { incomeApi } from '../services/incomeApi';
import { budgetApi } from '../services/budgetApi';
import { billApi } from '../services/billApi';
import { memoryApi } from '../services/memoryApi';
import { financeApi } from '../services/financeApi';

export const AIVerification = () => {
  const { familyId } = useFamily();
  const [latestTrace, setLatestTrace] = useState(null);
  const [liveData, setLiveData] = useState({
    income: 0,
    expenses: 0,
    budgetsCount: 0,
    upcomingBills: 0,
    savingsRecommendation: '',
    memoryCount: 0
  });
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchLiveDataAndTrace = async () => {
    setLoading(true);
    try {
      // 1. Fetch Latest Trace
      const traceRes = await fetch(`http://localhost:8000/finance/agent/debug/latest/trace`);
      if (traceRes.ok) {
        const traceData = await traceRes.json();
        setLatestTrace(Object.keys(traceData).length > 0 ? traceData : null);
      }

      // 2. Fetch Live data metrics
      const [inc, exp, bud, bills, mems] = await Promise.all([
        incomeApi.getIncome(familyId),
        expenseApi.getExpenses(familyId),
        budgetApi.getBudgets(familyId),
        billApi.getUpcomingBills(familyId),
        memoryApi.getMemories(familyId)
      ]);

      const totalIncome = inc.reduce((sum, item) => sum + parseFloat(item.amount), 0);
      const totalExpenses = exp.reduce((sum, item) => sum + parseFloat(item.amount), 0);

      setLiveData({
        income: totalIncome,
        expenses: totalExpenses,
        budgetsCount: bud.length,
        upcomingBills: bills.length,
        memoryCount: mems.count || mems.memories?.length || 0
      });
    } catch (err) {
      console.error('Error fetching verification details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveDataAndTrace();
  }, [familyId]);

  const handleRunTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      // Step 1-4: Fetch current financial metrics
      const [sumData, expData, budData, billData] = await Promise.all([
        financeApi.getFinancialSummary(familyId),
        expenseApi.getExpenses(familyId),
        budgetApi.getBudgets(familyId),
        billApi.getUpcomingBills(familyId)
      ]);

      // Step 5: Ask backend AI test question
      const testQuestion = "Analyze my current income vs expenses and tell me if I have budget room.";
      const res = await financeApi.askSupervisor(familyId, testQuestion);

      // Step 6-7: Display returned traces and check live db usage
      const hasLiveContext = res.data_sources?.some(src => 
        src.toLowerCase().includes('database') || 
        src.toLowerCase().includes('limit') ||
        src.toLowerCase().includes('expense') ||
        src.toLowerCase().includes('bill')
      ) || false;

      setTestResult({
        question: testQuestion,
        answer: res.answer,
        agents_used: res.agents_used || [],
        tools_used: res.tools_used || [],
        data_sources: res.data_sources || [],
        hasLiveContext
      });

      // Refresh latest trace
      const traceRes = await fetch(`http://localhost:8000/finance/agent/debug/latest/trace`);
      if (traceRes.ok) {
        const traceData = await traceRes.json();
        setLatestTrace(traceData);
      }
    } catch (err) {
      console.error('Error running dynamicity test:', err);
      setTestResult({ error: 'Verification failed. Backend unreachable or timed out.' });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
          <Cpu className="w-8 h-8 text-[#D4A72C]" />
          <span>AI & Live Data Verification Console</span>
        </h1>
        <p className="text-[#627D98] text-sm mt-1">
          Admin tools to inspect the multi-agent planning traces, database provenance, and dynamic PostgreSQL synchronization.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Live database records */}
        <div className="lg:col-span-4 space-y-6">
          <GlassCard className="p-6 border border-[#243B53]/30">
            <h2 className="text-sm font-bold uppercase tracking-widest text-[#D4A72C] flex items-center gap-2 mb-4">
              <Database className="w-4 h-4" />
              <span>Live Database Values</span>
            </h2>

            {loading ? (
              <div className="py-6 text-slate-400 text-xs">Loading Postgres tables...</div>
            ) : (
              <div className="space-y-4 text-slate-200">
                <div className="flex justify-between border-b border-[#243B53]/40 pb-2">
                  <span className="text-xs text-slate-400">Total Income:</span>
                  <span className="text-sm font-mono font-bold text-emerald-400">
                    ₹{liveData.income.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between border-b border-[#243B53]/40 pb-2">
                  <span className="text-xs text-slate-400">Total Expenses:</span>
                  <span className="text-sm font-mono font-bold text-rose-400">
                    ₹{liveData.expenses.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between border-b border-[#243B53]/40 pb-2">
                  <span className="text-xs text-slate-400">Budgets Configured:</span>
                  <span className="text-sm font-mono font-bold text-slate-200">
                    {liveData.budgetsCount}
                  </span>
                </div>
                <div className="flex justify-between border-b border-[#243B53]/40 pb-2">
                  <span className="text-xs text-slate-400">Upcoming Bills:</span>
                  <span className="text-sm font-mono font-bold text-slate-200">
                    {liveData.upcomingBills}
                  </span>
                </div>
                <div className="flex justify-between pb-2">
                  <span className="text-xs text-slate-400">Preference Memories:</span>
                  <span className="text-sm font-mono font-bold text-slate-200">
                    {liveData.memoryCount}
                  </span>
                </div>

                <button
                  onClick={handleRunTest}
                  disabled={testing}
                  className="w-full py-2.5 rounded-xl bg-[#0F766E] hover:bg-emerald-600 disabled:opacity-50 text-white font-bold text-xs shadow-lg shadow-[#0f766e]/20 transition-all flex items-center justify-center gap-2 cursor-pointer mt-4"
                >
                  {testing ? (
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Play className="w-3.5 h-3.5" />
                  )}
                  <span>Run Dynamicity Test</span>
                </button>
              </div>
            )}
          </GlassCard>

          {/* Test Results Card */}
          {testResult && (
            <GlassCard className="p-6 border border-[#243B53]/40 bg-[#0B1F33]/40">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[#D4A72C] flex items-center gap-2 mb-3">
                <Activity className="w-4 h-4" />
                <span>Test Execution Logs</span>
              </h2>

              {testResult.error ? (
                <div className="text-rose-400 text-xs">{testResult.error}</div>
              ) : (
                <div className="space-y-3 text-xs text-slate-300">
                  <div>
                    <span className="font-bold text-slate-400 block mb-0.5">Test Prompt:</span>
                    <p className="italic font-mono">"{testResult.question}"</p>
                  </div>
                  <div>
                    <span className="font-bold text-slate-400 block mb-0.5">Live DB Context Verified:</span>
                    {testResult.hasLiveContext ? (
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold uppercase text-[9px] tracking-wider flex items-center gap-1 w-max mt-1">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>VERIFIED (DYNAMIC DB FETCH)</span>
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold uppercase text-[9px] tracking-wider flex items-center gap-1 w-max mt-1">
                        <AlertTriangle className="w-3 h-3" />
                        <span>MOCKED / STATIC</span>
                      </span>
                    )}
                  </div>
                  <div>
                    <span className="font-bold text-slate-400 block mb-1">Agents Selected:</span>
                    <div className="flex gap-1.5 flex-wrap">
                      {testResult.agents_used.map((a, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-[#38BDF8] border border-slate-700">{a}</span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="font-bold text-slate-400 block mb-1">Tools Called:</span>
                    <div className="flex gap-1.5 flex-wrap">
                      {testResult.tools_used.map((t, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-slate-700">{t}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </GlassCard>
          )}
        </div>

        {/* Right Column: Latest Trace Details */}
        <div className="lg:col-span-8">
          <GlassCard className="p-6 border border-[#243B53]/30 h-full flex flex-col justify-between">
            <div>
              <h2 className="text-sm font-bold uppercase tracking-widest text-[#D4A72C] flex items-center gap-2 mb-4">
                <Layers className="w-4 h-4" />
                <span>Last AI Supervisor Trace Details</span>
              </h2>

              {!latestTrace ? (
                <div className="h-64 flex items-center justify-center text-slate-400 text-xs border border-dashed border-slate-800 rounded-xl">
                  No trace recorded yet. Ask a question to Father AI Chat first!
                </div>
              ) : (
                <div className="space-y-4 text-xs text-slate-200">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-b border-[#243B53]/40 pb-4">
                    <div>
                      <span className="text-slate-400 font-bold uppercase text-[10px]">Trace Request ID</span>
                      <p className="font-mono text-[11px] text-slate-300 mt-0.5">{latestTrace.request_id}</p>
                    </div>
                    <div>
                      <span className="text-slate-400 font-bold uppercase text-[10px]">Detected Intent</span>
                      <p className="font-bold text-[#38BDF8] mt-0.5">{latestTrace.intent}</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <span className="text-slate-400 font-bold uppercase text-[10px]">Selected Agents</span>
                      <div className="flex gap-1.5 flex-wrap mt-1">
                        {latestTrace.selected_agents?.map((a, i) => (
                          <span key={i} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[#38BDF8] font-mono">{a}</span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-400 font-bold uppercase text-[10px]">Executed Tools</span>
                      <div className="flex gap-1.5 flex-wrap mt-1">
                        {latestTrace.executed_tools?.map((t, i) => (
                          <span key={i} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-emerald-400 font-mono">{t}</span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-400 font-bold uppercase text-[10px]">Database Data Sources</span>
                      <div className="flex gap-1.5 flex-wrap mt-1">
                        {latestTrace.data_sources?.map((s, i) => (
                          <span key={i} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300 font-mono">{s}</span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-400 font-bold uppercase text-[10px]">Memories Retrieved</span>
                      {latestTrace.memory_retrieved && latestTrace.memory_retrieved.length > 0 ? (
                        <div className="space-y-1.5 mt-1">
                          {latestTrace.memory_retrieved.map((m, i) => (
                            <div key={i} className="p-2 rounded bg-slate-900 border border-slate-800 font-mono text-[10px]">
                              [{m.category}] {m.key}: {m.content}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-slate-500 italic mt-0.5">None retrieved.</p>
                      )}
                    </div>

                    <div>
                      <span className="text-slate-400 font-bold uppercase text-[10px]">Proposed Mutation Action</span>
                      {latestTrace.action ? (
                        <div className="p-2 rounded bg-slate-900 border border-slate-800 font-mono text-[10px] mt-1 space-y-1">
                          <div className="font-bold text-amber-400">Type: {latestTrace.action.type}</div>
                          <div>Payload: {JSON.stringify(latestTrace.action.payload)}</div>
                        </div>
                      ) : (
                        <p className="text-slate-500 italic mt-0.5">None proposed.</p>
                      )}
                    </div>

                    <div className="flex justify-between items-center border-t border-[#243B53]/40 pt-4 mt-4">
                      <div>
                        <span className="text-slate-400 font-bold uppercase text-[10px]">User Confirmation Required</span>
                        <p className="font-bold mt-0.5">{latestTrace.requires_confirmation ? 'YES' : 'NO'}</p>
                      </div>
                      <div>
                        <span className="text-slate-400 font-bold uppercase text-[10px]">Response Type</span>
                        <p className="font-bold text-emerald-400 text-right mt-0.5">{latestTrace.response_type}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div className="flex justify-end pt-4 mt-4 border-t border-[#243B53]/40">
              <button
                onClick={fetchLiveDataAndTrace}
                className="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 text-xs font-semibold hover:bg-slate-800 transition-all cursor-pointer flex items-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Refresh Trace Log</span>
              </button>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

// Add standard icon imports
const RefreshCw = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
    <path d="M21 3v5h-5" />
    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
    <path d="M3 21v-5h5" />
  </svg>
);

export default AIVerification;
