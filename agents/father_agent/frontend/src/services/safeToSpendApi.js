import apiClient from './apiClient';

export const safeToSpendApi = {
  getSafeToSpend: async (familyId = 1) => {
    const response = await apiClient.get(`/finance/safe-to-spend/${familyId}`);
    return response.data;
  },

  checkAffordability: async (familyId = 1, requestedAmount = 0) => {
    const response = await apiClient.post('/api/v1/family/affordability-check', {
      family_id: Number(familyId),
      requested_amount: Number(requestedAmount)
    });
    return response.data;
  }
};

export default safeToSpendApi;
