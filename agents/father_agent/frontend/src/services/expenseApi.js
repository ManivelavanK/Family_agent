import apiClient from './apiClient';

export const expenseApi = {
  getExpenses: async (familyId = 1) => {
    const response = await apiClient.get('/finance/expenses', {
      params: { family_id: familyId }
    });
    return response.data;
  },

  createExpense: async (expenseData) => {
    const response = await apiClient.post('/finance/expenses', expenseData);
    return response.data;
  },

  getExpenseSummary: async (familyId = 1) => {
    const response = await apiClient.get('/finance/expense-summary', {
      params: { family_id: familyId }
    });
    return response.data;
  },

  updateExpense: async (expenseId, expenseData) => {
    const response = await apiClient.put(`/finance/expenses/${expenseId}`, expenseData);
    return response.data;
  },

  deleteExpense: async (expenseId) => {
    const response = await apiClient.delete(`/finance/expenses/${expenseId}`);
    return response.data;
  }
};

export default expenseApi;
