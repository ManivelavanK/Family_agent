import { Message } from '../types/ai';
import { db } from '../data/mockData';
import { IS_MOCK_MODE, apiClient } from './api';

const LATENCY = 600;

export interface Alert {
  id: string;
  type: string;
  title: string;
  message: string;
  actionLabel: string;
  actionType: string;
  resolved: boolean;
}

export const aiService = {
  async getMessages(): Promise<Message[]> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve([...db.messages]);
        }, LATENCY);
      });
    }
    // The backend does not persist chat logs. We return the local message history.
    return [...db.messages];
  },

  async sendMessage(text: string): Promise<Message> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        // Record user message
        const userMsg: Message = {
          id: `msg-${Date.now()}-user`,
          sender: 'user',
          text,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        db.messages.push(userMsg);

        setTimeout(() => {
          let agentReplyText = "I have reviewed your query. Could you specify which household details you'd like me to look into?";
          let toolsUsed = ['Inventory Analysis'];
          let steps = ['🧠 Understanding request', '📦 Checking inventory'];

          const lowerText = text.toLowerCase();
          if (lowerText.includes('what should i buy') || lowerText.includes('shopping list') || lowerText.includes('buy this week')) {
            agentReplyText = 'Based on your inventory, consumption history, and planned meals, I recommend buying 5 kg Sona Masoori Rice, 2 L Organic Milk, 1 kg Tomatoes, and 2 kg Onions. This fits perfectly within your remaining weekly budget of ₹3,000.';
            toolsUsed = ['Inventory Analysis', 'Consumption Prediction', 'Meal Planning', 'Budget Analysis'];
            steps = [
              '🧠 Understanding request: "What should I buy this week?"',
              '📦 Checking inventory: Scanned 8 items, found 2 below critical threshold',
              '📈 Analyzing consumption: Evaluated average weekly depletion curves',
              '🍲 Checking meal plan: Verified missing items for Wednesday and Friday',
              '💰 Checking grocery budget: Estimated cost ₹575 fits remaining limit of ₹3,000',
              '✨ Generating recommendation: Compiled smart shopping list'
            ];
          } else if (lowerText.includes('waste') || lowerText.includes('prevent waste')) {
            agentReplyText = 'You have currently wasted ₹800 this month. Tomatoes are frequently purchased in excess. Reducing weekly tomato purchases by 500g could save around ₹120 and reduce food waste by 14%.';
            toolsUsed = ['Waste Monitor', 'Consumption Prediction'];
            steps = [
              '🧠 Analyzing user request regarding food waste',
              '📊 querying spending analytics database',
              '📈 estimating waste curves based on category consumption'
            ];
          } else if (lowerText.includes('hello') || lowerText.includes('hi')) {
            agentReplyText = 'Hello! I am Mother Agent. I monitor your inventory levels, consumption patterns, and coordinate meal plans and grocery budgets. How can I help you today?';
            steps = ['🧠 Processed greeting'];
          }

          const agentMsg: Message = {
            id: `msg-${Date.now()}-agent`,
            sender: 'agent',
            text: agentReplyText,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            toolsUsed,
            steps
          };

          db.messages.push(agentMsg);
          resolve(agentMsg);
        }, 2000); // 2 seconds delay to represent agent processing/reasoning
      });
    }

    // Add user message to history
    const userMsg: Message = {
      id: `msg-${Date.now()}-user`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    db.messages.push(userMsg);

    // Call real Llama model backend via kitchen-assistant ask route
    const response = await apiClient.post<any>('/kitchen-assistant/ask', { text });
    const agentMsg: Message = {
      id: `msg-${Date.now()}-agent`,
      sender: 'agent',
      text: response.data.response,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      toolsUsed: ['Llama 3.3 Agent Reasoning', 'Pantry DB Sync'],
      steps: [
        '🧠 Processing query via Llama LLM',
        '✨ Synthesizing culinary & kitchen response'
      ]
    };
    db.messages.push(agentMsg);
    return agentMsg;
  },

  async getAlerts(): Promise<Alert[]> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve([...db.alerts]);
        }, LATENCY);
      });
    }
    const response = await apiClient.get<any[]>('/alerts/active');
    return response.data.map(alert => ({
      id: String(alert.id),
      type: alert.severity === 'High' ? 'critical' : alert.severity === 'Medium' ? 'warning' : 'info',
      title: alert.title,
      message: `${alert.description} Recommendation: ${alert.recommended_action}`,
      actionLabel: alert.recommended_action || 'Resolve Alert',
      actionType: 'resolve',
      resolved: alert.status === 'Resolved'
    }));
  },

  async resolveAlert(id: string): Promise<boolean> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          const index = db.alerts.findIndex(a => a.id === id);
          if (index !== -1) {
            db.alerts[index].resolved = true;
          }
          resolve(true);
        }, LATENCY);
      });
    }
    await apiClient.post(`/alerts/${id}/resolve`);
    return true;
  },

  async getDashboardInsights(): Promise<string> {
    if (IS_MOCK_MODE) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve("Rice stock may run low in 4 days, vegetables are sufficient for 3 days, and grocery spending is currently 8% below your monthly budget.");
        }, LATENCY);
      });
    }
    const response = await apiClient.get<any>('/dashboard/summary');
    const reflections = response.data.latest_reflections || [];
    if (reflections.length > 0) {
      return reflections.map((r: any) => `${r.item}: ${r.insight}`).join(' | ');
    }
    return "Inventory and budget status are currently normal.";
  }
};
