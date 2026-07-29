import { api, isBackendUnavailable } from './api';
import { WhatsAppNotification } from '../types';
import { mockWhatsAppNotifications } from '../data/mockData';

const getLocalNotifications = (): WhatsAppNotification[] => {
  const local = localStorage.getItem('grandparent_notifications');
  if (!local) {
    localStorage.setItem('grandparent_notifications', JSON.stringify(mockWhatsAppNotifications));
    return mockWhatsAppNotifications;
  }
  return JSON.parse(local);
};

const saveLocalNotifications = (data: WhatsAppNotification[]) => {
  localStorage.setItem('grandparent_notifications', JSON.stringify(data));
};

export const notificationService = {
  getNotifications: async (): Promise<WhatsAppNotification[]> => {
    // Backend doesn't store/retrieve history of messages via a GET endpoint, 
    // so we manage notification history locally.
    return getLocalNotifications();
  },
  sendNotification: async (phone: string, template: string, customMessage?: string): Promise<WhatsAppNotification> => {
    try {
      const isCustom = template === 'custom';
      const type = isCustom ? 'custom' : template;
      const variables = isCustom 
        ? { message: customMessage || '' } 
        : {
            name: 'Lakshmi',
            medicine: 'Metformin',
            time: '8:00 PM',
            reason: 'Alert button pressed',
            severity: 'Critical',
            notes: 'Immediate attention required',
            doctor: 'Dr. Srinivasan',
            specialty: 'Cardiologist',
            count: '5',
            bp: '120/80',
            sugar: '110',
            sleep: '7.5',
            water: '1500',
            status: 'Good',
            url: 'http://localhost:8000/report/download'
          };

      const response = await api.post('/notification/send', { 
        phone, 
        type, 
        variables 
      });

      const resData = response.data;
      const newNotif: WhatsAppNotification = {
        id: resData?.sid || resData?.message_sid || `wa-${Date.now()}`,
        timestamp: new Date().toISOString(),
        recipient_phone: phone,
        message_type: template === 'custom' ? 'Ad-hoc' : 'Reminder',
        message_content: customMessage || `This is a test notification for template: ${template}`,
        status: (resData?.status === 'Delivered' || resData?.status === 'Mock Delivered') ? 'Delivered' : 'Failed'
      };

      const current = getLocalNotifications();
      current.unshift(newNotif);
      saveLocalNotifications(current);
      return newNotif;
    } catch (e) {
      if (isBackendUnavailable(e)) {
        const current = getLocalNotifications();
        const newNotif: WhatsAppNotification = {
          id: `wa-${Date.now()}`,
          timestamp: new Date().toISOString(),
          recipient_phone: phone,
          message_type: template === 'custom' ? 'Ad-hoc' : 'Reminder',
          message_content: customMessage || `This is a test notification for template: ${template}`,
          status: 'Delivered'
        };
        current.unshift(newNotif);
        saveLocalNotifications(current);
        return newNotif;
      }
      throw e;
    }
  }
};
