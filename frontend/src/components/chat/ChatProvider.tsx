import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ChatSession, ChatMessage, ChatWidget } from '../../types';

interface ChatContextType {
  chatWidget: ChatWidget;
  setChatWidget: (widget: ChatWidget) => void;
  currentSession: ChatSession | null;
  setCurrentSession: (session: ChatSession | null) => void;
  chatHistory: ChatMessage[];
  addToChatHistory: (message: ChatMessage) => void;
  clearChatHistory: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [chatWidget, setChatWidget] = useState<ChatWidget>({
    isOpen: false,
    isMinimized: false,
    unreadCount: 0,
    position: 'bottom-right'
  });

  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);

  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('automark_chat_history');
    if (savedHistory) {
      try {
        const parsedHistory = JSON.parse(savedHistory);
        setChatHistory(parsedHistory);
      } catch (error) {
        console.error('Failed to parse chat history:', error);
      }
    }

    // Load chat widget state
    const savedWidgetState = localStorage.getItem('automark_chat_widget_state');
    if (savedWidgetState) {
      try {
        const parsedState = JSON.parse(savedWidgetState);
        setChatWidget(prev => ({ ...prev, ...parsedState }));
      } catch (error) {
        console.error('Failed to parse chat widget state:', error);
      }
    }
  }, []);

  // Save chat history to localStorage when it changes
  useEffect(() => {
    if (chatHistory.length > 0) {
      localStorage.setItem('automark_chat_history', JSON.stringify(chatHistory));
    }
  }, [chatHistory]);

  // Save chat widget state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('automark_chat_widget_state', JSON.stringify({
      isMinimized: chatWidget.isMinimized,
      position: chatWidget.position
    }));
  }, [chatWidget.isMinimized, chatWidget.position]);

  const addToChatHistory = (message: ChatMessage) => {
    setChatHistory(prev => {
      const newHistory = [...prev, message];
      // Keep only last 100 messages to prevent localStorage from getting too large
      return newHistory.slice(-100);
    });
  };

  const clearChatHistory = () => {
    setChatHistory([]);
    localStorage.removeItem('automark_chat_history');
  };

  // Update unread count when new messages arrive and chat is closed
  useEffect(() => {
    if (currentSession && !chatWidget.isOpen) {
      const unreadMessages = currentSession.messages.filter(
        msg => msg.sender === 'agent' && 
        !chatHistory.some(histMsg => histMsg.id === msg.id)
      );
      
      if (unreadMessages.length > 0) {
        setChatWidget(prev => ({
          ...prev,
          unreadCount: prev.unreadCount + unreadMessages.length
        }));
      }
    }
  }, [currentSession?.messages, chatWidget.isOpen, chatHistory]);

  // Reset unread count when chat is opened
  useEffect(() => {
    if (chatWidget.isOpen && chatWidget.unreadCount > 0) {
      setChatWidget(prev => ({ ...prev, unreadCount: 0 }));
    }
  }, [chatWidget.isOpen]);

  const value: ChatContextType = {
    chatWidget,
    setChatWidget,
    currentSession,
    setCurrentSession,
    chatHistory,
    addToChatHistory,
    clearChatHistory
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export default ChatProvider;
