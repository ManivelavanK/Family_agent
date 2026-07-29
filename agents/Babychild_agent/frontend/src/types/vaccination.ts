export type VaccinationStatus = 'Completed' | 'Upcoming' | 'Overdue';

export interface Vaccination {
  id: string;
  name: string;
  dueDate: string;
  completedDate?: string;
  status: VaccinationStatus;
  doctor: string;
  hospital: string;
  notes?: string;
}
