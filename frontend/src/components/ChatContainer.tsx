import React, { useRef, useEffect, useState } from 'react';
import { ArrowDown } from 'lucide-react';
import MessageItem from './MessageItem';
import { Message } from '../types';

interface ChatContainerProps {
  messages: Message[];
}

const ChatContainer: React.FC<ChatContainerProps> = ({ messages }) => {
  const chatRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState<boolean>(false);
  
  // Function to scroll to bottom
  const scrollToBottom = (): void => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  };
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Add scroll event listener to show/hide scroll button
  useEffect(() => {
    const handleScroll = (): void => {
      if (!chatRef.current) return;
      
      const { scrollTop, scrollHeight, clientHeight } = chatRef.current;
      const isScrolledUp = scrollHeight - scrollTop - clientHeight > 100;
      
      setShowScrollButton(isScrolledUp);
    };
    
    const chatElement = chatRef.current;
    if (chatElement) {
      chatElement.addEventListener('scroll', handleScroll);
      return () => chatElement.removeEventListener('scroll', handleScroll);
    }
  }, []);
  
  // If no messages, show welcome message
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col bg-white m-2 rounded-lg shadow-md overflow-hidden">
        <div className="flex-1 flex items-center justify-center p-5">
          <div className="text-center max-w-lg">
            <h2 className="text-2xl font-bold text-primary mb-3">
              Welcome to SMC Documentation Assistant
            </h2>
            <p className="text-gray-600 mb-6">
              Ask any question about SMC devices and get accurate answers with references to the source documentation.
            </p>
            <div className="bg-blue-50 p-4 rounded-lg text-left">
              <p className="font-medium text-primary mb-2">Try asking questions like:</p>
              <ul className="space-y-2 text-gray-700">
                <li>• How do I reset the device?</li>
                <li>• What is the power range for the XYZ axis?</li>
                <li>• What are the troubleshooting steps for error code E45?</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex-1 flex flex-col bg-white m-2 rounded-lg shadow-md overflow-hidden relative">
      <div 
        ref={chatRef}
        className="flex-1 overflow-y-auto p-5 scroll-smooth"
      >
        {messages.map((message, index) => (
          <MessageItem 
            key={index} 
            message={message} 
            type={message.sender} 
          />
        ))}
      </div>
      
      {showScrollButton && (
        <button 
          onClick={scrollToBottom}
          className="absolute bottom-4 right-4 bg-white p-2 rounded-full shadow-lg hover:bg-gray-100 transition-colors"
          aria-label="Scroll to bottom"
        >
          <ArrowDown size={20} className="text-primary" />
        </button>
      )}
    </div>
  );
};

export default ChatContainer;