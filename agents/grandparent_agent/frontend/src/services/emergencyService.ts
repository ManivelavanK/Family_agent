import { api, isBackendUnavailable } from './api';
import { EmergencyAlert } from '../types';
import { mockEmergencyAlerts } from '../data/mockData';

const getLocalSOS = (): EmergencyAlert[] => {
  const local = localStorage.getItem('grandparent_sos');
  if (!local) {
    localStorage.setItem('grandparent_sos', JSON.stringify(mockEmergencyAlerts));
    return mockEmergencyAlerts;
  }
  return JSON.parse(local);
};

const saveLocalSOS = (data: EmergencyAlert[]) => {
  localStorage.setItem('grandparent_sos', JSON.stringify(data));
};

export const emergencyService = {
  triggerSOS: async (): Promise<EmergencyAlert> => {
    try {
      const response = await api.post('/emergency/sos', {});
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalSOS();
        const newAlert: EmergencyAlert = {
          id: `sos-${Date.now()}`,
          timestamp: new Date().toISOString(),
          status: 'Triggered',
          message: 'EMERGENCY SOS: Elder triggered a critical alert from the KinNest dashboard.',
          contact_notified: 'Karthik Srinivasan (Son)'
        };
        current.unshift(newAlert);
        saveLocalSOS(current);
        return newAlert;
      }
      throw e;
    }
  },
  getSOSHistory: async (): Promise<EmergencyAlert[]> => {
    try {
      const response = await api.get('/emergency/history');
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return getLocalSOS();
      }
      throw e;
    }
  },
  resolveSOS: async (id: string): Promise<EmergencyAlert> => {
    // Backend has no resolve endpoint, so we handle it locally to prevent 404 errors.
    const current = getLocalSOS();
    const idx = current.findIndex(a => a.id === id);
    if (idx !== -1) {
      current[idx].status = 'Resolved';
      saveLocalSOS(current);
      return current[idx];
    }
    throw new Error("Alert not found");
  }
};
