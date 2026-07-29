import { useState, useEffect } from 'react';
import { 
  Bell, 
  AlertTriangle
} from 'lucide-react';
import { AnimatePresence } from 'framer-motion';

// Import Services
import { plannerService } from './services/plannerService';
import { goalService } from './services/goalService';
import { taskService } from './services/taskService';
import { calendarService } from './services/calendarService';
import { habitService } from './services/habitService';
import { recommendationService } from './services/recommendationService';

// Import Types
import type { Goal, Habit, DigitalTwin, CalendarEvent, Task, Recommendation } from './services/api';

// Import Components & Pages
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import CalendarPage from './pages/CalendarPage';
import TasksPage from './pages/TasksPage';
import GoalsPage from './pages/GoalsPage';
import HabitsPage from './pages/HabitsPage';
import FamilyTimelinePage from './pages/FamilyTimelinePage';
import AIPlannerPage from './pages/AIPlannerPage';
import DigitalTwinPage from './pages/DigitalTwinPage';
import RecommendationsPage from './pages/RecommendationsPage';
import NotificationsPage from './pages/NotificationsPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Core Database States
  const [goals, setGoals] = useState<Goal[]>([]);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [digitalTwin, setDigitalTwin] = useState<DigitalTwin | null>(null);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [timelineData, setTimelineData] = useState<any[]>([]);
  const [scheduleHealth, setScheduleHealth] = useState(100);

  // AI Planner States
  const [aiPrompt, setAiPrompt] = useState('Plan my next week.');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState<any | null>(null);

  // Form Modals states
  const [showGoalForm, setShowGoalForm] = useState(false);
  const [newGoal, setNewGoal] = useState({ title: '', description: '', category: 'PERSONAL', progress: 0, deadline: '' });
  const [showHabitForm, setShowHabitForm] = useState(false);
  const [newHabit, setNewHabit] = useState({ title: '', category: 'CUSTOM' });
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [newTask, setNewTask] = useState({ title: '', description: '', priority: 'MEDIUM', due_date: '' });
  const [showEventForm, setShowEventForm] = useState(false);
  const [newEvent, setNewEvent] = useState({ title: '', description: '', start: '', end: '', type: 'FAMILY_EVENT', priority: 'MEDIUM' });

  // Notifications Feeds State
  const [notifications, setNotifications] = useState<any[]>([
    { id: 1, title: 'Schedule Conflict Resolved', description: 'AI Planner adjusted Grocery shopping to 4 PM to clear conflicts.', time: '10m ago', unread: true, type: 'INSIGHT' },
    { id: 2, title: 'Electricity Bill Reminder', description: 'Due in 2 days. Estimated cost: $120.', time: '1h ago', unread: true, type: 'ALERT' },
    { id: 3, title: 'Daily Study Completed', description: 'Habit check-in completed.', time: '3h ago', unread: false, type: 'SUCCESS' }
  ]);

  // Fetch initial data
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedGoals = await goalService.getGoals();
      const fetchedHabits = await habitService.getHabits();
      const twin = await plannerService.getDigitalTwin();
      const fetchedEvents = await calendarService.getEvents();
      const fetchedTasks = await taskService.getTasks();
      const recs = await recommendationService.getRecommendations();
      const timeline = await plannerService.getTimeline();

      setGoals(fetchedGoals);
      setHabits(fetchedHabits);
      setDigitalTwin(twin);
      setEvents(fetchedEvents);
      setTasks(fetchedTasks);
      setRecommendations(recs);
      setTimelineData(timeline.timeline || []);
      setScheduleHealth(timeline.schedule_health || 100);
    } catch (err: any) {
      console.error(err);
      setError('Could not retrieve planner data. Verify server connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAskAI = async () => {
    if (!aiPrompt.trim()) return;
    setAiLoading(true);
    setAiResponse(null);
    try {
      const response = await plannerService.queryAgent(aiPrompt);
      setAiResponse(response);
      fetchData(); // Refresh metrics
    } catch (err) {
      console.error(err);
    } finally {
      setAiLoading(false);
    }
  };

  const handleAddGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await goalService.createGoal({
        title: newGoal.title,
        description: newGoal.description,
        category: newGoal.category as any,
        progress: Number(newGoal.progress),
        deadline: newGoal.deadline || undefined,
        family_id: 'default_family'
      });
      setNewGoal({ title: '', description: '', category: 'PERSONAL', progress: 0, deadline: '' });
      setShowGoalForm(false);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateGoalProgress = async (id: number, currentProgress: number) => {
    const nextProgress = Math.min(100, currentProgress + 15);
    try {
      await goalService.updateGoal(id, { progress: nextProgress });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteGoal = async (id: number) => {
    try {
      await goalService.deleteGoal(id);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await habitService.createHabit({
        title: newHabit.title,
        category: newHabit.category as any,
        family_id: 'default_family'
      });
      setNewHabit({ title: '', category: 'CUSTOM' });
      setShowHabitForm(false);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogHabit = async (habitId: number, completed: boolean) => {
    const dateStr = new Date().toISOString().split('T')[0];
    try {
      await habitService.logHabit(habitId, dateStr, completed);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteHabit = async (habitId: number) => {
    try {
      await habitService.deleteHabit(habitId);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await taskService.createTask({
        title: newTask.title,
        description: newTask.description,
        priority: newTask.priority as any,
        due_date: newTask.due_date || undefined
      });
      setNewTask({ title: '', description: '', priority: 'MEDIUM', due_date: '' });
      setShowTaskForm(false);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleTaskStatus = async (task: Task) => {
    const nextStatus = task.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED';
    try {
      await taskService.updateTask(task.id, { status: nextStatus });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteTask = async (id: number) => {
    try {
      await taskService.deleteTask(id);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await calendarService.createEvent({
        title: newEvent.title,
        description: newEvent.description,
        start_datetime: newEvent.start,
        end_datetime: newEvent.end,
        event_type: newEvent.type,
        priority: newEvent.priority
      });
      setNewEvent({ title: '', description: '', start: '', end: '', type: 'FAMILY_EVENT', priority: 'MEDIUM' });
      setShowEventForm(false);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteEvent = async (id: number) => {
    try {
      await calendarService.deleteEvent(id);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, unread: false })));
  };

  const unreadCount = notifications.filter(n => n.unread).length;

  if (error) {
    return (
      <div className="flex h-screen bg-slate-50 items-center justify-center">
        <div className="text-center space-y-4 white-card p-8 border-rose-200">
          <AlertTriangle className="h-10 w-10 text-rose-500 mx-auto animate-bounce" />
          <p className="text-rose-600 font-bold">{error}</p>
          <button 
            onClick={fetchData} 
            className="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-semibold transition"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-slate-50 items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-slate-500 font-extrabold animate-pulse text-xs uppercase tracking-wider">Synchronizing KinNest Planner context...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#F8FAFC] text-slate-800 overflow-hidden font-sans">
      
      {/* Sidebar Component */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        notificationsCount={unreadCount}
      />

      {/* Main Workspace Frame */}
      <main className="flex-1 flex flex-col overflow-hidden">
        
        {/* Top Navbar */}
        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8 shrink-0 shadow-sm z-10">
          <div>
            <h2 className="text-md font-extrabold text-slate-800 capitalize leading-tight">
              {activeTab.replace('-', ' ')}
            </h2>
            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">KinNest Assistant Module</p>
          </div>

          <div className="flex items-center gap-4">
            <button 
              onClick={() => setActiveTab('notifications')}
              className="relative p-2 rounded-xl hover:bg-slate-50 text-slate-500 hover:text-slate-800 transition-colors border border-slate-200"
            >
              <Bell className="h-4.5 w-4.5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 h-2 w-2 bg-rose-500 rounded-full"></span>
              )}
            </button>

            <div className="h-6 w-px bg-slate-200"></div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-blue-600 bg-blue-50 border border-blue-100 px-3 py-1 rounded-full">
                Score: {digitalTwin?.planning_score || 85}%
              </span>
            </div>
          </div>
        </header>

        {/* Dynamic Pages Area */}
        <div className="flex-1 overflow-y-auto p-8 bg-[#F8FAFC]">
          <AnimatePresence mode="wait">
            {activeTab === 'dashboard' && (
              <DashboardPage 
                goals={goals}
                habits={habits}
                digitalTwin={digitalTwin}
                events={events}
                tasks={tasks}
                recommendations={recommendations}
                scheduleHealth={scheduleHealth}
                onNavigate={setActiveTab}
                onAddTask={() => setShowTaskForm(true)}
                onAddEvent={() => setShowEventForm(true)}
              />
            )}
            {activeTab === 'calendar' && (
              <CalendarPage 
                events={events}
                onAddEvent={() => setShowEventForm(true)}
                onDeleteEvent={handleDeleteEvent}
              />
            )}
            {activeTab === 'tasks' && (
              <TasksPage 
                tasks={tasks}
                onAddTask={() => setShowTaskForm(true)}
                onToggleStatus={handleToggleTaskStatus}
                onDeleteTask={handleDeleteTask}
              />
            )}
            {activeTab === 'goals' && (
              <GoalsPage 
                goals={goals}
                onAddGoal={() => setShowGoalForm(true)}
                onUpdateGoal={handleUpdateGoalProgress}
                onDeleteGoal={handleDeleteGoal}
              />
            )}
            {activeTab === 'habits' && (
              <HabitsPage 
                habits={habits}
                onAddHabit={() => setShowHabitForm(true)}
                onLogHabit={handleLogHabit}
                onDeleteHabit={handleDeleteHabit}
              />
            )}
            {activeTab === 'family-schedule' && (
              <FamilyTimelinePage 
                timelineData={timelineData}
                scheduleHealth={scheduleHealth}
              />
            )}
            {activeTab === 'ai-planner' && (
              <AIPlannerPage 
                promptValue={aiPrompt}
                setPromptValue={setAiPrompt}
                onSubmit={handleAskAI}
                loading={aiLoading}
                response={aiResponse}
              />
            )}
            {activeTab === 'digital-twin' && (
              <DigitalTwinPage 
                digitalTwin={digitalTwin}
              />
            )}
            {activeTab === 'recommendations' && (
              <RecommendationsPage 
                recommendations={recommendations}
              />
            )}
            {activeTab === 'notifications' && (
              <NotificationsPage 
                notifications={notifications}
                onMarkAllAsRead={handleMarkAllRead}
              />
            )}
            {activeTab === 'settings' && (
              <SettingsPage />
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* ============================================================== */}
      {/* GOAL MODAL FORM */}
      {/* ============================================================== */}
      {showGoalForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm">
          <div className="w-full max-w-md p-6 rounded-2xl bg-white border border-slate-200 space-y-4 shadow-2xl">
            <h4 className="font-extrabold text-slate-800 text-md">Add New Goal</h4>
            <form onSubmit={handleAddGoal} className="space-y-4 text-xs font-bold text-slate-500">
              <div className="space-y-1">
                <label>Goal Title</label>
                <input required type="text" value={newGoal.title} onChange={e => setNewGoal({...newGoal, title: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:border-blue-500 text-slate-800 font-medium" />
              </div>
              <div className="space-y-1">
                <label>Description</label>
                <textarea value={newGoal.description} onChange={e => setNewGoal({...newGoal, description: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:border-blue-500 h-20 resize-none text-slate-800 font-medium" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label>Category</label>
                  <select value={newGoal.category} onChange={e => setNewGoal({...newGoal, category: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none text-slate-800 font-medium">
                    <option value="PERSONAL">Personal</option>
                    <option value="ACADEMIC">Academic</option>
                    <option value="FINANCIAL">Financial</option>
                    <option value="HEALTH">Health</option>
                    <option value="HOUSEHOLD">Household</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label>Deadline</label>
                  <input type="date" value={newGoal.deadline} onChange={e => setNewGoal({...newGoal, deadline: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none text-slate-800 font-medium" />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowGoalForm(false)} className="px-4 py-2 text-slate-400 hover:text-slate-700 transition">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition">Save Goal</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* HABIT MODAL FORM */}
      {/* ============================================================== */}
      {showHabitForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm">
          <div className="w-full max-w-sm p-6 rounded-2xl bg-white border border-slate-200 space-y-4 shadow-2xl">
            <h4 className="font-extrabold text-slate-800 text-md">New Habit</h4>
            <form onSubmit={handleAddHabit} className="space-y-4 text-xs font-bold text-slate-500">
              <div className="space-y-1">
                <label>Habit Name</label>
                <input required type="text" value={newHabit.title} onChange={e => setNewHabit({...newHabit, title: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:border-blue-500 text-slate-800 font-medium" />
              </div>
              <div className="space-y-1">
                <label>Category</label>
                <select value={newHabit.category} onChange={e => setNewHabit({...newHabit, category: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none text-slate-800 font-medium">
                  <option value="WATER">Water</option>
                  <option value="EXERCISE">Exercise</option>
                  <option value="READING">Reading</option>
                  <option value="MEDITATION">Meditation</option>
                  <option value="STUDY">Study</option>
                  <option value="CODING">Coding</option>
                  <option value="CUSTOM">Custom</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowHabitForm(false)} className="px-4 py-2 text-slate-400 hover:text-slate-700 transition">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition">Save Habit</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* TASK MODAL FORM */}
      {/* ============================================================== */}
      {showTaskForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm">
          <div className="w-full max-w-md p-6 rounded-2xl bg-white border border-slate-200 space-y-4 shadow-2xl">
            <h4 className="font-extrabold text-slate-800 text-md">Create Task</h4>
            <form onSubmit={handleAddTask} className="space-y-4 text-xs font-bold text-slate-500">
              <div className="space-y-1">
                <label>Task Title</label>
                <input required type="text" value={newTask.title} onChange={e => setNewTask({...newTask, title: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:border-blue-500 text-slate-800 font-medium" />
              </div>
              <div className="space-y-1">
                <label>Description</label>
                <textarea value={newTask.description} onChange={e => setNewTask({...newTask, description: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none h-20 resize-none text-slate-800 font-medium" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label>Priority</label>
                  <select value={newTask.priority} onChange={e => setNewTask({...newTask, priority: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 font-medium">
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label>Due Date</label>
                  <input type="date" value={newTask.due_date} onChange={e => setNewTask({...newTask, due_date: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 font-medium" />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowTaskForm(false)} className="px-4 py-2 text-slate-400 hover:text-slate-700 transition">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition">Save Task</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* EVENT MODAL FORM */}
      {/* ============================================================== */}
      {showEventForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm">
          <div className="w-full max-w-md p-6 rounded-2xl bg-white border border-slate-200 space-y-4 shadow-2xl">
            <h4 className="font-extrabold text-slate-800 text-md">Add Calendar Event</h4>
            <form onSubmit={handleAddEvent} className="space-y-4 text-xs font-bold text-slate-500">
              <div className="space-y-1">
                <label>Event Title</label>
                <input required type="text" value={newEvent.title} onChange={e => setNewEvent({...newEvent, title: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:border-blue-500 text-slate-800 font-medium" />
              </div>
              <div className="space-y-1">
                <label>Description</label>
                <textarea value={newEvent.description} onChange={e => setNewEvent({...newEvent, description: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none h-16 resize-none text-slate-800 font-medium" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label>Start Time</label>
                  <input required type="datetime-local" value={newEvent.start} onChange={e => setNewEvent({...newEvent, start: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 font-medium" />
                </div>
                <div className="space-y-1">
                  <label>End Time</label>
                  <input required type="datetime-local" value={newEvent.end} onChange={e => setNewEvent({...newEvent, end: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 font-medium" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label>Event Type</label>
                  <select value={newEvent.type} onChange={e => setNewEvent({...newEvent, type: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 font-medium">
                    <option value="FAMILY_EVENT">Family Event</option>
                    <option value="BIRTHDAY">Birthday</option>
                    <option value="TRAVEL">Travel</option>
                    <option value="STUDY_EXAM">School/Exam</option>
                    <option value="MEDICAL">Medical</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label>Priority</label>
                  <select value={newEvent.priority} onChange={e => setNewEvent({...newEvent, priority: e.target.value})} className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 font-medium">
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowEventForm(false)} className="px-4 py-2 text-slate-400 hover:text-slate-700 transition">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition">Save Event</button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
