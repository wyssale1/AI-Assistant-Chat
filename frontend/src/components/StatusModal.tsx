import React from 'react';
import { X, Server, Database, Bot } from 'lucide-react';
import { SystemStatus } from '../types';

interface StatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  status: SystemStatus | null;
}

const StatusModal: React.FC<StatusModalProps> = ({ isOpen, onClose, status }) => {
  if (!isOpen) return null;

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'online':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-yellow-500';
    }
  };

  const formatStatusText = (statusStr: string): string => {
    if (statusStr === 'online') return 'Online';
    if (statusStr.startsWith('error:')) return statusStr.replace('error:', 'Error:');
    return 'Offline';
  };

  return (
    <div className="fixed inset-0 bg-gray-800 bg-opacity-40 backdrop-blur-sm flex items-center justify-center z-50 transition-all duration-200">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="text-lg font-medium">System Status</h3>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="p-5">
          {!status ? (
            <div className="text-center py-6">Loading status information...</div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center">
                  <Bot size={20} className="mr-3 text-blue-600" />
                  <div>
                    <p className="font-medium">AI Model (Ollama)</p>
                    <p className="text-sm text-gray-500">
                      {status.chat_model ? `Using ${status.chat_model}` : 'Model information unavailable'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center">
                  <span className={`w-3 h-3 rounded-full ${getStatusColor(status.ollama)} mr-2`}></span>
                  <span className="text-sm">{formatStatusText(status.ollama)}</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center">
                  <Database size={20} className="mr-3 text-blue-600" />
                  <div>
                    <p className="font-medium">Vector Database</p>
                    <p className="text-sm text-gray-500">
                      {status.document_count !== undefined 
                        ? `${status.document_count} document chunks`
                        : 'Document count unavailable'
                      }
                    </p>
                  </div>
                </div>
                <div className="flex items-center">
                  <span className={`w-3 h-3 rounded-full ${getStatusColor(status.vectordb)} mr-2`}></span>
                  <span className="text-sm">{formatStatusText(status.vectordb)}</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center">
                  <Server size={20} className="mr-3 text-blue-600" />
                  <div>
                    <p className="font-medium">Vision Model</p>
                    <p className="text-sm text-gray-500">
                      {status.vision_model ? `Using ${status.vision_model}` : 'Model information unavailable'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center">
                  <span className={`w-3 h-3 rounded-full ${status.ollama === 'online' ? 'bg-green-500' : 'bg-red-500'} mr-2`}></span>
                  <span className="text-sm">{status.ollama === 'online' ? 'Available' : 'Unavailable'}</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="bg-gray-50 p-3 flex justify-end rounded-b-lg">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default StatusModal;