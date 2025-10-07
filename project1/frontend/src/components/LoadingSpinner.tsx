// Story 2.5: Loading States

import './LoadingSpinner.css';

export function LoadingSpinner() {
  return (
    <div className="loading-spinner">
      <div className="loading-spinner__circle"></div>
      <p className="loading-spinner__text">Suggesties laden...</p>
    </div>
  );
}
