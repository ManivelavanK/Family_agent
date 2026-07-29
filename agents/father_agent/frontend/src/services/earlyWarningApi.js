import apiClient from './apiClient';

export const earlyWarningApi = {
  getEarlyWarnings: async (familyId = 1) => {
    const response = await apiClient.get(`/finance/early-warnings/${familyId}`);
    return response.data;
  }
};

export default earlyWarningApi;
