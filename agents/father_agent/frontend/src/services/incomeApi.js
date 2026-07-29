import apiClient from './apiClient';

export const incomeApi = {
  getIncome: async (familyId = 1) => {
    const response = await apiClient.get('/finance/income', {
      params: { family_id: familyId }
    });
    return response.data;
  },

  createIncome: async (incomeData) => {
    const response = await apiClient.post('/finance/income', incomeData);
    return response.data;
  },

  updateIncome: async (incomeId, incomeData) => {
    const response = await apiClient.put(`/finance/income/${incomeId}`, incomeData);
    return response.data;
  },

  deleteIncome: async (incomeId) => {
    const response = await apiClient.delete(`/finance/income/${incomeId}`);
    return response.data;
  }
};

export default incomeApi;
