import apiClient from './apiClient';

export const notificationApi = {
  getNotifications: async (familyId = 1) => {
    const response = await apiClient.get('/finance/notifications', {
      params: { family_id: familyId }
    });
    return response.data;
  }
};

export default notificationApi;
