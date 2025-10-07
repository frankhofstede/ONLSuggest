// Story 2.1: SearchBox Component

import { useState, FormEvent, ChangeEvent } from 'react';
import './SearchBox.css';

interface SearchBoxProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export function SearchBox({ onSearch, isLoading = false, placeholder = 'Typ uw vraag...' }: SearchBoxProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleClear = () => {
    setQuery('');
  };

  return (
    <form className="search-box" onSubmit={handleSubmit}>
      <div className="search-box__input-wrapper">
        <input
          type="text"
          className="search-box__input"
          value={query}
          onChange={handleChange}
          placeholder={placeholder}
          disabled={isLoading}
          autoFocus
        />
        {query && (
          <button
            type="button"
            className="search-box__clear"
            onClick={handleClear}
            aria-label="Wissen"
            disabled={isLoading}
          >
            ✕
          </button>
        )}
      </div>
      <button
        type="submit"
        className="search-box__submit"
        disabled={!query.trim() || isLoading}
      >
        {isLoading ? 'Zoeken...' : 'Zoeken'}
      </button>
    </form>
  );
}
