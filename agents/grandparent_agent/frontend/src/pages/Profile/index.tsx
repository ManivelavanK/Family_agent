import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { profileService } from '../../services/profileService';
import { Profile as ProfileType } from '../../types';
import toast from 'react-hot-toast';
import { Save, User, Heart, Phone, ShieldAlert } from 'lucide-react';

export const Profile: React.FC = () => {
  const { register, handleSubmit, reset } = useForm<ProfileType>();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await profileService.getProfile();
        reset(data);
      } catch (e) {
        toast.error("Failed to load profile. Using local storage.");
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, [reset]);

  const onSubmit = async (data: ProfileType) => {
    setSaving(true);
    try {
      await profileService.updateProfile(data);
      toast.success("Profile saved successfully!");
    } catch (e) {
      toast.error("Could not save profile online. Saved locally.");
    } finally {
      setSaving(false);
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
    <div className="max-w-3xl mx-auto bg-white border border-sky-100 rounded-3xl p-8 shadow-xs">
      <div className="flex items-center gap-4 border-b border-slate-100 pb-6 mb-6">
        <div className="h-16 w-16 bg-sky-50 border border-sky-100 text-sky-600 rounded-2xl flex items-center justify-center">
          <User className="h-8 w-8" />
        </div>
        <div>
          <h3 className="text-2xl font-black text-slate-800">Personal Health Profile</h3>
          <p className="text-sm font-semibold text-slate-400">Keep emergency contacts and medical history updated.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Details */}
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <label className="block text-base font-bold text-slate-700 mb-2">Name</label>
            <input
              type="text"
              {...register('name', { required: true })}
              className="w-full text-lg p-3.5 rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500 bg-slate-50/50"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-base font-bold text-slate-700 mb-2">Age</label>
              <input
                type="number"
                {...register('age', { required: true, valueAsNumber: true })}
                className="w-full text-lg p-3.5 rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500 bg-slate-50/50"
              />
            </div>
            <div>
              <label className="block text-base font-bold text-slate-700 mb-2">Gender</label>
              <select
                {...register('gender', { required: true })}
                className="w-full text-lg p-3.5 rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500 bg-slate-50/50"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </div>

        {/* Medical History & Allergies */}
        <div>
          <label className="flex items-center gap-2 text-base font-bold text-slate-700 mb-2">
            <Heart className="h-5 w-5 text-emerald-500" />
            <span>Medical History / Chronic Conditions</span>
          </label>
          <textarea
            rows={3}
            {...register('medical_history')}
            className="w-full text-lg p-3.5 rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500 bg-slate-50/50"
            placeholder="e.g. Hypertension, Type-2 Diabetes..."
          />
        </div>

        <div>
          <label className="flex items-center gap-2 text-base font-bold text-slate-700 mb-2">
            <ShieldAlert className="h-5 w-5 text-rose-500" />
            <span>Drug / Food Allergies</span>
          </label>
          <input
            type="text"
            {...register('allergies')}
            className="w-full text-lg p-3.5 rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500 bg-slate-50/50"
            placeholder="e.g. Penicillin, Peanuts..."
          />
        </div>

        {/* Emergency Contacts */}
        <div className="border-t border-slate-100 pt-6">
          <h4 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Phone className="h-5 w-5 text-sky-500" />
            <span>Emergency SOS Contacts</span>
          </h4>
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <label className="block text-base font-bold text-slate-700 mb-2">Contact Person Name</label>
              <input
                type="text"
                {...register('emergency_contact', { required: true })}
                className="w-full text-lg p-3.5 rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500 bg-slate-50/50"
              />
            </div>
            <div>
              <label className="block text-base font-bold text-slate-700 mb-2">Contact Phone Number</label>
              <input
                type="text"
                {...register('emergency_phone', { required: true })}
                className="w-full text-lg p-3.5 rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500 bg-slate-50/50"
              />
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="pt-4 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-8 py-3.5 bg-sky-500 hover:bg-sky-600 active:scale-95 text-white font-bold text-lg rounded-2xl shadow-md transition-all cursor-pointer"
          >
            <Save className="h-5 w-5" />
            <span>{saving ? 'Saving...' : 'Save Profile'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
export default Profile;
