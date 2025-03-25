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
  
  return (
    <div className="sticky bottom-0 bg-background p-5 border-t border-border-color z-10">
      <form onSubmit={handleSubmit} className="flex py-2">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          className="flex-1 p-3 border border-border-color rounded-full mr-2 text-base outline-none focus:border-accent focus:shadow-[0_0_0_2px_rgba(33,150,243,0.2)]"
          placeholder="Ask about SMC devices..."
        />
        <button
          type="submit"
          className="p-3 px-5 bg-accent text-white border-none rounded-full cursor-pointer hover:bg-blue-600 transition-colors"
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