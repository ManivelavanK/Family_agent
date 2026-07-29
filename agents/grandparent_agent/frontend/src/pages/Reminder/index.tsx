import React, { useEffect, useState } from 'react';
import { reminderService } from '../../services/reminderService';
import { Reminder as RemType } from '../../types';
import { Plus, Bell, Trash2, Calendar, Pill, Heart, Activity } from 'lucide-react';
import toast from 'react-hot-toast';
import Dialog from '../../components/common/Dialog';

export const Reminder: React.FC = () => {
  const [rems, setRems] = useState<RemType[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [title, setTitle] = useState('');
  const [time, setTime] = useState('09:00');
  const [category, setCategory] = useState('Medicine');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadReminders();
  }, []);

  const loadReminders = async () => {
    try {
      const data = await reminderService.getReminders();
      setRems(data);
    } catch (e) {
      toast.error("Failed to load reminders.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await reminderService.addReminder({
        title,
        reminder_time: time,
        category,
        is_active: true,
        recurring: true
      });
      toast.success("Reminder set successfully!");
      setIsModalOpen(false);
      setTitle('');
      loadReminders();
    } catch (e) {
      toast.error("Could not set reminder.");
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (id: string) => {
    try {
      await reminderService.toggleReminder(id);
      toast.success("Reminder status updated.");
      loadReminders();
    } catch (e) {
      toast.error("Error toggling reminder.");
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this reminder?")) return;
    try {
      await reminderService.deleteReminder(id);
      toast.success("Reminder deleted.");
      loadReminders();
    } catch (e) {
      toast.error("Could not delete.");
    }
  };

  const getCatIcon = (cat: string) => {
    switch (cat) {
      case 'Medicine': return Pill;
      case 'Appointment': return Calendar;
      case 'Activity': return Activity;
      default: return Bell;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-sky-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-slate-800">Daily Reminders</h3>
          <p className="text-sm font-semibold text-slate-400">Set timers for meds, warm water hydration, and physical walks.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-5 py-3 bg-sky-500 hover:bg-sky-600 active:scale-95 text-white font-bold rounded-xl transition-all cursor-pointer shadow-xs"
        >
          <Plus className="h-5 w-5" />
          <span>Add Reminder</span>
        </button>
      </div>

      <div className="grid gap-4 max-w-2xl">
        {rems.map((rem) => {
          const Icon = getCatIcon(rem.category);
          return (
            <div key={rem.id} className="bg-white border border-sky-100 p-4 rounded-xl flex items-center justify-between hover:shadow-xs transition-shadow">
              <div className="flex items-center gap-4">
                <span className="p-3 bg-sky-50 text-sky-600 rounded-xl border border-sky-100">
                  <Icon className="h-5 w-5" />
                </span>
                <div>
                  <h4 className={`text-lg font-bold text-slate-800 leading-tight ${rem.completed ? 'line-through opacity-50' : ''}`}>{rem.title}</h4>
                  <span className="text-sm font-semibold text-slate-400">Time: {rem.reminder_time} ({rem.category})</span>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <input
                  type="checkbox"
                  checked={rem.completed || false}
                  onChange={() => handleToggle(rem.id)}
                  className="h-6 w-6 text-sky-500 border-slate-300 rounded focus:ring-sky-500 cursor-pointer"
                />
                <button
                  onClick={() => handleDelete(rem.id)}
                  className="text-slate-400 hover:text-rose-600 p-1 rounded-lg hover:bg-rose-50 cursor-pointer transition-colors"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Reminder Modal */}
      <Dialog isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Set New Reminder">
        <form onSubmit={handleAddReminder} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Reminder Label</label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="e.g. Drink warm copper cup water"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Reminder Time</label>
              <input
                type="time"
                value={time}
                onChange={e => setTime(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Category</label>
              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none bg-white"
              >
                <option value="Medicine">Medicine</option>
                <option value="Appointment">Appointment</option>
                <option value="Activity">Activity</option>
                <option value="Hydration">Hydration</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-5 py-2.5 rounded-xl border border-slate-200 font-bold hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-600 active:scale-95 text-white font-bold transition-colors shadow-xs"
            >
              {saving ? 'Setting...' : 'Set Reminder'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
export default Reminder;
