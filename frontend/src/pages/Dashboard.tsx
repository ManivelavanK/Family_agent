import { useState, useEffect } from 'react';
import { Users, CheckCircle, Bell, Calendar, UserCircle, Baby } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';

export default function Dashboard() {
  const token = useAuthStore(state => state.token);
  const [profileData, setProfileData] = useState<any>(null);
  const [budgetData, setBudgetData] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!token) return;

    const fetchDashboardContext = async () => {
      try {
        const [profileRes, budgetRes] = await Promise.all([
          fetch('http://localhost:8000/orchestrator/context/profile', { headers: { Authorization: `Bearer ${token}` } }),
          fetch('http://localhost:8000/orchestrator/context/budget', { headers: { Authorization: `Bearer ${token}` } })
        ]);
        if (profileRes.ok) setProfileData(await profileRes.json());
        if (budgetRes.ok) setBudgetData(await budgetRes.json());
      } catch (err: any) {
        setErrorMsg(err.message);
      }
    };
    fetchDashboardContext();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Family Overview</h1>
        {errorMsg && <p className="text-red-500 text-sm bg-red-50/80 px-3 py-1 rounded-md">{errorMsg}</p>}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center">
          <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mr-4">
            <Users className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500">Family Members</p>
            <p className="text-2xl font-bold text-slate-900">6</p>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center">
          <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mr-4">
            <CheckCircle className="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500">Tasks Today</p>
            <p className="text-2xl font-bold text-slate-900">18</p>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center">
          <div className="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center mr-4">
            <Bell className="w-6 h-6 text-rose-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500">Active Alerts</p>
            <p className="text-2xl font-bold text-slate-900">5</p>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center">
          <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mr-4">
            <Calendar className="w-6 h-6 text-emerald-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500">Upcoming Events</p>
            <p className="text-2xl font-bold text-slate-900">5</p>
          </div>
        </div>
      </div>

      {(profileData || budgetData) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          {profileData && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-bold text-slate-900 mb-2">Profile Context</h3>
              <pre className="text-xs text-slate-600 overflow-auto bg-slate-50 p-2 rounded">{JSON.stringify(profileData, null, 2)}</pre>
            </div>
          )}
          {budgetData && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-bold text-slate-900 mb-2">Budget Context</h3>
              <pre className="text-xs text-slate-600 overflow-auto bg-slate-50 p-2 rounded">{JSON.stringify(budgetData, null, 2)}</pre>
            </div>
          )}
        </div>
      )}

      <h2 className="text-xl font-bold text-slate-900 mt-8">Active Agents</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Father Agent */}
        <Link to="/father" className="block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <UserCircle className="w-8 h-8 text-blue-500 mr-3" />
              <div>
                <h3 className="font-bold text-slate-900">Father Agent</h3>
                <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">Online</span>
              </div>
            </div>
          </div>
          <div className="text-sm text-slate-500">
            <p>Pending Tasks: <span className="font-medium text-slate-900">3</span></p>
            <p>Recent: <span className="text-slate-700">Budget review</span></p>
          </div>
        </Link>
        {/* Mother Agent */}
        <Link to="/mother" className="block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-pink-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <UserCircle className="w-8 h-8 text-pink-500 mr-3" />
              <div>
                <h3 className="font-bold text-slate-900">Mother Agent</h3>
                <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">Online</span>
              </div>
            </div>
          </div>
          <div className="text-sm text-slate-500">
            <p>Pending Tasks: <span className="font-medium text-slate-900">5</span></p>
            <p>Recent: <span className="text-slate-700">Shopping list updated</span></p>
          </div>
        </Link>
        {/* Children Agent */}
        <Link to="/children" className="block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-amber-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-amber-500 mr-3" />
              <div>
                <h3 className="font-bold text-slate-900">Children Agent</h3>
                <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">Online</span>
              </div>
            </div>
          </div>
          <div className="text-sm text-slate-500">
            <p>Pending Tasks: <span className="font-medium text-slate-900">2</span></p>
            <p>Recent: <span className="text-slate-700">Exam scheduled</span></p>
          </div>
        </Link>
        {/* Grandparent Agent */}
        <Link to="/grandparent" className="block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <UserCircle className="w-8 h-8 text-emerald-500 mr-3" />
              <div>
                <h3 className="font-bold text-slate-900">Grandparent Agent</h3>
                <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">Online</span>
              </div>
            </div>
          </div>
          <div className="text-sm text-slate-500">
            <p>Pending Tasks: <span className="font-medium text-slate-900">1</span></p>
            <p>Recent: <span className="text-slate-700">Medicine logged</span></p>
          </div>
        </Link>
        {/* Baby Care Agent */}
        <Link to="/baby" className="block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-violet-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <Baby className="w-8 h-8 text-violet-500 mr-3" />
              <div>
                <h3 className="font-bold text-slate-900">Baby Care Agent</h3>
                <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">Online</span>
              </div>
            </div>
          </div>
          <div className="text-sm text-slate-500">
            <p>Pending Tasks: <span className="font-medium text-slate-900">4</span></p>
            <p>Recent: <span className="text-slate-700">Feeding reminder</span></p>
          </div>
        </Link>
        {/* Life Planner Agent */}
        <Link to="/planner" className="block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <Calendar className="w-8 h-8 text-indigo-500 mr-3" />
              <div>
                <h3 className="font-bold text-slate-900">Life Planner</h3>
                <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">Online</span>
              </div>
            </div>
          </div>
          <div className="text-sm text-slate-500">
            <p>Pending Tasks: <span className="font-medium text-slate-900">3</span></p>
            <p>Recent: <span className="text-slate-700">Trip scheduled</span></p>
          </div>
        </Link>
      </div>
    </div>
  );
}