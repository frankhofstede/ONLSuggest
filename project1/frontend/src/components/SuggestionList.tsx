// Story 2.2: Suggestion List Component

import { Suggestion } from '../types';
import './SuggestionList.css';

interface SuggestionListProps {
  suggestions: Suggestion[];
  query: string;
}

export function SuggestionList({ suggestions, query }: SuggestionListProps) {
  if (suggestions.length === 0) {
    return (
      <div className="suggestion-list suggestion-list--empty">
        <p className="suggestion-list__empty-message">
          Geen suggesties gevonden voor "{query}". Probeer een ander zoekwoord.
        </p>
      </div>
    );
  }

  return (
    <div className="suggestion-list">
      <h2 className="suggestion-list__title">
        Suggesties voor "{query}"
      </h2>
      <ul className="suggestion-list__items">
        {suggestions.map((suggestion, index) => (
          <li key={index} className="suggestion-item">
            <div className="suggestion-item__header">
              <h3 className="suggestion-item__question">
                {suggestion.suggestion}
              </h3>
              <span className="suggestion-item__confidence" title="Betrouwbaarheid">
                {Math.round(suggestion.confidence * 100)}%
              </span>
            </div>
            <div className="suggestion-item__service">
              <span className="suggestion-item__service-name">
                {suggestion.service.name}
              </span>
              <span className="suggestion-item__category">
                {suggestion.service.category}
              </span>
            </div>
            <p className="suggestion-item__description">
              {suggestion.service.description}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
