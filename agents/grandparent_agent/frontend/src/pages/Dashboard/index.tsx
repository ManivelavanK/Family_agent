import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Heart, 
  Pill, 
  Calendar, 
  Droplet, 
  Footprints, 
  Moon, 
  AlertTriangle, 
  BrainCircuit, 
  Mic, 
  ShieldAlert, 
  Settings, 
  MessageSquare,
  TrendingUp,
  Activity as VitalsIcon
} from 'lucide-react';
import { vitalsService } from '../../services/vitalsService';
import { medicineService } from '../../services/medicineService';
import { appointmentService } from '../../services/appointmentService';
import { activityService } from '../../services/activityService';
import { nutritionService } from '../../services/nutritionService';
import { memoryService } from '../../services/memoryService';
import { Vitals, Medicine, Appointment, Activity, Nutrition, MemoryQuizResult } from '../../types';
import StatusBadge from '../../components/common/StatusBadge';

export const Dashboard: React.FC = () => {
  const [vitals, setVitals] = useState<Vitals | null>(null);
  const [meds, setMeds] = useState<Medicine[]>([]);
  const [appt, setAppt] = useState<Appointment | null>(null);
  const [activity, setActivity] = useState<Activity | null>(null);
  const [nutrition, setNutrition] = useState<Nutrition | null>(null);
  const [quizScore, setQuizScore] = useState<number>(85);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const vitLogs = await vitalsService.getVitals();
        if (vitLogs.length > 0) setVitals(vitLogs[0]);

        const medList = await medicineService.getMedicines();
        setMeds(medList);

        const apptList = await appointmentService.getAppointments();
        const upcoming = apptList.filter(a => a.status === 'Upcoming')[0];
        if (upcoming) setAppt(upcoming);

        const actList = await activityService.getActivities();
        if (actList.length > 0) setActivity(actList[0]);

        const nutList = await nutritionService.getNutrition();
        if (nutList.length > 0) setNutrition(nutList[0]);

        const quizList = await memoryService.getQuizResults();
        if (quizList.length > 0) setQuizScore(quizList[0].score);
      } catch (e) {
        console.error("Error loading dashboard data", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-sky-500 border-t-transparent" />
        <p className="text-lg font-semibold text-slate-500">Loading your health dashboard...</p>
      </div>
    );
  }

  const bpVal = vitals?.blood_pressure || "120/80";
  const sugarVal = vitals?.blood_sugar || 120;
  const hrVal = vitals?.heart_rate || 72;
  const tempVal = vitals?.temperature || 98.4;

  const cards = [
    {
      title: "Blood Pressure",
      value: `${bpVal} mmHg`,
      status: parseInt(bpVal.split('/')[0]) > 130 ? "Warning" : "Normal",
      trend: "Stable",
      icon: Heart,
      color: "border-sky-200 bg-sky-50/50 text-sky-700",
      link: "/vitals"
    },
    {
      title: "Blood Sugar",
      value: `${sugarVal} mg/dL`,
      status: sugarVal > 140 ? "Warning" : "Normal",
      trend: "Normal post-meal",
      icon: VitalsIcon,
      color: "border-emerald-200 bg-emerald-50/50 text-emerald-700",
      link: "/vitals"
    },
    {
      title: "Heart Rate",
      value: `${hrVal} bpm`,
      status: "Normal",
      trend: "Excellent",
      icon: TrendingUp,
      color: "border-teal-200 bg-teal-50/50 text-teal-700",
      link: "/vitals"
    },
    {
      title: "Body Temp",
      value: `${tempVal} °F`,
      status: "Normal",
      trend: "Normal",
      icon: Droplet,
      color: "border-amber-200 bg-amber-50/50 text-amber-600",
      link: "/vitals"
    },
    {
      title: "Medicines Today",
      value: `${meds.length} Prescribed`,
      status: "3 Taken",
      trend: "Next: Metformin 8:30 PM",
      icon: Pill,
      color: "border-purple-200 bg-purple-50/50 text-purple-700",
      link: "/medicine"
    },
    {
      title: "Next Appointment",
      value: appt ? appt.doctor_name : "No upcoming visits",
      status: appt ? appt.appointment_date : "Checked",
      trend: appt ? appt.specialty : "Routine visits done",
      icon: Calendar,
      color: "border-sky-200 bg-sky-50/50 text-sky-700",
      link: "/appointments"
    },
    {
      title: "Water Intake",
      value: `${nutrition?.water_intake_ml || 1200} ml`,
      status: (nutrition?.water_intake_ml || 1200) >= 2000 ? "Goal Met" : "Warning",
      trend: "Target: 2000ml",
      icon: Droplet,
      color: "border-blue-200 bg-blue-50/50 text-blue-700",
      link: "/nutrition"
    },
    {
      title: "Today's Steps",
      value: `${activity?.steps || 3200} steps`,
      status: (activity?.steps || 3200) > 4000 ? "Sufficient" : "Goal: 5000",
      trend: `${activity?.exercise_type || 'Walking'} done`,
      icon: Footprints,
      color: "border-emerald-200 bg-emerald-50/50 text-emerald-700",
      link: "/activity"
    },
    {
      title: "Sleep Duration",
      value: `${activity?.sleep_hours || 6.8} hours`,
      status: "Normal",
      trend: "Target: 7+ hours",
      icon: Moon,
      color: "border-indigo-200 bg-indigo-50/50 text-indigo-700",
      link: "/activity"
    },
    {
      title: "Memory Score",
      value: `${quizScore}% Quiz`,
      status: quizScore >= 80 ? "Sufficient" : "Attention",
      trend: "3 Journal entries",
      icon: BrainCircuit,
      color: "border-rose-200 bg-rose-50/50 text-rose-700",
      link: "/memory"
    },
    {
      title: "AI Health Risk",
      value: "Low Risk",
      status: "Normal",
      trend: "Diabetes controlled",
      icon: AlertTriangle,
      color: "border-emerald-200 bg-emerald-50/50 text-emerald-700",
      link: "/recommendations"
    },
    {
      title: "Voice Assistant",
      value: "Voice Ready",
      status: "Online",
      trend: "Microphone Active",
      icon: Mic,
      color: "border-sky-200 bg-sky-50/50 text-sky-700",
      link: "/voice"
    },
    {
      title: "Emergency Alert",
      value: "Active & Armed",
      status: "Normal",
      trend: "Contacts Monitored",
      icon: ShieldAlert,
      color: "border-rose-200 bg-rose-50/50 text-rose-700",
      link: "/emergency"
    },
    {
      title: "WhatsApp Alerts",
      value: "Notifications",
      status: "Online",
      trend: "1 Delivered today",
      icon: MessageSquare,
      color: "border-emerald-200 bg-emerald-50/50 text-emerald-700",
      link: "/whatsapp"
    }
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-sky-400 via-sky-500 to-emerald-400 p-6 md:p-8 text-white shadow-xl">
        <h3 className="text-3xl font-extrabold mb-2">Namaste, Gopalaswamy!</h3>
        <p className="text-lg font-medium opacity-90 max-w-xl">
          Everything is looking stable today. Your morning medicines are checked, and your vitals are within target ranges.
        </p>
      </div>

      {/* Grid of Actionable Health Cards */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {cards.map((card, i) => (
          <Link 
            key={i} 
            to={card.link}
            className={`flex flex-col justify-between p-6 rounded-2xl border bg-white hover:shadow-md hover:border-slate-300 transition-all`}
          >
            <div className="flex items-start justify-between">
              <span className={`rounded-xl p-3 border ${card.color}`}>
                <card.icon className="h-6 w-6" />
              </span>
              <StatusBadge status={card.status} />
            </div>
            <div className="mt-4 space-y-1">
              <span className="block text-sm font-semibold text-slate-400 uppercase tracking-wider">{card.title}</span>
              <span className="block text-2xl font-black text-slate-800 leading-tight">{card.value}</span>
              <span className="block text-xs font-semibold text-slate-500 mt-1">{card.trend}</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};
export default Dashboard;
