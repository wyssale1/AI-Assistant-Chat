import { useState } from 'react';
import axios, { AxiosResponse } from 'axios';
import { SystemStatus, Source } from '../types';

interface QueryResponse {
  answer: string;
  sources: Source[];
  timing?: {
    total_seconds: number;
  };
  error?: string;
}

interface FeedbackData {
  query: string;
  answer: string;
  rating: number;
  comment: string;
}

interface FeedbackResponse {
  status: string;
  message?: string;
}

const useAPI = () => {
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
  
    // Function to get system status
    const checkSystemStatus = async (): Promise<SystemStatus> => {
      try {
        setLoading(true);
        setError(null);
        const response: AxiosResponse<SystemStatus> = await axios.get('/status');
        return response.data;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to check system status';
        setError(errorMessage);
        return {
          system: 'error',
          ollama: 'error',
          vectordb: 'error',
        };
      } finally {
        setLoading(false);
      }
    };
  
    // Function to send a query
    const sendQuery = async (query: string): Promise<QueryResponse> => {
      try {
        setLoading(true);
        setError(null);
        const response: AxiosResponse<QueryResponse> = await axios.post('/ask', { query });
        return response.data;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to process query';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setLoading(false);
      }
    };
  
    // Function to send feedback
    const sendFeedback = async (queryData: FeedbackData): Promise<FeedbackResponse> => {
      try {
        setLoading(true);
        setError(null);
        const response: AxiosResponse<FeedbackResponse> = await axios.post('/feedback', queryData);
        return response.data;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to submit feedback';
        setError(errorMessage);
        throw new Error(errorMessage);
      } finally {
        setLoading(false);
      }
    };
  
    return {
      loading,
      error,
      checkSystemStatus,
      sendQuery,
      sendFeedback,
    };
  };
  
  export default useAPI;
  