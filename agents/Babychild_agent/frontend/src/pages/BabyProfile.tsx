import React from 'react';
import { db } from '../data/mockData';
import {
  Baby, Phone, Stethoscope, Users, AlertCircle,
  Weight, Ruler, Heart, Droplets,
} from 'lucide-react';

function ProfileRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between border-b border-slate-50 py-3 last:border-0">
      <span className="text-sm text-slate-500 font-medium">{label}</span>
      <span className="text-sm font-semibold text-slate-800 text-right max-w-[55%]">{value}</span>
    </div>
  );
}

export default function BabyProfile() {
  const { babyProfile: p, familyContext } = db;

  const ageMonths = 10;
  const ageDays = Math.floor(
    (Date.now() - new Date(p.birthDate).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <div className="space-y-6">
      {/* Hero Profile Card */}
      <div className="overflow-hidden rounded-2xl bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-600 p-6 text-white shadow-lg shadow-violet-200">
        <div className="flex items-center gap-6">
          {/* Avatar */}
          <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-full bg-white/20 text-white text-4xl font-bold shadow-lg backdrop-blur-sm border-2 border-white/30">
            {p.name[0]}
          </div>
          <div>
            <p className="text-sm font-medium text-white/70 mb-0.5">Baby Profile</p>
            <h2 className="text-3xl font-bold text-white">{p.name}</h2>
            <p className="text-base text-white/80 mt-1">{p.age} Old · {p.gender} · {p.bloodGroup}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="rounded-full bg-white/20 px-3 py-1 text-xs font-medium text-white">
                Born {new Date(p.birthDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
              </span>
              <span className="rounded-full bg-white/20 px-3 py-1 text-xs font-medium text-white">
                {ageDays} days old
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { icon: Weight, label: 'Weight', value: `${p.currentWeight} kg`, bg: 'bg-violet-50', color: 'text-violet-600' },
          { icon: Ruler, label: 'Height', value: `${p.currentHeight} cm`, bg: 'bg-blue-50', color: 'text-blue-600' },
          { icon: Baby, label: 'Head Circ.', value: `${p.headCircumference} cm`, bg: 'bg-indigo-50', color: 'text-indigo-600' },
        ].map(({ icon: Icon, label, value, bg, color }) => (
          <div key={label} className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm text-center">
            <div className={`mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-xl ${bg}`}>
              <Icon className={`h-5 w-5 ${color}`} />
            </div>
            <p className="text-xs text-slate-400 font-medium">{label}</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{value}</p>
          </div>
        ))}
      </div>

      {/* Info Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Personal Info */}
        <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Baby className="h-4 w-4 text-violet-600" />
            <h3 className="text-sm font-bold text-slate-700">Personal Information</h3>
          </div>
          <ProfileRow label="Full Name" value={p.name} />
          <ProfileRow label="Age" value={p.age} />
          <ProfileRow label="Gender" value={p.gender} />
          <ProfileRow label="Date of Birth" value={new Date(p.birthDate).toLocaleDateString('en-IN')} />
          <ProfileRow label="Blood Group" value={p.bloodGroup} />
        </div>

        {/* Pediatrician */}
        <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Stethoscope className="h-4 w-4 text-violet-600" />
            <h3 className="text-sm font-bold text-slate-700">Pediatrician</h3>
          </div>
          <ProfileRow label="Doctor" value={p.pediatrician.name} />
          <ProfileRow label="Clinic" value={p.pediatrician.clinic} />
          <ProfileRow label="Contact" value={p.pediatrician.contact} />
          <div className="mt-4">
            <a
              href={`tel:${p.pediatrician.contact}`}
              className="flex items-center justify-center gap-2 w-full rounded-xl bg-violet-600 py-2.5 text-sm font-semibold text-white hover:bg-violet-700 transition-colors"
            >
              <Phone className="h-4 w-4" />
              Call Dr. Priya
            </a>
          </div>
        </div>

        {/* Family Members */}
        <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Users className="h-4 w-4 text-violet-600" />
            <h3 className="text-sm font-bold text-slate-700">Family</h3>
          </div>
          {familyContext.members.map((m) => (
            <div key={m.name} className="flex items-center justify-between py-3 border-b border-slate-50 last:border-0">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-violet-100 text-violet-700 font-bold text-sm">
                  {m.name[0]}
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-800">{m.name}</p>
                  <p className="text-xs text-slate-400">{m.role}</p>
                </div>
              </div>
              {m.phone && (
                <a href={`tel:${m.phone}`} className="text-xs font-medium text-violet-600 hover:underline">
                  Call
                </a>
              )}
            </div>
          ))}
        </div>

        {/* Medical Info */}
        <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Heart className="h-4 w-4 text-rose-500" />
            <h3 className="text-sm font-bold text-slate-700">Medical Information</h3>
          </div>

          <div className="mb-4">
            <p className="text-xs font-medium text-slate-400 mb-2 uppercase tracking-wide">Conditions</p>
            <div className="flex flex-wrap gap-2">
              {p.medicalConditions.map((c) => (
                <span key={c} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  {c}
                </span>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-xs font-medium text-slate-400 mb-2 uppercase tracking-wide">Allergies</p>
            <div className="flex flex-wrap gap-2">
              {p.allergies.map((a) => (
                <span key={a} className="flex items-center gap-1 rounded-full bg-rose-50 px-3 py-1 text-xs font-medium text-rose-600 border border-rose-100">
                  <AlertCircle className="h-3 w-3" />
                  {a}
                </span>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-medium text-slate-400 mb-2 uppercase tracking-wide">Emergency Contact</p>
            <div className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-3">
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-emerald-600" />
                <div>
                  <p className="text-sm font-semibold text-slate-800">{p.emergencyContact.name}</p>
                  <p className="text-xs text-slate-400">{p.emergencyContact.relationship} · {p.emergencyContact.phone}</p>
                </div>
              </div>
              <Droplets className="h-4 w-4 text-rose-400" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
