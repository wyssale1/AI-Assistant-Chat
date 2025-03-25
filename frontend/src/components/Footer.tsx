import React, { useState, useEffect } from 'react';
import { Info, Server } from 'lucide-react';
import useAPI from '../hooks/useAPI';
import { SystemStatus } from '../types';

const Footer: React.FC = () => {
  const [systemInfo, setSystemInfo] = useState<string>('Checking...');
  const { checkSystemStatus } = useAPI();

  useEffect(() => {
    const fetchStatus = async (): Promise<void> => {
      try {
        const data: SystemStatus = await checkSystemStatus();
        
        if (data.ollama === 'online' && data.vectordb === 'online') {
          setSystemInfo('All systems operational');
        } else {
          let issues: string[] = [];
          if (data.ollama !== 'online') issues.push('LLM');
          if (data.vectordb !== 'online') issues.push('Vector Database');
          setSystemInfo(`Issues with: ${issues.join(', ')}`);
        }
      } catch (error) {
        setSystemInfo('Error checking system status');
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 300000);
    return () => clearInterval(interval);
  }, [checkSystemStatus]);

  return (
    <footer className="bg-gray-50 py-2 px-5 border-t border-gray-200">
      <div className="flex justify-between text-gray-500 text-sm flex-wrap">
        <div className="flex items-center my-1">
          <Info size={14} className="mr-2" />
          <span>Ask questions about SMC documentation to get detailed answers with source references.</span>
        </div>
        <div className="flex items-center my-1">
          <Server size={14} className="mr-2" />
          <span>System Status: {systemInfo}</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;