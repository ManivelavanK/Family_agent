export interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
  toolsUsed?: string[];
  steps?: string[];
}
