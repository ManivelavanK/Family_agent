import { BabyProfile } from '../types/baby';
import { FeedingRecord, FeedingAnalysis } from '../types/feeding';
import { SleepLog, SleepSummary } from '../types/sleep';
import { GrowthDataPoint, GrowthSummary } from '../types/growth';
import { Vaccination } from '../types/vaccination';
import { HealthLog } from '../types/health';
import { FamilyContext } from '../types/family';

// Helper to offset dates relative to current time for realistic logs
const getOffsetDate = (daysAgo: number, timeStr = '10:00 AM') => {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  const [time, modifier] = timeStr.split(' ');
  let [hours, minutes] = time.split(':').map(Number);
  if (modifier === 'PM' && hours < 12) hours += 12;
  if (modifier === 'AM' && hours === 12) hours = 0;
  date.setHours(hours, minutes, 0, 0);
  return date.toISOString();
};

export const familyContext: FamilyContext = {
  id: 'fam_01',
  name: 'Arunachalam Family',
  members: [
    { name: 'Lakshmi', role: 'Mother', phone: '+91 98765 43210' },
    { name: 'Manoj', role: 'Father', phone: '+91 98765 43211', isEmergencyContact: true },
    { name: 'Srinivasan', role: 'Grandparent', phone: '+91 98765 43212' },
  ],
};

export const babyProfile: BabyProfile = {
  id: 'baby_01',
  name: 'Aarav',
  age: '10 Months',
  gender: 'Male',
  birthDate: '2025-09-29',
  bloodGroup: 'O Positive',
  pediatrician: {
    name: 'Dr. Priya',
    clinic: 'Little Hearts Clinic, Chennai',
    contact: '+91 94440 12345',
  },
  parents: {
    mother: 'Lakshmi',
    father: 'Manoj',
  },
  emergencyContact: {
    name: 'Manoj',
    relationship: 'Father',
    phone: '+91 98765 43211',
  },
  medicalConditions: ['None'],
  allergies: ['Peanuts'],
  currentWeight: 8.4,
  currentHeight: 72.5,
  headCircumference: 45.2,
};

export const feedingHistory: FeedingRecord[] = [
  { id: 'f_1', time: getOffsetDate(0, '09:30 AM'), type: 'Bottle', quantity: '150 ml', notes: 'Formula milk' },
  { id: 'f_2', time: getOffsetDate(0, '07:00 AM'), type: 'Breastfeeding', quantity: '15 mins' },
  { id: 'f_3', time: getOffsetDate(0, '06:00 AM'), type: 'Water', quantity: '30 ml' },
  { id: 'f_4', time: getOffsetDate(1, '09:00 PM'), type: 'Bottle', quantity: '160 ml', notes: 'Formula milk' },
  { id: 'f_5', time: getOffsetDate(1, '06:30 PM'), type: 'Solid Food', quantity: '1 bowl', notes: 'Ragi porridge' },
  { id: 'f_6', time: getOffsetDate(1, '02:00 PM'), type: 'Formula', quantity: '120 ml' },
  { id: 'f_7', time: getOffsetDate(1, '10:30 AM'), type: 'Breastfeeding', quantity: '20 mins' },
  { id: 'f_8', time: getOffsetDate(1, '07:30 AM'), type: 'Breastfeeding', quantity: '15 mins' },
];

export const feedingAnalysis: FeedingAnalysis = {
  averageFeedingInterval: '3.5 hours',
  predictedNextFeed: '1:30 PM',
  hydrationStatus: 'Normal',
  confidence: '94%',
  recommendation: 'Next feeding recommended in 2 hours based on today\'s morning formula intake.',
};

export const sleepLogs: SleepLog[] = [
  { id: 's_1', type: 'Night Sleep', startTime: getOffsetDate(1, '09:30 PM'), endTime: getOffsetDate(0, '06:00 AM'), duration: 8.5, quality: 'Excellent', notes: 'Slept soundly throughout the night.' },
  { id: 's_2', type: 'Nap', startTime: getOffsetDate(0, '11:00 AM'), endTime: getOffsetDate(0, '12:30 PM'), duration: 1.5, quality: 'Good' },
  { id: 's_3', type: 'Nap', startTime: getOffsetDate(0, '03:30 PM'), endTime: getOffsetDate(0, '04:45 PM'), duration: 1.25, quality: 'Good' },
  { id: 's_4', type: 'Night Sleep', startTime: getOffsetDate(2, '09:00 PM'), endTime: getOffsetDate(1, '05:30 AM'), duration: 8.5, quality: 'Excellent' },
  { id: 's_5', type: 'Nap', startTime: getOffsetDate(1, '10:30 AM'), endTime: getOffsetDate(1, '12:00 PM'), duration: 1.5, quality: 'Fair', notes: 'Woke up once due to noise.' },
  { id: 's_6', type: 'Nap', startTime: getOffsetDate(1, '03:00 PM'), endTime: getOffsetDate(1, '04:15 PM'), duration: 1.25, quality: 'Good' },
];

export const sleepSummary: SleepSummary = {
  todayTotal: 11.25,
  weeklyAverage: 11.45,
  qualityStatus: 'Excellent',
  insight: 'Aarav slept well last night for 8.5 hours. Sleep quality remains excellent.',
};

export const growthData: GrowthDataPoint[] = [
  { ageMonths: 5, weightKg: 6.8, heightCm: 64.0, headCircumferenceCm: 42.5, weightPercentile: 52, heightPercentile: 50 },
  { ageMonths: 6, weightKg: 7.2, heightCm: 66.0, headCircumferenceCm: 43.1, weightPercentile: 51, heightPercentile: 51 },
  { ageMonths: 7, weightKg: 7.5, heightCm: 67.5, headCircumferenceCm: 43.8, weightPercentile: 49, heightPercentile: 49 },
  { ageMonths: 8, weightKg: 7.8, heightCm: 69.2, headCircumferenceCm: 44.3, weightPercentile: 50, heightPercentile: 50 },
  { ageMonths: 9, weightKg: 8.1, heightCm: 71.0, headCircumferenceCm: 44.8, weightPercentile: 48, heightPercentile: 48 },
  { ageMonths: 10, weightKg: 8.4, heightCm: 72.5, headCircumferenceCm: 45.2, weightPercentile: 50, heightPercentile: 50 },
];

export const growthSummary: GrowthSummary = {
  currentWeight: '8.4 kg',
  monthlyGain: '+0.3 kg',
  whoPercentileText: '50th Percentile (Median)',
  insight: 'Growth follows WHO healthy percentile curve perfectly.',
};

export const vaccinations: Vaccination[] = [
  { id: 'v_1', name: 'OPV 3 & Pentavalent 3', dueDate: getOffsetDate(30), completedDate: getOffsetDate(30), status: 'Completed', doctor: 'Dr. Priya', hospital: 'Little Hearts Clinic' },
  { id: 'v_2', name: 'IPV 2', dueDate: getOffsetDate(30), completedDate: getOffsetDate(30), status: 'Completed', doctor: 'Dr. Priya', hospital: 'Little Hearts Clinic' },
  { id: 'v_3', name: 'Measles 1st Dose / MR', dueDate: getOffsetDate(-5), status: 'Upcoming', doctor: 'Dr. Priya', hospital: 'Little Hearts Clinic', notes: 'Scheduled booster and MR vaccine.' },
  { id: 'v_4', name: 'Je 1st Dose', dueDate: getOffsetDate(-25), status: 'Upcoming', doctor: 'Dr. Priya', hospital: 'Little Hearts Clinic' },
];

export const healthLogs: HealthLog[] = [
  { id: 'h_1', timestamp: getOffsetDate(0, '09:00 AM'), temperature: 36.8, weight: 8.4, medicine: 'Vitamin D3 Drops', symptoms: ['None'], doctorNotes: 'Routine morning vitamin administration.' },
  { id: 'h_2', timestamp: getOffsetDate(2, '04:00 PM'), temperature: 38.2, medicine: 'Crocin Baby Drops', symptoms: ['Mild Fever'], doctorNotes: 'Post vaccination mild fever logged. Settled in 4 hours.' },
  { id: 'h_3', timestamp: getOffsetDate(5, '11:00 AM'), symptoms: ['Stuffy Nose'], doctorNotes: 'Saline nasal drops administered.' },
];

export const alerts = [
  { id: 'a_1', type: 'danger', message: 'Vaccination Due in 5 Days', timestamp: getOffsetDate(0, '08:00 AM'), read: false, route: '/vaccinations' },
  { id: 'a_2', type: 'warning', message: 'Feeding Delayed by 30 mins', timestamp: getOffsetDate(0, '01:00 PM'), read: false, route: '/feeding' },
  { id: 'a_3', type: 'warning', message: 'Sleep Duration Below Daily Average', timestamp: getOffsetDate(1, '08:00 AM'), read: true, route: '/sleep' },
  { id: 'a_4', type: 'success', message: 'Healthy Growth Percentile Maintained', timestamp: getOffsetDate(2, '09:00 AM'), read: true, route: '/growth' },
  { id: 'a_5', type: 'danger', message: 'Fever Logged (38.2°C)', timestamp: getOffsetDate(2, '04:00 PM'), read: true, route: '/health-logs' },
];

export const db = {
  familyContext,
  babyProfile,
  feedingHistory,
  feedingAnalysis,
  sleepLogs,
  sleepSummary,
  growthData,
  growthSummary,
  vaccinations,
  healthLogs,
  alerts,
};
