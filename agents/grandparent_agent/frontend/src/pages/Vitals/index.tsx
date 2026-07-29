import React, { useEffect, useState } from 'react';
import { vitalsService } from '../../services/vitalsService';
import { Vitals as VitalsType } from '../../types';
import { Plus, Search, Trash2, Heart, TrendingUp, Activity, Thermometer } from 'lucide-react';
import toast from 'react-hot-toast';
import Dialog from '../../components/common/Dialog';
import StatusBadge from '../../components/common/StatusBadge';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip 
} from 'recharts';

export const Vitals: React.FC = () => {
  const [logs, setLogs] = useState<VitalsType[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // New vital state
  const [systolic, setSystolic] = useState('120');
  const [diastolic, setDiastolic] = useState('80');
  const [sugar, setSugar] = useState('110');
  const [hr, setHr] = useState('72');
  const [temp, setTemp] = useState('98.4');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await vitalsService.getVitals();
      setLogs(data);
    } catch (e) {
      toast.error("Failed to fetch vitals data.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddVitals = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const newVital: VitalsType = {
        blood_pressure: `${systolic}/${diastolic}`,
        systolic: parseInt(systolic),
        diastolic: parseInt(diastolic),
        blood_sugar: parseInt(sugar),
        heart_rate: parseInt(hr),
        temperature: parseFloat(temp),
      };
      await vitalsService.addVitals(newVital);
      toast.success("Vitals log added successfully!");
      setIsModalOpen(false);
      loadLogs();
    } catch (e) {
      toast.error("Failed to record vitals log.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure you want to delete this log?")) return;
    try {
      await vitalsService.deleteVitals(id);
      toast.success("Log deleted.");
      loadLogs();
    } catch (e) {
      toast.error("Error deleting log.");
    }
  };

  // Filter & search logs
  const filteredLogs = logs.filter(log => {
    const statusMatch = statusFilter === 'All' || log.status === statusFilter;
    const searchMatch = 
      log.blood_pressure.includes(searchTerm) || 
      log.blood_sugar.toString().includes(searchTerm) ||
      (log.timestamp && new Date(log.timestamp).toLocaleDateString().includes(searchTerm));
    return statusMatch && searchMatch;
  });

  // Prepare chart data format
  const chartData = logs.map(log => ({
    date: log.timestamp ? new Date(log.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' }) : '',
    sugar: log.blood_sugar,
    heartRate: log.heart_rate,
    sys: log.systolic || parseInt(log.blood_pressure.split('/')[0]) || 120,
    dia: log.diastolic || parseInt(log.blood_pressure.split('/')[1]) || 80
  }));

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-sky-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Vitals Summary Row */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3.5 bg-rose-50 border border-rose-100 text-rose-600 rounded-xl">
            <Heart className="h-6 w-6" />
          </div>
          <div>
            <span className="block text-xs font-semibold text-slate-400 uppercase">Avg Blood Pressure</span>
            <span className="block text-2xl font-black text-slate-800">127/81 mmHg</span>
          </div>
        </div>

        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3.5 bg-emerald-50 border border-emerald-100 text-emerald-600 rounded-xl">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <span className="block text-xs font-semibold text-slate-400 uppercase">Avg Fasting Sugar</span>
            <span className="block text-2xl font-black text-slate-800">133 mg/dL</span>
          </div>
        </div>

        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3.5 bg-sky-50 border border-sky-100 text-sky-600 rounded-xl">
            <TrendingUp className="h-6 w-6" />
          </div>
          <div>
            <span className="block text-xs font-semibold text-slate-400 uppercase">Heart Rate Range</span>
            <span className="block text-2xl font-black text-slate-800">68 - 76 bpm</span>
          </div>
        </div>

        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center gap-4">
          <div className="p-3.5 bg-amber-50 border border-amber-100 text-amber-600 rounded-xl">
            <Thermometer className="h-6 w-6" />
          </div>
          <div>
            <span className="block text-xs font-semibold text-slate-400 uppercase">Body Temp</span>
            <span className="block text-2xl font-black text-slate-800">98.4 °F</span>
          </div>
        </div>
      </div>

      {/* Visual Trends Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Blood Sugar Graph */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Blood Glucose Trend (mg/dL)</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorSugar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} domain={['auto', 'auto']} />
                <Tooltip />
                <Area type="monotone" dataKey="sugar" name="Blood Sugar" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorSugar)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Blood Pressure Graph */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Blood Pressure Trend (mmHg)</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorSys" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorDia" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} domain={['auto', 'auto']} />
                <Tooltip />
                <Area type="monotone" dataKey="sys" name="Systolic (High)" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorSys)" />
                <Area type="monotone" dataKey="dia" name="Diastolic (Low)" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#colorDia)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Vitals Log Table */}
      <div className="bg-white border border-sky-100 rounded-2xl shadow-xs overflow-hidden">
        {/* Table Filters Header */}
        <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="relative flex-1 sm:flex-none">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                <Search className="h-5 w-5" />
              </span>
              <input
                type="text"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                placeholder="Search logs..."
                className="w-full sm:w-64 pl-10 pr-4 py-2 text-base rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500"
              />
            </div>
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="text-base rounded-xl border border-slate-200 p-2 focus:outline-none focus:border-sky-500 bg-white"
            >
              <option value="All">All Statuses</option>
              <option value="Normal">Normal</option>
              <option value="Warning">Warning</option>
              <option value="Critical">Critical</option>
            </select>
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold text-base rounded-xl transition-all cursor-pointer shadow-sm shadow-emerald-100"
          >
            <Plus className="h-5 w-5" />
            <span>Add Vitals Entry</span>
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Date & Time</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Blood Pressure</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Blood Glucose</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Heart Rate</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Temperature</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Status</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4 text-base font-semibold">
                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : ''}
                  </td>
                  <td className="px-6 py-4 text-base font-bold text-slate-800">{log.blood_pressure} mmHg</td>
                  <td className="px-6 py-4 text-base font-bold text-emerald-600">{log.blood_sugar} mg/dL</td>
                  <td className="px-6 py-4 text-base font-medium">{log.heart_rate} bpm</td>
                  <td className="px-6 py-4 text-base font-medium">{log.temperature} °F</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={log.status || 'Normal'} />
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => log.id && handleDelete(log.id)}
                      className="text-rose-500 hover:text-rose-700 p-1 rounded-lg hover:bg-rose-50 transition-colors cursor-pointer"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              ))}
              {filteredLogs.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400 font-medium">
                    No vitals entries match your filter rules.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Entry Modal */}
      <Dialog isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Log Health Vitals">
        <form onSubmit={handleAddVitals} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Systolic BP (High)</label>
              <input
                type="number"
                value={systolic}
                onChange={e => setSystolic(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Diastolic BP (Low)</label>
              <input
                type="number"
                value={diastolic}
                onChange={e => setDiastolic(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Blood Sugar (mg/dL)</label>
            <input
              type="number"
              value={sugar}
              onChange={e => setSugar(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Heart Rate (bpm)</label>
              <input
                type="number"
                value={hr}
                onChange={e => setHr(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Temperature (°F)</label>
              <input
                type="number"
                step="0.1"
                value={temp}
                onChange={e => setTemp(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-5 py-2.5 rounded-xl border border-slate-200 font-bold hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold transition-colors shadow-xs"
            >
              {saving ? 'Adding...' : 'Log Vitals'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
export default Vitals;
