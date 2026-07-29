import { api, isBackendUnavailable } from './api';
import { Medicine, MedicineLog } from '../types';
import { mockMedicines, mockMedicineLogs } from '../data/mockData';

const parseTimeOfDay = (timeOfDay: string): string[] => {
  if (!timeOfDay) return ['08:30'];
  // If it's already a list of times like "08:30, 20:30"
  if (timeOfDay.includes(':')) {
    return timeOfDay.split(',').map(t => t.trim());
  }
  const times: string[] = [];
  const lower = timeOfDay.toLowerCase();
  if (lower.includes('morning')) times.push('08:30');
  if (lower.includes('afternoon')) times.push('13:30');
  if (lower.includes('evening')) times.push('18:30');
  if (lower.includes('night')) times.push('21:30');
  
  if (times.length === 0) times.push('08:30');
  return times;
};

const getLocalMedicines = (): Medicine[] => {
  const local = localStorage.getItem('grandparent_medicines');
  if (!local) {
    localStorage.setItem('grandparent_medicines', JSON.stringify(mockMedicines));
    return mockMedicines;
  }
  return JSON.parse(local);
};

const saveLocalMedicines = (data: Medicine[]) => {
  localStorage.setItem('grandparent_medicines', JSON.stringify(data));
};

const getLocalLogs = (): MedicineLog[] => {
  const local = localStorage.getItem('grandparent_medicine_logs');
  if (!local) {
    localStorage.setItem('grandparent_medicine_logs', JSON.stringify(mockMedicineLogs));
    return mockMedicineLogs;
  }
  return JSON.parse(local);
};

const saveLocalLogs = (data: MedicineLog[]) => {
  localStorage.setItem('grandparent_medicine_logs', JSON.stringify(data));
};

export const medicineService = {
  getMedicines: async (): Promise<Medicine[]> => {
    try {
      const response = await api.get('/medicine/');
      return response.data.map((item: any) => ({
        id: String(item.id),
        name: item.name,
        dosage: item.dosage,
        frequency: item.frequency,
        times: parseTimeOfDay(item.time_of_day),
        inventory_remaining: item.inventory_count || 0,
        inventory_warning_threshold: 10,
        notes: item.notes || '',
        last_taken: item.updated_at
      }));
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return getLocalMedicines();
      }
      throw e;
    }
  },
  addMedicine: async (med: Omit<Medicine, 'id'>): Promise<Medicine> => {
    try {
      const backendMed = {
        name: med.name,
        dosage: med.dosage,
        frequency: med.frequency,
        time_of_day: med.times.join(', '),
        inventory_count: med.inventory_remaining || 0,
        is_active: true
      };
      const response = await api.post('/medicine/add', backendMed);
      const item = response.data;
      return {
        id: String(item.id),
        name: item.name,
        dosage: item.dosage,
        frequency: item.frequency,
        times: parseTimeOfDay(item.time_of_day),
        inventory_remaining: item.inventory_count || 0,
        inventory_warning_threshold: 10,
        notes: item.notes || '',
        last_taken: item.updated_at
      };
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalMedicines();
        const newMed = { ...med, id: `m-${Date.now()}` };
        current.push(newMed);
        saveLocalMedicines(current);
        return newMed as Medicine;
      }
      throw e;
    }
  },
  updateMedicine: async (id: string, med: Partial<Medicine>): Promise<Medicine> => {
    try {
      const backendMed: any = {};
      if (med.name) backendMed.name = med.name;
      if (med.dosage) backendMed.dosage = med.dosage;
      if (med.frequency) backendMed.frequency = med.frequency;
      if (med.times) backendMed.time_of_day = med.times.join(', ');
      if (med.inventory_remaining !== undefined) backendMed.inventory_count = med.inventory_remaining;

      const response = await api.put(`/medicine/${id}/update`, backendMed);
      const item = response.data;
      return {
        id: String(item.id),
        name: item.name,
        dosage: item.dosage,
        frequency: item.frequency,
        times: parseTimeOfDay(item.time_of_day),
        inventory_remaining: item.inventory_count || 0,
        inventory_warning_threshold: 10,
        notes: item.notes || '',
        last_taken: item.updated_at
      };
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalMedicines();
        const idx = current.findIndex(m => m.id === id);
        if (idx !== -1) {
          current[idx] = { ...current[idx], ...med };
          saveLocalMedicines(current);
          return current[idx];
        }
        throw new Error("Medicine not found");
      }
      throw e;
    }
  },
  deleteMedicine: async (id: string): Promise<void> => {
    try {
      await api.delete(`/medicine/${id}`);
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalMedicines();
        const filtered = current.filter(m => m.id !== id);
        saveLocalMedicines(filtered);
        return;
      }
      throw e;
    }
  },
  takeMedicine: async (id: string): Promise<MedicineLog> => {
    try {
      const meds = await medicineService.getMedicines();
      const med = meds.find(m => String(m.id) === String(id));
      if (!med) throw new Error("Medicine not found in list");

      await api.post(`/medicine/${encodeURIComponent(med.name)}/take`);
      
      const currentMeds = getLocalMedicines();
      const idx = currentMeds.findIndex(m => m.id === id);
      let medName = med.name;
      if (idx !== -1) {
        if (currentMeds[idx].inventory_remaining > 0) {
          currentMeds[idx].inventory_remaining -= 1;
        }
        currentMeds[idx].last_taken = new Date().toISOString();
        medName = currentMeds[idx].name;
        saveLocalMedicines(currentMeds);
      }

      const logs = getLocalLogs();
      const newLog: MedicineLog = {
        id: `ml-${Date.now()}`,
        medicine_id: id,
        medicine_name: medName,
        taken_at: new Date().toISOString(),
        status: 'Taken'
      };
      logs.push(newLog);
      saveLocalLogs(logs);
      return newLog;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const currentMeds = getLocalMedicines();
        const idx = currentMeds.findIndex(m => m.id === id);
        let medName = "Unknown Medicine";
        if (idx !== -1) {
          if (currentMeds[idx].inventory_remaining > 0) {
            currentMeds[idx].inventory_remaining -= 1;
          }
          currentMeds[idx].last_taken = new Date().toISOString();
          medName = currentMeds[idx].name;
          saveLocalMedicines(currentMeds);
        }

        const logs = getLocalLogs();
        const newLog: MedicineLog = {
          id: `ml-${Date.now()}`,
          medicine_id: id,
          medicine_name: medName,
          taken_at: new Date().toISOString(),
          status: 'Taken'
        };
        logs.push(newLog);
        saveLocalLogs(logs);
        return newLog;
      }
      throw e;
    }
  },
  getLogs: async (): Promise<MedicineLog[]> => {
    return getLocalLogs();
  }
};
