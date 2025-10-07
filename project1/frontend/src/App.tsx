// Story 2.4: Main Page Layout
// Story 2.5: Loading & Error States

import { useState } from 'react';
import { SearchBox } from './components/SearchBox';
import { SuggestionList } from './components/SuggestionList';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorMessage } from './components/ErrorMessage';
import { apiService } from './api';
import { Suggestion } from './types';
import './App.css';

export function App() {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (searchQuery: string) => {
    setQuery(searchQuery);
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await apiService.getSuggestions(searchQuery, 5);
      setSuggestions(response.suggestions);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Er is een onbekende fout opgetreden. Controleer of de API bereikbaar is.'
      );
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (query) {
      handleSearch(query);
    }
  };

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__header-content">
          <h1 className="app__title">ONLSuggest</h1>
          <p className="app__subtitle">
            Vind snel de gemeentelijke dienst die u zoekt
          </p>
        </div>
      </header>

      <main className="app__main">
        <div className="app__search-section">
          <SearchBox
            onSearch={handleSearch}
            isLoading={isLoading}
            placeholder="Zoek bijvoorbeeld: parkeervergunning, paspoort, verhuizen..."
          />
        </div>

        <div className="app__results-section">
          {isLoading && <LoadingSpinner />}

          {error && !isLoading && (
            <ErrorMessage error={error} onRetry={handleRetry} />
          )}

          {!isLoading && !error && hasSearched && (
            <SuggestionList suggestions={suggestions} query={query} />
          )}

          {!hasSearched && !isLoading && !error && (
            <div className="app__welcome">
              <p className="app__welcome-text">
                Voer een zoekterm in om relevante gemeentelijke diensten te vinden
              </p>
              <div className="app__examples">
                <p className="app__examples-title">Voorbeelden:</p>
                <ul className="app__examples-list">
                  <li>"parkeervergunning"</li>
                  <li>"paspoort aanvragen"</li>
                  <li>"verhuizen doorgeven"</li>
                  <li>"trouwen"</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="app__footer">
        <p className="app__footer-text">
          ONLSuggest © 2025 - Demo versie 0.1.0
        </p>
      </footer>
    </div>
  );
}
