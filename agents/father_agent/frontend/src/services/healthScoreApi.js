import apiClient from './apiClient';

export const healthScoreApi = {
  getHealthScore: async (familyId = 1) => {
    const response = await apiClient.get('/finance/health-score', {
      params: { family_id: familyId }
    });
    return response.data;
  }
};

export default healthScoreApi;
