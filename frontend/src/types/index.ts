export interface Message {
    sender: 'user' | 'assistant';
    text?: string;
    isLoading?: boolean;
    error?: string;
    sources?: Source[];
    timing?: {
      total_seconds: number;
    };
  }
  
  export interface Source {
    document: string;
    page: number;
    section?: string;
  }
  
  export interface SystemStatus {
    system: string;
    ollama: string;
    vectordb: string;
    chat_model?: string;
    vision_model?: string;
    document_count?: number;
    available_models?: string[];
  }