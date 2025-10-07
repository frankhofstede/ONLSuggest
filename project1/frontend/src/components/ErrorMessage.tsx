// Story 2.5: Error States

import './ErrorMessage.css';

interface ErrorMessageProps {
  error: string;
  onRetry?: () => void;
}

export function ErrorMessage({ error, onRetry }: ErrorMessageProps) {
  return (
    <div className="error-message">
      <div className="error-message__icon">⚠️</div>
      <h3 className="error-message__title">Er is iets misgegaan</h3>
      <p className="error-message__text">{error}</p>
      {onRetry && (
        <button className="error-message__retry" onClick={onRetry}>
          Opnieuw proberen
        </button>
      )}
    </div>
  );
}
