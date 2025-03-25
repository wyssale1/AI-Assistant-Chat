import React, { JSX } from "react"
import { Check, X } from 'lucide-react';
import { Source, Message } from '../types';

interface MessageItemProps {
  message: Message;
  type: 'user' | 'assistant';
}

const MessageItem: React.FC<MessageItemProps> = ({ message, type }) => {
  // Function to format source references
  const formatSources = (sources: Source[]): JSX.Element => {
    // Group pages by document
    const uniqueSources: Record<string, Set<number>> = {};
    sources.forEach(source => {
      const key = source.document;
      if (!uniqueSources[key]) {
        uniqueSources[key] = new Set<number>();
      }
      uniqueSources[key].add(source.page);
    });

    return (
      <div className="mt-4 text-sm text-text-secondary bg-gray-50 p-3 rounded border-l-3 border-l-accent">
        <div className="font-bold mb-1 text-accent">Sources:</div>
        {Object.entries(uniqueSources).map(([document, pageSet]) => (
          <div key={document}>
            <div className="font-bold mt-2">{document}</div>
            <ul className="list-none pl-4">
              {Array.from(pageSet).sort((a, b) => a - b).map(page => (
                <li key={page} className="my-0.5">Page {page}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    );
  };

  // Function to format answer with Markdown-like formatting
  const formatAnswer = (answer: string): JSX.Element => {
    // Handle bold text
    let formatted = answer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Handle italic text
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Handle source references
    formatted = formatted.replace(/\(([^,]+),\s*Page\s*(\d+)\)/g, 
      '<span class="bg-blue-50 px-1 py-0.5 rounded">(<strong>$1</strong>, Page $2)</span>'
    );
    
    return (
      <div dangerouslySetInnerHTML={{ __html: formatted.replace(/\n/g, '<br>') }} />
    );
  };

  if (type === 'user') {
    return (
      <div className="mb-5 p-4 bg-blue-50 rounded-lg ml-auto mr-0 max-w-[85%] text-right text-blue-900">
        {message.text}
      </div>
    );
  }
  
  if (type === 'assistant') {
    if (message.isLoading) {
      return (
        <div className="mb-5 p-4 bg-gray-100 rounded-lg mr-auto ml-0 max-w-[85%]">
          <div className="flex flex-col items-center">
            <div className="dot-elastic"></div>
            <div className="mt-2 text-text-secondary">Searching documentation...</div>
          </div>
        </div>
      );
    }
    
    if (message.error) {
      return (
        <div className="mb-5 p-4 bg-red-50 text-error rounded-lg mr-auto ml-0 max-w-[85%] flex items-center">
          <X className="mr-2" size={18} />
          <span>Sorry, there was an error: {message.error}</span>
        </div>
      );
    }
    
    return (
      <div className="mb-5 p-4 bg-gray-100 rounded-lg mr-auto ml-0 max-w-[85%]">
        {message.text && formatAnswer(message.text)}
        
        {message.sources && message.sources.length > 0 && message.text && !message.text.includes("Sources:") && (
          formatSources(message.sources)
        )}
        
        {message.timing && (
          <div className="text-right text-xs text-text-secondary mt-1">
            Response time: {message.timing.total_seconds}s
          </div>
        )}
      </div>
    );
  }
  
  return null;
};

export default MessageItem;