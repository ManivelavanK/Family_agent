import React, { useEffect, useState } from 'react';
import { memoryService } from '../../services/memoryService';
import { MemoryJournal, MemoryQuizResult } from '../../types';
import { Plus, BookOpen, Brain, Sparkles, Smile, History, HelpCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import Dialog from '../../components/common/Dialog';
import StatusBadge from '../../components/common/StatusBadge';

export const Memory: React.FC = () => {
  const [journals, setJournals] = useState<MemoryJournal[]>([]);
  const [quizzes, setQuizzes] = useState<MemoryQuizResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [isJournalModalOpen, setIsJournalModalOpen] = useState(false);
  const [isQuizModalOpen, setIsQuizModalOpen] = useState(false);

  // Journal Form
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [mood, setMood] = useState('Joyful');
  const [savingJournal, setSavingJournal] = useState(false);

  // Quiz State
  const [q1, setQ1] = useState('');
  const [q2, setQ2] = useState('');
  const [q3, setQ3] = useState('');
  const [submittingQuiz, setSubmittingQuiz] = useState(false);

  useEffect(() => {
    loadMemoryData();
  }, []);

  const loadMemoryData = async () => {
    setLoading(true);
    try {
      const journalList = await memoryService.getJournals();
      setJournals(journalList);
      const quizList = await memoryService.getQuizResults();
      setQuizzes(quizList);
    } catch (e) {
      toast.error("Failed to load cognitive care data.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddJournal = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingJournal(true);
    try {
      await memoryService.addJournal({ title, content, mood });
      toast.success("Journal saved! Keep writing to preserve memories.");
      setIsJournalModalOpen(false);
      setTitle('');
      setContent('');
      loadMemoryData();
    } catch (e) {
      toast.error("Could not save journal.");
    } finally {
      setSavingJournal(false);
    }
  };

  const handleSubmitQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingQuiz(true);
    try {
      let score = 0;
      if (q1.toLowerCase().includes("metformin") || q1.toLowerCase().includes("amlodipine")) score += 35;
      if (q2.toLowerCase().includes("srinivasan") || q2.toLowerCase().includes("karthik")) score += 35;
      if (q3.toLowerCase().includes("wednesday") || q3.toLowerCase().includes("29")) score += 30;

      await memoryService.addQuizResult({
        score,
        quiz_type: "Daily Orientation & Pill Trivia",
        notes: `Q1: ${q1} | Q2: ${q2} | Q3: ${q3}`
      });

      toast.success(`Memory Quiz Submitted! Your Cognitive Score today: ${score}%`);
      setIsQuizModalOpen(false);
      setQ1('');
      setQ2('');
      setQ3('');
      loadMemoryData();
    } catch (e) {
      toast.error("Failed to score quiz.");
    } finally {
      setSubmittingQuiz(false);
    }
  };

  const brainExercises = [
    { name: "Word Association", desc: "List 10 vegetables that start with the letter 'P'.", color: "bg-sky-50 text-sky-700" },
    { name: "Sanskrit Verse Recitation", desc: "Recite the Vishnu Sahasranamam verses slowly for 10 minutes.", color: "bg-emerald-50 text-emerald-700" },
    { name: "Number Recall", desc: "Memorize Karthik's phone number without writing it down.", color: "bg-amber-50 text-amber-700" }
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-sky-500 border-t-transparent" />
      </div>
    );
  }

  const latestQuiz = quizzes[0];

  return (
    <div className="space-y-8">
      {/* Header Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="p-3.5 bg-rose-50 text-rose-600 rounded-xl border border-rose-100">
              <Brain className="h-6 w-6" />
            </span>
            <div>
              <span className="block text-xs font-semibold text-slate-400 uppercase">Cognitive Score</span>
              <span className="block text-2xl font-black text-slate-800">{latestQuiz ? `${latestQuiz.score}%` : 'N/A'}</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="p-3.5 bg-emerald-50 text-emerald-600 rounded-xl border border-emerald-100">
              <BookOpen className="h-6 w-6" />
            </span>
            <div>
              <span className="block text-xs font-semibold text-slate-400 uppercase">Memory Journals</span>
              <span className="block text-2xl font-black text-slate-800">{journals.length} entries</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-sky-100 p-6 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="p-3.5 bg-amber-50 text-amber-600 rounded-xl border border-amber-100">
              <Smile className="h-6 w-6" />
            </span>
            <div>
              <span className="block text-xs font-semibold text-slate-400 uppercase">Latest Mood</span>
              <span className="block text-2xl font-black text-slate-800">{journals[0]?.mood || 'Calm'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Two column: Quiz / Exercises & Journals */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Side: Quiz & Exercises */}
        <div className="lg:col-span-1 space-y-6">
          {/* Cognitive Quiz Callout */}
          <div className="bg-gradient-to-br from-sky-400 to-sky-500 p-6 rounded-2xl text-white shadow-md">
            <HelpCircle className="h-8 w-8 mb-3" />
            <h4 className="text-xl font-bold mb-1">Daily Memory Quiz</h4>
            <p className="text-sm opacity-90 mb-4">Complete your short morning orientation quiz to test recall speed.</p>
            <button
              onClick={() => setIsQuizModalOpen(true)}
              className="w-full bg-white hover:bg-slate-50 text-sky-600 font-bold py-2.5 rounded-xl text-base transition-colors shadow-xs cursor-pointer"
            >
              Start Exercise
            </button>
          </div>

          {/* Brain Gym suggestions */}
          <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
            <h4 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-amber-500" />
              <span>Recommended Brain Exercises</span>
            </h4>
            <div className="space-y-3.5">
              {brainExercises.map((ex, i) => (
                <div key={i} className={`p-4 rounded-xl border border-slate-100`}>
                  <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold mb-1.5 ${ex.color}`}>
                    {ex.name}
                  </span>
                  <p className="text-sm font-semibold text-slate-700 leading-snug">{ex.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Side: Journal History & Writing */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
              <h4 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <History className="h-5 w-5 text-sky-500" />
                <span>Memory Journal History</span>
              </h4>
              <button
                onClick={() => setIsJournalModalOpen(true)}
                className="flex items-center gap-1.5 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold rounded-xl text-sm transition-all cursor-pointer shadow-xs"
              >
                <Plus className="h-4 w-4" />
                <span>Write Journal</span>
              </button>
            </div>

            <div className="space-y-4">
              {journals.map((j) => (
                <div key={j.id} className="p-4 border border-slate-100 hover:border-slate-200 rounded-xl transition-all bg-slate-50/20">
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="font-extrabold text-slate-800 text-base">{j.title}</h5>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-400">{j.date}</span>
                      <StatusBadge status={j.mood || 'Calm'} />
                    </div>
                  </div>
                  <p className="text-sm font-semibold text-slate-600 leading-relaxed">{j.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Journal Modal */}
      <Dialog isOpen={isJournalModalOpen} onClose={() => setIsJournalModalOpen(false)} title="Write in Memory Journal">
        <form onSubmit={handleAddJournal} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">What did you do today?</label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="e.g. Walking with grandchildren"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Write your thoughts/memories down</label>
            <textarea
              rows={4}
              value={content}
              onChange={e => setContent(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="Describe what you saw, what you remembered..."
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Current Mood / Feeling</label>
            <select
              value={mood}
              onChange={e => setMood(e.target.value)}
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none bg-white"
            >
              <option value="Joyful">Joyful</option>
              <option value="Peaceful">Peaceful</option>
              <option value="Calm">Calm</option>
              <option value="Tired">Tired</option>
              <option value="Anxious">Anxious</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsJournalModalOpen(false)}
              className="px-5 py-2.5 rounded-xl border border-slate-200 font-bold hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={savingJournal}
              className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold transition-colors shadow-xs"
            >
              {savingJournal ? 'Saving...' : 'Save Journal'}
            </button>
          </div>
        </form>
      </Dialog>

      {/* Quiz Modal */}
      <Dialog isOpen={isQuizModalOpen} onClose={() => setIsQuizModalOpen(false)} title="Daily Orientation Exercises">
        <form onSubmit={handleSubmitQuiz} className="space-y-4">
          <div className="bg-slate-50 p-4 rounded-xl text-sm font-semibold text-slate-500 leading-snug">
            These questions test short-term recall. Answer honestly from memory without checking papers.
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">1. What is the name of your blood pressure pill?</label>
            <input
              type="text"
              value={q1}
              onChange={e => setQ1(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="Your answer..."
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">2. What is your grandson's name?</label>
            <input
              type="text"
              value={q2}
              onChange={e => setQ2(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="Your answer..."
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">3. What day of the week is it today?</label>
            <input
              type="text"
              value={q3}
              onChange={e => setQ3(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="Your answer..."
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsQuizModalOpen(false)}
              className="px-5 py-2.5 rounded-xl border border-slate-200 font-bold hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingQuiz}
              className="px-5 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-600 active:scale-95 text-white font-bold transition-colors shadow-xs"
            >
              {submittingQuiz ? 'Calculating...' : 'Submit Answers'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
export default Memory;
