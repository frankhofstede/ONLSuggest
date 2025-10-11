// Story 3.1: Admin Feature Toggle for Suggestion Engine Selection
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminFetch } from '../utils/adminApi';
import './AdminSettings.css';

type SuggestionEngine = 'template' | 'koop';

interface SettingsResponse {
  suggestion_engine: SuggestionEngine;
}

interface UpdateResponse {
  success: boolean;
  suggestion_engine: SuggestionEngine;
}

export function AdminSettings() {
  const [engine, setEngine] = useState<SuggestionEngine>('template');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data: SettingsResponse = await adminFetch('/api/admin/settings');
      setEngine(data.suggestion_engine);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (newEngine: SuggestionEngine) => {
    if (newEngine === engine) return; // No change

    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const data: UpdateResponse = await adminFetch('/api/admin/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ suggestion_engine: newEngine }),
      });

      if (data.success) {
        setEngine(data.suggestion_engine);
        setSuccessMessage(`Suggestion engine gewijzigd naar: ${newEngine === 'template' ? 'Template Engine' : 'KOOP API'}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update setting');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="admin-settings">
      <header className="admin-settings__header">
        <h1>Instellingen</h1>
        <Link to="/admin" className="admin-settings__back-link">← Terug naar dashboard</Link>
      </header>

      <main className="admin-settings__main">
        {isLoading && <p>Instellingen laden...</p>}

        {error && (
          <div className="admin-settings__error">
            <p>Error: {error}</p>
            <button onClick={fetchSettings}>Opnieuw proberen</button>
          </div>
        )}

        {successMessage && (
          <div className="admin-settings__success">
            <p>✓ {successMessage}</p>
          </div>
        )}

        {!isLoading && (
          <section className="admin-settings__section">
            <h2>Suggestie Engine</h2>
            <p className="admin-settings__description">
              Kies welke suggestie engine gebruikt wordt voor het genereren van zoeksuggesties.
            </p>

            <div className="setting-group">
              <label className="setting-option">
                <input
                  type="radio"
                  name="suggestion_engine"
                  value="template"
                  checked={engine === 'template'}
                  onChange={() => handleToggle('template')}
                  disabled={isSaving}
                />
                <div className="setting-option__content">
                  <strong>Template Engine (Lokaal)</strong>
                  <p>Gebruikt lokale template engine met Nederlandse taalverwerking</p>
                </div>
              </label>

              <label className="setting-option">
                <input
                  type="radio"
                  name="suggestion_engine"
                  value="koop"
                  checked={engine === 'koop'}
                  onChange={() => handleToggle('koop')}
                  disabled={isSaving}
                />
                <div className="setting-option__content">
                  <strong>KOOP API (Extern)</strong>
                  <p>Gebruikt externe KOOP Suggester API van de overheid</p>
                </div>
              </label>
            </div>

            {isSaving && (
              <p className="admin-settings__saving">Opslaan...</p>
            )}

            <div className="admin-settings__status">
              <h3>Huidige status</h3>
              <div className="status-badge">
                <span className={`status-indicator status-indicator--${engine}`}></span>
                <strong>
                  {engine === 'template' ? 'Template Engine (Lokaal)' : 'KOOP API (Extern)'}
                </strong>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
