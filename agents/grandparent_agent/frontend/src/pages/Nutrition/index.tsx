import React, { useEffect, useState } from 'react';
import { nutritionService } from '../../services/nutritionService';
import { Nutrition as NutritionType } from '../../types';
import { Plus, Apple, Droplet, Flame, ClipboardList } from 'lucide-react';
import toast from 'react-hot-toast';
import Dialog from '../../components/common/Dialog';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip,
  BarChart,
  Bar
} from 'recharts';

export const Nutrition: React.FC = () => {
  const [logs, setLogs] = useState<NutritionType[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [meals, setMeals] = useState('Oats & Banana, Brown Rice with Sambar, Chapati & Veg Dal');
  const [calories, setCalories] = useState('1600');
  const [water, setWater] = useState('2000');
  const [notes, setNotes] = useState('Digestion was comfortable.');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadNutrition();
  }, []);

  const loadNutrition = async () => {
    setLoading(true);
    try {
      const data = await nutritionService.getNutrition();
      setLogs(data);
    } catch (e) {
      toast.error("Failed to load nutrition logs.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddNutrition = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const mealsArray = meals.split(',').map(m => m.trim());
      const newNut: NutritionType = {
        date: new Date().toISOString().split('T')[0],
        meals: mealsArray,
        calories_consumed: parseInt(calories) || 1500,
        water_intake_ml: parseInt(water) || 1500,
        food_notes: notes
      };
      await nutritionService.addNutrition(newNut);
      toast.success("Meal details logged successfully!");
      setIsModalOpen(false);
      loadNutrition();
    } catch (e) {
      toast.error("Failed to save nutrition entry.");
    } finally {
      setSaving(false);
    }
  };

  const chartData = logs.map(l => ({
    date: new Date(l.date).toLocaleDateString([], { month: 'short', day: 'numeric' }),
    water: l.water_intake_ml,
    calories: l.calories_consumed
  }));

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-sky-500 border-t-transparent" />
      </div>
    );
  }

  const latest = logs[logs.length - 1];

  return (
    <div className="space-y-8">
      {/* Nutrition Summary Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="p-3.5 bg-blue-50 text-blue-600 rounded-xl border border-blue-100">
              <Droplet className="h-6 w-6" />
            </span>
            <div>
              <span className="block text-xs font-semibold text-slate-400 uppercase">Water Intake</span>
              <span className="block text-2xl font-black text-slate-800">{latest?.water_intake_ml || 0} / 2000 ml</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="p-3.5 bg-emerald-50 text-emerald-600 rounded-xl border border-emerald-100">
              <Flame className="h-6 w-6" />
            </span>
            <div>
              <span className="block text-xs font-semibold text-slate-400 uppercase">Calories Intake</span>
              <span className="block text-2xl font-black text-slate-800">{latest?.calories_consumed || 0} kcal</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="p-3.5 bg-amber-50 text-amber-600 rounded-xl border border-amber-100">
              <Apple className="h-6 w-6" />
            </span>
            <div>
              <span className="block text-xs font-semibold text-slate-400 uppercase">Daily Meals Count</span>
              <span className="block text-2xl font-black text-slate-800">{latest?.meals.length || 0} meals</span>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Recharts */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Water Intake Chart */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Water Consumption History (ml)</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorWater" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Area type="monotone" dataKey="water" name="Water (ml)" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorWater)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Calories Intake Chart */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Daily Calories Intake Trend (kcal)</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Bar dataKey="calories" fill="#10b981" radius={[4, 4, 0, 0]} name="Calories (kcal)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Meal History Table */}
      <div className="bg-white border border-sky-100 rounded-2xl shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <h4 className="text-lg font-bold text-slate-800">Dietary & Meal History</h4>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold rounded-xl text-sm transition-all cursor-pointer shadow-xs"
          >
            <Plus className="h-4 w-4" />
            <span>Record Meals</span>
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Date</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Meals Consumed</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Total Calories</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Water Intake</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Digestion Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {logs.slice().reverse().map((log) => (
                <tr key={log.id} className="hover:bg-slate-50/50">
                  <td className="px-6 py-4 text-base font-semibold">{new Date(log.date).toLocaleDateString()}</td>
                  <td className="px-6 py-4 text-base font-semibold text-slate-800">
                    <ul className="list-disc pl-4 space-y-0.5">
                      {log.meals.map((meal, index) => (
                        <li key={index}>{meal}</li>
                      ))}
                    </ul>
                  </td>
                  <td className="px-6 py-4 text-base font-bold text-emerald-600">{log.calories_consumed} kcal</td>
                  <td className="px-6 py-4 text-base font-bold text-blue-600">{log.water_intake_ml} ml</td>
                  <td className="px-6 py-4 text-base italic text-slate-500">{log.food_notes || 'None'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Entry Modal */}
      <Dialog isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Log Daily Meals & Hydration">
        <form onSubmit={handleAddNutrition} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Meals Consumed (comma-separated)</label>
            <input
              type="text"
              value={meals}
              onChange={e => setMeals(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="e.g. Idli with Chutney, Roti & Curry"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Calories Consumed (kcal)</label>
              <input
                type="number"
                value={calories}
                onChange={e => setCalories(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Water Intake (ml)</label>
              <input
                type="number"
                value={water}
                onChange={e => setWater(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Digestion / Diet Notes</label>
            <textarea
              rows={2}
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="Felt light and sugar stayed controlled..."
            />
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
              {saving ? 'Saving...' : 'Save Meals'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
export default Nutrition;
