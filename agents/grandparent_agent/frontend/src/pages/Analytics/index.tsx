import React, { useEffect, useState } from 'react';
import { analyticsService, AnalyticsSummary } from '../../services/analyticsService';
import { vitalsService } from '../../services/vitalsService';
import { activityService } from '../../services/activityService';
import { Vitals, Activity } from '../../types';
import { BarChart3, Heart, Pill, Footprints, Droplet, Moon, Brain, Flame } from 'lucide-react';
import toast from 'react-hot-toast';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
} from 'recharts';

export const Analytics: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [vitalsData, setVitalsData] = useState<Vitals[]>([]);
  const [activityData, setActivityData] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      const data = await analyticsService.getSummary();
      setSummary(data);

      const vitLogs = await vitalsService.getVitals();
      // Reverse to chronological order (ascending) for charts
      setVitalsData([...vitLogs].reverse());

      const actLogs = await activityService.getActivities();
      // Reverse to chronological order (ascending) for charts
      setActivityData([...actLogs].reverse());
    } catch (e) {
      toast.error('Failed to load analytics data.');
    } finally {
      setLoading(false);
    }
  };

  if (loading || !summary) {
    return (
      <div className="flex justify-center items-center py-16">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-sky-500 border-t-transparent" />
      </div>
    );
  }

  const summaryCards = [
    { label: 'Average Blood Pressure', value: summary.average_bp + ' mmHg', icon: Heart, color: 'text-rose-600 bg-rose-50 border-rose-100' },
    { label: 'Average Blood Sugar', value: summary.average_sugar + ' mg/dL', icon: BarChart3, color: 'text-emerald-600 bg-emerald-50 border-emerald-100' },
    { label: 'Medicine Compliance', value: summary.medicine_compliance + '%', icon: Pill, color: 'text-sky-600 bg-sky-50 border-sky-100' },
    { label: 'Activity Score', value: summary.activity_score + ' / 100', icon: Footprints, color: 'text-amber-600 bg-amber-50 border-amber-100' },
    { label: 'Avg Water Intake', value: summary.water_intake_avg + ' ml', icon: Droplet, color: 'text-blue-600 bg-blue-50 border-blue-100' },
    { label: 'Avg Calories Intake', value: summary.calories_avg + ' kcal', icon: Flame, color: 'text-orange-600 bg-orange-50 border-orange-100' },
    { label: 'Average Sleep Duration', value: summary.sleep_avg + ' hrs', icon: Moon, color: 'text-indigo-600 bg-indigo-50 border-indigo-100' },
    { label: 'Memory Score Average', value: summary.memory_score_avg + '%', icon: Brain, color: 'text-purple-600 bg-purple-50 border-purple-100' },
  ];

  // Line chart data for vitals
  const vitalsChartData = vitalsData.map(v => ({
    date: new Date(v.timestamp || '').toLocaleDateString([], { month: 'short', day: 'numeric' }),
    sugar: v.blood_sugar,
    heartRate: v.heart_rate,
    sys: v.systolic || (v.blood_pressure ? parseInt(v.blood_pressure.split('/')[0]) : 120),
  }));

  // Bar chart data for activities
  const activityChartData = activityData.map(a => ({
    date: new Date(a.date).toLocaleDateString([], { month: 'short', day: 'numeric' }),
    steps: a.steps,
    sleep: a.sleep_hours * 100,
    duration: (a.exercise_duration_minutes || 0) * 10,
  }));

  // Pie chart data for medicine compliance
  const medicinePieData = [
    { name: 'Taken on Time', value: summary.medicine_compliance, fill: '#10b981' },
    { name: 'Missed / Late', value: 100 - summary.medicine_compliance, fill: '#f1f5f9' },
  ];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center gap-4 bg-gradient-to-r from-sky-50 to-indigo-50 border border-sky-100 rounded-2xl p-6">
        <div className="p-3 bg-sky-500 text-white rounded-xl">
          <BarChart3 className="h-6 w-6" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-slate-800">Health Analytics Overview</h3>
          <p className="text-sm font-semibold text-slate-400">Weekly averages and trend analysis across all health modules.</p>
        </div>
      </div>

      {/* Summary Cards Grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {summaryCards.map((card, i) => (
          <div key={i} className="bg-white border border-sky-100 p-5 rounded-2xl flex items-center gap-4">
            <span className={`p-3 rounded-xl border ${card.color}`}>
              <card.icon className="h-5 w-5" />
            </span>
            <div>
              <span className="block text-xs font-bold text-slate-400 uppercase leading-none mb-1">{card.label}</span>
              <span className="block text-xl font-black text-slate-800">{card.value}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row 1 */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Vitals Trend Line Chart */}
        <div className="lg:col-span-2 bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Weekly Vitals Trend</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={vitalsChartData}>
                <defs>
                  <linearGradient id="gSugar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gSys" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="sugar" name="Blood Sugar" stroke="#10b981" strokeWidth={2.5} fillOpacity={1} fill="url(#gSugar)" />
                <Area type="monotone" dataKey="sys" name="Systolic BP" stroke="#0ea5e9" strokeWidth={2.5} fillOpacity={1} fill="url(#gSys)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Medicine Compliance Pie Chart */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs flex flex-col">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Medicine Compliance</h4>
          <div className="flex-1 flex flex-col items-center justify-center">
            <div className="h-48">
              <ResponsiveContainer width={200} height="100%">
                <PieChart>
                  <Pie
                    data={medicinePieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    dataKey="value"
                    startAngle={90}
                    endAngle={-270}
                    strokeWidth={0}
                  >
                    {medicinePieData.map((entry, index) => (
                      <Cell key={index} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(val) => [`${val}%`, '']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="text-center -mt-4">
              <span className="block text-4xl font-black text-emerald-600">{summary.medicine_compliance}%</span>
              <span className="text-sm font-semibold text-slate-400">Adherence Rate</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Activity Bar Chart */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Weekly Activity Summary</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={activityChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Legend />
                <Bar dataKey="steps" name="Steps" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="duration" name="Exercise (×10)" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Health Score Overview */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Overall Wellness Scores</h4>
          <div className="space-y-4">
            {[
              { label: 'Heart Health (BP)', value: 78, color: 'bg-rose-500' },
              { label: 'Blood Sugar Control', value: 72, color: 'bg-emerald-500' },
              { label: 'Physical Activity', value: summary.activity_score, color: 'bg-amber-500' },
              { label: 'Cognitive (Memory)', value: summary.memory_score_avg, color: 'bg-purple-500' },
              { label: 'Hydration Level', value: Math.round((summary.water_intake_avg / 2000) * 100), color: 'bg-blue-500' },
            ].map((item, i) => (
              <div key={i}>
                <div className="flex justify-between text-sm font-bold text-slate-700 mb-1.5">
                  <span>{item.label}</span>
                  <span>{item.value}%</span>
                </div>
                <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${item.color}`}
                    style={{ width: `${Math.min(item.value, 100)}%`, transition: 'width 1s ease' }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
