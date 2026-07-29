import apiClient from './apiClient';

export const crossAgentApi = {
  getMotherHealth: async () => {
    const response = await apiClient.get('/family-agent/mother/health');
    return response.data;
  },

  getMotherInventory: async () => {
    const response = await apiClient.get('/family-agent/mother/inventory');
    return response.data;
  },

  getMotherShoppingList: async () => {
    const response = await apiClient.get('/family-agent/mother/shopping-list');
    return response.data;
  },

  recordExpenseFromMother: async (expenseData) => {
    const response = await apiClient.post('/api/v1/family/record-expense', expenseData);
    return response.data;
  }
};

export default crossAgentApi;
