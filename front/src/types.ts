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

// Graph types
export interface GraphNode {
  id: string;
  label: string;
  group: string;
  title: string;
  value: number;
}

export interface GraphEdge {
  from: string;
  to: string;
  value: number;
  title: string;
}

export interface GraphNodeTypes {
  [key: string]: number;
}

export interface MostConnectedNode {
  id: string;
  name: string;
  type: string;
  degree: number;
}

export interface DegreeDistribution {
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
}

export interface GraphStats {
  total_nodes: number;
  total_edges: number;
  node_types: GraphNodeTypes;
  avg_degree: number;
  max_degree: number;
  min_degree: number;
  most_connected_node: MostConnectedNode;
  top_connected_nodes: MostConnectedNode[];
  degree_distribution: DegreeDistribution;
  density: number;
  num_components: number;
  largest_component_size: number;
  avg_clustering: number;
  isolated_nodes: number;
  edge_types: Record<string, number>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: GraphStats;
}

// Node details types
export interface NodeAttributes {
  type: string;
  name: string;
  experiment_ids: string[];
}

export interface NodeDetails {
  id: string;
  attributes: NodeAttributes;
  degree: number;
  neighbors_count: number;
  neighbors: string[];
}
