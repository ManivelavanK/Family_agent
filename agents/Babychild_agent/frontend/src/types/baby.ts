export interface BabyProfile {
  id: string;
  name: string;
  photoUrl?: string;
  age: string; // e.g. "10 Months"
  gender: string;
  birthDate: string;
  bloodGroup: string;
  pediatrician: {
    name: string;
    clinic: string;
    contact: string;
  };
  parents: {
    mother: string;
    father: string;
  };
  emergencyContact: {
    name: string;
    relationship: string;
    phone: string;
  };
  medicalConditions: string[];
  allergies: string[];
  currentWeight: number; // in kg
  currentHeight: number; // in cm
  headCircumference?: number; // in cm
}
