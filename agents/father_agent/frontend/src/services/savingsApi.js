import apiClient from './apiClient';

export const savingsApi = {
  getSavingsRecommendation: async (familyId = 1) => {
    const response = await apiClient.get('/finance/savings-recommendation', {
      params: { family_id: familyId }
    });
    return response.data;
  }
};

export default savingsApi;
