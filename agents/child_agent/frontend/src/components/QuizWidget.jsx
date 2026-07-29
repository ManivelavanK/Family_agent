import React, { useState } from 'react';
import { Sparkles, HelpCircle, CheckCircle, XCircle } from 'lucide-react';
import { api } from '../services/api';

export default function QuizWidget({ subjects = [] }) {
  const [selectedSubject, setSelectedSubject] = useState('');
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('Medium');
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);

  const generateQuiz = async () => {
    if (!selectedSubject || !topic) return;
    setLoading(true);
    setQuiz(null);
    setSubmitted(false);
    setSelectedAnswer('');
    try {
      const data = await api.generateQuiz(selectedSubject, topic, difficulty);
      setQuiz(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = () => {
    if (!selectedAnswer || !quiz) return;
    setSubmitted(true);
    const correct = selectedAnswer.trim().toLowerCase() === quiz.correct_answer.trim().toLowerCase();
    setIsCorrect(correct);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-brandBorder shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <HelpCircle className="text-brandPurple" size={22} />
        <h3 className="font-bold text-lg text-brandNavyDark">AI Practice Quiz</h3>
      </div>

      {!quiz ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-gray-500 block mb-1">Subject</label>
              <select 
                value={selectedSubject} 
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="w-full bg-brandBg border border-brandBorder rounded-xl px-3 py-2 text-sm text-brandText focus:outline-none focus:border-brandIndigo"
              >
                <option value="">Select</option>
                {subjects.map(s => (
                  <option key={s.id} value={s.name}>{s.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-gray-500 block mb-1">Difficulty</label>
              <select 
                value={difficulty} 
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full bg-brandBg border border-brandBorder rounded-xl px-3 py-2 text-sm text-brandText focus:outline-none focus:border-brandIndigo"
              >
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-gray-500 block mb-1">Topic</label>
            <input 
              type="text" 
              placeholder="e.g. Recursion, Thermodynamics" 
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full bg-brandBg border border-brandBorder rounded-xl px-3 py-2 text-sm text-brandText focus:outline-none focus:border-brandIndigo"
            />
          </div>

          <button
            onClick={generateQuiz}
            disabled={loading || !selectedSubject || !topic}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-brandIndigo to-brandPurple text-white font-semibold text-sm hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/20 disabled:opacity-50"
          >
            <Sparkles size={16} />
            {loading ? "Generating Quiz..." : "Generate AI Question"}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm font-semibold text-brandNavyDark bg-brandBg p-3 rounded-xl border border-brandBorder/40">
            {quiz.question}
          </p>

          <div className="space-y-2">
            {quiz.options.map((opt, i) => (
              <label 
                key={i} 
                className={`flex items-center gap-3 px-4 py-3 rounded-xl border cursor-pointer transition-all ${
                  selectedAnswer === opt 
                    ? 'border-brandIndigo bg-indigo-50/50' 
                    : 'border-brandBorder hover:bg-brandBg'
                }`}
              >
                <input 
                  type="radio" 
                  name="quiz-answer" 
                  value={opt}
                  checked={selectedAnswer === opt}
                  onChange={() => setSelectedAnswer(opt)}
                  disabled={submitted}
                  className="accent-brandIndigo"
                />
                <span className="text-sm text-brandText">{opt}</span>
              </label>
            ))}
          </div>

          {!submitted ? (
            <div className="flex gap-3">
              <button
                onClick={handleAnswerSubmit}
                disabled={!selectedAnswer}
                className="flex-1 py-2.5 rounded-xl bg-brandNavyMedium text-white font-semibold text-sm hover:bg-brandNavyDark transition-colors disabled:opacity-50"
              >
                Submit Answer
              </button>
              <button
                onClick={() => setQuiz(null)}
                className="px-4 py-2.5 rounded-xl border border-brandBorder text-brandText text-sm hover:bg-brandBg transition-colors"
              >
                Cancel
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <div className={`p-4 rounded-xl border flex items-start gap-3 ${
                isCorrect 
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-800' 
                  : 'bg-rose-50 border-rose-200 text-rose-800'
              }`}>
                {isCorrect ? <CheckCircle className="shrink-0 text-emerald-600" size={20} /> : <XCircle className="shrink-0 text-rose-600" size={20} />}
                <div>
                  <h4 className="font-bold text-sm">{isCorrect ? "Correct!" : "Incorrect"}</h4>
                  <p className="text-xs mt-1">{quiz.explanation}</p>
                </div>
              </div>

              <button
                onClick={() => setQuiz(null)}
                className="w-full py-2.5 rounded-xl bg-brandBg border border-brandBorder text-brandText font-semibold text-sm hover:bg-gray-100 transition-colors"
              >
                Try Another Question
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
