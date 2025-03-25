import React, { useState, useEffect } from 'react';
import { Bot } from 'lucide-react';
import useAPI from '../hooks/useAPI';
import { SystemStatus } from '../types';

interface HeaderProps {
  modelName?: string;
}

const Header: React.FC<HeaderProps> = ({ modelName = 'phi4' }) => {
  const [status, setStatus] = useState<{
    dot: string;
    text: string;
  }>({
    dot: 'bg-gray-400',
    text: 'Checking status...',
  });
  
  const { checkSystemStatus } = useAPI();

  useEffect(() => {
    const fetchStatus = async (): Promise<void> => {
      try {
        const data: SystemStatus = await checkSystemStatus();
        
        if (data.ollama === 'online' && data.vectordb === 'online') {
          setStatus({
            dot: 'bg-success',
            text: 'Online',
          });
        } else if (data.ollama === 'online' || data.vectordb === 'online') {
          setStatus({
            dot: 'bg-warning',
            text: 'Partial',
          });
        } else {
          setStatus({
            dot: 'bg-error',
            text: 'Offline',
          });
        }
      } catch (error) {
        setStatus({
          dot: 'bg-error',
          text: 'Error',
        });
      }
    };

    fetchStatus();
    // Refresh status every 60 seconds
    const interval = setInterval(fetchStatus, 60000);
    return () => clearInterval(interval);
  }, [checkSystemStatus]);

  return (
    <header className="sticky top-0 h-20 bg-background z-10 flex justify-between items-center px-5 border-b border-border-color flex-wrap">
      <h1 className="text-primary text-2xl font-bold flex-1">SMC Documentation Assistant</h1>
      <div className="flex items-center bg-card-bg py-2 px-4 rounded-full shadow-custom">
        <span className="text-primary mr-2"><Bot size={20} /></span>
        <span className="font-semibold text-primary">{modelName}</span>
        <div className="flex items-center ml-4 text-sm">
          <span className={`w-2.5 h-2.5 rounded-full ${status.dot} mr-1`}></span>
          <span className="text-text-secondary">{status.text}</span>
        </div>
      </div>
    </header>
  );
};

export default Header;