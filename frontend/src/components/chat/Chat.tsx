import React from 'react';
import ChatWidget from './ChatWidget';
import { useChatContext } from './ChatProvider';

const Chat: React.FC = () => {
  const { chatWidget, setChatWidget } = useChatContext();

  const handleToggle = () => {
    setChatWidget({
      ...chatWidget,
      isOpen: !chatWidget.isOpen,
      isMinimized: false
    });
  };

  const handleMinimize = () => {
    setChatWidget({
      ...chatWidget,
      isMinimized: !chatWidget.isMinimized
    });
  };

  return (
    <ChatWidget
      isOpen={chatWidget.isOpen}
      onToggle={handleToggle}
      onMinimize={handleMinimize}
      isMinimized={chatWidget.isMinimized}
      unreadCount={chatWidget.unreadCount}
    />
  );
};

export default Chat;
