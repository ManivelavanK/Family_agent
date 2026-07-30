import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { motion } from 'framer-motion';
import { Mail, Lock, UserPlus, Users, ArrowRight } from 'lucide-react';

export default function WorkspaceFlow() {
  const [mode, setMode] = useState<'login' | 'register' | 'select_workspace' | 'create_workspace' | 'join_workspace'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [familyName, setFamilyName] = useState('');
  const [houseAddress, setHouseAddress] = useState('');
  const [role, setRole] = useState('Child');
  const [workspaceCode, setWorkspaceCode] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();
  const login = useAuthStore(state => state.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (mode === 'register') {
      // Just progress to workspace selection
      setMode('select_workspace');
      return;
    }

    setIsLoading(true);
    try {
      if (mode === 'login') {
        const res = await fetch('http://localhost:8000/orchestrator/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: email, password })
        });
        if (!res.ok) {
          const errData = await res.json().catch(() => null);
          let msg = 'Login failed. Please check your credentials.';
          if (errData?.detail) {
            msg = Array.isArray(errData.detail) ? errData.detail[0].msg : errData.detail;
          }
          throw new Error(msg);
        }
        const data = await res.json();
        login({ name: data.username }, data.family_id, data.access_token);
        navigate('/dashboard');
      } else if (mode === 'create_workspace') {
        const res = await fetch('http://localhost:8000/orchestrator/auth/workspace/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            family_name: familyName,
            house_address: houseAddress,
            admin_username: email,
            admin_password: password
          })
        });
        if (!res.ok) {
          const errData = await res.json().catch(() => null);
          let msg = 'Failed to create workspace.';
          if (errData?.detail) {
            msg = Array.isArray(errData.detail) ? errData.detail[0].msg : errData.detail;
          }
          throw new Error(msg);
        }
        const data = await res.json();
        login({ name: data.username }, data.family_id, data.access_token);
        navigate('/dashboard');
      } else if (mode === 'join_workspace') {
        const res = await fetch('http://localhost:8000/orchestrator/auth/workspace/join', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            join_code: workspaceCode,
            username: email,
            password: password,
            role: role
          })
        });
        if (!res.ok) {
          const errData = await res.json().catch(() => null);
          let msg = 'Failed to join workspace.';
          if (errData?.detail) {
            msg = Array.isArray(errData.detail) ? errData.detail[0].msg : errData.detail;
          }
          throw new Error(msg);
        }
        const data = await res.json();
        login({ name: data.username }, data.family_id, data.access_token);
        navigate('/dashboard');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-6 z-10">
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.98, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md bg-white/70 backdrop-blur-xl border border-amber-100/50 shadow-2xl shadow-amber-900/10 rounded-3xl p-10 relative overflow-hidden"
      >
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-amber-400/20 rounded-full blur-[40px] pointer-events-none"></div>
        <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-emerald-400/20 rounded-full blur-[40px] pointer-events-none"></div>

        <div className="text-center mb-8 relative z-10">
          <h2 className="text-4xl font-bold text-slate-800 mb-2 font-serif text-glow-gold">
            {mode === 'login' ? 'Welcome Back' : 
             mode === 'register' ? 'Create Account' : 
             mode === 'select_workspace' ? 'Setup Workspace' :
             mode === 'create_workspace' ? 'Create Workspace' : 'Join Workspace'}
          </h2>
          <p className="text-slate-600 font-medium">KinNest Family Operating System</p>
          {errorMsg && <p className="text-red-500 mt-2 text-sm bg-red-50/80 px-3 py-1 rounded-md inline-block">{errorMsg}</p>}
        </div>

        {mode === 'select_workspace' ? (
          <div className="space-y-4 relative z-10">
            <p className="text-center text-slate-600 mb-6">You need to connect to a family workspace to continue.</p>
            
            <button
              onClick={() => setMode('create_workspace')}
              className="w-full p-4 border border-amber-200/60 bg-white/50 rounded-xl hover:bg-amber-50 hover:border-amber-300 transition-all group flex flex-col items-center justify-center text-slate-700"
            >
              <Users className="w-8 h-8 text-amber-500 mb-2 group-hover:scale-110 transition-transform" />
              <span className="font-bold text-lg">Create a new Family Workspace</span>
              <span className="text-xs text-slate-500 mt-1">Setup a new home and invite family members</span>
            </button>

            <button
              onClick={() => setMode('join_workspace')}
              className="w-full p-4 border border-emerald-200/60 bg-white/50 rounded-xl hover:bg-emerald-50 hover:border-emerald-300 transition-all group flex flex-col items-center justify-center text-slate-700"
            >
              <UserPlus className="w-8 h-8 text-emerald-500 mb-2 group-hover:scale-110 transition-transform" />
              <span className="font-bold text-lg">Join an existing Workspace</span>
              <span className="text-xs text-slate-500 mt-1">Use a join code provided by your family admin</span>
            </button>

            <button
              onClick={() => setMode('register')}
              className="mt-6 text-sm font-medium text-slate-500 hover:text-amber-700 transition-colors block w-full relative after:content-[''] after:absolute after:-bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-0 after:h-0.5 after:bg-amber-400 after:transition-all hover:after:w-8 text-center"
            >
              Back to Registration
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
            {mode === 'create_workspace' && (
              <>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Family Name</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Users className="h-5 w-5 text-amber-500/70" />
                    </div>
                    <input type="text" value={familyName} onChange={e => setFamilyName(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="e.g. The Smiths" required />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">House Address</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <UserPlus className="h-5 w-5 text-amber-500/70" />
                    </div>
                    <input type="text" value={houseAddress} onChange={e => setHouseAddress(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="Home address" required />
                  </div>
                </div>
              </>
            )}

            {mode === 'join_workspace' && (
              <>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Role</label>
                  <select value={role} onChange={e => setRole(e.target.value)} className="w-full px-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all text-slate-700 font-medium appearance-none" required>
                    <option value="Parent">Parent</option>
                    <option value="Child">Child</option>
                    <option value="Grandparent">Grandparent</option>
                    <option value="Baby Caregiver">Baby Caregiver</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Workspace Code</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-amber-500/70" />
                    </div>
                    <input type="text" value={workspaceCode} onChange={e => setWorkspaceCode(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="Enter join code" required />
                  </div>
                </div>
              </>
            )}

            {(mode === 'login' || mode === 'register') && (
              <>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Email</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Mail className="h-5 w-5 text-amber-500/70" />
                    </div>
                    <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="hello@family.com" required />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Password</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-amber-500/70" />
                    </div>
                    <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-white/50 border border-amber-200/60 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none transition-all placeholder:text-slate-400 text-slate-700 font-medium" placeholder="••••••••" required />
                  </div>
                </div>
              </>
            )}

            <motion.button
              whileHover={{ scale: isLoading ? 1 : 1.02 }}
              whileTap={{ scale: isLoading ? 1 : 0.98 }}
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 mt-2 rounded-xl text-slate-800 font-bold shadow-[0_8px_20px_-6px_rgba(217,119,6,0.3)] hover:shadow-[0_10px_25px_-6px_rgba(217,119,6,0.5)] transition-all flex justify-center items-center group relative overflow-hidden disabled:opacity-70 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-amber-300 via-amber-200 to-emerald-200"></div>
              <span className="relative flex items-center">
                {isLoading ? 'Loading...' : mode === 'login' ? 'Enter KinNest' : mode === 'register' ? 'Continue' : 'Complete Registration'}
                {!isLoading && <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />}
              </span>
            </motion.button>
          </form>
        )}

        <div className="mt-8 text-center space-y-3 relative z-10">
          {(mode === 'create_workspace' || mode === 'join_workspace') && (
            <button
              onClick={() => setMode('select_workspace')}
              className="text-sm font-medium text-slate-500 hover:text-amber-700 transition-colors block w-full relative after:content-[''] after:absolute after:-bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-0 after:h-0.5 after:bg-amber-400 after:transition-all hover:after:w-8"
            >
              Back to Selection
            </button>
          )}

          {mode === 'login' && (
            <button
              onClick={() => setMode('register')}
              className="text-sm font-medium text-slate-600 hover:text-amber-700 transition-colors block w-full"
            >
              Don't have an account? <span className="font-bold underline decoration-amber-400 underline-offset-4">Sign Up</span>
            </button>
          )}

          {mode === 'register' && (
            <button
              onClick={() => setMode('login')}
              className="text-sm font-medium text-slate-600 hover:text-emerald-700 transition-colors block w-full"
            >
              Already have an account? <span className="font-bold underline decoration-emerald-400 underline-offset-4">Sign In</span>
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}