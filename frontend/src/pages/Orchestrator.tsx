import { motion } from 'framer-motion';
import { Network, ArrowRight } from 'lucide-react';

export default function Orchestrator() {
  return (
    <div className="space-y-6">
      <div className="flex items-center mb-8">
        <Network className="w-8 h-8 text-blue-600 mr-3" />
        <h1 className="text-2xl font-bold text-slate-900">AI Orchestrator</h1>
      </div>

      <div className="bg-slate-900 rounded-3xl p-8 shadow-xl min-h-[500px] flex flex-col items-center justify-center relative overflow-hidden">
        {/* Simple animated visualization */}
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>

        <div className="grid grid-cols-3 gap-16 relative z-10 w-full max-w-4xl">
          {/* Agents layout */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col items-center">
            <div className="w-20 h-20 bg-blue-500 rounded-full flex items-center justify-center shadow-lg shadow-blue-500/50 mb-3">
              <span className="text-white font-bold">Father</span>
            </div>
          </motion.div>
          
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="flex flex-col items-center justify-center">
            <div className="w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-purple-500/50 mb-3 z-20">
              <span className="text-white font-bold">Core</span>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="flex flex-col items-center">
            <div className="w-20 h-20 bg-pink-500 rounded-full flex items-center justify-center shadow-lg shadow-pink-500/50 mb-3">
              <span className="text-white font-bold">Mother</span>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="flex flex-col items-center">
            <div className="w-16 h-16 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg shadow-emerald-500/50 mb-3">
              <span className="text-white font-bold text-sm">Grand</span>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="flex flex-col items-center justify-center">
            <div className="w-16 h-16 bg-indigo-500 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/50 mb-3">
              <span className="text-white font-bold text-sm">Planner</span>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className="flex flex-col items-center">
            <div className="w-16 h-16 bg-amber-500 rounded-full flex items-center justify-center shadow-lg shadow-amber-500/50 mb-3">
              <span className="text-white font-bold text-sm">Children</span>
            </div>
          </motion.div>
        </div>

        {/* Message Logs */}
        <div className="mt-16 w-full max-w-2xl bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <h3 className="text-slate-300 font-medium mb-4 flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
            Live Agent Communication Stream
          </h3>
          <div className="space-y-3">
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex items-center text-sm">
              <span className="text-slate-500 mr-4">09:15 AM</span>
              <span className="text-pink-400 font-medium">Mother Agent</span>
              <ArrowRight className="w-4 h-4 mx-2 text-slate-500" />
              <span className="text-blue-400 font-medium">Father Agent</span>
              <span className="ml-4 text-slate-300 bg-slate-800 px-3 py-1 rounded-md">Shopping List Updated</span>
            </motion.div>
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 1 }} className="flex items-center text-sm">
              <span className="text-slate-500 mr-4">09:16 AM</span>
              <span className="text-blue-400 font-medium">Father Agent</span>
              <ArrowRight className="w-4 h-4 mx-2 text-slate-500" />
              <span className="text-pink-400 font-medium">Mother Agent</span>
              <span className="ml-4 text-slate-300 bg-slate-800 px-3 py-1 rounded-md">Budget Approved</span>
            </motion.div>
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 2 }} className="flex items-center text-sm">
              <span className="text-slate-500 mr-4">09:18 AM</span>
              <span className="text-amber-400 font-medium">Children Agent</span>
              <ArrowRight className="w-4 h-4 mx-2 text-slate-500" />
              <span className="text-indigo-400 font-medium">Life Planner</span>
              <span className="ml-4 text-slate-300 bg-slate-800 px-3 py-1 rounded-md">Exam Scheduled</span>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}