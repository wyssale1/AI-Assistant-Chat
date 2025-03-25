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
  }, [checkSystemStatus]);

  return (
    <footer className="bg-background py-2 px-5 border-t border-border-color h-15">
      <div className="flex justify-between text-text-secondary text-sm flex-wrap">
        <div className="flex items-center my-1">
          <Info size={16} className="mr-2" />
          <span>Ask questions about SMC documentation to get detailed answers with source references.</span>
        </div>
        <div className="flex items-center my-1">
          <Server size={16} className="mr-2" />
          <span>System Status: {systemInfo}</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;