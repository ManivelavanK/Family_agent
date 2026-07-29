import apiClient from './apiClient';

export const budgetApi = {
  getBudgets: async (familyId = 1) => {
    const response = await apiClient.get('/finance/budgets', {
      params: { family_id: familyId }
    });
    return response.data;
  },

  createBudget: async (budgetData) => {
    const response = await apiClient.post('/finance/budgets', budgetData);
    return response.data;
  },

  getBudgetAnalytics: async (familyId = 1) => {
    const response = await apiClient.get('/finance/budget-analytics', {
      params: { family_id: familyId }
    });
    return response.data;
  },

  updateBudget: async (budgetId, budgetData) => {
    const response = await apiClient.put(`/finance/budgets/${budgetId}`, budgetData);
    return response.data;
  },

  deleteBudget: async (budgetId) => {
    const response = await apiClient.delete(`/finance/budgets/${budgetId}`);
    return response.data;
  }
};

export default budgetApi;
