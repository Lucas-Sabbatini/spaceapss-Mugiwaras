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

// Interface completa do artigo enriquecido (retornado pelo endpoint /article/{experiment_id})
export interface ArticleDetail {
  experiment_id: string;
  doi?: string;
  title?: string;
  abstract?: string;
  summary_en?: string;
  year?: number;
  url?: string;
  authors: string[];
  institutions: string[];
  funding: string[];
  objectives: string[];
  hypotheses: string[];
  organisms: string[];
  conditions: string[];
  methods: string[];
  parameters_measured: string[];
  results_summary?: string;
  significant_findings: string[];
  implications: string[];
  limitations: string[];
  future_directions: string[];
  duration?: string;
  sample_size?: number;
  conditions_control: string[];
  related_projects: string[];
  citations?: number;
  full_text?: string;
  mesh_terms: string[];
  journal?: string;
  pmid?: string;
  created_at?: string;
  updated_at?: string;
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
