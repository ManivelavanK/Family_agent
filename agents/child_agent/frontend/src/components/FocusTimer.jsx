import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Award } from 'lucide-react';
import { api } from '../services/api';

export default function FocusTimer({ subjects = [], onSessionComplete }) {
  const [selectedSubjectId, setSelectedSubjectId] = useState('');
  const [topic, setTopic] = useState('');
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes default
  const [isRunning, setIsRunning] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [startTime, setStartTime] = useState(null);

  useEffect(() => {
    if (subjects.length > 0 && !selectedSubjectId) {
      setSelectedSubjectId(subjects[0].id);
    }
  }, [subjects, selectedSubjectId]);

  useEffect(() => {
    let timer = null;
    if (isRunning && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && isRunning) {
      handleTimerComplete();
    }
    return () => clearInterval(timer);
  }, [isRunning, timeLeft]);

  const handleStartPause = () => {
    if (!isRunning && !startTime) {
      setStartTime(new Date());
    }
    setIsRunning(!isRunning);
  };

  const handleReset = () => {
    setIsRunning(false);
    setTimeLeft(25 * 60);
    setIsCompleted(false);
    setStartTime(null);
  };

  const handleTimerComplete = async () => {
    setIsRunning(false);
    setIsCompleted(true);
    
    const endTime = new Date();
    const actualStartTime = startTime || new Date(endTime.getTime() - 25 * 60 * 1000);
    
    try {
      await api.recordStudySession({
        student_id: 1,
        subject_id: parseInt(selectedSubjectId),
        topic: topic || "Focused Study Session",
        start_time: actualStartTime.toISOString(),
        end_time: endTime.toISOString(),
        focus_score: 95,
        notes: "Completed Pomodoro timer session."
      });
      if (onSessionComplete) onSessionComplete();
    } catch (e) {
      console.error("Failed to log study session:", e);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-brandBorder shadow-sm flex flex-col items-center">
      <h3 className="font-bold text-lg text-brandNavyDark mb-4">Focus Pomodoro</h3>

      <div className="w-full space-y-3 mb-6">
        <div>
          <label className="text-xs font-semibold text-gray-500 block mb-1">Subject</label>
          <select 
            value={selectedSubjectId} 
            onChange={(e) => setSelectedSubjectId(e.target.value)}
            className="w-full bg-brandBg border border-brandBorder rounded-xl px-3 py-2 text-sm text-brandText focus:outline-none focus:border-brandIndigo"
          >
            {subjects.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-gray-500 block mb-1">Study Topic</label>
          <input 
            type="text" 
            placeholder="e.g. Electromagnetism Formulas" 
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="w-full bg-brandBg border border-brandBorder rounded-xl px-3 py-2 text-sm text-brandText focus:outline-none focus:border-brandIndigo"
          />
        </div>
      </div>

      {/* Clock Face */}
      <div className="relative w-44 h-44 rounded-full bg-gradient-to-tr from-brandNavyMedium to-brandNavyDark flex items-center justify-center shadow-xl border-4 border-indigo-900/40 mb-6">
        <div className="text-center">
          <span className="text-3xl font-extrabold tracking-wider text-white block">
            {formatTime(timeLeft)}
          </span>
          <span className="text-xxs uppercase tracking-widest text-indigo-400 font-bold">
            {isRunning ? "Studying" : "Paused"}
          </span>
        </div>
      </div>

      {isCompleted && (
        <div className="flex items-center gap-1.5 text-emerald-600 font-semibold text-sm mb-4">
          <Award size={18} />
          <span>Session Logged to database!</span>
        </div>
      )}

      {/* Controls */}
      <div className="flex gap-4">
        <button 
          onClick={handleStartPause}
          className="w-12 h-12 rounded-full bg-brandIndigo text-white flex items-center justify-center hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-500/25"
        >
          {isRunning ? <Pause size={20} /> : <Play size={20} className="ml-1" />}
        </button>
        <button 
          onClick={handleReset}
          className="w-12 h-12 rounded-full bg-brandBg border border-brandBorder text-brandText flex items-center justify-center hover:bg-gray-100 transition-colors"
        >
          <RotateCcw size={18} />
        </button>
      </div>
    </div>
  );
}
