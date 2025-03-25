import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

interface FeedbackSectionProps {
  onSubmit: (rating: number, comment: string) => void;
  onClose: () => void;
}

const FeedbackSection: React.FC<FeedbackSectionProps> = ({ onSubmit, onClose }) => {
  const [showComment, setShowComment] = useState<boolean>(false);
  const [comment, setComment] = useState<string>('');
  const [status, setStatus] = useState<string | null>(null);

  const handlePositiveFeedback = (): void => {
    onSubmit(5, '');
    setStatus('success');
    setTimeout(() => {
      onClose();
    }, 3000);
  };

  const handleNegativeFeedback = (): void => {
    setShowComment(true);
  };

  const handleSubmitComment = (): void => {
    onSubmit(1, comment);
    setStatus('success');
    setShowComment(false);
    setTimeout(() => {
      onClose();
    }, 3000);
  };

  if (status === 'success') {
    return (
      <div className="mt-4 p-3 bg-card-bg rounded-lg shadow-custom">
        <div className="text-center text-success font-medium">
          Thank you for your feedback!
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="mt-4 p-3 bg-card-bg rounded-lg shadow-custom">
        <div className="text-center text-error font-medium">
          Error submitting feedback
        </div>
      </div>
    );
  }

  return (
    <div className="mt-4 p-3 bg-card-bg rounded-lg shadow-custom">
      <div className="font-medium mb-2">Was this answer helpful?</div>
      
      <div className="flex gap-2">
        <button
          onClick={handlePositiveFeedback}
          className="flex items-center py-2 px-4 bg-green-50 text-success rounded hover:bg-green-100 transition-colors"
        >
          <ThumbsUp size={16} className="mr-1" />
          Yes
        </button>
        
        <button
          onClick={handleNegativeFeedback}
          className="flex items-center py-2 px-4 bg-red-50 text-error rounded hover:bg-red-100 transition-colors"
        >
          <ThumbsDown size={16} className="mr-1" />
          No
        </button>
      </div>
      
      {showComment && (
        <div className="mt-4">
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className="w-full h-20 p-2 border border-border-color rounded resize-none mb-2"
            placeholder="How can we improve?"
          />
          <button
            onClick={handleSubmitComment}
            className="py-2 px-4 bg-accent text-white rounded hover:bg-blue-600 transition-colors"
          >
            Submit
          </button>
        </div>
      )}
    </div>
  );
};

export default FeedbackSection;