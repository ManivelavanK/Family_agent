import { motion } from 'framer-motion';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { Cpu, Heart, Award, Zap, Compass } from 'lucide-react';
import type { DigitalTwin } from '../services/api';

interface DigitalTwinPageProps {
  digitalTwin: DigitalTwin | null;
}

export default function DigitalTwinPage({ digitalTwin }: DigitalTwinPageProps) {
  
  const metrics = [
    { title: 'Planning Score', val: `${digitalTwin?.planning_score || 85}%`, icon: compassIcon(), color: 'text-blue-600 bg-blue-50' },
    { title: 'Routine Consistency', val: `${digitalTwin?.routine_consistency || 78}%`, icon: awardIcon(), color: 'text-indigo-600 bg-indigo-50' },
    { title: 'Goal Completion', val: `${digitalTwin?.goal_completion || 70}%`, icon: zapIcon(), color: 'text-purple-600 bg-purple-50' },
    { title: 'Time Utilization', val: `${digitalTwin?.time_utilization || 82}%`, icon: cpuIcon(), color: 'text-emerald-600 bg-emerald-50' },
    { title: 'Stress Level', val: `${digitalTwin?.stress_level || 25}%`, icon: heartIcon(), color: 'text-rose-600 bg-rose-50' },
    { title: 'Productivity Rate', val: `${digitalTwin?.productivity || 80}%`, icon: shieldIcon(), color: 'text-amber-600 bg-amber-50' }
  ];

  // Helper icons
  function compassIcon() { return <Compass className="h-4.5 w-4.5" />; }
  function awardIcon() { return <Award className="h-4.5 w-4.5" />; }
  function zapIcon() { return <Zap className="h-4.5 w-4.5" />; }
  function cpuIcon() { return <Cpu className="h-4.5 w-4.5" />; }
  function heartIcon() { return <Heart className="h-4.5 w-4.5" />; }
  function shieldIcon() { return <Award className="h-4.5 w-4.5" />; }

  const radarData = [
    { subject: 'Consistency', A: digitalTwin?.routine_consistency || 78, fullMark: 100 },
    { subject: 'Productivity', A: digitalTwin?.productivity || 80, fullMark: 100 },
    { subject: 'Goals', A: digitalTwin?.goal_completion || 70, fullMark: 100 },
    { subject: 'Time Utilization', A: digitalTwin?.time_utilization || 82, fullMark: 100 },
    { subject: 'Planning', A: digitalTwin?.planning_score || 85, fullMark: 100 },
  ];

  const historyData = [
    { name: 'W1', score: 70, stress: 35 },
    { name: 'W2', score: 75, stress: 30 },
    { name: 'W3', score: 80, stress: 28 },
    { name: 'W4', score: 85, stress: 25 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.25 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
            <Cpu className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-lg leading-tight">Planner Digital Twin</h3>
            <p className="text-[11px] text-slate-400 font-semibold">AI replica mapping schedule load, efficiency limits, and stress factors</p>
          </div>
        </div>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        {metrics.map((item, idx) => (
          <div key={idx} className="white-card p-4 flex flex-col justify-between hover:scale-[1.03] transition-all">
            <div className="flex justify-between items-start">
              <span className="text-[9px] uppercase font-extrabold text-slate-400 tracking-wider leading-none">{item.title}</span>
              <div className={`p-1.5 rounded-lg ${item.color}`}>
                {item.icon}
              </div>
            </div>
            <p className="text-xl font-extrabold text-slate-800 mt-2">{item.val}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Radar profile */}
        <div className="white-card p-6 flex flex-col justify-between items-center text-center">
          <h4 className="text-xs uppercase font-extrabold text-slate-400 tracking-wider mb-4 self-start">Behavior Profile</h4>
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="#E2E8F0" />
                <PolarAngleAxis dataKey="subject" stroke="#64748B" fontSize={10} fontWeight="bold" />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#E2E8F0" tick={false} />
                <Radar name="Digital Twin" dataKey="A" stroke="#1D4ED8" fill="#1D4ED8" fillOpacity={0.15} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Consistency trend */}
        <div className="lg:col-span-2 white-card p-6 flex flex-col justify-between">
          <h4 className="text-xs uppercase font-extrabold text-slate-400 tracking-wider mb-4">Historical Progression</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={historyData}>
                <defs>
                  <linearGradient id="colorTwin" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1D4ED8" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#1D4ED8" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" stroke="#94A3B8" fontSize={11} axisLine={false} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#FFF', borderRadius: '12px', border: '1px solid #E2E8F0' }} />
                <Area type="monotone" dataKey="score" stroke="#1D4ED8" strokeWidth={2.5} fillOpacity={1} fill="url(#colorTwin)" name="Aggregate Score %" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
