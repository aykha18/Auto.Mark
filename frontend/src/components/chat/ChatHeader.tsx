import React from 'react';

interface ChatHeaderProps {
  isConnected: boolean;
  onMinimize: () => void;
  onClose: () => void;
  isMinimized: boolean;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({
  isConnected,
  onMinimize,
  onClose,
  isMinimized
}) => {
  return (
    <div className="bg-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="relative">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
            isConnected ? 'bg-green-400' : 'bg-red-400'
          }`} />
        </div>
        <div>
          <h3 className="font-semibold text-sm">Auto.Mark Assistant</h3>
          <p className="text-xs text-blue-100">
            {isConnected ? 'Online' : 'Connecting...'}
          </p>
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={onMinimize}
          className="text-blue-100 hover:text-white transition-colors p-1 rounded"
          aria-label={isMinimized ? "Expand chat" : "Minimize chat"}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {isMinimized ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 14l9-9 3 3L9 18l-2-2z" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
            )}
          </svg>
        </button>
        <button
          onClick={onClose}
          className="text-blue-100 hover:text-white transition-colors p-1 rounded"
          aria-label="Close chat"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ChatHeader;