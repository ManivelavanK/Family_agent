import fs from 'fs';
import path from 'path';

const files = {
  'src/pages/Landing.tsx': 
"import { Link } from 'react-router-dom';\n" +
"import { UserCircle, Users, Baby, Calendar } from 'lucide-react';\n\n" +
"export default function Landing() {\n" +
"  return (\n" +
"    <div className=\"min-h-screen bg-slate-50\">\n" +
"      <div className=\"max-w-6xl mx-auto px-6 py-20\">\n" +
"        <div className=\"text-center mb-16\">\n" +
"          <h1 className=\"text-5xl font-extrabold text-slate-900 mb-6 tracking-tight\">\n" +
"            KinNest – AI Powered <span className=\"text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600\">Family Operating System</span>\n" +
"          </h1>\n" +
"          <p className=\"text-xl text-slate-600 max-w-3xl mx-auto\">\n" +
"            One intelligent platform where specialized AI Agents collaborate to manage every aspect of family life.\n" +
"          </p>\n" +
"          <div className=\"mt-10 flex justify-center space-x-4\">\n" +
"            <Link to=\"/workspace\" className=\"px-8 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors shadow-sm\">\n" +
"              Get Started\n" +
"            </Link>\n" +
"            <button className=\"px-8 py-3 bg-white text-slate-700 border border-slate-200 rounded-xl font-medium hover:bg-slate-50 transition-colors shadow-sm\">\n" +
"              Learn More\n" +
"            </button>\n" +
"          </div>\n" +
"        </div>\n\n" +
"        <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6\">\n" +
"          {/* Father Agent */}\n" +
"          <div className=\"bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow\">\n" +
"            <div className=\"w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4\">\n" +
"              <UserCircle className=\"w-6 h-6 text-blue-600\" />\n" +
"            </div>\n" +
"            <h3 className=\"text-xl font-bold text-slate-900 mb-2\">Father Agent</h3>\n" +
"            <p className=\"text-slate-600 mb-4\">Manages finances, structural decisions, and overarching family goals.</p>\n" +
"          </div>\n" +
"          {/* Mother Agent */}\n" +
"          <div className=\"bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow\">\n" +
"            <div className=\"w-12 h-12 bg-pink-100 rounded-xl flex items-center justify-center mb-4\">\n" +
"              <UserCircle className=\"w-6 h-6 text-pink-600\" />\n" +
"            </div>\n" +
"            <h3 className=\"text-xl font-bold text-slate-900 mb-2\">Mother Agent</h3>\n" +
"            <p className=\"text-slate-600 mb-4\">Handles daily operations, emotional well-being, and household management.</p>\n" +
"          </div>\n" +
"          {/* Children Agent */}\n" +
"          <div className=\"bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow\">\n" +
"            <div className=\"w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-4\">\n" +
"              <Users className=\"w-6 h-6 text-amber-600\" />\n" +
"            </div>\n" +
"            <h3 className=\"text-xl font-bold text-slate-900 mb-2\">Children Agent</h3>\n" +
"            <p className=\"text-slate-600 mb-4\">Tracks education, activities, and development milestones.</p>\n" +
"          </div>\n" +
"          {/* Grandparent Agent */}\n" +
"          <div className=\"bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow\">\n" +
"            <div className=\"w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4\">\n" +
"              <UserCircle className=\"w-6 h-6 text-emerald-600\" />\n" +
"            </div>\n" +
"            <h3 className=\"text-xl font-bold text-slate-900 mb-2\">Grandparent Agent</h3>\n" +
"            <p className=\"text-slate-600 mb-4\">Monitors health routines, medications, and connection with family.</p>\n" +
"          </div>\n" +
"          {/* Baby Care Agent */}\n" +
"          <div className=\"bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow\">\n" +
"            <div className=\"w-12 h-12 bg-violet-100 rounded-xl flex items-center justify-center mb-4\">\n" +
"              <Baby className=\"w-6 h-6 text-violet-600\" />\n" +
"            </div>\n" +
"            <h3 className=\"text-xl font-bold text-slate-900 mb-2\">Baby Care Agent</h3>\n" +
"            <p className=\"text-slate-600 mb-4\">Manages feeding schedules, sleep tracking, and pediatric checkups.</p>\n" +
"          </div>\n" +
"          {/* Life Planner Agent */}\n" +
"          <div className=\"bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow\">\n" +
"            <div className=\"w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-4\">\n" +
"              <Calendar className=\"w-6 h-6 text-indigo-600\" />\n" +
"            </div>\n" +
"            <h3 className=\"text-xl font-bold text-slate-900 mb-2\">Life Planner Agent</h3>\n" +
"            <p className=\"text-slate-600 mb-4\">Coordinates events, vacations, and global schedule alignment.</p>\n" +
"          </div>\n" +
"        </div>\n" +
"      </div>\n" +
"    </div>\n" +
"  );\n" +
"}",
  'src/pages/WorkspaceFlow.tsx': 
"import { useState } from 'react';\n" +
"import { useNavigate } from 'react-router-dom';\n" +
"import { useAuthStore } from '../store/useAuthStore';\n\n" +
"export default function WorkspaceFlow() {\n" +
"  const [mode, setMode] = useState<'login' | 'create' | 'join'>('login');\n" +
"  const navigate = useNavigate();\n" +
"  const login = useAuthStore(state => state.login);\n\n" +
"  const handleLogin = (e: React.FormEvent) => {\n" +
"    e.preventDefault();\n" +
"    login({ name: 'User' }, 'KIN-29431');\n" +
"    navigate('/dashboard');\n" +
"  };\n\n" +
"  return (\n" +
"    <div className=\"min-h-screen bg-slate-50 flex items-center justify-center p-6\">\n" +
"      <div className=\"w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 p-8\">\n" +
"        <div className=\"text-center mb-8\">\n" +
"          <h2 className=\"text-3xl font-bold text-slate-900 mb-2\">\n" +
"            {mode === 'login' ? 'Welcome Back' : mode === 'create' ? 'Create Workspace' : 'Join Workspace'}\n" +
"          </h2>\n" +
"          <p className=\"text-slate-500\">KinNest Family Operating System</p>\n" +
"        </div>\n\n" +
"        <form onSubmit={handleLogin} className=\"space-y-4\">\n" +
"          {mode === 'create' && (\n" +
"            <>\n" +
"              <div>\n" +
"                <label className=\"block text-sm font-medium text-slate-700 mb-1\">Family Name</label>\n" +
"                <input type=\"text\" className=\"w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none\" required />\n" +
"              </div>\n" +
"              <div>\n" +
"                <label className=\"block text-sm font-medium text-slate-700 mb-1\">House Address</label>\n" +
"                <input type=\"text\" className=\"w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none\" required />\n" +
"              </div>\n" +
"            </>\n" +
"          )}\n\n" +
"          {mode === 'join' && (\n" +
"            <>\n" +
"              <div>\n" +
"                <label className=\"block text-sm font-medium text-slate-700 mb-1\">Role</label>\n" +
"                <select className=\"w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none\" required>\n" +
"                  <option value=\"Father\">Father</option>\n" +
"                  <option value=\"Mother\">Mother</option>\n" +
"                  <option value=\"Child\">Child</option>\n" +
"                  <option value=\"Grandparent\">Grandparent</option>\n" +
"                  <option value=\"Baby Caregiver\">Baby Caregiver</option>\n" +
"                </select>\n" +
"              </div>\n" +
"              <div>\n" +
"                <label className=\"block text-sm font-medium text-slate-700 mb-1\">Family Password</label>\n" +
"                <input type=\"password\" className=\"w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none\" required />\n" +
"              </div>\n" +
"            </>\n" +
"          )}\n\n" +
"          {mode === 'login' && (\n" +
"            <>\n" +
"              <div>\n" +
"                <label className=\"block text-sm font-medium text-slate-700 mb-1\">Email</label>\n" +
"                <input type=\"email\" className=\"w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none\" required />\n" +
"              </div>\n" +
"              <div>\n" +
"                <label className=\"block text-sm font-medium text-slate-700 mb-1\">Password</label>\n" +
"                <input type=\"password\" className=\"w-full px-4 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none\" required />\n" +
"              </div>\n" +
"            </>\n" +
"          )}\n\n" +
"          <button type=\"submit\" className=\"w-full py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors mt-6\">\n" +
"            {mode === 'login' ? 'Login' : mode === 'create' ? 'Create Workspace' : 'Join Workspace'}\n" +
"          </button>\n" +
"        </form>\n\n" +
"        <div className=\"mt-8 text-center space-y-2\">\n" +
"          {mode !== 'login' && (\n" +
"            <button onClick={() => setMode('login')} className=\"text-sm text-blue-600 hover:underline block w-full\">\n" +
"              Already have an account? Login\n" +
"            </button>\n" +
"          )}\n" +
"          {mode !== 'create' && (\n" +
"            <button onClick={() => setMode('create')} className=\"text-sm text-blue-600 hover:underline block w-full\">\n" +
"              Create a new Family Workspace\n" +
"            </button>\n" +
"          )}\n" +
"          {mode !== 'join' && (\n" +
"            <button onClick={() => setMode('join')} className=\"text-sm text-blue-600 hover:underline block w-full\">\n" +
"              Join an existing Family Workspace\n" +
"            </button>\n" +
"          )}\n" +
"        </div>\n" +
"      </div>\n" +
"    </div>\n" +
"  );\n" +
"}",
  'src/pages/Dashboard.tsx': 
"import { Users, CheckCircle, Bell, Calendar, UserCircle, Baby } from 'lucide-react';\n" +
"import { Link } from 'react-router-dom';\n\n" +
"export default function Dashboard() {\n" +
"  return (\n" +
"    <div className=\"space-y-6\">\n" +
"      <h1 className=\"text-2xl font-bold text-slate-900\">Family Overview</h1>\n" +
"      \n" +
"      <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6\">\n" +
"        <div className=\"bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center\">\n" +
"          <div className=\"w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mr-4\">\n" +
"            <Users className=\"w-6 h-6 text-blue-600\" />\n" +
"          </div>\n" +
"          <div>\n" +
"            <p className=\"text-sm font-medium text-slate-500\">Family Members</p>\n" +
"            <p className=\"text-2xl font-bold text-slate-900\">6</p>\n" +
"          </div>\n" +
"        </div>\n" +
"        <div className=\"bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center\">\n" +
"          <div className=\"w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mr-4\">\n" +
"            <CheckCircle className=\"w-6 h-6 text-indigo-600\" />\n" +
"          </div>\n" +
"          <div>\n" +
"            <p className=\"text-sm font-medium text-slate-500\">Tasks Today</p>\n" +
"            <p className=\"text-2xl font-bold text-slate-900\">18</p>\n" +
"          </div>\n" +
"        </div>\n" +
"        <div className=\"bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center\">\n" +
"          <div className=\"w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center mr-4\">\n" +
"            <Bell className=\"w-6 h-6 text-rose-600\" />\n" +
"          </div>\n" +
"          <div>\n" +
"            <p className=\"text-sm font-medium text-slate-500\">Active Alerts</p>\n" +
"            <p className=\"text-2xl font-bold text-slate-900\">5</p>\n" +
"          </div>\n" +
"        </div>\n" +
"        <div className=\"bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center\">\n" +
"          <div className=\"w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mr-4\">\n" +
"            <Calendar className=\"w-6 h-6 text-emerald-600\" />\n" +
"          </div>\n" +
"          <div>\n" +
"            <p className=\"text-sm font-medium text-slate-500\">Upcoming Events</p>\n" +
"            <p className=\"text-2xl font-bold text-slate-900\">5</p>\n" +
"          </div>\n" +
"        </div>\n" +
"      </div>\n\n" +
"      <h2 className=\"text-xl font-bold text-slate-900 mt-8\">Active Agents</h2>\n" +
"      <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6\">\n" +
"        {/* Father Agent */}\n" +
"        <Link to=\"/father\" className=\"block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group\">\n" +
"          <div className=\"absolute top-0 left-0 w-1 h-full bg-blue-500\"></div>\n" +
"          <div className=\"flex justify-between items-start mb-4\">\n" +
"            <div className=\"flex items-center\">\n" +
"              <UserCircle className=\"w-8 h-8 text-blue-500 mr-3\" />\n" +
"              <div>\n" +
"                <h3 className=\"font-bold text-slate-900\">Father Agent</h3>\n" +
"                <span className=\"text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full\">Online</span>\n" +
"              </div>\n" +
"            </div>\n" +
"          </div>\n" +
"          <div className=\"text-sm text-slate-500\">\n" +
"            <p>Pending Tasks: <span className=\"font-medium text-slate-900\">3</span></p>\n" +
"            <p>Recent: <span className=\"text-slate-700\">Budget review</span></p>\n" +
"          </div>\n" +
"        </Link>\n" +
"        {/* Mother Agent */}\n" +
"        <Link to=\"/mother\" className=\"block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group\">\n" +
"          <div className=\"absolute top-0 left-0 w-1 h-full bg-pink-500\"></div>\n" +
"          <div className=\"flex justify-between items-start mb-4\">\n" +
"            <div className=\"flex items-center\">\n" +
"              <UserCircle className=\"w-8 h-8 text-pink-500 mr-3\" />\n" +
"              <div>\n" +
"                <h3 className=\"font-bold text-slate-900\">Mother Agent</h3>\n" +
"                <span className=\"text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full\">Online</span>\n" +
"              </div>\n" +
"            </div>\n" +
"          </div>\n" +
"          <div className=\"text-sm text-slate-500\">\n" +
"            <p>Pending Tasks: <span className=\"font-medium text-slate-900\">5</span></p>\n" +
"            <p>Recent: <span className=\"text-slate-700\">Shopping list updated</span></p>\n" +
"          </div>\n" +
"        </Link>\n" +
"        {/* Children Agent */}\n" +
"        <Link to=\"/children\" className=\"block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group\">\n" +
"          <div className=\"absolute top-0 left-0 w-1 h-full bg-amber-500\"></div>\n" +
"          <div className=\"flex justify-between items-start mb-4\">\n" +
"            <div className=\"flex items-center\">\n" +
"              <Users className=\"w-8 h-8 text-amber-500 mr-3\" />\n" +
"              <div>\n" +
"                <h3 className=\"font-bold text-slate-900\">Children Agent</h3>\n" +
"                <span className=\"text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full\">Online</span>\n" +
"              </div>\n" +
"            </div>\n" +
"          </div>\n" +
"          <div className=\"text-sm text-slate-500\">\n" +
"            <p>Pending Tasks: <span className=\"font-medium text-slate-900\">2</span></p>\n" +
"            <p>Recent: <span className=\"text-slate-700\">Exam scheduled</span></p>\n" +
"          </div>\n" +
"        </Link>\n" +
"        {/* Grandparent Agent */}\n" +
"        <Link to=\"/grandparent\" className=\"block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group\">\n" +
"          <div className=\"absolute top-0 left-0 w-1 h-full bg-emerald-500\"></div>\n" +
"          <div className=\"flex justify-between items-start mb-4\">\n" +
"            <div className=\"flex items-center\">\n" +
"              <UserCircle className=\"w-8 h-8 text-emerald-500 mr-3\" />\n" +
"              <div>\n" +
"                <h3 className=\"font-bold text-slate-900\">Grandparent Agent</h3>\n" +
"                <span className=\"text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full\">Online</span>\n" +
"              </div>\n" +
"            </div>\n" +
"          </div>\n" +
"          <div className=\"text-sm text-slate-500\">\n" +
"            <p>Pending Tasks: <span className=\"font-medium text-slate-900\">1</span></p>\n" +
"            <p>Recent: <span className=\"text-slate-700\">Medicine logged</span></p>\n" +
"          </div>\n" +
"        </Link>\n" +
"        {/* Baby Care Agent */}\n" +
"        <Link to=\"/baby\" className=\"block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group\">\n" +
"          <div className=\"absolute top-0 left-0 w-1 h-full bg-violet-500\"></div>\n" +
"          <div className=\"flex justify-between items-start mb-4\">\n" +
"            <div className=\"flex items-center\">\n" +
"              <Baby className=\"w-8 h-8 text-violet-500 mr-3\" />\n" +
"              <div>\n" +
"                <h3 className=\"font-bold text-slate-900\">Baby Care Agent</h3>\n" +
"                <span className=\"text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full\">Online</span>\n" +
"              </div>\n" +
"            </div>\n" +
"          </div>\n" +
"          <div className=\"text-sm text-slate-500\">\n" +
"            <p>Pending Tasks: <span className=\"font-medium text-slate-900\">4</span></p>\n" +
"            <p>Recent: <span className=\"text-slate-700\">Feeding reminder</span></p>\n" +
"          </div>\n" +
"        </Link>\n" +
"        {/* Life Planner Agent */}\n" +
"        <Link to=\"/planner\" className=\"block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow relative overflow-hidden group\">\n" +
"          <div className=\"absolute top-0 left-0 w-1 h-full bg-indigo-500\"></div>\n" +
"          <div className=\"flex justify-between items-start mb-4\">\n" +
"            <div className=\"flex items-center\">\n" +
"              <Calendar className=\"w-8 h-8 text-indigo-500 mr-3\" />\n" +
"              <div>\n" +
"                <h3 className=\"font-bold text-slate-900\">Life Planner</h3>\n" +
"                <span className=\"text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full\">Online</span>\n" +
"              </div>\n" +
"            </div>\n" +
"          </div>\n" +
"          <div className=\"text-sm text-slate-500\">\n" +
"            <p>Pending Tasks: <span className=\"font-medium text-slate-900\">3</span></p>\n" +
"            <p>Recent: <span className=\"text-slate-700\">Trip scheduled</span></p>\n" +
"          </div>\n" +
"        </Link>\n" +
"      </div>\n" +
"    </div>\n" +
"  );\n" +
"}",
  'src/pages/Orchestrator.tsx': 
"import { motion } from 'framer-motion';\n" +
"import { Network, ArrowRight } from 'lucide-react';\n\n" +
"export default function Orchestrator() {\n" +
"  return (\n" +
"    <div className=\"space-y-6\">\n" +
"      <div className=\"flex items-center mb-8\">\n" +
"        <Network className=\"w-8 h-8 text-blue-600 mr-3\" />\n" +
"        <h1 className=\"text-2xl font-bold text-slate-900\">AI Orchestrator</h1>\n" +
"      </div>\n\n" +
"      <div className=\"bg-slate-900 rounded-3xl p-8 shadow-xl min-h-[500px] flex flex-col items-center justify-center relative overflow-hidden\">\n" +
"        {/* Simple animated visualization */}\n" +
"        <div className=\"absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10\"></div>\n\n" +
"        <div className=\"grid grid-cols-3 gap-16 relative z-10 w-full max-w-4xl\">\n" +
"          {/* Agents layout */}\n" +
"          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className=\"flex flex-col items-center\">\n" +
"            <div className=\"w-20 h-20 bg-blue-500 rounded-full flex items-center justify-center shadow-lg shadow-blue-500/50 mb-3\">\n" +
"              <span className=\"text-white font-bold\">Father</span>\n" +
"            </div>\n" +
"          </motion.div>\n" +
"          \n" +
"          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className=\"flex flex-col items-center justify-center\">\n" +
"            <div className=\"w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-purple-500/50 mb-3 z-20\">\n" +
"              <span className=\"text-white font-bold\">Core</span>\n" +
"            </div>\n" +
"          </motion.div>\n\n" +
"          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className=\"flex flex-col items-center\">\n" +
"            <div className=\"w-20 h-20 bg-pink-500 rounded-full flex items-center justify-center shadow-lg shadow-pink-500/50 mb-3\">\n" +
"              <span className=\"text-white font-bold\">Mother</span>\n" +
"            </div>\n" +
"          </motion.div>\n\n" +
"          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className=\"flex flex-col items-center\">\n" +
"            <div className=\"w-16 h-16 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg shadow-emerald-500/50 mb-3\">\n" +
"              <span className=\"text-white font-bold text-sm\">Grand</span>\n" +
"            </div>\n" +
"          </motion.div>\n\n" +
"          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className=\"flex flex-col items-center justify-center\">\n" +
"            <div className=\"w-16 h-16 bg-indigo-500 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/50 mb-3\">\n" +
"              <span className=\"text-white font-bold text-sm\">Planner</span>\n" +
"            </div>\n" +
"          </motion.div>\n\n" +
"          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className=\"flex flex-col items-center\">\n" +
"            <div className=\"w-16 h-16 bg-amber-500 rounded-full flex items-center justify-center shadow-lg shadow-amber-500/50 mb-3\">\n" +
"              <span className=\"text-white font-bold text-sm\">Children</span>\n" +
"            </div>\n" +
"          </motion.div>\n" +
"        </div>\n\n" +
"        {/* Message Logs */}\n" +
"        <div className=\"mt-16 w-full max-w-2xl bg-slate-800/50 rounded-xl p-4 border border-slate-700\">\n" +
"          <h3 className=\"text-slate-300 font-medium mb-4 flex items-center\">\n" +
"            <span className=\"w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse\"></span>\n" +
"            Live Agent Communication Stream\n" +
"          </h3>\n" +
"          <div className=\"space-y-3\">\n" +
"            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className=\"flex items-center text-sm\">\n" +
"              <span className=\"text-slate-500 mr-4\">09:15 AM</span>\n" +
"              <span className=\"text-pink-400 font-medium\">Mother Agent</span>\n" +
"              <ArrowRight className=\"w-4 h-4 mx-2 text-slate-500\" />\n" +
"              <span className=\"text-blue-400 font-medium\">Father Agent</span>\n" +
"              <span className=\"ml-4 text-slate-300 bg-slate-800 px-3 py-1 rounded-md\">Shopping List Updated</span>\n" +
"            </motion.div>\n" +
"            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 1 }} className=\"flex items-center text-sm\">\n" +
"              <span className=\"text-slate-500 mr-4\">09:16 AM</span>\n" +
"              <span className=\"text-blue-400 font-medium\">Father Agent</span>\n" +
"              <ArrowRight className=\"w-4 h-4 mx-2 text-slate-500\" />\n" +
"              <span className=\"text-pink-400 font-medium\">Mother Agent</span>\n" +
"              <span className=\"ml-4 text-slate-300 bg-slate-800 px-3 py-1 rounded-md\">Budget Approved</span>\n" +
"            </motion.div>\n" +
"            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 2 }} className=\"flex items-center text-sm\">\n" +
"              <span className=\"text-slate-500 mr-4\">09:18 AM</span>\n" +
"              <span className=\"text-amber-400 font-medium\">Children Agent</span>\n" +
"              <ArrowRight className=\"w-4 h-4 mx-2 text-slate-500\" />\n" +
"              <span className=\"text-indigo-400 font-medium\">Life Planner</span>\n" +
"              <span className=\"ml-4 text-slate-300 bg-slate-800 px-3 py-1 rounded-md\">Exam Scheduled</span>\n" +
"            </motion.div>\n" +
"          </div>\n" +
"        </div>\n" +
"      </div>\n" +
"    </div>\n" +
"  );\n" +
"}"
};

Object.entries(files).forEach(([filepath, content]) => {
  fs.writeFileSync(path.join(process.cwd(), filepath), content.trim());
});

console.log('Scaffolding 2 complete.');
