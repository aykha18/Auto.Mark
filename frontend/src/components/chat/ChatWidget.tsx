import React, { useState, useEffect, useRef } from 'react';
import { ChatSession, ChatMessage, VoiceRecognitionState } from '../../types';
import ChatMessageList from './ChatMessageList';
import ChatInput from './ChatInput';
import VoiceInput from './VoiceInput';
import ChatHeader from './ChatHeader';

interface ChatWidgetProps {
  isOpen: boolean;
  onToggle: () => void;
  onMinimize: () => void;
  isMinimized: boolean;
  unreadCount: number;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({
  isOpen,
  onToggle,
  onMinimize,
  isMinimized,
  unreadCount
}) => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [voiceState, setVoiceState] = useState<VoiceRecognitionState>({
    isListening: false,
    isSupported: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window,
    transcript: '',
    confidence: 0
  });
  
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize chat session and WebSocket connection
  useEffect(() => {
    if (isOpen && !session) {
      initializeChat();
    }
  }, [isOpen]);

  // WebSocket connection management
  useEffect(() => {
    if (session && !wsRef.current) {
      connectWebSocket();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [session]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [session?.messages]);

  const initializeChat = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/chat/initialize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context: {
            currentPage: window.location.pathname,
            userProgress: {
              assessmentCompleted: localStorage.getItem('assessmentCompleted') === 'true',
              crmSelected: localStorage.getItem('selectedCRM'),
              readinessScore: localStorage.getItem('readinessScore') ? 
                parseInt(localStorage.getItem('readinessScore')!) : undefined
            }
          }
        })
      });

      if (response.ok) {
        const chatSession: ChatSession = await response.json();
        setSession(chatSession);
      }
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const connectWebSocket = () => {
    if (!session) return;
    
    // Skip WebSocket connection if disabled
    if (process.env.REACT_APP_DISABLE_WEBSOCKET === 'true') {
      console.log('Chat WebSocket disabled via environment variable');
      return;
    }

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/chat/ws/${session.id}`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      setIsConnected(true);
    };

    wsRef.current.onmessage = (event) => {
      const message: ChatMessage = JSON.parse(event.data);
      setSession(prev => prev ? {
        ...prev,
        messages: [...prev.messages, message]
      } : null);
    };

    wsRef.current.onclose = () => {
      setIsConnected(false);
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (session && isOpen) {
          connectWebSocket();
        }
      }, 3000);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
  };

  const sendMessage = async (content: string, type: 'text' | 'voice' = 'text') => {
    if (!session || !content.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: content.trim(),
      sender: 'user',
      timestamp: new Date(),
      type
    };

    // Add user message immediately
    setSession(prev => prev ? {
      ...prev,
      messages: [...prev.messages, userMessage]
    } : null);

    // Send via WebSocket if connected, otherwise fallback to HTTP
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify(userMessage));
    } else {
      try {
        await fetch(`/api/v1/chat/${session.id}/message`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userMessage)
        });
      } catch (error) {
        console.error('Failed to send message:', error);
      }
    }
  };

  const handleVoiceInput = (transcript: string) => {
    if (transcript.trim()) {
      sendMessage(transcript, 'voice');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={onToggle}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-200 hover:scale-105 relative"
          aria-label="Open chat"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          {unreadCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>
      </div>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 bg-white rounded-lg shadow-2xl border transition-all duration-300 ${
      isMinimized ? 'w-80 h-16' : 'w-96 h-[600px]'
    }`}>
      <ChatHeader
        isConnected={isConnected}
        onMinimize={onMinimize}
        onClose={onToggle}
        isMinimized={isMinimized}
      />
      
      {!isMinimized && (
        <>
          <div className="flex-1 overflow-hidden flex flex-col h-[520px]">
            {isLoading ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : session ? (
              <>
                <ChatMessageList 
                  messages={session.messages} 
                  isLoading={false}
                />
                <div ref={messagesEndRef} />
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                Failed to initialize chat. Please refresh and try again.
              </div>
            )}
          </div>
          
          <div className="border-t p-4 space-y-2">
            {voiceState.isSupported && (
              <VoiceInput
                voiceState={voiceState}
                onVoiceStateChange={setVoiceState}
                onTranscript={handleVoiceInput}
              />
            )}
            <ChatInput
              onSendMessage={sendMessage}
              disabled={!session || !isConnected}
              placeholder={isConnected ? "Ask about CRM integrations..." : "Connecting..."}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default ChatWidget;