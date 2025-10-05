import type { ChatRequest, ChatResponse, ArticleDetail } from '../types';

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
