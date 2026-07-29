import React, { useEffect, useState } from 'react';
import { forecastService } from '../../services/forecastService';
import { Forecast as ForecastType } from '../../types';
import { TrendingUp, Cpu, Award, RefreshCw, BarChart2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip 
} from 'recharts';

export const Forecast: React.FC = () => {
  const [forecasts, setForecasts] = useState<ForecastType[]>([]);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);

  useEffect(() => {
    loadForecasts();
  }, []);

  const loadForecasts = async () => {
    try {
      const data = await forecastService.getForecasts();
      setForecasts(data);
    } catch (e) {
      toast.error("Failed to load forecast trends.");
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModel = async () => {
    setTraining(true);
    try {
      const res = await forecastService.trainModel();
      toast.success(res.message || "Model trained successfully!");
      loadForecasts();
    } catch (e) {
      toast.error("Failed to train model.");
    } finally {
      setTraining(false);
    }
  };

  const chartData = forecasts.map(f => ({
    date: new Date(f.date).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' }),
    bpSys: f.predicted_systolic,
    bpDia: f.predicted_diastolic,
    sugar: f.predicted_blood_sugar,
    confidence: f.confidence_score
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
      {/* AI Model Trainer Header */}
      <div className="bg-white border border-sky-100 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <span className="p-3.5 bg-sky-50 text-sky-600 rounded-xl border border-sky-100">
            <Cpu className="h-6 w-6" />
          </span>
          <div>
            <h3 className="text-xl font-bold text-slate-800">AI Health Predictive Forecast</h3>
            <p className="text-sm font-semibold text-slate-400">ML models analyze historic sugar levels, BP records, and sleep logs to forecast trends.</p>
          </div>
        </div>
        <button
          onClick={handleTrainModel}
          disabled={training}
          className="flex items-center gap-2 px-5 py-3 bg-sky-500 hover:bg-sky-600 active:scale-95 text-white font-bold rounded-xl transition-all cursor-pointer shadow-xs whitespace-nowrap"
        >
          <RefreshCw className={`h-5 w-5 ${training ? 'animate-spin' : ''}`} />
          <span>{training ? 'Training...' : 'Train ML Model'}</span>
        </button>
      </div>

      {/* Prediction Graphs */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Forecasted Blood Sugar */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Predicted Blood Glucose Trend (mg/dL)</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorForeSugar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} domain={['auto', 'auto']} />
                <Tooltip />
                <Area type="monotone" dataKey="sugar" name="Predicted Glucose" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorForeSugar)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Forecasted Blood Pressure */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4">Predicted BP Range (mmHg)</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorForeSys" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} domain={['auto', 'auto']} />
                <Tooltip />
                <Area type="monotone" dataKey="bpSys" name="Systolic Prediction" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorForeSys)" />
                <Area type="monotone" dataKey="bpDia" name="Diastolic Prediction" stroke="#6366f1" strokeWidth={2} fillOpacity={0} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Forecast Table with Confidence scores */}
      <div className="bg-white border border-sky-100 rounded-2xl shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <h4 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <BarChart2 className="h-5 w-5 text-sky-500" />
            <span>AI Predictive Readings Schedule</span>
          </h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Predicted Date</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Forecasted Blood Pressure</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Forecasted Sugar Levels</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">AI Prediction Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {forecasts.map((f, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50">
                  <td className="px-6 py-4 text-base font-semibold">
                    {new Date(f.date).toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                  </td>
                  <td className="px-6 py-4 text-base font-bold text-sky-700">{f.predicted_systolic}/{f.predicted_diastolic} mmHg</td>
                  <td className="px-6 py-4 text-base font-bold text-emerald-600">{f.predicted_blood_sugar} mg/dL</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-slate-100 h-2.5 rounded-full overflow-hidden">
                        <div className="bg-sky-500 h-full" style={{ width: `${f.confidence_score}%` }} />
                      </div>
                      <span className="text-sm font-bold text-slate-700">{f.confidence_score}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default Forecast;
