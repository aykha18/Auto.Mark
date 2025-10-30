import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Mic, Send, Volume2 } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  isVoice?: boolean;
}

const ConversationalAIDemo: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const aiResponses = [
    "Based on your current campaign data, I recommend increasing your Facebook ad spend by 20% and shifting budget from Google Ads. Your Facebook campaigns are showing 34% higher conversion rates.",
    "I've analyzed your email performance and noticed Tuesday sends at 2:30 PM get 23% better open rates. Should I automatically optimize your send times?",
    "Your landing page conversion rate dropped 8% this week. I detected the issue is with mobile users on the checkout page. I can implement a fix that should recover the lost conversions.",
    "I found 1,247 website visitors who viewed your pricing page but didn't convert. I've created a targeted retargeting campaign that typically recovers 18% of these prospects.",
    "Your competitor just launched a similar campaign. Based on market analysis, I suggest adjusting your messaging to emphasize your unique AI capabilities. This could increase your competitive advantage by 31%."
  ];

  const quickQuestions = [
    "How are my campaigns performing?",
    "What optimization opportunities do you see?",
    "Show me my best performing channels",
    "Predict next month's performance"
  ];

  useEffect(() => {
    // Initial AI greeting
    if (messages.length === 0) {
      setTimeout(() => {
        addAIMessage("Hi! I'm your AI marketing assistant. I've been monitoring your campaigns 24/7. What would you like to know about your marketing performance?");
      }, 1000);
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = (content: string, type: 'user' | 'ai', isVoice = false) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
      isVoice
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const addAIMessage = (content: string) => {
    setIsTyping(true);
    setTimeout(() => {
      addMessage(content, 'ai');
      setIsTyping(false);
    }, 1500);
  };

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      addMessage(inputValue, 'user');
      setInputValue('');
      
      // Simulate AI response
      const randomResponse = aiResponses[Math.floor(Math.random() * aiResponses.length)];
      addAIMessage(randomResponse);
    }
  };

  const handleQuickQuestion = (question: string) => {
    addMessage(question, 'user');
    const randomResponse = aiResponses[Math.floor(Math.random() * aiResponses.length)];
    addAIMessage(randomResponse);
  };

  const handleVoiceInput = () => {
    setIsListening(true);
    // Simulate voice input
    setTimeout(() => {
      setIsListening(false);
      const voiceMessage = "What's my campaign ROI this month?";
      addMessage(voiceMessage, 'user', true);
      addAIMessage("Your campaign ROI this month is 340%, up 23% from last month. Your best performing channel is LinkedIn with 450% ROI, followed by email marketing at 380% ROI.");
    }, 2000);
  };

  const speakMessage = (content: string) => {
    // Simulate text-to-speech
    console.log('Speaking:', content);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 h-96 flex flex-col">
      {/* Header */}
      <div className="flex items-center p-4 border-b border-gray-200">
        <MessageCircle className="w-6 h-6 text-green-600 mr-3" />
        <div>
          <h3 className="text-lg font-semibold text-gray-900">AI Marketing Assistant</h3>
          <p className="text-sm text-gray-600">Voice-enabled, context-aware consultation</p>
        </div>
        <div className="ml-auto flex items-center">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2" />
          <span className="text-xs text-green-600 font-medium">Online</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="flex items-start justify-between">
                <p className="text-sm">{message.content}</p>
                {message.type === 'ai' && (
                  <button
                    onClick={() => speakMessage(message.content)}
                    className="ml-2 p-1 hover:bg-gray-200 rounded"
                  >
                    <Volume2 className="w-3 h-3 text-gray-600" />
                  </button>
                )}
                {message.isVoice && (
                  <Mic className="w-3 h-3 ml-2 text-blue-300" />
                )}
              </div>
              <p className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Questions */}
      {messages.length <= 2 && (
        <div className="px-4 py-2 border-t border-gray-100">
          <p className="text-xs text-gray-500 mb-2">Quick questions:</p>
          <div className="flex flex-wrap gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleQuickQuestion(question)}
                className="text-xs px-3 py-1 bg-blue-50 text-blue-600 rounded-full hover:bg-blue-100 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <button
            onClick={handleVoiceInput}
            disabled={isListening}
            className={`p-2 rounded-lg transition-colors ${
              isListening 
                ? 'bg-red-100 text-red-600' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Mic className={`w-4 h-4 ${isListening ? 'animate-pulse' : ''}`} />
          </button>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask about your marketing performance..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim()}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConversationalAIDemo;