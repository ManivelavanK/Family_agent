import React, { useEffect, useState } from 'react';
import { insuranceService } from '../../services/insuranceService';
import { Insurance as InsuranceType } from '../../types';
import { Plus, ShieldCheck, Trash2, ShieldAlert, PhoneCall, Calendar } from 'lucide-react';
import toast from 'react-hot-toast';
import Dialog from '../../components/common/Dialog';

export const Insurance: React.FC = () => {
  const [policies, setPolicies] = useState<InsuranceType[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [provider, setProvider] = useState('');
  const [policyNumber, setPolicyNumber] = useState('');
  const [coverage, setCoverage] = useState('');
  const [expiry, setExpiry] = useState('');
  const [contact, setContact] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadInsurance();
  }, []);

  const loadInsurance = async () => {
    setLoading(true);
    try {
      const data = await insuranceService.getInsurance();
      setPolicies(data);
    } catch (e) {
      toast.error("Failed to load insurance policies.");
    } finally {
      setLoading(false);
    }
  };

  const handleAddInsurance = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const newIns: Omit<InsuranceType, 'id'> = {
        provider,
        policy_number: policyNumber,
        coverage_details: coverage,
        expiry_date: expiry,
        contact_number: contact
      };
      await insuranceService.addInsurance(newIns);
      toast.success("Policy added successfully!");
      setIsModalOpen(false);
      resetForm();
      loadInsurance();
    } catch (e) {
      toast.error("Could not save insurance policy details.");
    } finally {
      setSaving(false);
    }
  };

  const resetForm = () => {
    setProvider('');
    setPolicyNumber('');
    setCoverage('');
    setExpiry('');
    setContact('');
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Remove this insurance policy?")) return;
    try {
      await insuranceService.deleteInsurance(id);
      toast.success("Policy removed.");
      loadInsurance();
    } catch (e) {
      toast.error("Failed to delete.");
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
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-slate-800">Health Insurance Policies</h3>
          <p className="text-sm font-semibold text-slate-400">Manage claims contact information, senior citizen policies, and expiry notifications.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-5 py-3 bg-sky-500 hover:bg-sky-600 active:scale-95 text-white font-bold rounded-xl transition-all cursor-pointer shadow-xs"
        >
          <Plus className="h-5 w-5" />
          <span>Add Policy Details</span>
        </button>
      </div>

      {/* Grid of Policies */}
      <div className="grid gap-6 md:grid-cols-2">
        {policies.map((p) => {
          const daysToExpiry = Math.ceil((new Date(p.expiry_date).getTime() - new Date().getTime()) / (1000 * 3600 * 24));
          const isNearExpiry = daysToExpiry <= 30;

          return (
            <div key={p.id} className="bg-white border border-sky-100 p-6 rounded-2xl flex flex-col justify-between hover:shadow-md transition-shadow relative">
              {isNearExpiry && (
                <span className="absolute top-4 right-4 flex items-center gap-1 bg-amber-50 text-amber-600 text-xs font-bold px-2.5 py-1 rounded-full border border-amber-200 animate-pulse">
                  <ShieldAlert className="h-3.5 w-3.5" />
                  <span>Renewal Pending</span>
                </span>
              )}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className="p-3 bg-sky-50 text-sky-600 rounded-xl border border-sky-100">
                    <ShieldCheck className="h-6 w-6" />
                  </span>
                  <div>
                    <h4 className="text-lg font-black text-slate-800 leading-tight">{p.provider}</h4>
                    <span className="text-sm font-semibold text-slate-400">Policy: {p.policy_number}</span>
                  </div>
                </div>

                <div className="bg-slate-50 p-4 rounded-xl space-y-2 text-sm text-slate-700">
                  <div>
                    <span className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Coverage Details</span>
                    <span className="font-semibold text-slate-700">{p.coverage_details}</span>
                  </div>
                  <div className="flex items-center gap-2 pt-2 text-xs font-bold text-slate-500">
                    <Calendar className="h-4 w-4" />
                    <span>Expires on: {p.expiry_date} ({daysToExpiry} days remaining)</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2 mt-6 pt-3 border-t border-slate-100">
                <a
                  href={`tel:${p.contact_number}`}
                  className="flex-1 flex items-center justify-center gap-1.5 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold text-sm py-2.5 rounded-xl transition-all cursor-pointer"
                >
                  <PhoneCall className="h-4 w-4" />
                  <span>Call Agent ({p.contact_number})</span>
                </a>
                <button
                  onClick={() => handleDelete(p.id)}
                  className="p-2.5 border border-slate-200 hover:bg-rose-50 hover:text-rose-600 hover:border-rose-200 text-slate-400 rounded-xl transition-colors cursor-pointer"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          );
        })}
        {policies.length === 0 && (
          <div className="bg-slate-50 border border-dashed border-slate-200 p-8 rounded-2xl text-center text-slate-400 col-span-2">
            No health insurance policies logged yet. Keep your policies handy here.
          </div>
        )}
      </div>

      {/* Add Policy Modal */}
      <Dialog isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Insurance Policy">
        <form onSubmit={handleAddInsurance} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Insurance Provider</label>
            <input
              type="text"
              value={provider}
              onChange={e => setProvider(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="e.g. Star Health Insurance"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Policy Number</label>
              <input
                type="text"
                value={policyNumber}
                onChange={e => setPolicyNumber(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
                placeholder="e.g. SH-89302"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">TPA Claims Helpline</label>
              <input
                type="text"
                value={contact}
                onChange={e => setContact(e.target.value)}
                required
                className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
                placeholder="e.g. 1800-425-2255"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Coverage Details & Sum Insured</label>
            <textarea
              rows={3}
              value={coverage}
              onChange={e => setCoverage(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
              placeholder="e.g. Sum insured 5 Lakhs. Covers pre-existing hypertension..."
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Policy Expiry Date</label>
            <input
              type="date"
              value={expiry}
              onChange={e => setExpiry(e.target.value)}
              required
              className="w-full text-base p-2.5 rounded-lg border border-slate-200 focus:outline-none"
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
              {saving ? 'Saving...' : 'Save Policy'}
            </button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
export default Insurance;
