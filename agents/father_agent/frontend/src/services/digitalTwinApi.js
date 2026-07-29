import apiClient from './apiClient';

export const digitalTwinApi = {
  getDigitalTwin: async (familyId = 1) => {
    const response = await apiClient.get(`/finance/digital-twin/${familyId}`);
    return response.data;
  }
};

export default digitalTwinApi;
