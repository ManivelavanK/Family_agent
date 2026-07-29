import React, { useEffect, useState } from 'react';
import { notificationService } from '../../services/notificationService';
import { WhatsAppNotification } from '../../types';
import { MessageSquare, Send, CheckCircle, XCircle, Clock, Phone } from 'lucide-react';
import toast from 'react-hot-toast';
import StatusBadge from '../../components/common/StatusBadge';

const TEMPLATES = [
  { id: 'morning_meds', label: '💊 Morning Medicine Reminder', preview: 'Good morning! Please take your Metformin and Glimepiride after breakfast.' },
  { id: 'bp_alert', label: '❤️ Blood Pressure Alert', preview: 'Your BP reading today was higher than normal. Please rest and avoid salty food.' },
  { id: 'appointment', label: '📅 Doctor Appointment Reminder', preview: 'Reminder: You have a doctor appointment tomorrow. Please carry your reports.' },
  { id: 'water', label: '💧 Hydration Reminder', preview: 'You have not logged your water intake. Please drink 2 glasses of water now.' },
  { id: 'sos_followup', label: '🚨 Post-SOS Follow-up', preview: 'Elder is safe. The earlier emergency alert has been resolved by the family.' },
  { id: 'custom', label: '✏️ Custom Message', preview: '' },
];

export const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<WhatsAppNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(TEMPLATES[0].id);
  const [customMessage, setCustomMessage] = useState('');
  const [recipientPhone, setRecipientPhone] = useState('+91 98765 43210');

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await notificationService.getNotifications();
      setNotifications(data);
    } catch (e) {
      toast.error('Failed to load notification history.');
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    const template = TEMPLATES.find(t => t.id === selectedTemplate);
    const messageContent = selectedTemplate === 'custom' ? customMessage : template?.preview || '';
    if (!messageContent.trim()) {
      toast.error('Please enter a message or select a valid template.');
      return;
    }
    setSending(true);
    try {
      await notificationService.sendNotification(recipientPhone, selectedTemplate, messageContent);
      toast.success('✅ WhatsApp message sent successfully!');
      loadNotifications();
      setCustomMessage('');
    } catch (e) {
      toast.error('Failed to send message.');
    } finally {
      setSending(false);
    }
  };

  const getStatusIcon = (status: string) => {
    if (status === 'Delivered') return <CheckCircle className="h-4 w-4 text-emerald-500" />;
    if (status === 'Failed') return <XCircle className="h-4 w-4 text-rose-500" />;
    return <Clock className="h-4 w-4 text-amber-500" />;
  };

  const selectedTemplateData = TEMPLATES.find(t => t.id === selectedTemplate);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4 bg-gradient-to-r from-emerald-50 to-sky-50 border border-emerald-100 rounded-2xl p-6">
        <div className="p-3 bg-emerald-500 text-white rounded-xl">
          <MessageSquare className="h-6 w-6" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-slate-800">WhatsApp Health Notifications</h3>
          <p className="text-sm font-semibold text-slate-400">Send medicine, appointment, and emergency reminders to family contacts via WhatsApp.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Send Notification Panel */}
        <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Send className="h-5 w-5 text-emerald-500" />
            <span>Send Notification</span>
          </h4>

          <div className="space-y-4">
            {/* Recipient */}
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1 flex items-center gap-1.5">
                <Phone className="h-4 w-4" />
                <span>Recipient Phone Number</span>
              </label>
              <input
                type="text"
                value={recipientPhone}
                onChange={e => setRecipientPhone(e.target.value)}
                className="w-full text-base p-3 rounded-xl border border-slate-200 focus:outline-none focus:border-emerald-400"
                placeholder="+91 98765 43210"
              />
            </div>

            {/* Template Selector */}
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Select Message Template</label>
              <div className="space-y-2">
                {TEMPLATES.map(template => (
                  <label
                    key={template.id}
                    className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                      selectedTemplate === template.id
                        ? 'border-emerald-400 bg-emerald-50'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="template"
                      value={template.id}
                      checked={selectedTemplate === template.id}
                      onChange={e => setSelectedTemplate(e.target.value)}
                      className="text-emerald-500 h-4 w-4"
                    />
                    <span className="text-sm font-bold text-slate-700">{template.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Preview or Custom Message */}
            {selectedTemplate === 'custom' ? (
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-1">Custom Message</label>
                <textarea
                  rows={3}
                  value={customMessage}
                  onChange={e => setCustomMessage(e.target.value)}
                  className="w-full text-base p-3 rounded-xl border border-slate-200 focus:outline-none focus:border-emerald-400"
                  placeholder="Type your custom WhatsApp message here..."
                />
              </div>
            ) : selectedTemplateData?.preview ? (
              <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4">
                <span className="text-xs font-bold text-emerald-500 uppercase tracking-wider">Message Preview</span>
                <p className="text-sm font-semibold text-slate-700 mt-1.5 leading-relaxed">{selectedTemplateData.preview}</p>
              </div>
            ) : null}

            <button
              onClick={handleSend}
              disabled={sending}
              className="w-full flex items-center justify-center gap-2 px-5 py-3.5 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold text-base rounded-xl transition-all cursor-pointer shadow-sm"
            >
              <Send className="h-5 w-5" />
              <span>{sending ? 'Sending...' : 'Send WhatsApp Message'}</span>
            </button>
          </div>
        </div>

        {/* Notification History */}
        <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-xs">
          <h4 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Clock className="h-5 w-5 text-slate-400" />
            <span>Message History</span>
          </h4>

          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-4 border-emerald-500 border-t-transparent" />
            </div>
          ) : (
            <div className="space-y-3 overflow-y-auto max-h-[480px] pr-1">
              {notifications.map(notif => (
                <div key={notif.id} className="border border-slate-100 rounded-xl p-4 hover:border-slate-200 transition-colors">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-1.5">
                      {getStatusIcon(notif.status)}
                      <span className="text-xs font-bold text-slate-500 uppercase">{notif.message_type}</span>
                    </div>
                    <StatusBadge status={notif.status} />
                  </div>
                  <p className="text-sm font-semibold text-slate-700 leading-relaxed mb-2">{notif.message_content}</p>
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
                    <span>To: {notif.recipient_phone}</span>
                    <span>{new Date(notif.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              ))}
              {notifications.length === 0 && (
                <p className="text-center py-6 text-slate-400 font-medium">No messages sent yet.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default Notifications;
