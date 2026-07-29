import React, { useState, useEffect } from 'react';
import { aiService } from '../services/aiService';
import { Message } from '../types/ai';
import { ChatInterface } from '../components/ai/ChatInterface';
import { ActivityPanel } from '../components/ai/ActivityPanel';
import { Sparkles, HelpCircle } from 'lucide-react';

export const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [activeSteps, setActiveSteps] = useState<string[]>([]);
  
  // Set default welcome message from initial db state
  useEffect(() => {
    async function loadMessages() {
      try {
        const msgs = await aiService.getMessages();
        setMessages(msgs);
        
        // Find last agent message to pre-fill steps
        const agentMsgs = msgs.filter(m => m.sender === 'agent' && m.steps);
        if (agentMsgs.length > 0) {
          setActiveSteps(agentMsgs[agentMsgs.length - 1].steps || []);
        }
      } catch (err) {
        console.error(err);
      }
    }
    loadMessages();
  }, []);

  const handleSendMessage = async (text: string) => {
    setChatLoading(true);
    // Set placeholder loading steps for the activity panel
    setActiveSteps([
      '🧠 Understanding request',
      '📦 Checking inventory database...',
      '📈 Checking budget constraints...'
    ]);

    try {
      const response = await aiService.sendMessage(text);
      setMessages(prev => [...prev, response]);
      // Update with final reasoning steps
      setActiveSteps(response.steps || []);
    } catch (err) {
      console.error(err);
      setActiveSteps(['❌ An error occurred during reasoning pipeline execution.']);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Mother Agent AI Assistant</h1>
        <p className="text-slate-500 font-medium text-xs mt-1">Converse with the household AI. Get instant recommendations on shopping lists, pantry assets, and meal planning.</p>
      </div>

      {/* Main chat and activity columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Interface Column */}
        <div className="lg:col-span-2">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            loading={chatLoading}
          />
        </div>

        {/* Agent Activity Terminal Column */}
        <div>
          <div className="sticky top-20 space-y-4">
            <div className="flex items-center gap-2 font-bold text-slate-800 text-sm">
              <Sparkles className="h-4.5 w-4.5 text-indigo-600" />
              <span>Multi-Agent Activity Log</span>
            </div>
            <ActivityPanel
              steps={activeSteps}
              loading={chatLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
export default AIAssistant;
