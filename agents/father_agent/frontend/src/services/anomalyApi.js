import apiClient from './apiClient';

export const anomalyApi = {
  getAnomalies: async (familyId = 1) => {
    const response = await apiClient.get(`/finance/anomalies/${familyId}`);
    return response.data;
  }
};

export default anomalyApi;
