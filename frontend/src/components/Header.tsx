import React, { useState, useEffect } from 'react';
import { Bot } from 'lucide-react';
import useAPI from '../hooks/useAPI';
import { SystemStatus } from '../types';
import StatusModal from './StatusModal';

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
  
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const { checkSystemStatus } = useAPI();

  useEffect(() => {
    const fetchStatus = async (): Promise<void> => {
      try {
        const data: SystemStatus = await checkSystemStatus();
        setSystemStatus(data);
        
        if (data.ollama === 'online' && data.vectordb === 'online') {
          setStatus({
            dot: 'bg-green-500',
            text: 'Online',
          });
        } else if (data.ollama === 'online' || data.vectordb === 'online') {
          setStatus({
            dot: 'bg-yellow-500',
            text: 'Partial',
          });
        } else {
          setStatus({
            dot: 'bg-red-500',
            text: 'Offline',
          });
        }
      } catch (error) {
        setStatus({
          dot: 'bg-red-500',
          text: 'Error',
        });
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 300000);
    return () => clearInterval(interval);
  }, [checkSystemStatus]);

  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <>
      <header className="py-3 px-5 border-b border-gray-200 flex justify-between items-center">
        <h1 className="text-blue-600 text-base font-medium">SMC Documentation Assistant</h1>
        <button 
          onClick={openModal}
          className="flex items-center bg-white py-2 px-4 rounded-full shadow-sm border border-gray-100 hover:bg-gray-50 transition-colors"
        >
          <span className="text-blue-600 mr-2"><Bot size={16} /></span>
          <span className="font-medium text-gray-700">AI</span>
          <div className="flex items-center ml-4 text-sm">
            <span className={`w-2 h-2 rounded-full ${status.dot} mr-1`}></span>
            <span className="text-gray-500">{status.text}</span>
          </div>
        </button>
      </header>
      
      <StatusModal 
        isOpen={isModalOpen} 
        onClose={closeModal} 
        status={systemStatus}
      />
    </>
  );
};

export default Header;