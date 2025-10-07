/**
 * TypeScript type definitions for ONLSuggest suggestion system.
 */

/**
 * A single suggestion returned by the backend.
 */
export interface Suggestion {
  /**
   * Full-text question suggestion (e.g., "Hoe vraag ik een parkeervergunning aan in Amsterdam?")
   */
  suggestion: string;

  /**
   * Confidence score (0.0 to 1.0)
   */
  confidence: number;

  /**
   * Optional service information if matched
   */
  service?: {
    id: number;
    name: string;
    description: string;
    category: string;
  };

  /**
   * Optional gemeente information if matched
   */
  gemeente?: {
    id: number;
    name: string;
    description: string;
  };
}

/**
 * Response from the /api/v1/suggestions endpoint.
 */
export interface SuggestionResponse {
  /**
   * User's partial query input
   */
  query: string;

  /**
   * List of suggestions (max 5)
   */
  suggestions: Suggestion[];

  /**
   * Response time in milliseconds
   */
  response_time_ms: number;
}
