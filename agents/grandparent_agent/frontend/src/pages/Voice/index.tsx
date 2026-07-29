import React, { useState, useRef, useEffect } from 'react';
import { voiceService } from '../../services/voiceService';
import { VoiceMessage } from '../../types';
import { Mic, MicOff, Send, Volume2, Bot, User, Sparkles, WifiOff } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

export const Voice: React.FC = () => {
  const [messages, setMessages] = useState<VoiceMessage[]>([
    {
      sender: 'assistant',
      text: 'Namaste! I am your KinNest health assistant. You can ask me about your blood pressure, blood sugar, medicine schedule, upcoming appointments, or trigger an emergency alert. How can I help you today?',
      timestamp: new Date().toISOString(),
      intent: 'greeting'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const supported = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
    setSpeechSupported(supported);
    if (supported) {
      const SpeechRecognitionCtor = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognitionCtor();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-IN';
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setListening(false);
      };
      recognition.onerror = () => {
        toast.error('Microphone access denied or not available.');
        setListening(false);
      };
      recognition.onend = () => setListening(false);
      recognitionRef.current = recognition;
    }
  }, []);


  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleMicToggle = () => {
    if (!speechSupported) {
      toast.error('Speech recognition is not supported in this browser. Please type your question.');
      return;
    }
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
    } else {
      recognitionRef.current?.start();
      setListening(true);
      toast.success('Listening... Speak your question now.', { duration: 3000 });
    }
  };

  const handleSend = async () => {
    const query = inputText.trim();
    if (!query) return;

    const userMessage: VoiceMessage = {
      sender: 'user',
      text: query,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      const response = await voiceService.sendMessage(query);
      const assistantMessage: VoiceMessage = {
        ...response,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Speak response using TTS if available
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response.text);
        utterance.lang = 'en-IN';
        utterance.rate = 0.85;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
      }
    } catch (e) {
      toast.error('Could not get a response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const speakMessage = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-IN';
      utterance.rate = 0.85;
      window.speechSynthesis.speak(utterance);
      toast.success('Playing audio response...');
    } else {
      toast.error('Audio playback not supported in this browser.');
    }
  };

  const quickPrompts = [
    'What is my blood pressure today?',
    'Have I taken all my medicines?',
    'When is my next doctor appointment?',
    'How much water should I drink today?',
  ];

  return (
    <div className="flex flex-col gap-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-sky-400 to-sky-500 rounded-2xl p-6 text-white flex items-center gap-4">
        <div className="p-3 bg-white/20 rounded-xl">
          <Sparkles className="h-7 w-7" />
        </div>
        <div>
          <h3 className="text-xl font-extrabold">AI Voice Health Assistant</h3>
          <p className="text-sm font-semibold opacity-85">Ask health questions, check vitals, or trigger emergency SOS using voice or text.</p>
        </div>
        {!speechSupported && (
          <div className="ml-auto flex items-center gap-1.5 bg-amber-400 text-amber-900 text-xs font-bold px-3 py-1.5 rounded-full">
            <WifiOff className="h-3.5 w-3.5" />
            <span>Voice Not Supported</span>
          </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="flex flex-wrap gap-2">
        {quickPrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => setInputText(prompt)}
            className="text-sm font-bold px-4 py-2 rounded-full bg-sky-50 border border-sky-100 text-sky-700 hover:bg-sky-100 transition-colors cursor-pointer"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Chat Window */}
      <div className="bg-white border border-sky-100 rounded-2xl overflow-hidden flex flex-col shadow-xs">
        {/* Messages */}
        <div className="flex-1 p-6 space-y-4 overflow-y-auto min-h-[350px] max-h-[450px]">
          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className={`flex items-start gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
              >
                {/* Avatar */}
                <div className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center border-2 ${
                  msg.sender === 'user'
                    ? 'bg-emerald-100 border-emerald-200 text-emerald-700'
                    : 'bg-sky-100 border-sky-200 text-sky-700'
                }`}>
                  {msg.sender === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                {/* Bubble */}
                <div className={`max-w-sm lg:max-w-md rounded-2xl p-4 ${
                  msg.sender === 'user'
                    ? 'bg-emerald-500 text-white rounded-tr-sm'
                    : 'bg-slate-50 border border-slate-100 text-slate-800 rounded-tl-sm'
                }`}>
                  <p className="text-base font-semibold leading-relaxed">{msg.text}</p>
                  <div className="flex items-center justify-between mt-2 gap-2">
                    <span className={`text-xs font-semibold ${msg.sender === 'user' ? 'text-emerald-100' : 'text-slate-400'}`}>
                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {msg.sender === 'assistant' && (
                      <button
                        onClick={() => speakMessage(msg.text)}
                        className="text-slate-400 hover:text-sky-600 transition-colors cursor-pointer"
                        title="Play Audio"
                      >
                        <Volume2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading indicator */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3"
            >
              <div className="w-9 h-9 rounded-full bg-sky-100 border-2 border-sky-200 text-sky-700 flex items-center justify-center">
                <Bot className="h-4 w-4" />
              </div>
              <div className="bg-slate-50 border border-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1.5 items-center">
                <span className="w-2 h-2 bg-sky-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-2 h-2 bg-sky-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-2 h-2 bg-sky-400 rounded-full animate-bounce" />
              </div>
            </motion.div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-100 p-4 flex items-center gap-3 bg-slate-50/50">
          {/* Microphone Button */}
          <button
            onClick={handleMicToggle}
            className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center border-2 transition-all cursor-pointer font-bold ${
              listening
                ? 'bg-rose-500 border-rose-400 text-white animate-pulse'
                : 'bg-white border-slate-200 text-slate-500 hover:border-sky-400 hover:text-sky-600'
            }`}
            title={listening ? 'Stop Listening' : 'Start Voice Input'}
          >
            {listening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
          </button>

          {/* Text Input */}
          <input
            type="text"
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={listening ? 'Listening... speak now.' : 'Type or speak your health question...'}
            className="flex-1 text-base font-semibold text-slate-800 bg-white border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:border-sky-400 placeholder:text-slate-400"
          />

          {/* Send Button */}
          <button
            onClick={handleSend}
            disabled={!inputText.trim() || loading}
            className="flex-shrink-0 w-12 h-12 rounded-xl bg-sky-500 hover:bg-sky-600 active:scale-95 disabled:opacity-40 text-white flex items-center justify-center transition-all cursor-pointer"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Intent Detection Badge */}
      {messages.length > 1 && messages[messages.length - 1].sender === 'assistant' && messages[messages.length - 1].intent && (
        <div className="flex items-center gap-2 px-4 py-2 bg-slate-50 border border-slate-100 rounded-xl w-fit text-sm text-slate-500 font-semibold">
          <Sparkles className="h-4 w-4 text-sky-400" />
          <span>Detected Intent: <strong className="text-sky-600">{messages[messages.length - 1].intent}</strong></span>
        </div>
      )}
    </div>
  );
};
export default Voice;
