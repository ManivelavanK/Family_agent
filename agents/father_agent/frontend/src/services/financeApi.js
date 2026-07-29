import apiClient from './apiClient';

export const financeApi = {
  checkHealth: async () => {
    const response = await apiClient.get('/api/v1/family/health');
    return response.data;
  },

  getFinancialSummary: async (familyId = 1) => {
    const response = await apiClient.get(`/api/v1/family/financial-summary/${familyId}`);
    return response.data;
  },

  askSupervisor: async (familyId, question) => {
    const response = await apiClient.post('/finance/agent', {
      family_id: Number(familyId),
      question: question
    });
    return response.data;
  },

  askFinance: async (familyId, question) => {
    const response = await apiClient.post('/finance/ask', {
      family_id: Number(familyId),
      question: question
    });
    return response.data;
  }
};

export default financeApi;
