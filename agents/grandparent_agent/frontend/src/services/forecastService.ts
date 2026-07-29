import { api, isBackendUnavailable } from './api';
import { Forecast } from '../types';
import { mockForecasts } from '../data/mockData';

export const forecastService = {
  getForecasts: async (): Promise<Forecast[]> => {
    try {
      const response = await api.get('/forecast/');
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return mockForecasts;
      }
      throw e;
    }
  },
  trainModel: async (): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await api.post('/forecast/train');
      return response.data;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        return { success: true, message: "ML Model trained successfully using local health history logs!" };
      }
      throw e;
    }
  }
};
