import { 
  Profile, 
  Vitals, 
  Medicine, 
  MedicineLog, 
  Activity, 
  Nutrition, 
  Appointment, 
  Insurance, 
  MemoryJournal, 
  MemoryQuizResult, 
  Recommendation, 
  Reminder, 
  Forecast, 
  EmergencyAlert, 
  WhatsAppNotification 
} from '../types';

export const mockProfile: Profile = {
  name: "Gopalaswamy Srinivasan",
  age: 78,
  gender: "Male",
  medical_history: "Type-2 Diabetes, Mild Hypertension, Occasional Knee Osteoarthritis",
  allergies: "Penicillin, Sulfa drugs",
  emergency_contact: "Karthik Srinivasan (Son)",
  emergency_phone: "+91 98765 43210"
};

export const mockVitals: Vitals[] = [
  { id: "v-1", timestamp: "2026-07-28T08:00:00Z", blood_pressure: "128/82", systolic: 128, diastolic: 82, blood_sugar: 135, heart_rate: 72, temperature: 98.4, status: "Normal" },
  { id: "v-2", timestamp: "2026-07-28T12:00:00Z", blood_pressure: "130/84", systolic: 130, diastolic: 84, blood_sugar: 148, heart_rate: 76, temperature: 98.6, status: "Warning" },
  { id: "v-3", timestamp: "2026-07-28T18:00:00Z", blood_pressure: "125/80", systolic: 125, diastolic: 80, blood_sugar: 122, heart_rate: 68, temperature: 98.2, status: "Normal" },
  { id: "v-4", timestamp: "2026-07-29T08:00:00Z", blood_pressure: "127/81", systolic: 127, diastolic: 81, blood_sugar: 130, heart_rate: 70, temperature: 98.4, status: "Normal" }
];

export const mockMedicines: Medicine[] = [
  {
    id: "m-1",
    name: "Metformin",
    dosage: "500mg",
    frequency: "Daily",
    times: ["08:30", "20:30"],
    inventory_remaining: 18,
    inventory_warning_threshold: 10,
    notes: "Take after meals to prevent stomach upset.",
    last_taken: "2026-07-29T08:35:00Z"
  },
  {
    id: "m-2",
    name: "Amlodipine",
    dosage: "5mg",
    frequency: "Daily",
    times: ["09:00"],
    inventory_remaining: 4,
    inventory_warning_threshold: 7,
    notes: "For blood pressure management. Best in morning.",
    last_taken: "2026-07-29T09:05:00Z"
  },
  {
    id: "m-3",
    name: "Glimepiride",
    dosage: "2mg",
    frequency: "Daily",
    times: ["08:30"],
    inventory_remaining: 25,
    inventory_warning_threshold: 8,
    notes: "For diabetes control. Watch out for hypoglycemia.",
    last_taken: "2026-07-29T08:32:00Z"
  }
];

export const mockMedicineLogs: MedicineLog[] = [
  { id: "ml-1", medicine_id: "m-1", medicine_name: "Metformin", taken_at: "2026-07-28T08:32:00Z", status: "Taken" },
  { id: "ml-2", medicine_id: "m-2", medicine_name: "Amlodipine", taken_at: "2026-07-28T09:02:00Z", status: "Taken" },
  { id: "ml-3", medicine_id: "m-1", medicine_name: "Metformin", taken_at: "2026-07-28T20:38:00Z", status: "Taken" },
  { id: "ml-4", medicine_id: "m-1", medicine_name: "Metformin", taken_at: "2026-07-29T08:35:00Z", status: "Taken" },
  { id: "ml-5", medicine_id: "m-2", medicine_name: "Amlodipine", taken_at: "2026-07-29T09:05:00Z", status: "Taken" },
  { id: "ml-6", medicine_id: "m-3", medicine_name: "Glimepiride", taken_at: "2026-07-29T08:32:00Z", status: "Taken" }
];

export const mockActivities: Activity[] = [
  { id: "a-1", date: "2026-07-25", steps: 4200, sleep_hours: 6.5, exercise_type: "Walking", exercise_duration_minutes: 20, calories_burned: 150 },
  { id: "a-2", date: "2026-07-26", steps: 5100, sleep_hours: 7.0, exercise_type: "Walking", exercise_duration_minutes: 30, calories_burned: 180 },
  { id: "a-3", date: "2026-07-27", steps: 3800, sleep_hours: 5.5, exercise_type: "Yoga", exercise_duration_minutes: 15, calories_burned: 90 },
  { id: "a-4", date: "2026-07-28", steps: 6000, sleep_hours: 7.2, exercise_type: "Walking", exercise_duration_minutes: 40, calories_burned: 220 },
  { id: "a-5", date: "2026-07-29", steps: 3200, sleep_hours: 6.8, exercise_type: "Yoga", exercise_duration_minutes: 20, calories_burned: 110 }
];

export const mockNutrition: Nutrition[] = [
  { id: "n-1", date: "2026-07-26", meals: ["Ragi Kanji, Papaya", "Brown Rice, Sambar, Cabbage Poriyal", "Green Tea, Roasted Chana", "Broken Wheat Upma, Cucumber Salad"], calories_consumed: 1650, water_intake_ml: 1800, food_notes: "Felt full today. Kept spices low." },
  { id: "n-2", date: "2026-07-27", meals: ["Idli (2), Coconut Chutney", "Quinoa Salad, Buttermilk", "Sprout Salad", "Chapati (2), Dal, Ladies Finger"], calories_consumed: 1720, water_intake_ml: 2000, food_notes: "Hydration was good. Sugar was stable." },
  { id: "n-3", date: "2026-07-28", meals: ["Oats Porridge with Almonds", "Millet Biryani, Cucumber Raitha", "Apple slices", "Dosa (2), Tomato Chutney"], calories_consumed: 1800, water_intake_ml: 2200, food_notes: "Post-lunch walk helped digestion." },
  { id: "n-4", date: "2026-07-29", meals: ["Ragi Roti, Mint Chutney", "Brown Rice, Rasam, Beans Palya", "Green Tea"], calories_consumed: 1100, water_intake_ml: 1200, food_notes: "Today's summary in-progress." }
];

export const mockAppointments: Appointment[] = [
  { id: "ap-1", doctor_name: "Dr. Srinivasa Raghavan", specialty: "Diabetologist & Endocrinologist", hospital_name: "Apollo Hospitals, Chennai", appointment_date: "2026-08-05", appointment_time: "10:30", notes: "Routine HbA1c review. Carry latest fasting and post-prandial blood sugar logs.", status: "Upcoming" },
  { id: "ap-2", doctor_name: "Dr. K. Ganesan", specialty: "Cardiologist", hospital_name: "Kauvery Hospital", appointment_date: "2026-08-18", appointment_time: "16:00", notes: "Echocardiogram and BP checkup.", status: "Upcoming" },
  { id: "ap-3", doctor_name: "Dr. R. Kamala", specialty: "Orthopedic Surgeon", hospital_name: "Apollo Joint Clinic", appointment_date: "2026-07-15", appointment_time: "11:00", notes: "Knee osteoarthritis follow-up. Prescribed gel application and physical therapy.", status: "Completed" }
];

export const mockInsurance: Insurance[] = [
  { id: "i-1", provider: "Star Health & Allied Insurance", policy_number: "SH-89302-2026", coverage_details: "Senior Citizens Red Carpet Policy. 100% hospitalization cover up to 5 Lakhs. Covers pre-existing diabetes and hypertension after 1 year.", expiry_date: "2027-03-15", contact_number: "1800-425-2255" }
];

export const mockMemoryJournals: MemoryJournal[] = [
  { id: "j-1", date: "2026-07-26", title: "Morning walk with my grandson", content: "Today Karthik accompanied me to the neighborhood park. We saw a pair of beautiful green parrots nesting on the old Banyan tree. I told him stories about my childhood visits to our ancestral village in Thanjavur.", mood: "Joyful", cognitive_score: 85 },
  { id: "j-2", date: "2026-07-27", title: "Remembered the school prayer song", content: "Woke up with the melody of the prayer song we sang at High School. Sang the first two stanzas correctly to my wife. It felt wonderful to retrieve a memory from almost 65 years ago.", mood: "Peaceful", cognitive_score: 90 },
  { id: "j-3", date: "2026-07-28", title: "Misplaced my reading spectacles", content: "Spent 30 minutes looking for my reading glasses. Eventually found them on the dining cabinet shelf under the newspaper. Need to remember to put them in the designated blue box on my side table.", mood: "Anxious", cognitive_score: 70 }
];

export const mockMemoryQuizResults: MemoryQuizResult[] = [
  { id: "q-1", date: "2026-07-25", score: 90, quiz_type: "Visual Recognition & Names", notes: "Identified family members and recalled past events correctly. Mild delay in word recall." },
  { id: "q-2", date: "2026-07-27", score: 80, quiz_type: "Number Sequences & Spacial Memory", notes: "Missed one card pair match. Good response speed." },
  { id: "q-3", date: "2026-07-29", score: 100, quiz_type: "Daily Routine Trivia", notes: "Recalled morning medicine names, today's day/date, and grandson's phone prefix accurately." }
];

export const mockRecommendations: Recommendation[] = [
  { id: "r-1", category: "Health Warning", title: "Post-lunch sugar surge detected", content: "Your blood sugar rose to 148 mg/dL post-lunch yesterday. Consider replacing white rice with brown rice/millets and reducing the quantity by 20%.", priority: "High", reason: "Blood sugar readings consistently > 140 mg/dL", created_at: "2026-07-28T13:00:00Z" },
  { id: "r-2", category: "Hydration", title: "Increase morning fluid intake", content: "Water intake logs show you consume less than 500ml before noon. Try drinking two full copper cups of warm water right after waking up.", priority: "Medium", reason: "Improves digestion and maintains blood pressure stability", created_at: "2026-07-29T07:00:00Z" },
  { id: "r-3", category: "Exercise", title: "Low-impact knee stretches recommended", content: "Since your steps are lower today due to knee stiffness, perform 10 repetitions of seated quadriceps sets to strengthen the knee joint.", priority: "Medium", reason: "Prevents joint lock and improves blood circulation", created_at: "2026-07-29T10:00:00Z" },
  { id: "r-4", category: "Sleep", title: "Maintain a stable sleep schedule", content: "Sleep tracking showed under 6 hours on July 27. Try taking a warm bath or listening to MS Subbulakshmi devotional songs 20 minutes before bedtime.", priority: "Low", reason: "Sleep duration strongly correlates with cognitive scores", created_at: "2026-07-28T22:00:00Z" }
];

export const mockReminders: Reminder[] = [
  { id: "rem-1", title: "Take Amlodipine (BP medicine)", reminder_time: "09:00", category: "Medicine", is_active: true, recurring: true, completed: true },
  { id: "rem-2", title: "Drink coconut water", reminder_time: "11:30", category: "Hydration", is_active: true, recurring: true, completed: false },
  { id: "rem-3", title: "Evening walk (30 mins)", reminder_time: "17:30", category: "Activity", is_active: true, recurring: true, completed: false },
  { id: "rem-4", title: "Take Metformin (Sugar medicine)", reminder_time: "20:30", category: "Medicine", is_active: true, recurring: true, completed: false }
];

export const mockForecasts: Forecast[] = [
  { date: "2026-07-30", predicted_systolic: 126, predicted_diastolic: 81, predicted_blood_sugar: 132, confidence_score: 88 },
  { date: "2026-07-31", predicted_systolic: 125, predicted_diastolic: 80, predicted_blood_sugar: 129, confidence_score: 85 },
  { date: "2026-08-01", predicted_systolic: 127, predicted_diastolic: 82, predicted_blood_sugar: 135, confidence_score: 82 },
  { date: "2026-08-02", predicted_systolic: 128, predicted_diastolic: 82, predicted_blood_sugar: 138, confidence_score: 79 }
];

export const mockEmergencyAlerts: EmergencyAlert[] = [
  { id: "sos-1", timestamp: "2026-07-20T10:15:00Z", status: "Resolved", message: "SOS Button pressed on smartwatch. Fall detected alert sent to contacts.", contact_notified: "Karthik Srinivasan (Son)" },
  { id: "sos-2", timestamp: "2026-07-28T16:45:00Z", status: "Resolved", message: "Manual SOS triggered. False alarm - grandfather was demonstrating safety features.", contact_notified: "All primary emergency contacts" }
];

export const mockWhatsAppNotifications: WhatsAppNotification[] = [
  { id: "wa-1", timestamp: "2026-07-29T08:30:00Z", recipient_phone: "+91 98765 43210", message_type: "Reminder", message_content: "Good morning! Please take your Metformin and Glimepiride after breakfast.", status: "Delivered" },
  { id: "wa-2", timestamp: "2026-07-29T09:00:00Z", recipient_phone: "+91 98765 43210", message_type: "Reminder", message_content: "Time for your morning BP medicine: Amlodipine 5mg.", status: "Delivered" },
  { id: "wa-3", timestamp: "2026-07-29T10:15:00Z", recipient_phone: "+91 98765 43210", message_type: "Alert", message_content: "CRITICAL: Daily Water Intake is below target for this hour. Please drink 2 glasses of water now.", status: "Sent" }
];
