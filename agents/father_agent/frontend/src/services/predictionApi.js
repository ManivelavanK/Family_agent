import apiClient from './apiClient';

export const predictionApi = {
  getSpendingPrediction: async (familyId = 1) => {
    const response = await apiClient.get('/finance/spending-prediction', {
      params: { family_id: familyId }
    });
    return response.data;
  }
};

export default predictionApi;
