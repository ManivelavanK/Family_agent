// Profile types
export interface Profile {
  name: string;
  age: number;
  gender: string;
  medical_history: string; // comma-separated or text
  allergies: string; // comma-separated or text
  emergency_contact: string;
  emergency_phone: string;
}

// Health Vitals types
export interface Vitals {
  id?: string;
  timestamp?: string;
  blood_pressure: string; // e.g. "120/80"
  systolic?: number;
  diastolic?: number;
  blood_sugar: number; // mg/dL
  heart_rate: number; // bpm
  temperature: number; // Fahrenheit
  status?: string; // "Normal", "Warning", "Critical"
}

// Medicine types
export interface Medicine {
  id: string;
  name: string;
  dosage: string;
  frequency: string; // "Daily", "Weekly", etc.
  times: string[]; // e.g. ["09:00", "21:00"]
  inventory_remaining: number;
  inventory_warning_threshold: number;
  notes?: string;
  last_taken?: string; // ISO string or time taken
}

export interface MedicineLog {
  id: string;
  medicine_id: string;
  medicine_name: string;
  taken_at: string;
  status: 'Taken' | 'Missed' | 'Scheduled';
}

// Activity types
export interface Activity {
  id?: string;
  date: string;
  steps: number;
  sleep_hours: number;
  exercise_type: string;
  exercise_duration_minutes: number;
  calories_burned?: number;
}

// Nutrition types
export interface Nutrition {
  id?: string;
  date: string;
  meals: string[]; // e.g. ["Oatmeal & Bananas", "Rice & Sambar"]
  calories_consumed: number;
  water_intake_ml: number;
  food_notes?: string;
}

// Appointment types
export interface Appointment {
  id: string;
  doctor_name: string;
  specialty: string;
  hospital_name: string;
  appointment_date: string; // YYYY-MM-DD
  appointment_time: string; // HH:MM
  notes?: string;
  status: 'Upcoming' | 'Completed' | 'Cancelled';
}

// Insurance types
export interface Insurance {
  id: string;
  provider: string;
  policy_number: string;
  coverage_details: string;
  expiry_date: string; // YYYY-MM-DD
  contact_number: string;
}

// Memory Care types
export interface MemoryJournal {
  id: string;
  date: string;
  title: string;
  content: string;
  mood?: string;
  cognitive_score?: number; // Calculated by LLM or quiz
}

export interface MemoryQuizResult {
  id: string;
  date: string;
  score: number; // e.g. 8/10 -> 80
  quiz_type: string;
  notes?: string;
}

// AI Recommendation types
export interface Recommendation {
  id: string;
  category: 'Diet' | 'Exercise' | 'Medicine' | 'Hydration' | 'Sleep' | 'Health Warning';
  title: string;
  content: string;
  priority: 'Low' | 'Medium' | 'High';
  reason: string;
  created_at: string;
}

// Reminder types
export interface Reminder {
  id: string;
  title: string;
  reminder_time: string; // HH:MM or ISO
  category: string; // "Medicine", "Appointment", "Activity", "Other"
  is_active: boolean;
  recurring: boolean;
  completed?: boolean;
}

// Forecast types
export interface Forecast {
  date: string;
  predicted_systolic: number;
  predicted_diastolic: number;
  predicted_blood_sugar: number;
  confidence_score: number;
}

// Emergency SOS types
export interface EmergencyAlert {
  id: string;
  timestamp: string;
  status: 'Triggered' | 'Resolved' | 'Escalated';
  message: string;
  contact_notified: string;
}

// Voice Assistant types
export interface VoiceMessage {
  sender: 'user' | 'assistant';
  text: string;
  audio_url?: string;
  timestamp: string;
  intent?: string;
}

// WhatsApp Notification types
export interface WhatsAppNotification {
  id: string;
  timestamp: string;
  recipient_phone: string;
  message_type: 'Alert' | 'Reminder' | 'Update' | 'Ad-hoc';
  message_content: string;
  status: 'Sent' | 'Delivered' | 'Failed' | 'Pending';
}
