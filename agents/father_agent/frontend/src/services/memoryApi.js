import apiClient from './apiClient';

export const memoryApi = {
  getMemories: async (familyId = 1, query = '', category = '') => {
    const params = {};
    if (query) params.q = query;
    if (category) params.category = category;

    const response = await apiClient.get(`/finance/memory/${familyId}`, { params });
    return response.data;
  },

  storeMemory: async (memoryData) => {
    const response = await apiClient.post('/finance/memory', memoryData);
    return response.data;
  }
};

export default memoryApi;
