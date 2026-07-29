import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { billApi } from '../services/billApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AnimatedNumber } from '../components/ui/AnimatedNumber';
import { FileText, Plus, CheckCircle, Clock, Calendar, AlertCircle, Check, X } from 'lucide-react';

export const Bills = () => {
  const { familyId, triggerRefresh } = useFamily();
  const [loading, setLoading] = useState(true);
  const [bills, setBills] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Form State
  const [billType, setBillType] = useState('Electricity');
  const [amount, setAmount] = useState('');
  const [dueDate, setDueDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchBills = async () => {
    setLoading(true);
    try {
      const data = await billApi.getBills(familyId);
      setBills(data || []);
    } catch (err) {
      console.error('Error fetching bills:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBills();
  }, [familyId]);

  const handleCreateBill = async (e) => {
    e.preventDefault();
    if (!billType || !amount || !dueDate) return;

    setSubmitting(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      await billApi.createBill({
        family_id: Number(familyId),
        bill_type: billType,
        amount: parseFloat(amount),
        due_date: dueDate,
      });

      setSuccessMsg(`Upcoming bill recorded: ${billType}`);
      setAmount('');
      setIsModalOpen(false);
      triggerRefresh();
      fetchBills();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create bill');
    } finally {
      setSubmitting(false);
    }
  };

  const handlePayBill = async (billId) => {
    try {
      await billApi.payBill(billId);
      setSuccessMsg('Bill marked as paid in ledger!');
      triggerRefresh();
      fetchBills();
    } catch (err) {
      console.error('Failed to pay bill:', err);
    }
  };

  const pendingBills = bills.filter((b) => b.status === 'Pending');
  const paidBills = bills.filter((b) => b.status === 'Paid');
  const totalPendingAmount = pendingBills.reduce((acc, b) => acc + Number(b.amount || 0), 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
            <FileText className="w-8 h-8 text-[#D97706]" />
            <span>Bills & Subscriptions</span>
          </h1>
          <p className="text-[#627D98] text-sm mt-1">
            Automated obligation schedule, due date alerts, and one-click bill payment.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#102A43] hover:bg-[#243B53] text-white font-medium text-sm shadow-lg shadow-[#102A43]/15 transition-all hover:scale-[1.02] cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Add Bill</span>
        </button>
      </div>

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard glow={true}>
          <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Pending Bills Total</div>
          <div className="text-3xl font-black text-[#D97706] mt-1">
            <AnimatedNumber value={totalPendingAmount} />
          </div>
          <p className="text-xs text-[#627D98] mt-2">{pendingBills.length} pending obligations</p>
        </GlassCard>

        <GlassCard>
          <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Paid Bills</div>
          <div className="text-3xl font-black text-[#2F855A] mt-1">{paidBills.length}</div>
          <p className="text-xs text-[#627D98] mt-2">Completed bill payments</p>
        </GlassCard>

        <GlassCard>
          <div className="text-xs font-semibold text-[#627D98] uppercase tracking-wider">Total Bills Tracked</div>
          <div className="text-3xl font-black text-[#0F766E] mt-1">{bills.length}</div>
          <p className="text-xs text-[#627D98] mt-2">Active recurring commitments</p>
        </GlassCard>
      </div>

      {/* Bills Timeline */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-bold text-[#102A43] mb-4">Upcoming Bill Timeline</h3>

        {loading ? (
          <div className="py-12 text-center text-[#627D98]">Loading bill timeline...</div>
        ) : bills.length > 0 ? (
          <div className="space-y-4">
            {bills.map((bill) => {
              const isPaid = bill.status === 'Paid';
              return (
                <div
                  key={bill.id}
                  className={`p-4 rounded-xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                    isPaid
                      ? 'bg-[#F7F9FC] border-[#D9E2EC] opacity-75'
                      : 'bg-white border-[#D9E2EC] shadow-sm'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`p-3 rounded-xl ${
                        isPaid ? 'bg-emerald-500/10 text-emerald-700' : 'bg-amber-500/10 text-amber-700'
                      }`}
                    >
                      <Calendar className="w-5 h-5" />
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-[#172B4D] text-base">{bill.bill_type}</h4>
                        <span
                          className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase ${
                            isPaid
                              ? 'bg-emerald-500/15 text-emerald-700 border border-emerald-500/25'
                              : 'bg-amber-500/15 text-amber-700 border border-amber-500/25'
                          }`}
                        >
                          {bill.status}
                        </span>
                      </div>
                      <p className="text-xs text-[#627D98] flex items-center gap-1 mt-1">
                        <Clock className="w-3.5 h-3.5" />
                        <span>Due Date: {bill.due_date}</span>
                        {isPaid && bill.paid_date && <span className="ml-2 text-[#2F855A]">• Paid on {bill.paid_date}</span>}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-4">
                    <div className="text-lg font-black text-[#102A43]">
                      ₹{Number(bill.amount).toLocaleString('en-IN')}
                    </div>

                    {!isPaid && (
                      <button
                        onClick={() => handlePayBill(bill.id)}
                        className="px-3.5 py-1.5 rounded-xl bg-[#2F855A] hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-500/10 flex items-center gap-1 transition-all cursor-pointer"
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>Pay Now</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="py-12 text-center text-[#627D98]">No bills found for this family.</div>
        )}
      </GlassCard>

      {/* Add Bill Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-[#0B1F33]/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white border border-[#D9E2EC] rounded-2xl p-6 relative shadow-2xl">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-[#627D98] hover:text-[#102A43] p-1 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-xl font-extrabold text-[#102A43] mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-[#D97706]" />
              <span>Record Upcoming Bill</span>
            </h3>

            {errorMsg && (
              <div className="mb-4 p-3 rounded-xl bg-[#C53030]/10 border border-[#C53030]/30 text-[#C53030] text-xs">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreateBill} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Bill Type / Service</label>
                <select
                  value={billType}
                  onChange={(e) => setBillType(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm bg-white cursor-pointer"
                >
                  <option value="Electricity">Electricity</option>
                  <option value="Internet / Fiber">Internet / Fiber</option>
                  <option value="Water">Water</option>
                  <option value="Insurance Premium">Insurance Premium</option>
                  <option value="Credit Card">Credit Card</option>
                  <option value="School / Tuition Fee">School / Tuition Fee</option>
                  <option value="Rent">Rent</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Amount (₹)</label>
                <input
                  type="number"
                  required
                  step="0.01"
                  placeholder="3200"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#627D98] mb-1">Due Date</label>
                <input
                  type="date"
                  required
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl glass-input text-sm"
                />
              </div>

              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-[#627D98] hover:text-[#102A43] cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-[#102A43] hover:bg-[#243B53] text-white shadow-lg shadow-[#102A43]/15 cursor-pointer"
                >
                  {submitting ? 'Adding...' : 'Save Bill'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Bills;
