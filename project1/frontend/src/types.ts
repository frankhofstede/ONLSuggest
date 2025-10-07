// Story 2.3: API Integration Types

export interface Service {
  id: number;
  name: string;
  description: string;
  category: string;
}

export interface Suggestion {
  suggestion: string;
  confidence: number;
  service: Service;
  gemeente: string | null;
}

export interface SuggestionsResponse {
  query: string;
  suggestions: Suggestion[];
  response_time_ms: number;
}

export interface ApiError {
  detail: string;
}
