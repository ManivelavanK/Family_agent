import React, { useEffect, useState } from 'react';
import { appointmentService } from '../../services/appointmentService';
import { Appointment as AppointmentType } from '../../types';
import { Plus, Calendar, Trash2, CheckCircle, ExternalLink, MapPin } from 'lucide-react';
import toast from 'react-hot-toast';
import Dialog from '../../components/common/Dialog';
import StatusBadge from '../../components/common/StatusBadge';

export const Appointments: React.FC = () => {
  const [appts, setAppts] = useState<AppointmentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [doctor, setDoctor] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [hospital, setHospital] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('10:00');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadAppointments();
  }, []);

  const loadAppointments = async () => {
    setLoading(true);
    try {
      const data = await appointmentService.getAppointments();
      setAppts(data);
    } catch (e) {
      toast.error("Failed to load appointments.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddAppointment = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const newAppt: Omit<AppointmentType, 'id' | 'status'> = {
        doctor_name: doctor,
        specialty,
        hospital_name: hospital,
        appointment_date: date,
        appointment_time: time,
        notes
      };
      await appointmentService.addAppointment(newAppt);
      toast.success("Appointment scheduled!");
      setIsModalOpen(false);
      resetForm();
      loadAppointments();
    } catch (e) {
      toast.error("Could not schedule appointment.");
    } finally {
      setSaving(false);
    }
  };

  const resetForm = () => {
    setDoctor('');
    setSpecialty('');
    setHospital('');
    setDate('');
    setTime('10:00');
    setNotes('');
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Cancel this appointment?")) return;
    try {
      await appointmentService.deleteAppointment(id);
      toast.success("Appointment cancelled.");
      loadAppointments();
    } catch (e) {
      toast.error("Failed to delete.");
    }
  };

  const handleMarkCompleted = async (id: string) => {
    try {
      await appointmentService.updateAppointment(id, { status: 'Completed' });
      toast.success("Appointment marked as completed!");
      loadAppointments();
    } catch (e) {
      toast.error("Error updating status.");
    }
  };

  const upcoming = appts.filter(a => a.status === 'Upcoming');
  const past = appts.filter(a => a.status === 'Completed' || a.status === 'Cancelled');

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-sky-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-slate-800">Doctor Appointments</h3>
          <p className="text-sm font-semibold text-slate-400">Keep track of checkups, consultations, and test reminders.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-5 py-3 bg-sky-500 hover:bg-sky-600 active:scale-95 text-white font-bold rounded-xl transition-all cursor-pointer shadow-xs"
        >
          <Plus className="h-5 w-5" />
          <span>Schedule Appointment</span>
        </button>
      </div>

      {/* Grid: Upcoming appointments */}
      <div>
        <h4 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-sky-500 animate-pulse" />
          <span>Upcoming Consultations</span>
        </h4>
        <div className="grid gap-6 md:grid-cols-2">
          {upcoming.map((appt) => (
            <div key={appt.id} className="bg-white border border-sky-100 p-6 rounded-2xl flex flex-col justify-between hover:shadow-md transition-shadow relative">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h5 className="text-lg font-black text-slate-800 leading-tight">{appt.doctor_name}</h5>
                    <span className="text-sm text-sky-600 font-bold">{appt.specialty}</span>
                  </div>
                  <StatusBadge status={appt.status} />
                </div>

                <div className="space-y-1.5 border-t border-slate-100 pt-3 text-sm">
                  <div className="flex items-center gap-2 text-slate-600">
                    <MapPin className="h-4 w-4 text-slate-400" />
                    <span className="font-semibold">{appt.hospital_name}</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-600">
                    <Calendar className="h-4 w-4 text-slate-400" />
                    <span className="font-bold">{appt.appointment_date} at {appt.appointment_time}</span>
                  </div>
                  {appt.notes && (
                    <p className="text-xs italic text-slate-500 bg-slate-50 p-2.5 rounded-lg mt-2">{appt.notes}</p>
                  )}
                </div>
              </div>

              <div className="flex gap-2 mt-4 pt-3 border-t border-slate-100">
                <button
                  onClick={() => handleMarkCompleted(appt.id)}
                  className="flex-1 flex items-center justify-center gap-1.5 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold text-sm py-2.5 rounded-xl transition-all cursor-pointer"
                >
                  <CheckCircle className="h-4 w-4" />
                  <span>Mark Done</span>
                </button>
                <button
                  onClick={() => handleDelete(appt.id)}
                  className="p-2 border border-slate-200 hover:bg-rose-50 hover:text-rose-600 hover:border-rose-200 text-slate-400 rounded-xl transition-colors cursor-pointer"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
          {upcoming.length === 0 && (
            <div className="bg-slate-50 border border-dashed border-slate-200 p-8 rounded-2xl text-center text-slate-400 col-span-2">
              No upcoming appointments. Schedule one above if you are due for a routine checkup.
            </div>
          )}
        </div>
      </div>

      {/* Past/History list */}
      <div className="bg-white border border-sky-100 rounded-2xl shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <h4 className="text-lg font-bold text-slate-800">Visit History</h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100">
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Doctor</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Hospital</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Date & Time</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Notes</th>
                <th className="px-6 py-4 text-sm font-bold text-slate-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {past.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50/50">
                  <td className="px-6 py-4 text-base font-bold text-slate-800">
                    {a.doctor_name}
                    <span className="block text-xs font-semibold text-sky-600">{a.specialty}</span>
                  </td>
                  <td className="px-6 py-4 text-base font-semibold">{a.hospital_name}</td>
                  <td className="px-6 py-4 text-base font-semibold">{a.appointment_date} at {a.appointment_time}</td>
                  <td className="px-6 py-4 text-base italic text-slate-500">{a.notes || 'None'}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={a.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Appointment Modal */}
      <Dialog isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Schedule Consultation">
        <form onSubmit={handleAddAppointment} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Doctor Name</label>
            <input
              type="text"
              value={doctor}
              onChange={e => setDoctor(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="e.g. Dr. Srinivasa Raghavan"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Specialty</label>
              <input
                type="text"
                value={specialty}
                onChange={e => setSpecialty(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
                placeholder="e.g. Diabetologist"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Hospital / Clinic</label>
              <input
                type="text"
                value={hospital}
                onChange={e => setHospital(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
                placeholder="e.g. Apollo Hospitals"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Appointment Date</label>
              <input
                type="date"
                value={date}
                onChange={e => setDate(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Appointment Time</label>
              <input
                type="time"
                value={time}
                onChange={e => setTime(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Preparation Notes / Instructions</label>
            <textarea
              rows={2}
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="e.g. Carry glucose reports. Keep fasting 8 hours before."
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
              {saving ? 'Scheduling...' : 'Save Appointment'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
export default Appointments;
