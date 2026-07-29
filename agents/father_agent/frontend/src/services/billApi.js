import apiClient from './apiClient';

export const billApi = {
  getBills: async (familyId = 1) => {
    const response = await apiClient.get('/finance/bills', {
      params: { family_id: familyId }
    });
    return response.data;
  },

  createBill: async (billData) => {
    const response = await apiClient.post('/finance/bills', billData);
    return response.data;
  },

  payBill: async (billId) => {
    const response = await apiClient.put(`/finance/bills/${billId}/pay`);
    return response.data;
  },

  getUpcomingBills: async (familyId = 1) => {
    const response = await apiClient.get('/finance/upcoming-bills', {
      params: { family_id: familyId }
    });
    return response.data;
  }
};

export default billApi;
