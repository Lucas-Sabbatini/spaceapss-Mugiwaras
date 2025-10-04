export interface ChatRequest {
  question: string;
  topK?: number;
}

export interface Source {
  id: string;
  title: string;
  year?: number;
  doi?: string;
  url?: string;
  score?: number;
}

export interface Section {
  heading: string;
  content: string;
}

export interface Article {
  id: string;
  title: string;
  authors: string[];
  year: number;
  doi?: string;
  url?: string;
  abstract: string;
  sections?: Section[];
  references?: string[];
  metadata?: Record<string, any>;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  article: Article;
}

export interface Message {
  role: 'user' | 'agent';
  content: string;
  sources?: Source[];
  article?: Article;
  timestamp: Date;
}
