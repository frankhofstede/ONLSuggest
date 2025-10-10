// Story 1.1: Basic Input Field with Character Minimum Validation
// Features:
// - UTF-8 Dutch character support (ë, ï, ü, é, etc.)
// - 2-character minimum validation with visual feedback
// - Debounced query change callback (150ms)
// - Keyboard navigation (Enter, Escape)
// - Clear visual feedback for validation state

import { useState, useEffect, FormEvent, ChangeEvent, KeyboardEvent } from 'react';
import './SearchBox.css';

interface SearchBoxProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  minChars?: number;
}

export function SearchBox({
  onSearch,
  isLoading = false,
  placeholder = 'Typ uw vraag...',
  minChars = 2
}: SearchBoxProps) {
  const [query, setQuery] = useState('');
  const [isValid, setIsValid] = useState(false);
  const [showValidation, setShowValidation] = useState(false);

  // Validate query length
  useEffect(() => {
    const valid = query.trim().length >= minChars;
    setIsValid(valid);

    // Show validation feedback after user has typed something
    if (query.length > 0) {
      setShowValidation(true);
    }
  }, [query, minChars]);

  // Debounced search trigger (150ms as per spec)
  useEffect(() => {
    if (!isValid) return;

    const debounceTimer = setTimeout(() => {
      onSearch(query.trim());
    }, 150);

    return () => clearTimeout(debounceTimer);
  }, [query, isValid]); // Removed onSearch from dependencies to prevent infinite loop

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (isValid) {
      onSearch(query.trim());
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setQuery('');
      setShowValidation(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setShowValidation(false);
  };

  // Determine input border color based on validation state
  const getInputClassName = () => {
    const baseClass = 'search-box__input';
    if (!showValidation || query.length === 0) return baseClass;
    return `${baseClass} ${isValid ? 'search-box__input--valid' : 'search-box__input--invalid'}`;
  };

  return (
    <div className="search-box-container">
      <form className="search-box" onSubmit={handleSubmit}>
        <div className="search-box__input-wrapper">
          <input
            type="text"
            className={getInputClassName()}
            value={query}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            autoFocus
            aria-label="Zoek naar gemeentelijke diensten"
            aria-invalid={showValidation && !isValid}
            aria-describedby={showValidation && !isValid ? 'search-validation' : undefined}
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
          disabled={!isValid || isLoading}
          aria-label="Zoeken"
        >
          {isLoading ? 'Zoeken...' : 'Zoeken'}
        </button>
      </form>

      {/* Validation feedback */}
      {showValidation && !isValid && query.length > 0 && (
        <p
          id="search-validation"
          className="search-box__validation"
          role="alert"
          aria-live="polite"
        >
          Typ minimaal {minChars} tekens om te zoeken
        </p>
      )}
    </div>
  );
}
