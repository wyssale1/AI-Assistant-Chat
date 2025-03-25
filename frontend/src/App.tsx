import React, { useState } from 'react';
import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import InputArea from './components/InputArea';
import Footer from './components/Footer';
import useAPI from './hooks/useAPI';
import { Message } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [lastQuery, setLastQuery] = useState<string>('');
  const [lastAnswer, setLastAnswer] = useState<string>('');
  const [showFeedback, setShowFeedback] = useState<boolean>(false);
  const { sendQuery, sendFeedback, error } = useAPI();

  const handleSendMessage = async (text: string): Promise<void> => {
    // Save query for feedback
    setLastQuery(text);
    
    // Add user message
    setMessages(prev => [...prev, {
      sender: 'user',
      text,
    }]);
    
    // Add loading message
    setMessages(prev => [...prev, {
      sender: 'assistant',
      isLoading: true,
    }]);
    
    try {
      // Send to API
      const response = await sendQuery(text);
      
      // Remove loading message and add actual response
      setMessages(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [...filtered, {
          sender: 'assistant',
          text: response.answer,
          sources: response.sources,
          timing: response.timing,
        }];
      });
      
      // Save answer for feedback
      setLastAnswer(response.answer);
      
      // Show feedback options
      setShowFeedback(true);
      
    } catch (err) {
      // Remove loading message and add error
      setMessages(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [...filtered, {
          sender: 'assistant',
          error: err instanceof Error ? err.message : 'Failed to process query',
        }];
      });
    }
  };

  const handleSubmitFeedback = async (rating: number, comment: string): Promise<void> => {
    try {
      await sendFeedback({
        query: lastQuery,
        answer: lastAnswer,
        rating,
        comment,
      });
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const handleCloseFeedback = (): void => {
    setShowFeedback(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto flex flex-col h-screen bg-white shadow-lg">
        <Header />
        <ChatContainer messages={messages} />
        <InputArea 
          onSendMessage={handleSendMessage} 
          showFeedback={showFeedback}
          onSubmitFeedback={handleSubmitFeedback}
          onCloseFeedback={handleCloseFeedback}
        />
        <Footer />
      </div>
    </div>
  );
}

export default App;