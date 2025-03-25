import React, { useState, useRef, FormEvent, useEffect } from "react";
import { Send } from "lucide-react";
import FeedbackSection from "./FeedbackSection";
import useAPI from "../hooks/useAPI";

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
  onCloseFeedback,
}) => {
  const [inputValue, setInputValue] = useState<string>("");
  const [backendStatus, setBackendStatus] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const { checkSystemStatus } = useAPI();

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await checkSystemStatus();
        // Backend is available if both ollama and vectordb are online
        setBackendStatus(
          status.ollama === "online" && status.vectordb === "online"
        );
      } catch (error) {
        setBackendStatus(false);
      }
    };

    checkStatus();
    // Check status every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, [checkSystemStatus]);

  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (inputValue.trim() && backendStatus) {
      onSendMessage(inputValue);
      setInputValue("");
      // Focus back on input for convenience
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };

  // Determine if button should be active based on input and backend status
  const isActive = inputValue.trim().length > 0 && backendStatus;

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
          className={
            isActive
              ? "p-3 px-5 bg-blue-500 text-white border-none rounded-full cursor-pointer hover:bg-blue-600 active:bg-blue-700 transition-colors"
              : "p-3 px-5 bg-gray-300 text-gray-500 border-none rounded-full cursor-not-allowed"
          }
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
