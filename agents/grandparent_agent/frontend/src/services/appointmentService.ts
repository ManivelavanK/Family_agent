import { api, isBackendUnavailable } from './api';
import { Appointment } from '../types';
import { mockAppointments } from '../data/mockData';

const getLocalAppointments = (): Appointment[] => {
  const local = localStorage.getItem('grandparent_appointments');
  if (!local) {
    localStorage.setItem('grandparent_appointments', JSON.stringify(mockAppointments));
    return mockAppointments;
  }
  return JSON.parse(local);
};

const saveLocalAppointments = (data: Appointment[]) => {
  localStorage.setItem('grandparent_appointments', JSON.stringify(data));
};

export const appointmentService = {
  getAppointments: async (): Promise<Appointment[]> => {
    try {
      const response = await api.get('/appointment/');
      return response.data.map((item: any) => {
        const dt = new Date(item.appointment_time);
        return {
          id: String(item.id),
          doctor_name: item.doctor_name,
          specialty: item.specialty,
          hospital_name: item.location || '',
          appointment_date: item.appointment_time.split('T')[0] || item.appointment_time.split(' ')[0],
          appointment_time: item.appointment_time.includes('T') 
            ? item.appointment_time.split('T')[1]?.substring(0, 5) || '10:00'
            : item.appointment_time.split(' ')[1]?.substring(0, 5) || '10:00',
          notes: item.notes || '',
          status: dt > new Date() ? 'Upcoming' : 'Completed'
        };
      });
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return getLocalAppointments();
      }
      throw e;
    }
  },
  addAppointment: async (appt: Omit<Appointment, 'id' | 'status'>): Promise<Appointment> => {
    try {
      const datetimeStr = `${appt.appointment_date}T${appt.appointment_time}:00`;
      const backendAppt = {
        doctor_name: appt.doctor_name,
        specialty: appt.specialty,
        appointment_time: datetimeStr,
        location: appt.hospital_name,
        notes: appt.notes || ''
      };
      
      const response = await api.post('/appointment/add', backendAppt);
      const item = response.data;
      
      const dt = new Date(item.appointment_time);
      return {
        id: String(item.id),
        doctor_name: item.doctor_name,
        specialty: item.specialty,
        hospital_name: item.location || '',
        appointment_date: item.appointment_time.split('T')[0] || item.appointment_time.split(' ')[0],
        appointment_time: item.appointment_time.includes('T') 
          ? item.appointment_time.split('T')[1]?.substring(0, 5) || '10:00'
          : item.appointment_time.split(' ')[1]?.substring(0, 5) || '10:00',
        notes: item.notes || '',
        status: dt > new Date() ? 'Upcoming' : 'Completed'
      };
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalAppointments();
        const newAppt: Appointment = { ...appt, id: `ap-${Date.now()}`, status: 'Upcoming' };
        current.push(newAppt);
        saveLocalAppointments(current);
        return newAppt;
      }
      throw e;
    }
  },
  updateAppointment: async (id: string, appt: Partial<Appointment>): Promise<Appointment> => {
    try {
      const backendAppt: any = {};
      if (appt.doctor_name) backendAppt.doctor_name = appt.doctor_name;
      if (appt.specialty) backendAppt.specialty = appt.specialty;
      if (appt.hospital_name) backendAppt.location = appt.hospital_name;
      if (appt.notes !== undefined) backendAppt.notes = appt.notes;
      if (appt.appointment_date && appt.appointment_time) {
        backendAppt.appointment_time = `${appt.appointment_date}T${appt.appointment_time}:00`;
      }

      const response = await api.put(`/appointment/${id}`, backendAppt);
      const item = response.data;
      
      const dt = new Date(item.appointment_time);
      return {
        id: String(item.id),
        doctor_name: item.doctor_name,
        specialty: item.specialty,
        hospital_name: item.location || '',
        appointment_date: item.appointment_time.split('T')[0] || item.appointment_time.split(' ')[0],
        appointment_time: item.appointment_time.includes('T') 
          ? item.appointment_time.split('T')[1]?.substring(0, 5) || '10:00'
          : item.appointment_time.split(' ')[1]?.substring(0, 5) || '10:00',
        notes: item.notes || '',
        status: dt > new Date() ? 'Upcoming' : 'Completed'
      };
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalAppointments();
        const idx = current.findIndex(a => a.id === id);
        if (idx !== -1) {
          current[idx] = { ...current[idx], ...appt } as Appointment;
          saveLocalAppointments(current);
          return current[idx];
        }
        throw new Error("Appointment not found");
      }
      throw e;
    }
  },
  deleteAppointment: async (id: string): Promise<void> => {
    try {
      await api.delete(`/appointment/${id}`);
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalAppointments();
        const filtered = current.filter(a => a.id !== id);
        saveLocalAppointments(filtered);
        return;
      }
      throw e;
    }
  }
};
