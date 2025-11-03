import React from 'react';
import { ChatMessage } from '../../types';

interface ChatMessageBubbleProps {
  message: ChatMessage;
}

const ChatMessageBubble: React.FC<ChatMessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  const isVoice = message.type === 'voice';
  
  const formatTime = (timestamp: Date | string | undefined) => {
    try {
      if (!timestamp) return 'Now';
      
      const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Now';
      }
      
      return date.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return 'Now';
    }
  };

  const renderMessageContent = () => {
    // Handle CRM-specific recommendations
    if (message.metadata?.crmRecommendation) {
      return (
        <div className="space-y-2">
          <p>{message.content}</p>
          <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-blue-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-sm font-medium text-blue-800">CRM Integration Tip</p>
                <p className="text-sm text-blue-700">{message.metadata.crmRecommendation}</p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // Handle assessment references
    if (message.metadata?.assessmentReference) {
      return (
        <div className="space-y-2">
          <p>{message.content}</p>
          <div className="bg-green-50 border-l-4 border-green-400 p-3 rounded">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-green-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-sm font-medium text-green-800">Assessment Insight</p>
                <p className="text-sm text-green-700">{message.metadata.assessmentReference}</p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // Handle integration tips
    if (message.metadata?.integrationTip) {
      return (
        <div className="space-y-2">
          <p>{message.content}</p>
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-sm font-medium text-yellow-800">Integration Tip</p>
                <p className="text-sm text-yellow-700">{message.metadata.integrationTip}</p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // Format message content with basic markdown-style rendering
    const formatContent = (content: string) => {
      // Split by double newlines for paragraphs
      const paragraphs = content.split('\n\n');
      
      return paragraphs.map((paragraph, index) => {
        // Handle bullet points
        if (paragraph.includes('•') || paragraph.includes('✅')) {
          const lines = paragraph.split('\n');
          return (
            <div key={index} className="mb-2">
              {lines.map((line, lineIndex) => {
                if (line.trim().startsWith('•') || line.trim().startsWith('✅')) {
                  return (
                    <div key={lineIndex} className="flex items-start mb-1">
                      <span className="mr-2 text-blue-500 font-bold">
                        {line.trim().startsWith('✅') ? '✅' : '•'}
                      </span>
                      <span className="text-sm">{line.replace(/^[•✅]\s*/, '').replace(/\*\*(.*?)\*\*/g, '$1')}</span>
                    </div>
                  );
                } else if (line.trim()) {
                  return <p key={lineIndex} className="text-sm mb-1 font-medium">{line.replace(/\*\*(.*?)\*\*/g, '$1')}</p>;
                }
                return null;
              })}
            </div>
          );
        } else {
          // Regular paragraph
          return (
            <p key={index} className="text-sm mb-2 leading-relaxed">
              {paragraph.replace(/\*\*(.*?)\*\*/g, '$1')}
            </p>
          );
        }
      });
    };

    return <div className="space-y-1">{formatContent(message.content)}</div>;
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-sm lg:max-w-lg px-3 py-2 rounded-lg ${
        isUser 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-100 text-gray-800'
      }`}>
        <div className="flex items-start space-x-2">
          {isVoice && (
            <svg className={`w-3 h-3 mt-1 flex-shrink-0 ${
              isUser ? 'text-blue-200' : 'text-gray-500'
            }`} fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 715 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
            </svg>
          )}
          <div className="flex-1 text-sm leading-relaxed">
            {renderMessageContent()}
          </div>
        </div>
        <div className={`text-xs mt-1 ${
          isUser ? 'text-blue-200' : 'text-gray-500'
        }`}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default ChatMessageBubble;
