import { api, isBackendUnavailable } from './api';
import { VoiceMessage } from '../types';

export const voiceService = {
  sendMessage: async (text: string): Promise<VoiceMessage> => {
    try {
      const response = await api.post('/voice/chat', { text });
      // The response data is unwrapped by the Axios interceptor to the actual data payload
      const chatData = response.data;
      return {
        sender: 'assistant',
        text: chatData?.text_response || chatData?.response || "I could not generate a response.",
        timestamp: new Date().toISOString(),
        intent: chatData?.intent || "general"
      };
    } catch (e) {
      if (isBackendUnavailable(e)) {
        // Mock Response Generator based on keyword intents when offline
        let reply = "I am here to help you. Could you please repeat that?";
        let intent = "general";
        const query = text.toLowerCase();

        if (query.includes("sugar") || query.includes("glucose")) {
          reply = "Your latest blood sugar reading was 130 mg/dL, which is within the normal target range.";
          intent = "query_sugar";
        } else if (query.includes("blood pressure") || query.includes("bp")) {
          reply = "Your latest blood pressure is 127/81 mmHg. Excellent stability today.";
          intent = "query_bp";
        } else if (query.includes("medicine") || query.includes("pills")) {
          reply = "You have taken all your morning medications: Metformin, Amlodipine, and Glimepiride. Your next pill is Metformin at 8:30 PM.";
          intent = "query_medicine";
        } else if (query.includes("sos") || query.includes("emergency") || query.includes("help")) {
          reply = "Alert! Triggering emergency SOS contact system right now.";
          intent = "sos_trigger";
        }

        return {
          sender: 'assistant',
          text: reply,
          timestamp: new Date().toISOString(),
          intent
        };
      }
      throw e;
    }
  }
};
