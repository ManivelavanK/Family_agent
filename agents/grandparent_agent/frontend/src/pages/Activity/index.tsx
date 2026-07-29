import React, { useEffect, useState } from 'react';
import { activityService } from '../../services/activityService';
import { Activity as ActivityType } from '../../types';
import { Footprints, Moon, Plus, PlusCircle, Flame, Timer } from 'lucide-react';
import toast from 'react-hot-toast';
import Dialog from '../../components/common/Dialog';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  LineChart, 
  Line 
} from 'recharts';

export const Activity: React.FC = () => {
  const [activities, setActivities] = useState<ActivityType[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [steps, setSteps] = useState('4500');
  const [sleep, setSleep] = useState('7.0');
  const [exerciseType, setExerciseType] = useState('Walking');
  const [duration, setDuration] = useState('30');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    setLoading(true);
    try {
      const data = await activityService.getActivities();
      setActivities(data);
    } catch (e) {
      toast.error("Failed to load activities.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddActivity = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const newAct: ActivityType = {
        date: new Date().toISOString().split('T')[0],
        steps: parseInt(steps) || 0,
        sleep_hours: parseFloat(sleep) || 0,
        exercise_type: exerciseType,
        exercise_duration_minutes: parseInt(duration) || 0,
        calories_burned: Math.round((parseInt(duration) || 0) * 5.5) // approx multiplier
      };
      await activityService.addActivity(newAct);
      toast.success("Activity logged!");
      setIsModalOpen(false);
      loadActivities();
    } catch (e) {
      toast.error("Failed to save activity log.");
    } finally {
      setSaving(false);
    }
  };

  const chartData = activities.map(act => ({
    date: new Date(act.date).toLocaleDateString([], { month: 'short', day: 'numeric' }),
    steps: act.steps,
    sleep: act.sleep_hours,
    duration: act.exercise_duration_minutes
  }));

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-sky-500 border-t-transparent" />
      </div>
    );
  }

  const latest = activities[activities.length - 1];

  return (
    <div className="space-y-8">
      {/* Overview Rows */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="p-3.5 bg-emerald-50 text-emerald-600 rounded-xl border border-emerald-100">
              <Footprints className="h-6 w-6" />
            </span>
            <div>
              <span className="block text-xs font-semibold text-slate-400 uppercase">Steps Logged</span>
              <span className="block text-2xl font-black text-slate-800">{latest?.steps || 0} / 5000 steps</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="p-3.5 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">
              <Moon className="h-6 w-6" />
            </span>
            <div>
              <span className="block text-xs font-semibold text-slate-400 uppercase">Last Night Sleep</span>
              <span className="block text-2xl font-black text-slate-800">{latest?.sleep_hours || 0} hours</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="p-3.5 bg-sky-50 text-sky-600 rounded-xl border border-sky-100">
              <Timer className="h-6 w-6" />
            </span>
            <div>
              <span className="block text-xs font-semibold text-slate-400 uppercase">Exercise Session</span>
              <span className="block text-2xl font-black text-slate-800">{latest?.exercise_duration_minutes || 0} mins ({latest?.exercise_type || 'None'})</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recharts Displays */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Step Trend Bar Chart */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Daily Step Count (7-Day Trend)</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Bar dataKey="steps" fill="#10b981" radius={[4, 4, 0, 0]} name="Steps Count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sleep Line Chart */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Sleep Hours Log (Target: 7 hrs)</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="sleep" stroke="#6366f1" strokeWidth={3} dot={{ r: 5 }} name="Sleep Hours" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Activity Table */}
      <div className="bg-white border border-sky-100 rounded-2xl shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <h4 className="text-lg font-bold text-slate-800">Physical Activity History</h4>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold rounded-xl text-sm transition-all cursor-pointer shadow-xs"
          >
            <Plus className="h-4 w-4" />
            <span>Log Activity</span>
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Date</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Steps Taken</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Sleep Hours</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Exercise Type</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Duration</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Est. Calories</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {activities.slice().reverse().map((act) => (
                <tr key={act.id} className="hover:bg-slate-50/50">
                  <td className="px-6 py-4 text-base font-semibold">{new Date(act.date).toLocaleDateString()}</td>
                  <td className="px-6 py-4 text-base font-bold text-emerald-600">{act.steps.toLocaleString()} steps</td>
                  <td className="px-6 py-4 text-base font-medium">{act.sleep_hours} hrs</td>
                  <td className="px-6 py-4 text-base font-semibold text-slate-800">{act.exercise_type}</td>
                  <td className="px-6 py-4 text-base font-medium">{act.exercise_duration_minutes} mins</td>
                  <td className="px-6 py-4 text-base font-medium text-amber-600">{act.calories_burned || 0} kcal</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Activity Modal */}
      <Dialog isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Log Daily Activity">
        <form onSubmit={handleAddActivity} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Steps Count</label>
            <input
              type="number"
              value={steps}
              onChange={e => setSteps(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Sleep Duration (Hours)</label>
            <input
              type="number"
              step="0.1"
              value={sleep}
              onChange={e => setSleep(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Exercise Type</label>
              <select
                value={exerciseType}
                onChange={e => setExerciseType(e.target.value)}
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none bg-white"
              >
                <option value="Walking">Walking</option>
                <option value="Yoga">Yoga</option>
                <option value="Stretching">Stretching</option>
                <option value="None">None</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Duration (Minutes)</label>
              <input
                type="number"
                value={duration}
                onChange={e => setDuration(e.target.value)}
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
              {saving ? 'Saving...' : 'Save Log'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
export default Activity;
