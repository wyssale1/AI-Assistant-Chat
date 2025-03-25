import React, { useState, useRef, FormEvent } from 'react';
import { Send } from 'lucide-react';
import FeedbackSection from './FeedbackSection';

interface InputAreaProps {
  onSendMessage: (message: string) => void;
  showFeedback: boolean;
  onSubmitFeedback: (rating: number, comment: string) => void;
  onCloseFeedback: () => void;
}

const InputArea: React.FC<InputAreaProps> = ({ 
  onSendMessage, 
  showFeedback, 
  onSubmitFeedback, 
  onCloseFeedback 
}) => {
  const [inputValue, setInputValue] = useState<string>('');
  const inputRef = useRef<HTMLInputElement>(null);
  
  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
      // Focus back on input for convenience
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };
  
  // Determine if button should be active based on input
  const isActive = inputValue.trim().length > 0;
  
  return (
    <div className="sticky bottom-0 bg-white p-4 border-t border-gray-200 z-10">
      <form onSubmit={handleSubmit} className="flex py-2">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          className="flex-1 p-3 border border-gray-300 rounded-full mr-2 text-base outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
          placeholder="Ask about SMC devices..."
        />
        <button
          type="submit"
          disabled={!isActive}
          className={`p-3 px-5 border-none rounded-full cursor-pointer transition-colors ${
            isActive 
              ? 'bg-blue-500 text-white hover:bg-blue-600 active:bg-blue-700' 
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          <Send size={18} />
        </button>
      </form>
      
      {showFeedback && (
        <FeedbackSection 
          onSubmit={onSubmitFeedback}
          onClose={onCloseFeedback}
        />
      )}
    </div>
  );
};

export default InputArea;