import type { ChatRequest, ChatResponse, ArticleDetail, GraphData, NodeDetails, GraphStats } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new ApiError(
        response.status,
        `Falha ao consultar o agente: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error('Erro de conexão com o servidor. Verifique se o backend está rodando.');
  }
}

export async function getArticleDetail(experimentId: string): Promise<ArticleDetail> {
  try {
    const response = await fetch(`${API_URL}/article/${experimentId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new ApiError(404, `Article ${experimentId} not found in the database`);
      }
      throw new ApiError(
        response.status,
        `Failed to fetch article: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error('Erro de conexão com o servidor. Verifique se o backend está rodando.');
  }
}

export async function checkHealth(): Promise<{ status: string; redis: string; version: string }> {
  try {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return await response.json();
  } catch (error) {
    throw new Error('Backend não está acessível');
  }
}

export async function getGraph(experimentId: string): Promise<GraphData> {
  try {
    const response = await fetch(`${API_URL}/api/graph?experiment_id=${experimentId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new ApiError(404, `Graph for experiment ${experimentId} not found`);
      }
      throw new ApiError(
        response.status,
        `Failed to fetch graph: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error('Erro de conexão com o servidor. Verifique se o backend está rodando.');
  }
}

export async function getNodeDetails(nodeId: string): Promise<NodeDetails> {
  try {
    const response = await fetch(`${API_URL}/api/graph/node/${encodeURIComponent(nodeId)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new ApiError(404, `Node ${nodeId} not found`);
      }
      throw new ApiError(
        response.status,
        `Failed to fetch node details: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error('Erro de conexão com o servidor. Verifique se o backend está rodando.');
  }
}

export async function getGraphStats(): Promise<GraphStats> {
  try {
    const response = await fetch(`${API_URL}/api/graph/stats`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new ApiError(404, 'Graph statistics not found');
      }
      throw new ApiError(
        response.status,
        `Failed to fetch graph stats: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error('Erro de conexão com o servidor. Verifique se o backend está rodando.');
  }
}
