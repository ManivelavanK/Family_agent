import React, { useState } from 'react';
import {
  Settings as SettingsIcon, Bell, MessageSquare, Mic, User, Phone,
  Stethoscope, Sparkles, Shield, ChevronRight, Save,
} from 'lucide-react';
import { db } from '../data/mockData';

function Section({ title, icon: Icon, children }: { title: string; icon: React.ElementType; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2 mb-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50">
          <Icon className="h-4 w-4 text-violet-600" />
        </div>
        <h3 className="text-sm font-bold text-slate-700">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function Toggle({ label, sub, defaultOn = false }: { label: string; sub?: string; defaultOn?: boolean }) {
  const [on, setOn] = useState(defaultOn);
  return (
    <div className="flex items-center justify-between py-3 border-b border-slate-50 last:border-0">
      <div>
        <p className="text-sm font-medium text-slate-700">{label}</p>
        {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
      </div>
      <button
        onClick={() => setOn(!on)}
        className={`relative inline-flex h-5 w-9 cursor-pointer rounded-full transition-colors ${on ? 'bg-violet-600' : 'bg-slate-200'}`}
      >
        <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition-transform ${on ? 'translate-x-4' : 'translate-x-0'}`} />
      </button>
    </div>
  );
}

export default function Settings() {
  const { babyProfile: p, familyContext } = db;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500 mt-0.5">Configure KinNest Baby Care Agent preferences</p>
      </div>

      {/* Baby Profile */}
      <Section title="Baby Profile" icon={User}>
        <div className="flex items-center gap-4 mb-5 p-4 rounded-xl bg-violet-50">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-violet-200 text-violet-700 font-bold text-xl">
            {p.name[0]}
          </div>
          <div>
            <p className="text-base font-bold text-slate-800">{p.name}</p>
            <p className="text-xs text-slate-500">{p.age} · {p.gender} · {p.bloodGroup}</p>
          </div>
          <button className="ml-auto text-xs font-medium text-violet-600 hover:underline flex items-center gap-1">
            Edit <ChevronRight className="h-3 w-3" />
          </button>
        </div>
        {[
          { label: 'Date of Birth', value: new Date(p.birthDate).toLocaleDateString('en-IN') },
          { label: 'Blood Group', value: p.bloodGroup },
          { label: 'Allergies', value: p.allergies.join(', ') },
        ].map(({ label, value }) => (
          <div key={label} className="flex items-center justify-between py-2.5 border-b border-slate-50 last:border-0">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="text-sm font-semibold text-slate-800">{value}</p>
          </div>
        ))}
      </Section>

      {/* Emergency Contacts */}
      <Section title="Emergency Contacts" icon={Phone}>
        {familyContext.members.map((m) => (
          <div key={m.name} className="flex items-center justify-between py-3 border-b border-slate-50 last:border-0">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 font-bold text-slate-600 text-sm">
                {m.name[0]}
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">{m.name}</p>
                <p className="text-xs text-slate-400">{m.role} · {m.phone}</p>
              </div>
            </div>
            {m.isEmergencyContact && (
              <span className="rounded-full bg-rose-100 px-2 py-0.5 text-[10px] font-bold text-rose-700">Emergency</span>
            )}
          </div>
        ))}
        <button className="mt-3 flex items-center gap-2 text-sm font-medium text-violet-600 hover:underline">
          <Phone className="h-4 w-4" />
          Add Contact
        </button>
      </Section>

      {/* Notification Preferences */}
      <Section title="Notification Preferences" icon={Bell}>
        <Toggle label="Push Notifications" sub="In-app alerts for feeding, sleep, vaccines" defaultOn={true} />
        <Toggle label="Feeding Reminders" sub="Get reminded when next feed is due" defaultOn={true} />
        <Toggle label="Sleep Alerts" sub="Alert when total sleep drops below average" defaultOn={true} />
        <Toggle label="Vaccination Reminders" sub="7 and 1 day reminders before due date" defaultOn={true} />
        <Toggle label="Growth Milestones" sub="Celebrate when Aarav hits a new milestone" defaultOn={true} />
      </Section>

      {/* WhatsApp & Voice */}
      <Section title="WhatsApp & Voice Alerts" icon={MessageSquare}>
        <Toggle label="WhatsApp Notifications" sub="Send alerts to Lakshmi's WhatsApp" defaultOn={false} />
        <Toggle label="Family WhatsApp Broadcast" sub="Share daily summaries with Arunachalam Family" defaultOn={false} />
        <Toggle label="Voice Assistant" sub="Enable voice commands via KinNest Assistant" defaultOn={false} />
        <div className="mt-4 p-3 rounded-xl bg-slate-50 flex items-start gap-2">
          <Mic className="h-4 w-4 text-slate-400 shrink-0 mt-0.5" />
          <p className="text-xs text-slate-500">Voice assistant is currently in beta. Say "Hey KinNest" to activate.</p>
        </div>
      </Section>

      {/* Pediatrician */}
      <Section title="Pediatrician Information" icon={Stethoscope}>
        {[
          { label: 'Doctor', value: p.pediatrician.name },
          { label: 'Clinic', value: p.pediatrician.clinic },
          { label: 'Contact', value: p.pediatrician.contact },
        ].map(({ label, value }) => (
          <div key={label} className="flex items-center justify-between py-2.5 border-b border-slate-50 last:border-0">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="text-sm font-semibold text-slate-800">{value}</p>
          </div>
        ))}
        <button className="mt-3 flex items-center gap-2 text-sm font-medium text-violet-600 hover:underline">
          Edit Pediatrician Info <ChevronRight className="h-3.5 w-3.5" />
        </button>
      </Section>

      {/* AI Preferences */}
      <Section title="AI Preferences" icon={Sparkles}>
        <Toggle label="AI Insights on Dashboard" sub="Show daily AI-generated health summary" defaultOn={true} />
        <Toggle label="Predictive Feeding Alerts" sub="AI predicts next feeding time" defaultOn={true} />
        <Toggle label="Sleep Pattern Analysis" sub="Weekly AI analysis of sleep quality" defaultOn={true} />
        <Toggle label="Growth Predictions" sub="AI estimates next milestone based on trend" defaultOn={true} />
        <Toggle label="Emergency AI Guidance" sub="AI provides first-aid guidance in emergencies" defaultOn={true} />
      </Section>

      {/* Privacy */}
      <Section title="Privacy & Security" icon={Shield}>
        <Toggle label="Data Encryption" sub="All baby data is encrypted at rest" defaultOn={true} />
        <Toggle label="Anonymous Analytics" sub="Help improve KinNest with usage analytics" defaultOn={false} />
        <div className="mt-3">
          <button className="w-full flex items-center justify-center gap-2 rounded-xl bg-slate-800 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 transition-colors">
            <Save className="h-4 w-4" />
            Save Settings
          </button>
        </div>
      </Section>
    </div>
  );
}
