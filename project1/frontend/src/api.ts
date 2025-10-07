// Story 2.3: API Integration Service

import { SuggestionsResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async getSuggestions(query: string, maxResults: number = 5): Promise<SuggestionsResponse> {
    if (!query || query.trim().length === 0) {
      return {
        query: '',
        suggestions: [],
        response_time_ms: 0,
      };
    }

    const response = await fetch(`${this.baseUrl}/api/v1/suggestions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query.trim(),
        max_results: maxResults,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async checkHealth(): Promise<{ status: string; version: string; service: string }> {
    const response = await fetch(`${this.baseUrl}/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return response.json();
  }
}

// Export singleton instance
export const apiService = new ApiService();
