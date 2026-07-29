import React, { useEffect, useState } from 'react';
import { medicineService } from '../../services/medicineService';
import { Medicine as MedicineType, MedicineLog } from '../../types';
import { Plus, Pill, AlertTriangle, CheckCircle, Trash2, Calendar, ClipboardList } from 'lucide-react';
import toast from 'react-hot-toast';
import Dialog from '../../components/common/Dialog';
import StatusBadge from '../../components/common/StatusBadge';

export const Medicine: React.FC = () => {
  const [meds, setMeds] = useState<MedicineType[]>([]);
  const [logs, setLogs] = useState<MedicineLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [name, setName] = useState('');
  const [dosage, setDosage] = useState('500mg');
  const [frequency, setFrequency] = useState('Daily');
  const [times, setTimes] = useState('08:30, 20:30');
  const [inventory, setInventory] = useState('30');
  const [warningThreshold, setWarningThreshold] = useState('10');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadMedsAndLogs();
  }, []);

  const loadMedsAndLogs = async () => {
    setLoading(true);
    try {
      const medList = await medicineService.getMedicines();
      setMeds(medList);
      const logList = await medicineService.getLogs();
      setLogs(logList);
    } catch (e) {
      toast.error("Failed to load medicine dashboard.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddMedicine = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const timesArray = times.split(',').map(t => t.trim());
      const newMed: Omit<MedicineType, 'id'> = {
        name,
        dosage,
        frequency,
        times: timesArray,
        inventory_remaining: parseInt(inventory) || 0,
        inventory_warning_threshold: parseInt(warningThreshold) || 10,
        notes
      };
      await medicineService.addMedicine(newMed);
      toast.success("Medicine added successfully.");
      setIsModalOpen(false);
      resetForm();
      loadMedsAndLogs();
    } catch (e) {
      toast.error("Could not register medicine.");
    } finally {
      setSaving(false);
    }
  };

  const resetForm = () => {
    setName('');
    setDosage('500mg');
    setFrequency('Daily');
    setTimes('08:30, 20:30');
    setInventory('30');
    setWarningThreshold('10');
    setNotes('');
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Remove this medication?")) return;
    try {
      await medicineService.deleteMedicine(id);
      toast.success("Medicine removed.");
      loadMedsAndLogs();
    } catch (e) {
      toast.error("Error deleting medication.");
    }
  };

  const handleTake = async (id: string) => {
    try {
      await medicineService.takeMedicine(id);
      toast.success("Medication checked off as taken! Log updated.");
      loadMedsAndLogs();
    } catch (e) {
      toast.error("Failed to record taken medication.");
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
      {/* Overview stats & trigger */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-slate-800">Medication Management</h3>
          <p className="text-sm font-semibold text-slate-400">Track prescriptions, daily schedules, and pill inventory.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-5 py-3 bg-sky-500 hover:bg-sky-600 active:scale-95 text-white font-bold rounded-xl transition-all cursor-pointer shadow-sm shadow-sky-100"
        >
          <Plus className="h-5 w-5" />
          <span>Add New Prescription</span>
        </button>
      </div>

      {/* Grid: Pills list with inventory warnings */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {meds.map((med) => {
          const isLowStock = med.inventory_remaining <= med.inventory_warning_threshold;
          return (
            <div key={med.id} className="bg-white border border-sky-100 p-6 rounded-2xl flex flex-col justify-between hover:shadow-md transition-shadow relative">
              {isLowStock && (
                <span className="absolute top-4 right-4 flex items-center gap-1 bg-rose-50 text-rose-600 text-xs font-bold px-2.5 py-1 rounded-full border border-rose-200 animate-pulse">
                  <AlertTriangle className="h-3 w-3" />
                  <span>Low Stock!</span>
                </span>
              )}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className={`p-3 rounded-xl border ${isLowStock ? 'bg-rose-50 text-rose-600 border-rose-100' : 'bg-sky-50 text-sky-600 border-sky-100'}`}>
                    <Pill className="h-6 w-6" />
                  </span>
                  <div>
                    <h4 className="text-lg font-black text-slate-800 leading-tight">{med.name}</h4>
                    <span className="text-sm text-slate-500 font-semibold">{med.dosage} — {med.frequency}</span>
                  </div>
                </div>

                <div className="space-y-1.5 border-t border-slate-100 pt-3">
                  <div className="flex justify-between text-sm">
                    <span className="font-semibold text-slate-400">Scheduled Times:</span>
                    <span className="font-bold text-slate-700">{med.times.join(', ')}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="font-semibold text-slate-400">Remaining Inventory:</span>
                    <span className={`font-bold ${isLowStock ? 'text-rose-600' : 'text-slate-700'}`}>{med.inventory_remaining} pills</span>
                  </div>
                  {med.notes && (
                    <p className="text-xs italic text-slate-500 bg-slate-50 p-2 rounded-lg mt-1">{med.notes}</p>
                  )}
                </div>
              </div>

              <div className="flex gap-2 mt-4 pt-3 border-t border-slate-100">
                <button
                  onClick={() => handleTake(med.id)}
                  className="flex-1 flex items-center justify-center gap-1.5 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold text-sm py-2.5 rounded-xl transition-all cursor-pointer"
                >
                  <CheckCircle className="h-4 w-4" />
                  <span>Take Now</span>
                </button>
                <button
                  onClick={() => handleDelete(med.id)}
                  className="p-2 border border-slate-200 hover:bg-rose-50 hover:text-rose-600 hover:border-rose-200 text-slate-400 rounded-xl transition-colors cursor-pointer"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Two columns: Log History and Today's Schedule */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Medicine Schedule Tracker */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Calendar className="h-5 w-5 text-sky-500" />
            <span>Today's Medicine Schedule</span>
          </h4>
          <div className="space-y-3">
            {meds.flatMap(med => med.times.map(time => ({ med, time }))).sort((a, b) => a.time.localeCompare(b.time)).map(({ med, time }, idx) => {
              const wasTaken = logs.some(l => l.medicine_id === med.id && new Date(l.taken_at).toLocaleDateString() === new Date().toLocaleDateString() && new Date(l.taken_at).getHours() === parseInt(time.split(':')[0]));
              return (
                <div key={idx} className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl hover:bg-slate-100/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <span className="text-base font-bold text-sky-600 bg-sky-50 px-2.5 py-1 rounded-lg border border-sky-100">{time}</span>
                    <div>
                      <span className="block font-bold text-slate-800 text-base">{med.name}</span>
                      <span className="block text-xs font-semibold text-slate-400">{med.dosage}</span>
                    </div>
                  </div>
                  <button
                    disabled={wasTaken}
                    onClick={() => handleTake(med.id)}
                    className={`px-4 py-1.5 rounded-lg font-bold text-sm ${wasTaken ? 'bg-emerald-50 text-emerald-600 border border-emerald-200' : 'bg-sky-500 text-white hover:bg-sky-600 transition-colors cursor-pointer'}`}
                  >
                    {wasTaken ? 'Taken ✓' : 'Mark Taken'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Medication Intake Logs */}
        <div className="bg-white border border-sky-100 p-6 rounded-2xl shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <ClipboardList className="h-5 w-5 text-emerald-500" />
            <span>Medication Logs History</span>
          </h4>
          <div className="overflow-y-auto max-h-80 space-y-2">
            {logs.slice().reverse().map((log) => (
              <div key={log.id} className="flex items-center justify-between p-3 border border-slate-100 rounded-xl">
                <div>
                  <span className="block font-bold text-slate-800">{log.medicine_name}</span>
                  <span className="block text-xs font-semibold text-slate-400">{new Date(log.taken_at).toLocaleString()}</span>
                </div>
                <StatusBadge status={log.status || 'Taken'} />
              </div>
            ))}
            {logs.length === 0 && (
              <p className="text-center py-6 text-slate-400 font-medium">No medication logs available yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Add Medicine Modal */}
      <Dialog isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Register Prescription">
        <form onSubmit={handleAddMedicine} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Medication Name</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="e.g. Metformin"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Dosage</label>
              <input
                type="text"
                value={dosage}
                onChange={e => setDosage(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
                placeholder="e.g. 500mg"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Frequency</label>
              <select
                value={frequency}
                onChange={e => setFrequency(e.target.value)}
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none bg-white"
              >
                <option value="Daily">Daily</option>
                <option value="Weekly">Weekly</option>
                <option value="As Needed">As Needed</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Scheduled Times (comma-separated)</label>
            <input
              type="text"
              value={times}
              onChange={e => setTimes(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="e.g. 08:30, 20:30"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Initial Stock (Pills)</label>
              <input
                type="number"
                value={inventory}
                onChange={e => setInventory(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Low Warning Threshold</label>
              <input
                type="number"
                value={warningThreshold}
                onChange={e => setWarningThreshold(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Usage Notes</label>
            <textarea
              rows={2}
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="Take after meals..."
            />
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
              {saving ? 'Saving...' : 'Add Medicine'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
export default Medicine;
